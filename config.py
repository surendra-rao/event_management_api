from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables or .env file.
    """
    DATABASE_URL: str = "mysql+asyncmy://user:password@lhost:port/database_name"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()