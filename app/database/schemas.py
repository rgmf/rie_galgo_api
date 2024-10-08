from sqlalchemy import (
    DateTime, Boolean, Column, ForeignKey, UniqueConstraint, Integer, String,
    Text, func, Double
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    password = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    albums = relationship("Album", back_populates="user")


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    hash = Column(String(172), nullable=False)
    data = Column(Text, nullable=False)
    thumbnail = Column(Text, nullable=False)
    size = Column(Integer, nullable=False)
    media_created = Column(DateTime, nullable=False, default="1970-01-01 00:00:00")
    media_type = Column(String(255))
    mime_type = Column(String(255))
    latitude = Column(Double)
    longitude = Column(Double)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    album_media = relationship("AlbumMedia", back_populates="media", uselist=False)

    __table_args__ = (
        UniqueConstraint('hash', 'size', 'media_created', name='hash_size_media_created_uc'),
    )

    @property
    def album(self):
        return self.album_media.album if self.album_media else None


class Album(Base):
    __tablename__ = 'albums'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    public = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship('User', back_populates='albums')
    album_media = relationship('AlbumMedia', back_populates='album')


class AlbumMedia(Base):
    __tablename__ = 'album_media'

    id = Column(Integer, primary_key=True, autoincrement=True)
    album_id = Column(Integer, ForeignKey('albums.id', ondelete="CASCADE"), nullable=False)
    media_id = Column(Integer, ForeignKey('medias.id', ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    album = relationship('Album', back_populates='album_media')
    media = relationship('Media', back_populates="album_media")

    __table_args__ = (UniqueConstraint('album_id', 'media_id', name='album_id_media_id_uc'),)


class Trash(Base):
    __tablename__ = 'trash'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    hash = Column(String(172), unique=True)
    data = Column(Text, nullable=False)
    size = Column(Integer, nullable=False)
    media_type = Column(String(255))
    mime_type = Column(String(255))
    longitude = Column(String(50))
    latitude = Column(String(50))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
