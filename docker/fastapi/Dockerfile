FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN apt-get update && apt-get install -y ffmpeg

COPY ./app /app/app
COPY ./alembic.ini /app
COPY ./tests /app/tests

WORKDIR /app
