# db.py

from contextlib import contextmanager
import struct
from typing import Dict, Optional

import pyodbc
import warnings

from azure.identity import ClientSecretCredential, DefaultAzureCredential

from core.config import settings

if settings.USE_KEY_VAULT:
    from core.key_vault import get_secret


warnings.filterwarnings(
    "ignore",category=UserWarning,
      message="pandas only supports SQLAlchemy connectable"
)

# Build SQL connection string
def _build_connection_string() -> str:
    """Build a connection string from env variables or Key Vault secrets."""

    server = settings.DB_SERVER
    database = settings.DB_NAME

    if settings.USE_KEY_VAULT:
        if settings.DB_SERVER_SECRET_NAME:
            server = get_secret(settings.DB_SERVER_SECRET_NAME)
        if settings.DB_NAME_SECRET_NAME:
            database = get_secret(settings.DB_NAME_SECRET_NAME)

    if not server or not database:
        raise RuntimeError("Database server and name must be configured")

    conn_parts = [
        f"Driver={settings.DB_DRIVER};",
        f"Server={server};",
        f"Database={database};",
        "Encrypt=yes;",
        "TrustServerCertificate=no;",
    ]

    # Allow environments to keep classic Authentication mode if needed
    if settings.DB_AUTH:
        conn_parts.append(f"Authentication={settings.DB_AUTH};")

    return "".join(conn_parts)


def _build_azure_credential() -> Optional[ClientSecretCredential]:
    """Create a credential using either KV secrets or env vars."""

    tenant_id = settings.AZURE_TENANT_ID
    client_id = settings.AZURE_CLIENT_ID
    client_secret = settings.AZURE_CLIENT_SECRET

    if settings.USE_KEY_VAULT:
        if settings.AZURE_TENANT_ID_SECRET_NAME:
            tenant_id = get_secret(settings.AZURE_TENANT_ID_SECRET_NAME)
        if settings.AZURE_CLIENT_ID_SECRET_NAME:
            client_id = get_secret(settings.AZURE_CLIENT_ID_SECRET_NAME)
        if settings.AZURE_CLIENT_SECRET_SECRET_NAME:
            client_secret = get_secret(settings.AZURE_CLIENT_SECRET_SECRET_NAME)

    if not tenant_id or not client_id or not client_secret:
        return None

    return ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )


def _get_sql_access_token() -> Optional[bytes]:
    """Return a token for Azure SQL if configured for Azure AD auth."""

    if not settings.USE_AZURE_AD_TOKEN_AUTH:
        return None

    credential = _build_azure_credential()
    if credential is None:
        # Fall back to managed identity / default credentials if available
        default_credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
        token = default_credential.get_token("https://database.windows.net/.default")
    else:
        token = credential.get_token("https://database.windows.net/.default")

    # pyodbc expects UTF-16-LE encoded token with length prefix
    access_token = token.token.encode("utf-16-le")
    return struct.pack("<I", len(access_token)) + access_token


# New Connection Getter
def get_raw_connection() -> pyodbc.Connection:
    """Return a fresh pyodbc connection, adding Azure AD tokens if configured."""

    conn_str = _build_connection_string()
    attrs: Dict[int, bytes] = {}

    token_bytes = _get_sql_access_token()
    if token_bytes:
        SQL_COPT_SS_ACCESS_TOKEN = 1256  # pyodbc constant not exported
        attrs[SQL_COPT_SS_ACCESS_TOKEN] = token_bytes

    return pyodbc.connect(conn_str, attrs_before=attrs or None)


# Context Manager
@contextmanager
def db_connection():
    """
    Usage:
        with db_connection() as conn:
            cursor = conn.cursor()
            ...
    """
    conn = get_raw_connection()
    try:
        yield conn
    finally:
        conn.close()


def get_db():
    """
    FastAPI dependency for routes or services.
    Each request gets a fresh connection. We are not using this right now
    we will use this if we use dependency injection
    """
    conn = get_raw_connection()
    try:
        yield conn
    finally:
        conn.close()
