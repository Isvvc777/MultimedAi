from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    api_title: str = "MultiMedAI API"
    api_version: str = "1.0.0"
    cors_origins: str = "http://localhost:3000,http://localhost"

    postgres_user: str
    postgres_password: str
    postgres_db: str
    database_url: str

    redis_url: str
    celery_broker_url: str
    celery_result_backend: str

    minio_root_user: str
    minio_root_password: str
    minio_endpoint: str
    minio_bucket_name: str = "multimedai"
    minio_use_ssl: bool = False
    minio_external_url: str

    qdrant_url: str
    ollama_base_url: str
    openai_api_key: str | None = None

    yolo_model_path: str = "yolov11n.pt"
    yolo_confidence_threshold: float = 0.25

    weight_image: float = 0.35
    weight_text: float = 0.30
    weight_pdf: float = 0.20
    weight_sensor: float = 0.15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

settings = Settings()
