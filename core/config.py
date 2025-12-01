# core/config.py

import os

from dotenv import load_dotenv

# Load .env values
load_dotenv()


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"{var_name} environment variable is required")
    return value


class Settings:
    # ---------------------
    # Database configuration
    # ---------------------
    DB_SERVER: str = _require_env("DB_SERVER")
    DB_NAME: str = _require_env("DB_NAME")
    DB_USER: str = _require_env("DB_USER")
    DB_PASSWORD: str = _require_env("DB_PASSWORD")

    # ---------------------
    # JWT / Auth config
    # ---------------------
    SECRET_KEY: str = _require_env("SECRET_KEY")
    ACCESS_TOKEN_VALIDITY: int = int(os.getenv("ACCESS_TOKEN_VALIDITY", 480))  # minutes

    # ---------------------
    # CORS settings
    # ---------------------
    ALLOWED_ORIGINS = [os.getenv("FRONTEND_URL", "http://localhost:3000")]


settings = Settings()
