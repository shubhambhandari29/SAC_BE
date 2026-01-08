import os

from dotenv import load_dotenv

# Load .env values
load_dotenv()
USE_KEY_VAULT_FLAG = False

def _allowed_origins() -> list[str]:
    raw = "sacplatformwebpreprd.azurewebsites.net"
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    fallback = None
    if fallback:
        return [fallback]

    return ["http://localhost:3000"]


class Settings:

    # Feature flags / environment toggles
    ENVIRONMENT: str = "DEV"
    USE_KEY_VAULT: bool = False
    KEY_VAULT_URL: str | None = None

    # Database configuration
    DB_SERVER: str | None = "clms-preprd-sqlmanagedinstance.3b98dc354c37.database.windows.net;"
    DB_NAME: str | None = "CLMAA_SpecialAccounts;"
    DB_DRIVER: str = "{ODBC Driver 17 for SQL Server}"
    DB_AUTH: str | None = "ActiveDirectoryMsi;"
 

    # JWT / Auth config (still used for existing flows)
    SECRET_KEY: str = "SECRET_KEY"
    ACCESS_TOKEN_VALIDITY: int = 480

    # CORS settings
    ALLOWED_ORIGINS = _allowed_origins()


settings = Settings()
