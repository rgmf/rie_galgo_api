import logging

from datetime import datetime, UTC

from fastapi import APIRouter, status, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.error_models import ErrorModel
from app.auth.auth import get_auth_user
from app.database.database import get_db
from app.database.models import (
    User, Album, AlbumIn, AlbumOut, AlbumObjectOut, AlbumCreate, MediaCreate,
    MediaUpload, MediaUploadOut, MediaOut, AlbumWithCover, Media, MediaErrorUpload
)
from app.database.crud import (
    get_albums,
    get_album_by_id,
    get_album_medias,
    get_album_cover,
    create_album as crud_create_album,
    create_media as crud_create_media
)
from app.tasks.files import FileUploader, get_base64_media_data

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(
    prefix="/albums",
    tags=["albums"]
)


def validate_album_access(album: Album, user: User):
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    if album.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden action for the user")


@router.get("/", response_model=AlbumOut, status_code=status.HTTP_200_OK)
def read_albums(
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    albums: list[Album] = get_albums(db, user.username)
    response: list[AlbumWithCover] = []
    for a in albums:
        media_cover: Media | None = get_album_cover(db, a.id)
        album_with_cover = AlbumWithCover(**a.model_dump())
        album_with_cover.cover = get_base64_media_data(media_cover.thumbnail) if media_cover else None
        response.append(album_with_cover)

    return AlbumOut(data=response)


@router.get(
    "/{id}/medias/",
    response_model=MediaOut,
    status_code=status.HTTP_200_OK,
    responses={403: {"model": ErrorModel}, 404: {"model": ErrorModel}}
)
def read_album_medias(
        id: int,
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    album: Album = get_album_by_id(db, id)
    validate_album_access(album, user)
    return MediaOut(data=get_album_medias(db, id))


@router.post("/", response_model=AlbumObjectOut, status_code=status.HTTP_201_CREATED)
def create_album(
        album: AlbumIn,
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    album_to_create = AlbumCreate(
        name=album.name,
        public=album.public,
        description=album.description,
        user_id=user.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    album: Album = crud_create_album(db, album_to_create)
    if not album:
        return HTTPException(500, "Albums seems to be created but not returned")

    return AlbumObjectOut(data=AlbumWithCover(**album.model_dump()))


@router.post(
    "/{id}/medias/",
    response_model=MediaUploadOut,
    status_code=status.HTTP_201_CREATED,
    responses={403: {"model": ErrorModel}, 404: {"model": ErrorModel}}
)
async def create_media(
        id: int,
        files: list[UploadFile],
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    album: Album = get_album_by_id(db, id)
    validate_album_access(album, user)

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
                    thumbnail=file_uploader.relative_thumbnail_path,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    size=file_uploader.file_size,
                    media_created=file_uploader.metadata.date_time_original_dt,
                    mime_type=file_uploader.mime_type,
                    media_type=file_uploader.media_type,
                    latitude=file_uploader.metadata.latitude_decimal_degrees,
                    longitude=file_uploader.metadata.longitude_decimal_degrees
                )
                media_upload_out.data.valid.append(crud_create_media(db, media_create, album.id))
            except IntegrityError as e:
                db.rollback()
                media_upload_out.data.invalid.append(
                    MediaErrorUpload(
                        name=file.filename,
                        error=f"Error uploading {file.filename}: the file already exists"
                    )
                )
                logging.debug(f"Error uploading {file.filename}: the file already exists: {e}")
        else:
            media_upload_out.data.invalid.append(
                MediaErrorUpload(
                    name=file.filename,
                    error=f"Error uploading {file.filename} file: {file_uploader.error()}"
                )
            )

    return media_upload_out
