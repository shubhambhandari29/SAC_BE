import os

from dotenv import load_dotenv

# Load .env values
load_dotenv()


def _allowed_origins() -> list[str]:
    raw = os.getenv("FRONTEND_URLS", "sacplatformwebpreprd.azurewebsites.net")
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    fallback = os.getenv("FRONTEND_URL")
    if fallback:
        return [fallback]

    return ["http://localhost:3000"]


class Settings:

    # Feature flags / environment toggles
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "DEV")
    USE_KEY_VAULT: bool = False
    KEY_VAULT_URL: str | None = None

    # Database configuration
    DB_SERVER: str | None = os.getenv(
        "DB_SERVER", "clms-preprd-sqlmanagedinstance.3b98dc354c37.database.windows.net;"
    )
    DB_NAME: str | None = os.getenv("DB_NAME", "CLMAA_SpecialAccounts;")
    DB_DRIVER: str = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
    DB_AUTH: str | None = os.getenv("DB_AUTH", "ActiveDirectoryMsi;")

    # JWT / Auth config (still used for existing flows)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SECRET_KEY")
    ACCESS_TOKEN_VALIDITY: int = int(os.getenv("ACCESS_TOKEN_VALIDITY", 480))

    # CORS settings
    ALLOWED_ORIGINS = _allowed_origins()


settings = Settings()
