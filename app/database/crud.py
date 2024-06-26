from sqlalchemy.orm import Session

from . import schemas


def get_user_by_username(db: Session, username: str):
    return db.query(schemas.User).filter(schemas.User.username == username).first()
