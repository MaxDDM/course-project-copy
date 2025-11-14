import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def in_docker() -> bool:
    return os.path.exists("/.dockerenv") or os.getenv("IN_DOCKER") == "1"


SQLALCHEMY_DATABASE_URL = ""

if in_docker():
    SQLALCHEMY_DATABASE_URL = "sqlite:////app/data/workouts.db"
else:
    SQLALCHEMY_DATABASE_URL = "./data/workouts.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_tables():
    Base.metadata.create_all(bind=engine)
