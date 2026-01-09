import os

from dotenv import load_dotenv

# Load .env values
load_dotenv()


class Settings:

    # Feature flags / environment toggles
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")


    # Azure AD app credentials (used with SSO login)
    AZURE_TENANT_ID: str | None = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_ID: str | None = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET: str | None = os.getenv("AZURE_CLIENT_SECRET")

    # JWT / Auth config (still used for existing flows)
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_VALIDITY: int = int(os.getenv("ACCESS_TOKEN_VALIDITY", 480))  # minutes

    # CORS settings
    ALLOWED_ORIGINS: list = [os.getenv("FRONTEND_URL","http://localhost:3000")]


settings = Settings()
