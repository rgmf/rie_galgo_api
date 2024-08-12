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


class AlbumBase(BaseModel):
    name: str
    public: bool
    description: str | None = None


class AlbumCreate(AlbumBase):
    user_id: int
    created_at: datetime
    updated_at: datetime


class Album(AlbumCreate):
    id: int

    class Config:
        from_attributes = True


class AlbumIn(AlbumBase):
    pass


class AlbumWithCover(Album):
    cover: str | None = None


class AlbumOut(BaseModel):
    data: list[AlbumWithCover]


class AlbumObjectOut(BaseModel):
    data: AlbumWithCover


class AlbumMediaBase(BaseModel):
    created_at: datetime
    updated_at: datetime


class AlbumMediaCreate(AlbumMediaBase):
    album_id: int
    media_id: int


class AlbumMedia(AlbumMediaCreate):
    id: int

    class Config:
        from_attributes = True


class MediaBase(BaseModel):
    name: str
    hash: str
    data: str
    thumbnail: str
    created_at: datetime
    updated_at: datetime
    size: int
    media_created: datetime
    media_type: str | None = None
    mime_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class MediaCreate(MediaBase):
    pass


class Media(MediaBase):
    id: int
    album: Album | None = None

    class Config:
        from_attributes = True


class MediaOut(BaseModel):
    data: list[Media]


class MediaObjectOut(BaseModel):
    data: Media


class MediaUpload(BaseModel):
    filename: str
    upload_error: bool
    message: str
    media: Media | None = None


class MediaUploadOut(BaseModel):
    data: MediaUpload
