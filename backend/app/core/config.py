from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core Environment
    ENV: str = Field(
        default="development",
        description="Runtime environment (development, test, production)",
    )
    DEBUG: bool = Field(default=True, description="Debug mode")
    APP_NAME: str = Field(
        default="Tamil Nadu Farmer Rain Alert & Marketplace",
        description="Application Name",
    )
    APP_HOST: str = Field(default="0.0.0.0", description="Host binding")
    APP_PORT: int = Field(default=8000, description="Port binding")
    SECRET_KEY: str = Field(
        default="dev-secret-key-must-be-replaced-in-production-min32chars",
        description="Secret key for JWT and session signing",
    )

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "tn_farmer_weather"
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/tn_farmer_weather",
        description="Full database connection URI",
    )

    # Localization
    DEFAULT_LANGUAGE: str = "ta"
    SUPPORTED_LANGUAGES: list[str] = ["ta", "en"]
    TIMEZONE: str = "Asia/Kolkata"

    # Cookies & Session
    LANGUAGE_COOKIE_NAME: str = "tn_farmer_lang"
    THEME_COOKIE_NAME: str = "tn_farmer_theme"

    # Placeholders for future phases
    WEATHER_PROVIDER: str = "mock"
    SMS_PROVIDER: str = "mock"
    WHATSAPP_PROVIDER: str = "mock"


settings = Settings()
