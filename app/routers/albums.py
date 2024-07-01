from datetime import datetime, UTC

from fastapi import APIRouter, status, Depends, UploadFile
from sqlalchemy.orm import Session

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
from app.tasks.files import upload_file, read_exif, Exif, UploadFileResult

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
        result: UploadFileResult | None = await upload_file(file)
        if result:
            exif: Exif = await read_exif(result.relative_file_path)
            media_create = MediaCreate(
                name=str(file.filename),
                hash=result.hash_base64,
                data=result.relative_file_path,
                thumbnail=result.relative_file_path,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                size=result.file_size,
                media_created=exif.date_time_original_dt,
                mime_type=result.mime_type,
                media_type=result.media_type,
                latitude=exif.latitude_decimal_degrees,
                longitude=exif.longitude_decimal_degrees
            )
            media_upload_out.data.valid.append(crud_create_media(db, media_create))
        else:
            media_upload_out.data.invalid.append(f"{file.filename} is not a valid and accepted media file")

    return media_upload_out
