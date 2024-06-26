from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    password: str
    albums: list["Album"] = []

    class Config:
        from_attributes = True


class MediaBase(BaseModel):
    name: str
    hash: str
    data: str
    thumbnail: str
    created_at: datetime
    updated_at: datetime
    size: int | None = None
    media_created: datetime | None = None
    media_type: str | None = None
    mime_type: str | None = None
    latitude: str | None = None
    longitude: str | None = None


class MediaCreate(MediaBase):
    pass


class Media(MediaBase):
    id: int

    class Config:
        from_attributes = True


class AlbumBase(BaseModel):
    name: str
    public: bool
    created_at: datetime
    updated_at: datetime
    description: str | None = None


class AlbumCreate(AlbumBase):
    pass


class Album(AlbumBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class AlbumMediaBase(BaseModel):
    created_at: datetime
    updated_at: datetime


class AlbumMediaCreate(AlbumMediaBase):
    pass


class AlbumMedia(AlbumMediaBase):
    id: int
    album_id: int
    media_id: int

    class Config:
        from_attributes = True
