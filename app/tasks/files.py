import os
import logging

import exifread
import imagehash

from PIL import Image
from pathlib import Path
from datetime import datetime, date
from dataclasses import dataclass, field
from fractions import Fraction

from fastapi import UploadFile

logging.basicConfig(level=logging.DEBUG)

BASE_UPLOAD_DIR = os.getenv("UPLOAD_DIR", "")

TMP_DIR_NAME = "tmp"
MEDIAS_DIR_NAME = "medias"

TMP_PATH = os.path.join(BASE_UPLOAD_DIR, TMP_DIR_NAME)
MEDIAS_PATH = os.path.join(BASE_UPLOAD_DIR, MEDIAS_DIR_NAME)

UNKNOWN_FORMAT_KEY = "unknown"
IMAGE_FORMAT_KEY = "image"
VIDEO_FORMAT_KEY = "video"
SUPPORTED_FORMATS = {
    IMAGE_FORMAT_KEY: {
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "giff": "image/gif",
        "bmp": "image/bmp",
        "tiff": "image/tiff"
    },
    VIDEO_FORMAT_KEY: {
    },
    UNKNOWN_FORMAT_KEY: "unknown/unknown"
}


@dataclass
class Exif:
    date_time_original_dt: datetime | None = field(init=False)
    date_time_original: exifread.classes.IfdTag | None = None

    latitude_decimal_degrees: float | None = field(init=False)
    latitude_ref: exifread.classes.IfdTag | None = None
    latitude: exifread.classes.IfdTag | None = None

    longitude_decimal_degrees: float | None = field(init=False)
    longitude_ref: exifread.classes.IfdTag | None = None
    longitude: exifread.classes.IfdTag | None = None

    def __post_init__(self):
        self.__compute_date_time_original()
        self.__compute_latitude_and_longitude()

    def __compute_date_time_original(self):
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

    def __compute_latitude_and_longitude(self):
        if (
                not self.latitude or not self.longitude or not self.latitude_ref or not self.longitude_ref or
                len(self.latitude.values) != 3 or len(self.longitude.values) != 3
        ):
            self.latitude_decimal_degrees = None
            self.longitude_decimal_degrees = None
            return

        self.latitude_decimal_degrees = convert_to_decimal_degrees(self.latitude.values)
        self.longitude_decimal_degrees = convert_to_decimal_degrees(self.longitude.values)

        if str(self.latitude_ref) != "N":
            self.latitude_decimal_degrees = -self.latitude_decimal_degrees

        if str(self.longitude_ref) != "E":
            self.longitude_decimal_degrees = -self.longitude_decimal_degrees


def convert_to_decimal_degrees(values: list[float, float, float]) -> float:
    degrees = float(values[0])
    minutes = float(values[1])
    seconds = float(Fraction(values[2]))

    decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)

    return decimal_degrees


class FileUploader:
    def __init__(self, file: UploadFile):
        Path(TMP_PATH).mkdir(parents=True, exist_ok=True)

        self.__file: UploadFile = file
        self.__tmp_file_path: str = os.path.join(TMP_PATH, file.filename)
        self.__relative_dir_path: str = os.path.join(MEDIAS_DIR_NAME, date.today().isoformat())
        self.__absolute_dir_path: str = os.path.join(BASE_UPLOAD_DIR, self.__relative_dir_path)

        self.__absolute_file_path: str | None = None
        self.relative_file_path: str | None = None
        self.file_hash: str | None = None
        self.file_size: float | None = None
        self.mime_type: str | None = None
        self.media_type: str = IMAGE_FORMAT_KEY
        self.__exif: Exif | None = None

        self.__error: str | None = None

    async def upload(self):
        await self.__upload_tmp_file()
        if self.has_error():
            return

        await self.__process_image()
        if self.has_error():
            return

        await self.__read_exif()

    def cleanup(self):
        try:
            Path(self.__tmp_file_path).unlink()
        except FileNotFoundError:
            pass

    def has_error(self) -> bool:
        return self.__error is not None

    def error(self) -> str:
        return self.__error if self.__error is not None else ""

    def exif(self) -> Exif:
        return self.__exif if self.__exif is not None else Exif()

    async def __upload_tmp_file(self):
        try:
            with open(self.__tmp_file_path, "wb") as fo:
                chunk: bytes = await self.__file.read(10_000)
                while chunk:
                    fo.write(chunk)
                    chunk = await self.__file.read(10_000)
        except OSError as error:
            self.__error = f"Error uploading {self.__file.filename}."
            logging.debug(f"{self.__error}: {error}")
        except Exception as error:
            logging.error(f"Error saving temp file '{self.__tmp_file_path}': {error}")

    async def __process_image(self):
        try:
            with Image.open(self.__tmp_file_path) as im:
                self.file_hash = str(imagehash.phash(im))

                Path(self.__absolute_dir_path).mkdir(parents=True, exist_ok=True)

                extension = self.__file.filename.split(".")[-1]

                self.relative_file_path = os.path.join(self.__relative_dir_path, f"{self.file_hash}.{extension}")
                self.__absolute_file_path = os.path.join(BASE_UPLOAD_DIR, self.relative_file_path)
                Path(self.__tmp_file_path).rename(Path(self.__absolute_file_path))

                self.file_size = Path(self.__absolute_file_path).stat().st_size
                format = im.format.lower()
                self.mime_type = (
                    SUPPORTED_FORMATS[IMAGE_FORMAT_KEY][format]
                    if format in SUPPORTED_FORMATS[IMAGE_FORMAT_KEY]
                    else SUPPORTED_FORMATS[UNKNOWN_FORMAT_KEY]
                )
        except OSError as error:
            self.__error = f"'{self.__tmp_file_path}' is not an image: {error}"
            logging.debug(self.__error)
        except Exception as error:
            logging.error(f"Error uploading file '{self.__tmp_file_path}': {error}")

    async def __read_exif(self):
        date_time_original = None
        latitude = None
        longitude = None
        latitude_ref = None
        longitude_ref = None

        try:
            with open(self.__absolute_file_path, "rb") as file_object:
                tags = exifread.process_file(file_object)

                if "Image DateTimeOriginal" in tags:
                    date_time_original = tags["Image DateTimeOriginal"]
                elif "Image DateTime" in tags:
                    date_time_original = tags["Image DateTime"]

                if (
                        "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags and
                        "GPS GPSLatitudeRef" in tags and "GPS GPSLongitudeRef" in tags
                ):
                    latitude = tags["GPS GPSLatitude"]
                    longitude = tags["GPS GPSLongitude"]
                    latitude_ref = tags["GPS GPSLatitudeRef"]
                    longitude_ref = tags["GPS GPSLongitudeRef"]
        except OSError as error:
            logging.debug(f"Error reading exif data from {self.__absolute_file_path}: {error}")
        except Exception as error:
            logging.error(f"Error reading exif data from {self.__absolute_file_path}: {error}")

        self.__exif = Exif(
            date_time_original=date_time_original,
            latitude=latitude,
            longitude=longitude,
            latitude_ref=latitude_ref,
            longitude_ref=longitude_ref
        )
