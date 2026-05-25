from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://fermentai:fermentai123@localhost:5432/fermentai"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_PUBLIC_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "fermentai-datasets"
    MINIO_SECURE: bool = False
    MINIO_PUBLIC_SECURE: bool = False  # True en producción con HTTPS

    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    RESEND_API_KEY: str = ""
    SMTP_FROM: str = "onboarding@resend.dev"
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8-sig"
        extra = "ignore"


settings = Settings()
