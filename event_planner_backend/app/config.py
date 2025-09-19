import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration loaded from environment variables with sensible defaults."""
    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "1") == "1"

    # Database: default to SQLite file for local/dev; can be overridden via env
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///event_planner.sqlite3"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # OpenAPI / API docs (flask-smorest)
    API_TITLE: str = os.getenv("API_TITLE", "Weather-Aware Event Planner API")
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    OPENAPI_VERSION: str = os.getenv("OPENAPI_VERSION", "3.0.3")
    OPENAPI_URL_PREFIX: str = os.getenv("OPENAPI_URL_PREFIX", "/docs")
    OPENAPI_SWAGGER_UI_PATH: str = os.getenv("OPENAPI_SWAGGER_UI_PATH", "")
    OPENAPI_SWAGGER_UI_URL: str = os.getenv(
        "OPENAPI_SWAGGER_UI_URL",
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
    )
