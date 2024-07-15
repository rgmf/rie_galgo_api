from .conftest import test_data


def assert_album(album_dict, should_has_cover=True):
    assert "id" in album_dict and album_dict["id"] is not None
    assert "name" in album_dict and album_dict["name"] is not None
    assert "description" in album_dict
    assert "public" in album_dict and album_dict["public"] in [0, 1]
    assert "user_id" in album_dict and album_dict["user_id"] is not None
    assert "created_at" in album_dict and album_dict["created_at"] is not None
    assert "updated_at" in album_dict and album_dict["updated_at"] is not None
    if should_has_cover:
        assert "cover" in album_dict and album_dict["cover"] is not None


def assert_media(media_dict):
    assert "id" in media_dict and media_dict["id"] is not None
    assert "name" in media_dict and media_dict["name"] is not None
    assert "hash" in media_dict and media_dict["hash"] is not None
    assert "data" in media_dict and media_dict["data"] is not None
    assert "thumbnail" in media_dict and media_dict["thumbnail"] is not None
    assert "created_at" in media_dict and media_dict["created_at"] is not None
    assert "updated_at" in media_dict and media_dict["updated_at"] is not None
    assert "size" in media_dict and media_dict["size"] is not None
    assert "media_created" in media_dict and media_dict["media_created"] is not None
    assert "media_type" in media_dict
    assert "mime_type" in media_dict
    assert "latitude" in media_dict
    assert "longitude" in media_dict
    assert "album" in media_dict and media_dict["album"] is not None
    assert_album(media_dict["album"], False)


def test_get_albums(client):
    """User 'alice' has 2 albums: one public and another one private."""
    response = client.get("/albums/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 2
    assert len([i for i in data["data"] if i["public"] == 1]) == 1
    assert len([i for i in data["data"] if i["public"] == 0]) == 1
    for album_dict in data["data"]:
        assert_album(album_dict)


def test_get_album_medias(client):
    response = client.get(f"/albums/{test_data.album_public.id}/medias/") 
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    for media_dict in data["data"]:
        assert_media(media_dict)
