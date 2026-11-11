import os
from pathlib import Path

from dotenv import load_dotenv

# Load the repository-root .env before any setting below is read from the
# environment. Real environment variables always win (override=False).
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://shellfinance:shellfinance_dev_only@localhost:5434/shellfinance",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JSON_SORT_KEYS = False

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
