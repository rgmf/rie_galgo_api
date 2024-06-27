import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

user = os.getenv("MYSQL_USER", "riegalgo")
password = os.getenv("MYSQL_PASSWORD", "")
server = os.getenv("MYSQL_SERVER", "rie_galgo_mysql")
port = os.getenv("MYSQL_PORT", "3306")
db = os.getenv("MYSQL_DB", "riegalgo")

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@{server}:{port}/{db}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
