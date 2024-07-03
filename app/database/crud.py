from datetime import datetime, UTC

from sqlalchemy.orm import Session

from . import schemas, models


def get_user_by_username(db: Session, username: str):
    return db.query(schemas.User).filter(schemas.User.username == username).first()


def get_album_by_id(db: Session, id: int):
    return db.query(schemas.Album).get(id)


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


def get_media_by_id(db: Session, id: int):
    return db.query(schemas.Media).get(id)


def get_ephemeris(db: Session, username: str):
    return []


def create_media(db: Session, media: models.MediaCreate, album_id: int):
    db_media = schemas.Media(**media.dict())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)

    album_media = models.AlbumMediaCreate(
        media_id=db_media.id,
        album_id=album_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db_album_media = schemas.AlbumMedia(**album_media.dict())
    db.add(db_album_media)
    db.commit()
    db.refresh(db_album_media)

    return db_media
