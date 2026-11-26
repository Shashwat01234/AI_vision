"""
Application configuration using pydantic-settings.
Loads settings from .env file with validation and computed properties.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./storage/accessibility.db"

    # --- File Upload ---
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./storage/uploads"
    PROCESSED_DIR: str = "./storage/processed"
    AUDIO_DIR: str = "./storage/audio"

    # --- YOLO ---
    YOLO_MODEL_PATH: str = "./models/custom/best.pt"
    YOLO_PRETRAINED_PATH: str = "./models/pretrained/yolo11n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.25

    # --- PaddleOCR ---
    OCR_LANG: str = "en"
    OCR_USE_GPU: bool = False

    # --- VLM ---
    ENABLE_VLM: bool = False
    VLM_MODEL_NAME: str = "vikhyatk/moondream2"
    VLM_DEVICE: str = "cpu"
    VLM_TIMEOUT_SECONDS: int = 20

    # --- LLM ---
    LLM_PROVIDER: str = "none"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "tinyllama"
    EXTERNAL_LLM_API_KEY: Optional[str] = None
    EXTERNAL_LLM_BASE_URL: Optional[str] = None
    EXTERNAL_LLM_MODEL: Optional[str] = None

    # --- Piper TTS ---
    PIPER_VOICE: str = "en_US-lessac-medium"
    PIPER_VOICES_DIR: str = "./models/pretrained/piper_voices"
    PIPER_SAMPLE_RATE: int = 22050

    # --- Data Retention ---
    DATA_RETENTION_DAYS: int = 30

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # ── Validators ──────────────────────────────────────────────────────

    @field_validator("MAX_UPLOAD_SIZE_MB")
    @classmethod
    def validate_upload_size(cls, v: int) -> int:
        if v < 1 or v > 500:
            raise ValueError("MAX_UPLOAD_SIZE_MB must be between 1 and 500")
        return v

    @field_validator("YOLO_CONFIDENCE_THRESHOLD")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("YOLO_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
        return v

    @field_validator("LLM_PROVIDER")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        allowed = {"none", "local", "external"}
        if v not in allowed:
            raise ValueError(f"LLM_PROVIDER must be one of {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return upper

    # ── Computed properties ─────────────────────────────────────────────

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def max_upload_size_bytes(self) -> int:
        """Maximum upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # ── Path helpers ────────────────────────────────────────────────────

    @property
    def project_root(self) -> Path:
        """Root directory of the project."""
        return Path(__file__).resolve().parent.parent.parent

    def get_database_path(self) -> Path:
        """Return absolute path to SQLite database."""
        rel = self.DATABASE_URL.replace("sqlite:///", "").lstrip("./")
        target = (self.project_root / rel).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def get_upload_dir(self) -> Path:
        """Return absolute upload directory path."""
        rel = self.UPLOAD_DIR.lstrip("./")
        target = (self.project_root / rel).resolve()
        target.mkdir(parents=True, exist_ok=True)
        return target

    def get_processed_dir(self) -> Path:
        """Return absolute processed directory path."""
        rel = self.PROCESSED_DIR.lstrip("./")
        target = (self.project_root / rel).resolve()
        target.mkdir(parents=True, exist_ok=True)
        return target

    def get_audio_dir(self) -> Path:
        """Return absolute audio directory path."""
        rel = self.AUDIO_DIR.lstrip("./")
        target = (self.project_root / rel).resolve()
        target.mkdir(parents=True, exist_ok=True)
        return target

    def get_yolo_model_path(self) -> Path:
        """Return absolute YOLO model path."""
        rel = self.YOLO_MODEL_PATH.lstrip("./")
        return (self.project_root / rel).resolve()

    def get_yolo_pretrained_path(self) -> Path:
        """Return absolute YOLO pretrained model path."""
        rel = self.YOLO_PRETRAINED_PATH.lstrip("./")
        return (self.project_root / rel).resolve()

    def get_piper_voices_dir(self) -> Path:
        """Return absolute Piper voices directory path."""
        rel = self.PIPER_VOICES_DIR.lstrip("./")
        target = (self.project_root / rel).resolve()
        target.mkdir(parents=True, exist_ok=True)
        return target

    def ensure_directories(self) -> None:
        """Create all required storage directories."""
        for d in [self.get_upload_dir(), self.get_processed_dir(), self.get_audio_dir(), self.get_piper_voices_dir()]:
            d.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = Settings()
