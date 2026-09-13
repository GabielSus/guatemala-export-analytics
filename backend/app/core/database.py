from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import sqlalchemy_database_url


engine = create_engine(
    sqlalchemy_database_url(),
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
