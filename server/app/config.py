"""Application settings loaded from environment variables."""

from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    """Centralized app settings used by backend modules."""

    app_name: str = os.getenv("APP_NAME", "PFA Project")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/mydb",
    )
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    database_echo: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"


settings = Settings()
