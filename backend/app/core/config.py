from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "JobPilot AI"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://jobpilot:jobpilot@localhost:5432/jobpilot"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
