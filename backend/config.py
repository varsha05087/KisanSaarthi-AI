import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for the backend project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if it exists
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    APP_NAME: str = "KisanSaarthi AI Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    @property
    def cors_origins(self) -> list[str]:
        """
        Allowed CORS origins for frontend communication.
        Includes FRONTEND_URL and standard local development ports.
        """
        origins = [
            self.FRONTEND_URL.rstrip("/"),
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "http://localhost:3002",
            "http://127.0.0.1:3002",
            "http://localhost:3003",
            "http://127.0.0.1:3003",
            "http://localhost:3004",
            "http://127.0.0.1:3004",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
            "http://[::1]:3000",
            "http://[::1]:3001",
            "http://[::1]:3002",
            "http://[::1]:3003",
        ]
        # Return unique origins preserving order
        return list(dict.fromkeys(origins))


settings = Settings()
