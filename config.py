import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-this")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///autopost.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-this")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")
    WORDPRESS_URL = os.getenv("WORDPRESS_URL", "")
    WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME", "")
    WORDPRESS_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")
    DEFAULT_PUBLISHING_MODE = os.getenv("DEFAULT_PUBLISHING_MODE", "draft")
    DEFAULT_POSTS_PER_WEEK = int(os.getenv("DEFAULT_POSTS_PER_WEEK", "2"))
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Singapore")
