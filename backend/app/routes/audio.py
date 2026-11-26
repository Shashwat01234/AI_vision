"""
Audio API Routes
Handles speech narration generation and audio file streaming.
"""
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import crud
from app.services.audio_service import audio_service
from app.config import settings

router = APIRouter(prefix="/audio", tags=["Audio Generation"])
logger = logging.getLogger(__name__)


class GenerateAudioRequest(BaseModel):
    upload_id: int
    text: str
    voice: Optional[str] = None
    speed: Optional[float] = 1.0


@router.post("/generate")
async def generate_speech_audio(
    req: GenerateAudioRequest,
    db: Session = Depends(get_db),
):
    if not req.text or not req.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text for audio generation cannot be empty.",
        )

    upload = crud.get_upload(db, req.upload_id)
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload ID {req.upload_id} not found.",
        )

    voice = req.voice or settings.PIPER_VOICE
    speed = req.speed if (req.speed and 0.5 <= req.speed <= 2.0) else 1.0

    audio_id = await audio_service.generate(
        text=req.text.strip(),
        upload_id=req.upload_id,
        voice=voice,
        speed=speed,
    )

    if not audio_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech synthesis engine is currently unavailable. Written results remain accessible.",
        )

    audio_path = audio_service.get_audio_path(audio_id)
    if not audio_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Audio file was generated but could not be located.",
        )

    record = crud.create_audio_record(
        db=db,
        upload_id=req.upload_id,
        audio_path=audio_path,
        voice=voice,
        speed=speed,
        audio_id=audio_id,
    )

    return {
        "audio_id": record.audio_id,
        "upload_id": req.upload_id,
        "voice": voice,
        "speed": speed,
        "audio_url": f"/api/audio/{record.audio_id}",
        "message": "Audio generated successfully",
    }


@router.get("/{audio_id}")
def get_audio_stream(
    audio_id: str,
    db: Session = Depends(get_db),
):
    record = crud.get_audio_record(db, audio_id)
    audio_path = record.audio_path if record else audio_service.get_audio_path(audio_id)

    if not audio_path or not Path(audio_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file with ID {audio_id} not found.",
        )

    media_type = "audio/wav" if str(audio_path).endswith(".wav") else "audio/mpeg"
    return FileResponse(
        path=audio_path,
        media_type=media_type,
        filename=Path(audio_path).name,
    )
