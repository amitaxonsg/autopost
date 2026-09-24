import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-this-before-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'autopost.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-this")\n    ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
    CREDENTIAL_ENCRYPTION_KEY = os.getenv("CREDENTIAL_ENCRYPTION_KEY", "")

    DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-5-mini")
    DEFAULT_IMAGE_MODEL = os.getenv("DEFAULT_IMAGE_MODEL", "gpt-image-1-mini")
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Singapore")
    DEFAULT_POSTS_PER_WEEK = int(os.getenv("DEFAULT_POSTS_PER_WEEK", "2"))

    CLIENT_MEMORY_PATH = os.getenv(
        "CLIENT_MEMORY_PATH",
        str(BASE_DIR / "clients" / "chezsuzette" / "MEMORY.md"),
    )

    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "1") == "1"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT = None
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    BRAND_NAME = "AutoPost"
    BRAND_BYLINE = "Developed by Axon 1Pro"
    BRAND_URL = "https://axon.com.sg"
    SUPPORT_EMAIL = "support@axon.com.sg"
