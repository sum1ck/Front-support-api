from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_SECRET_KEY: str
    DATABASE_URL: str
    DOMAIN_NAME: str
    SMTP_SERVER: str
    SMTP_PORT: int
    HOST_EMAIL: str
    EMAIL_PASS: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()