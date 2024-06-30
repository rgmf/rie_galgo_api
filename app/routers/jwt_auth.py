from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth import Token, create_access_token, verify_password
from app.database.models import User
from app.database.database import get_db
from app.database.crud import get_user_by_username

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


def authenticate_user(user: User, password: str) -> User | None:
    if user is None:
        return None

    if not verify_password(password, user.password):
        return None

    return user


@router.post("/login/", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user: User | None = authenticate_user(
        get_user_by_username(db, form_data.username),
        form_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username and/or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return create_access_token(user)
