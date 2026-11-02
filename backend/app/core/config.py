from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "JobPilot AI"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    # SQLite works out of the box for local testing. Set DATABASE_URL for PostgreSQL.
    database_url: str = "sqlite:///./jobpilot.db"
    secret_key: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_BEFORE_DEPLOYMENT"
    access_token_expire_minutes: int = 60 * 24
    upload_dir: str = "uploads"
    max_upload_mb: int = 5
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
