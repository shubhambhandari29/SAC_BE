# db.py

from contextlib import contextmanager

import pyodbc


# -----------------------------
# Build SQL connection string
# -----------------------------
def _build_connection_string() -> str:
    return (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost,1433;"
        "DATABASE=sac_db;"  # or your DB name
        "UID=sa;"
        "PWD=Shubh&0209;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )


# -----------------------------
# New Connection Getter
# -----------------------------
def get_raw_connection() -> pyodbc.Connection:
    """
    Returns a NEW pyodbc connection.
    Services or context managers will use this.
    """
    conn_str = _build_connection_string()
    return pyodbc.connect(conn_str)


# -----------------------------
# Context Manager (preferred)
# -----------------------------
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
    Each request gets a fresh connection.
    """
    conn = get_raw_connection()
    try:
        yield conn
    finally:
        conn.close()
