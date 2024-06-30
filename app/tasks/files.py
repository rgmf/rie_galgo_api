import os
import base64
import logging

import exifread

from PIL import Image
from pathlib import Path
from datetime import datetime, UTC, date
from dataclasses import dataclass, field

from fastapi import UploadFile
from passlib.context import CryptContext

logging.basicConfig(level=logging.DEBUG)

BASE_UPLOAD_DIR = os.getenv("UPLOAD_DIR", "")

TMP_DIR_NAME = "tmp"
MEDIAS_DIR_NAME = "medias"

TMP_PATH = os.path.join(BASE_UPLOAD_DIR, TMP_DIR_NAME)
MEDIAS_PATH = os.path.join(BASE_UPLOAD_DIR, MEDIAS_DIR_NAME)


@dataclass
class Exif:
    date_time_original_dt: datetime | None = field(init=False)
    date_time_original: exifread.classes.IfdTag | None

    def __post_init__(self):
        if self.date_time_original is None:
            self.date_time_original_dt = None
            return

        dto: str = str(self.date_time_original)
        if len(dto) != 19:
            self.date_time_original_dt = None
            return

        try:
            self.date_time_original_dt = datetime.fromisoformat(
                dto[:4] + "-" + dto[5:7] + "-" + dto[8:10] + "T" +
                dto[11:13] + ":" + dto[14:16] + ":" + dto[17:19]
            )
        except Exception:
            self.date_time_original_dt = None


def generate_base64_hash(text: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    combined_string = f"{text}{datetime.now(UTC).isoformat()}"
    hash = pwd_context.hash(combined_string)
    return base64.urlsafe_b64encode(hash.encode('utf-8')).decode('utf-8')


async def upload_file(file: UploadFile) -> tuple[str, str, float] | None:
    Path(TMP_PATH).mkdir(parents=True, exist_ok=True)

    tmp_file_path: str = os.path.join(TMP_PATH, file.filename)
    with open(tmp_file_path, "wb") as fo:
        chunk: bytes = await file.read(10_000)
        while chunk:
            fo.write(chunk)
            chunk = await file.read(10_000)

    try:
        with Image.open(tmp_file_path) as im:
            relative_dir_path = os.path.join(MEDIAS_DIR_NAME, date.today().isoformat())
            dst_path = os.path.join(BASE_UPLOAD_DIR, relative_dir_path)
            Path(dst_path).mkdir(parents=True, exist_ok=True)

            hash_base64 = generate_base64_hash(relative_dir_path)

            extension = file.filename.split('.')[-1]

            relative_file_path = os.path.join(relative_dir_path, f"{hash_base64}.{extension}")
            absolute_file_path = os.path.join(BASE_UPLOAD_DIR, relative_file_path)
            Path(tmp_file_path).rename(Path(absolute_file_path))

            file_size = Path(absolute_file_path).stat().st_size

            return relative_file_path, hash_base64, file_size

    except OSError as error:
        logging.debug(f"'{tmp_file_path}' is not an image: {error}")
        Path(tmp_file_path).unlink()

    return None


async def read_exif(relative_file_path: str) -> Exif:
    date_time_original = None

    with open(os.path.join(BASE_UPLOAD_DIR, relative_file_path), "rb") as fo:
        tags = exifread.process_file(fo)
        if "Image DateTimeOriginal" in tags:
            date_time_original = tags["Image DateTimeOriginal"]
        elif "Image DateTime" in tags:
            date_time_original = tags["Image DateTime"]

    return Exif(date_time_original=date_time_original)
