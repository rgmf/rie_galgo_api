from sqlalchemy.orm import Session

from . import schemas, models


def get_user_by_username(db: Session, username: str):
    return db.query(schemas.User).filter(schemas.User.username == username).first()


def get_albums(db: Session, username: str):
    return db.query(schemas.Album)\
             .join(schemas.User)\
             .filter(schemas.User.username == username)\
             .order_by(schemas.Album.updated_at.desc())\
             .all()


def create_album(db: Session, album: models.AlbumCreate):
    db_album = schemas.Album(**album.dict())
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album


def get_ephemeris(db: Session, username: str):
    return []


def create_media(db: Session, media: models.MediaCreate):
    db_media = schemas.Media(**media.dict())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media
