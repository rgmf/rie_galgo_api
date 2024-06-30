import os
import base64
import logging

from pathlib import Path
from PIL import Image
from datetime import datetime, UTC, date

from fastapi import APIRouter, status, Depends, UploadFile
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.auth.auth import get_auth_user
from app.database.database import get_db
from app.database.models import User, AlbumIn, AlbumOut, AlbumObjectOut, AlbumCreate, MediaOut, MediaCreate
from app.database.crud import (
    get_albums,
    create_album as crud_create_album,
    create_media as crud_create_media
)

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(
    prefix="/albums",
    tags=["albums"]
)


@router.get("/", response_model=AlbumOut, status_code=status.HTTP_200_OK)
def read_albums(
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    return AlbumOut(data=get_albums(db, user.username))


@router.post("/", response_model=AlbumObjectOut, status_code=status.HTTP_200_OK)
def create_album(
        album: AlbumIn,
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    album = AlbumCreate(
        name=album.name,
        public=album.public,
        description=album.description,
        user_id=user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    return AlbumObjectOut(data=crud_create_album(db, album))


@router.post("/{album_id}/medias/", response_model=MediaOut, status_code=status.HTTP_200_OK)
async def create_media(
        album_id: int,
        files: list[UploadFile],
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    media_out = MediaOut(
        data=[]
    )

    upload_dir: str = os.getenv("UPLOAD_DIR")
    tmp_files_folder: str = os.path.join(upload_dir, "tmp")
    Path(tmp_files_folder).mkdir(parents=True, exist_ok=True)

    for file in files:
        # Copy file to a temporary location
        tmp_file_path: str = os.path.join(tmp_files_folder, file.filename)
        with open(tmp_file_path, "wb") as fo:
            chunk: bytes = await file.read(10_000)
            while chunk:
                fo.write(chunk)
                chunk = await file.read(10_000)

        # Check if it's a valid image... if os then move it to the destination
        try:
            with Image.open(tmp_file_path) as im:
                relative_dir_path = os.path.join("medias", date.today().isoformat())
                dst_path = os.path.join(upload_dir, relative_dir_path)
                Path(dst_path).mkdir(parents=True, exist_ok=True)

                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                combined_string = f"{relative_dir_path}{datetime.now(UTC).isoformat()}"
                hash = pwd_context.hash(combined_string)
                hash_base64 = base64.urlsafe_b64encode(hash.encode('utf-8')).decode('utf-8')

                extension = file.filename.split('.')[-1]

                relative_file_path = os.path.join(relative_dir_path, f"{hash_base64}.{extension}")
                Path(tmp_file_path)\
                    .rename(Path(os.path.join(upload_dir, relative_file_path)))

                media_create = MediaCreate(
                    name=str(file.filename),
                    hash=hash_base64,
                    data=str(relative_file_path),
                    thumbnail=str(relative_file_path),
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    size=0
                )
                media_out.data.append(crud_create_media(db, media_create))
        except OSError as error:
            logging.debug(f"'{tmp_file_path}' is not an image: {error}")
            # Delete the temporary file
            Path(tmp_file_path).unlink()

    return media_out
