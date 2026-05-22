"""Application settings loaded from environment variables."""

from dotenv import load_dotenv
import os
from typing import List

load_dotenv()


class Settings:
    """Centralized app settings used by backend modules."""

    app_name: str = os.getenv("APP_NAME", "PFA Project")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    
    # ✅ Changer pour une liste d'origines
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    
    # ✅ Ajouter une propriété pour les origines CORS
    @property
    def cors_origins(self) -> List[str]:
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            self.frontend_origin,  # Ajouter celle du .env aussi
        ]

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:ahlem2003@localhost:5432/pfa_examens",
    )
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    database_echo: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"


settings = Settings()