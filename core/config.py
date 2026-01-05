import os

from dotenv import load_dotenv

# Load .env values
load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


USE_KEY_VAULT_FLAG = _as_bool(os.getenv("USE_KEY_VAULT"), default=False)


def _require_env(var_name: str, *, optional: bool = False) -> str | None:
    value = os.getenv(var_name)
    if not value and not optional:
        raise RuntimeError(f"{var_name} environment variable is required")
    return value


def _allowed_origins() -> list[str]:
    raw = os.getenv("FRONTEND_URLS")
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    fallback = os.getenv("FRONTEND_URL")
    if fallback:
        return [fallback]

    return ["http://localhost:3000"]


class Settings:

    # Feature flags / environment toggles
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    USE_KEY_VAULT: bool = USE_KEY_VAULT_FLAG
    KEY_VAULT_URL: str | None = os.getenv("KEY_VAULT_URL")

    # Database configuration
    DB_SERVER: str | None = _require_env("DB_SERVER", optional=USE_KEY_VAULT_FLAG)
    DB_NAME: str | None = _require_env("DB_NAME", optional=USE_KEY_VAULT_FLAG)
    DB_DRIVER: str = os.getenv("DB_DRIVER", "{ODBC Driver 18 for SQL Server}")
    DB_AUTH: str | None = os.getenv("DB_AUTH")
    USE_AZURE_AD_TOKEN_AUTH: bool = _as_bool(
        os.getenv("USE_AZURE_AD_TOKEN_AUTH"), default=False
    )  # set True in azure

    # Azure AD app credentials (used when not pulling from Key Vault)
    AZURE_TENANT_ID: str | None = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_ID: str | None = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET: str | None = os.getenv("AZURE_CLIENT_SECRET")

    # JWT / Auth config (still used for existing flows)
    SECRET_KEY: str = _require_env("SECRET_KEY")
    ACCESS_TOKEN_VALIDITY: int = int(os.getenv("ACCESS_TOKEN_VALIDITY", 480))  # minutes

    # CORS settings
    ALLOWED_ORIGINS = _allowed_origins()


settings = Settings()
