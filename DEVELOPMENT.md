# Exif
[Exif Tool](https://exiftool.org/)

# Rebuild docker container
For instance, if you change dependencies in `rie_galgo_api` then you have tu run these commands to re-build the container:

```shell
$ docker compose -f docker-compose-dev.yml up -d --build rie_galgo_api

$ docker compose -f docker-compose-dev.yml stop rie_galgo_api
$ docker compose -f docker-compose-dev.yml rm -f rie_galgo_api

$ docker compose -f docker-compose-dev.yml up -d rie_galgo_api
```

In a single line:

```shell
$ docker compose -f docker-compose-dev.yml up -d --build rie_galgo_api && docker compose -f docker-compose-dev.yml stop rie_galgo_api && docker compose -f docker-compose-dev.yml rm -f rie_galgo_api && docker compose -f docker-compose-dev.yml up -d rie_galgo_api
```

# Change .env file (add/delete/modify environment variables)
If you change the `.env` file then you'll need to recreate the containers. You can do that like this (this keeps data and don't delete anything):

```shell
$ docker compose -f docker-compose-dev.yml up --force-recreate -d
```

# Migrations: alembic
Import *SQLAlchemy* models in `app/alembic/env.py` (these models are in `app/database/schemas.py`).

Autogenerate migration: 

```shell
$ docker compose -f docker-compose-dev.yml exec rie_galgo_api alembic revision --autogenerate -m "Initial migration"
```

Apply migration:

```shell
$ docker compose -f docker-compose-dev.yml exec rie_galgo_api alembic upgrade head
```

# Run tests
`docker compose -f docker-compose-dev.yml exec -e UPLOAD_DIR=/app/tests/media rie_galgo_api pytest`

As you can see `UPLOAD_DIR` variable environment is needed to be rewritten to use media from tests.

If you want to see what you print then use option `-s`:

`docker compose -f docker-compose-dev.yml exec -e UPLOAD_DIR=/app/tests/media rie_galgo_api pytest -s`

# See logs
`docker compose -f docker-compose-dev.yml logs rie_galgo_api --follow`

# Webpages and references
## Pages for get GPS coordinates and conversion
https://www.coordenadas-gps.com/convertidor-de-coordenadas-gps
