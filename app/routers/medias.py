from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.auth.auth import get_auth_user
from app.database.database import get_db
from app.database.models import User, MediaOut
from app.database.crud import get_ephemeris

router = APIRouter(
    prefix="/medias",
    tags=["medias"]
)


@router.get("/ephemeris/", response_model=MediaOut, status_code=status.HTTP_200_OK)
def read_ephemeris(
        user: User = Depends(get_auth_user),
        db: Session = Depends(get_db)
):
    return MediaOut(data=get_ephemeris(db, user.username))
