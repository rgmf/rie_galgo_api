import logging

from datetime import datetime, UTC

from fastapi import APIRouter, status, Depends, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.auth.auth import get_auth_user
from app.database.database import get_db
from app.database.models import (
    User, AlbumIn, AlbumOut, AlbumObjectOut, AlbumCreate, MediaCreate,
    MediaUpload, MediaUploadOut
)
from app.database.crud import (
    get_albums,
    create_album as crud_create_album,
    create_media as crud_create_media
)
from app.tasks.files import FileUploader

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


@router.post("/{album_id}/medias/", response_model=MediaUploadOut, status_code=status.HTTP_200_OK)
async def create_media(
        album_id: int,
        files: list[UploadFile],
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    media_upload_out = MediaUploadOut(
        data=MediaUpload(valid=[], invalid=[])
    )

    for file in files:
        file_uploader = FileUploader(file)
        await file_uploader.upload()
        file_uploader.cleanup()

        if not file_uploader.has_error():
            try:
                media_create = MediaCreate(
                    name=str(file.filename),
                    hash=file_uploader.file_hash,
                    data=file_uploader.relative_file_path,
                    thumbnail=file_uploader.relative_file_path,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    size=file_uploader.file_size,
                    media_created=file_uploader.metadata().date_time_original_dt,
                    mime_type=file_uploader.mime_type,
                    media_type=file_uploader.media_type,
                    latitude=file_uploader.metadata().latitude_decimal_degrees,
                    longitude=file_uploader.metadata().longitude_decimal_degrees
                )
                media_upload_out.data.valid.append(crud_create_media(db, media_create))
            except IntegrityError as e:
                media_upload_out.data.invalid.append(
                    f"Error uploading {file.filename}: the file already exists"
                )
                logging.debug(f"Error uploading {file.filename}: the file already exists: {e}")
        else:
            media_upload_out.data.invalid.append(
                f"Error uploading {file.filename} file: {file_uploader.error()}"
            )

    return media_upload_out
