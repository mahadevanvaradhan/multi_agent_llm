
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB=os.getenv("POSTGRES_DB")
POSTGRES_HOST=os.getenv("POSTGRES_HOST")
POSTGRES_PORT=os.getenv("POSTGRES_PORT")

# Replace with your actual PostgreSQL connection string
SQLALCHEMY_DATABASE_URL = "postgresql://POSTGRES_USER:POSTGRES_PASSWORD@POSTGRES_HOST:5432/trackdb" 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()