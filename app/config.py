from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "SmartWardrobe AI"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./smartwardrobe.db"

    # Claude API — required for Phase 3; defaults to "" so app starts without it
    ANTHROPIC_API_KEY: str = ""

    # Gemini API — required when AI_PROVIDER=gemini
    GEMINI_API_KEY: str = ""

    # ZhipuAI API — required when AI_PROVIDER=zhipu
    ZHIPU_API_KEY: str = ""

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI provider — "mock" for testing, "anthropic" for production
    AI_PROVIDER: str = "mock"

    # Image upload
    UPLOAD_DIR: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
