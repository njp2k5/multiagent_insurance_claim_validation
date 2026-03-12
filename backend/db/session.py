from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # allow extra env vars like SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
    )


settings = Settings()
DATABASE_URL = settings.DATABASE_URL

# Create engine safely for SQLite and PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

