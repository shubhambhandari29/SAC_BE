"""Helpers for retrieving secrets from Azure Key Vault."""

from functools import lru_cache
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from core.config import settings

_credential: Optional[DefaultAzureCredential] = None
_secret_client: Optional[SecretClient] = None


def _build_client() -> SecretClient:
    global _credential, _secret_client

    if _secret_client:
        return _secret_client

    if not settings.KEY_VAULT_URL:
        raise RuntimeError("KEY_VAULT_URL must be set when USE_KEY_VAULT is true")

    _credential = DefaultAzureCredential()
    _secret_client = SecretClient(vault_url=settings.KEY_VAULT_URL, credential=_credential)
    return _secret_client


@lru_cache(maxsize=None)
def get_secret(secret_name: str) -> str:
    """Fetch a secret from Key Vault and cache it for future use."""

    client = _build_client()
    return client.get_secret(secret_name).value
