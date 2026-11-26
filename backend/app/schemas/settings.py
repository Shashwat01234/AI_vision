"""Pydantic v2 schemas for user settings."""
from typing import Optional
from pydantic import BaseModel, Field


class SettingsSchema(BaseModel):
    voice: str = "en_US-lessac-medium"
    speech_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    text_size: str = "md"
    high_contrast: bool = False
    reduced_motion: bool = False
    screen_reader_optimized: bool = True
    data_retention_days: int = Field(default=30, ge=0, le=365)


class SettingsUpdate(BaseModel):
    voice: Optional[str] = None
    speech_speed: Optional[float] = Field(default=None, ge=0.5, le=2.0)
    text_size: Optional[str] = None
    high_contrast: Optional[bool] = None
    reduced_motion: Optional[bool] = None
    screen_reader_optimized: Optional[bool] = None
    data_retention_days: Optional[int] = Field(default=None, ge=0, le=365)
