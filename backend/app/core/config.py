import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DATA_DIR, "campusmind.db").replace("\\", "/")


class Settings(BaseSettings):
    PROJECT_NAME: str = "CampusMind AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "campusmind-super-secure-secret-key-change-in-production-2025"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "campusmind2025"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ALGORITHM: str = "HS256"

    # LLM Provider Configuration
    LLM_PROVIDER: str = "gemini"  # 'gemini' or 'mock'
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Embedding Provider Configuration
    EMBEDDING_PROVIDER: str = "tfidf"  # 'tfidf' or 'gemini'

    # RAG Retrieval Parameters
    SIMILARITY_THRESHOLD: float = 0.13
    TOP_K_RETRIEVAL: int = 4
    CHUNK_SIZE: int = 650
    CHUNK_OVERLAP: int = 120

    # Storage & Database (Absolute paths to prevent directory-shift bugs)
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    DOCUMENTS_DIR: str = os.path.join(DEFAULT_DATA_DIR, "documents")
    VECTOR_STORE_DIR: str = os.path.join(DEFAULT_DATA_DIR, "vector_store")
    EVALUATION_DATASET_PATH: str = os.path.join(DEFAULT_DATA_DIR, "evaluation", "dataset.json")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["*"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()
