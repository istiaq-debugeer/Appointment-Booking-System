from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from core.settings import settings


engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print(
                f"Database connected successfully, test query result: {result.scalar()}"
            )
    except Exception as e:
        print(f"Error connecting to the database: {e}")


if __name__ == "__main__":
    test_connection()
