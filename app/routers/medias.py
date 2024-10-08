import os

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.error_models import ErrorModel
from app.auth.auth import get_auth_user
from app.database.database import get_db
from app.database.models import User, MediaOut, MediaObjectOut, Media
from app.database.crud import get_ephemeris, get_media_by_id
from app.tasks.files import BASE_UPLOAD_DIR, THUMBNAIL_FALLBACK_FILE_PATH


router = APIRouter(
    prefix="/medias",
    tags=["medias"]
)


def validate_media_access(media: Media, user: User):
    if media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    if media.album is None:
        raise HTTPException(status_code=404, detail="Album for this media not found")
    if media.album.user_id != user.id and not media.album.public:
        raise HTTPException(status_code=403, detail="Forbidden access to a media from other user private album")


@router.get("/ephemeris/", response_model=MediaOut, status_code=status.HTTP_200_OK)
def read_ephemeris(
        skip: int = 0,
        limit: int = 50,
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    return MediaOut(data=get_ephemeris(db, user.id, skip, limit))


@router.get(
    "/{id}/",
    response_model=MediaObjectOut,
    status_code=status.HTTP_201_CREATED,
    responses={403: {"model": ErrorModel}, 404: {"model": ErrorModel}}
)
def read_media(
        id: int,
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    media: Media = get_media_by_id(db, id)
    validate_media_access(media, user)
    return MediaObjectOut(data=media)


@router.get(
    "/{id}/data/",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
    responses={403: {"model": ErrorModel}, 404: {"model": ErrorModel}}
)
def read_media_data(
        id: int,
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    media: Media = get_media_by_id(db, id)
    validate_media_access(media, user)

    file_path: str = os.path.join(BASE_UPLOAD_DIR, media.data)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return file_path


@router.get(
    "/{id}/thumbnail/",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
    responses={403: {"model": ErrorModel}, 404: {"model": ErrorModel}}
)
def read_media_thumbnail(
        id: int,
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    media: Media = get_media_by_id(db, id)
    validate_media_access(media, user)

    file_path: str = os.path.join(BASE_UPLOAD_DIR, media.thumbnail)
    if os.path.exists(file_path):
        return file_path

    if os.path.exists(THUMBNAIL_FALLBACK_FILE_PATH):
        return THUMBNAIL_FALLBACK_FILE_PATH

    raise HTTPException(status_code=404, detail="Thumbnail file not found")
