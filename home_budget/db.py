from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

engine = create_engine("postgresql+psycopg2://user:password@localhost/postgres", )
pg_session_factory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)
SessionFactory = scoped_session(pg_session_factory)
Base = declarative_base()


def get_session() -> Generator[Session, None, None]:
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()


def get_base() -> Base:
    return Base
