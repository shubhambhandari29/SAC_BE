import os
from typing import Optional

from dotenv import load_dotenv

# Load .env values
load_dotenv()


def _as_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


USE_KEY_VAULT_FLAG = _as_bool(os.getenv("USE_KEY_VAULT"), default=False)


def _require_env(var_name: str, *, optional: bool = False) -> Optional[str]:
    value = os.getenv(var_name)
    if not value and not optional:
        raise RuntimeError(f"{var_name} environment variable is required")
    return value


class Settings:

    # Feature flags / environment toggles
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    USE_KEY_VAULT: bool = USE_KEY_VAULT_FLAG
    KEY_VAULT_URL: Optional[str] = os.getenv("KEY_VAULT_URL")

    # Database configuration
    DB_SERVER: Optional[str] = _require_env("DB_SERVER", optional=USE_KEY_VAULT_FLAG)
    DB_NAME: Optional[str] = _require_env("DB_NAME", optional=USE_KEY_VAULT_FLAG)
    DB_DRIVER: str = os.getenv("DB_DRIVER", "{ODBC Driver 18 for SQL Server}")
    DB_AUTH: Optional[str] = os.getenv("DB_AUTH")
    USE_AZURE_AD_TOKEN_AUTH: bool = _as_bool(os.getenv("USE_AZURE_AD_TOKEN_AUTH"), default=False)  #set True in azure

    # Optional secret names for Key Vault-driven configuration
    DB_SERVER_SECRET_NAME: Optional[str] = os.getenv("DB_SERVER_SECRET_NAME")
    DB_NAME_SECRET_NAME: Optional[str] = os.getenv("DB_NAME_SECRET_NAME")
    AZURE_TENANT_ID_SECRET_NAME: Optional[str] = os.getenv("AZURE_TENANT_ID_SECRET_NAME")
    AZURE_CLIENT_ID_SECRET_NAME: Optional[str] = os.getenv("AZURE_CLIENT_ID_SECRET_NAME")
    AZURE_CLIENT_SECRET_SECRET_NAME: Optional[str] = os.getenv("AZURE_CLIENT_SECRET_SECRET_NAME")

    # Azure AD app credentials (used when not pulling from Key Vault)
    AZURE_TENANT_ID: Optional[str] = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_ID: Optional[str] = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET: Optional[str] = os.getenv("AZURE_CLIENT_SECRET")

    # JWT / Auth config (still used for existing flows)
    SECRET_KEY: str = _require_env("SECRET_KEY")
    ACCESS_TOKEN_VALIDITY: int = int(os.getenv("ACCESS_TOKEN_VALIDITY", 480))  # minutes

    # CORS settings
    ALLOWED_ORIGINS = [os.getenv("FRONTEND_URL", "http://localhost:3000")]


settings = Settings()
