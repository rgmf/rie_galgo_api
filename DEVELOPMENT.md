# Rebuild docker container
For instance, if you change dependencies in `rie_galgo_api` then you have tu run these commands to re-build the container:

```shell
$ docker compose up -d --build rie_galgo_api

$ docker compose stop rie_galgo_api
$ docker compose rm -f rie_galgo_api

$ docker compose up -d rie_galgo_api
```

In a single line:

```shell
$ docker compose up -d --build rie_galgo_api && docker compose stop rie_galgo_api && docker compose rm -f rie_galgo_api && docker compose up -d rie_galgo_api
```

# Migrations: alembic
Import *SQLAlchemy* models in `app/alembic/env.py` (these models are in `app/database/schemas.py`).

Autogenerate migration: 

```shell
$ docker compose exec rie_galgo_api alembic revision --autogenerate -m "Initial migration"
```

Apply migration:

```shell
$ docker compose exec rie_galgo_api alembic upgrade head
```

# Run tests
`docker compose exec rie_galgo_api pytest`

# See logs
`docker compose logs rie_galgo_api --follow`
