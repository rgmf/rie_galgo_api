"""Tests description

In this conftest a database with a user es created and populated.

The username is 'alice' and she has two albums (public and private) with
several tests images that you can see in media/*
"""
from datetime import datetime

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.database import models, schemas
from app.auth.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://riegalgo:riegalgo@rie_galgo_mysql_test:3306/riegalgo_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestData:
    def __init__(self):
        self.db_session = None
        self.user = None
        self.album_public = None
        self.album_private = None

test_data = TestData()


@pytest.fixture(scope="function")
def db_session():
    """Create database and dropt it at the end."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def create_user(db_session):
    """Create and add a user into database."""
    user = models.UserCreate(
        username="alice",
        email="alice@alice.al",
        password=get_password_hash("alice")
    )
    db_user = schemas.User(**user.dict())
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


def create_albums_for_user(db_session, db_user):
    """Create two albums: public and private for the user db_User."""
    album_public = models.AlbumCreate(
        name=f"Album public {db_user.username}",
        public=True,
        user_id=db_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_album_public = schemas.Album(**album_public.dict())
    db_session.add(db_album_public)
    db_session.commit()
    db_session.refresh(db_album_public)

    album_private = models.AlbumCreate(
        name=f"Album private {db_user.username}",
        public=False,
        user_id=db_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_album_private = schemas.Album(**album_private.dict())
    db_session.add(db_album_private)
    db_session.commit()
    db_session.refresh(db_album_private)

    return db_album_public, db_album_private


def create_and_add_medias_to_album(db_session, db_album, from_num, to_num):
    """Create and add count medias to the album."""
    for i in range(from_num, to_num + 1):
        media = models.MediaCreate(
            name=f"Media {i}",
            hash=f"hash{i}",
            data=f"medias/2024-07-0{i}/{i}.jpg",
            thumbnail=f"thumbnails/2024-07-0{i}/{i}.jpg",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            size=30000,
            media_created=f"2024-07-0{i}T00:00:00"
        )
        db_media = schemas.Media(**media.dict())
        db_session.add(db_media)
        db_session.commit()
        db_session.refresh(db_media)

        album_media = models.AlbumMediaCreate(
            media_id=db_media.id,
            album_id=db_album.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_album_media = schemas.AlbumMedia(**album_media.dict())
        db_session.add(db_album_media)
        db_session.commit()
        db_session.refresh(db_album_media)


@pytest.fixture(scope="function")
def populate_test_data(db_session):
    """Populate database.

    For tests there are images whose names are 1.jpg, 2.jpg...

    See tests/media/medias/*
    """
    # Create user and albums (public and privete) for that user
    db_user= create_user(db_session)
    db_album_public, db_album_private = create_albums_for_user(db_session, db_user)

    # From image 1.jpg to 3.jpg
    create_and_add_medias_to_album(db_session, db_album_public, 1, 3)

    # From image 4.jpg to 5.jpg
    create_and_add_medias_to_album(db_session, db_album_private, 4, 5)

    test_data.db_session = db_session
    test_data.user = db_user
    test_data.album_public = db_album_public
    test_data.album_private = db_album_private

    yield test_data


@pytest.fixture(scope="function")
def client(populate_test_data):
    def _get_test_db():
        try:
            yield test_data.db_session
        finally:
            test_data.db_session.close()

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        response = client.post(
            "/auth/login/",
            data={"username": "alice", "password": "alice"}
        )
        token = response.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client
    app.dependency_overrides.clear()
