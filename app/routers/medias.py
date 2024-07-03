from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.error_models import Error404Model
from app.auth.auth import get_auth_user
from app.database.database import get_db
from app.database.models import User, MediaOut, MediaObjectOut, Media
from app.database.crud import get_ephemeris, get_media_by_id

router = APIRouter(
    prefix="/medias",
    tags=["medias"]
)


@router.get(
    "/{id}/",
    response_model=MediaObjectOut,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": Error404Model}}
)
def read_media(
        id: int,
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    media: Media = get_media_by_id(db, id)
    if media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    return MediaObjectOut(data=media)


@router.get("/ephemeris/", response_model=MediaOut, status_code=status.HTTP_200_OK)
def read_ephemeris(
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    return MediaOut(data=get_ephemeris(db, user.username))
