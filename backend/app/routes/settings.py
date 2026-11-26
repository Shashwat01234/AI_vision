"""
Settings API Routes
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import crud
from app.schemas.settings import SettingsSchema, SettingsUpdate
from app.ai_models.model_manager import model_manager

router = APIRouter(prefix="/settings", tags=["Settings"])
logger = logging.getLogger(__name__)


@router.get("", response_model=SettingsSchema)
def get_user_settings(
    db: Session = Depends(get_db),
):
    user_settings = crud.get_settings(db)
    return SettingsSchema(
        voice=user_settings.voice,
        speech_speed=user_settings.speech_speed,
        text_size=user_settings.text_size,
        high_contrast=user_settings.high_contrast,
        reduced_motion=user_settings.reduced_motion,
        screen_reader_optimized=user_settings.screen_reader_optimized,
        data_retention_days=user_settings.data_retention_days,
    )


@router.put("", response_model=SettingsSchema)
def update_user_settings(
    settings_in: SettingsUpdate,
    db: Session = Depends(get_db),
):
    update_data = {k: v for k, v in settings_in.model_dump().items() if v is not None}
    updated = crud.update_settings(db, **update_data)
    return SettingsSchema(
        voice=updated.voice,
        speech_speed=updated.speech_speed,
        text_size=updated.text_size,
        high_contrast=updated.high_contrast,
        reduced_motion=updated.reduced_motion,
        screen_reader_optimized=updated.screen_reader_optimized,
        data_retention_days=updated.data_retention_days,
    )


@router.get("/models-status")
def get_models_status():
    return model_manager.status_report()
