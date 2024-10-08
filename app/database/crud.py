from datetime import datetime, UTC

from sqlalchemy import extract, or_
from sqlalchemy.orm import Session

from . import schemas, models


def get_user_by_username(db: Session, username: str) -> models.User | None:
    user = db.query(schemas.User).filter(schemas.User.username == username).first()
    if user is None:
        return None
    return models.User.from_orm(user)


def get_album_by_id(db: Session, id: int) -> models.Album | None:
    album = db.query(schemas.Album).get(id)
    if album is None:
        return None
    return models.Album.from_orm(album)


def get_albums(db: Session, username: str) -> list[models.Album]:
    albums = db.query(schemas.Album)\
               .join(schemas.User)\
               .filter(schemas.User.username == username)\
               .order_by(schemas.Album.updated_at.desc())\
               .all()
    return [models.Album.from_orm(a) for a in albums]


def get_album_medias(db: Session, id: int, skip: int, limit: int) -> list[models.Media]:
    medias = db.query(schemas.Media)\
               .join(schemas.AlbumMedia, schemas.Media.id == schemas.AlbumMedia.media_id)\
               .filter(schemas.AlbumMedia.album_id == id)\
               .order_by(schemas.Media.media_created.desc())\
               .offset(skip)\
               .limit(limit)\
               .all()
    return [models.Media.from_orm(m) for m in medias]


def get_album_cover(db: Session, id: int) -> models.Media:
    return db.query(schemas.Media)\
             .join(schemas.AlbumMedia, schemas.Media.id == schemas.AlbumMedia.media_id)\
             .filter(schemas.AlbumMedia.album_id == id)\
             .order_by(schemas.Media.media_created.desc())\
             .first()


def create_album(db: Session, album: models.AlbumCreate) -> models.Album:
    db_album = schemas.Album(**album.dict())
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return models.Album.from_orm(db_album)


def get_media_by_id(db: Session, id: int) -> models.Media | None:
    media = db.query(schemas.Media).get(id)
    if media is None:
        return None
    return models.Media.from_orm(media)


def get_ephemeris(db: Session, user_id: int, skip: int, limit: int) -> list[models.Media]:
    medias = db.query(schemas.Media)\
                .join(schemas.AlbumMedia, schemas.Media.id == schemas.AlbumMedia.media_id)\
                .join(schemas.Album, schemas.AlbumMedia.album_id == schemas.Album.id)\
                .filter(
                    extract("month", schemas.Media.media_created) == datetime.today().month,
                    extract("day", schemas.Media.media_created) == datetime.today().day,
                    or_(schemas.Album.user_id == user_id, schemas.Album.public.is_(True))
                )\
                .distinct(schemas.Media.id)\
                .order_by(schemas.Media.media_created.asc())\
                .offset(skip)\
                .limit(limit)\
                .all()

    return [models.Media.from_orm(m) for m in medias]


def create_media(db: Session, media: models.MediaCreate, album_id: int) -> models.Media:
    db_media = schemas.Media(**media.dict())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)

    db_album = db.query(schemas.Album).get(album_id)
    db_album.updated_at = datetime.now(UTC)
    db.commit()

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

    return models.Media.from_orm(db_media)
