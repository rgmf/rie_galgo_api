from fastapi import APIRouter, status, Depends

from app.auth.auth import get_auth_user
from app.database.models import User, UserBase, UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me/", response_model=UserOut, status_code=status.HTTP_200_OK)
def read_user(
    user: User = Depends(get_auth_user)
):
    return UserOut(data=UserBase(username=user.username, email=user.email))
