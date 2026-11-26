"""
Synchronous CRUD operations for SQLite models.
"""
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import Session
from app.database.models import (
    UploadRecord, AnalysisResult, DocumentResult,
    AudioRecord, UserSettings
)


# ─── Upload ────────────────────────────────────────────────────────────────

def create_upload(db: Session, **kwargs) -> UploadRecord:
    record = UploadRecord(**kwargs)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_upload(db: Session, upload_id: int) -> Optional[UploadRecord]:
    return db.query(UploadRecord).filter(UploadRecord.id == upload_id).first()


def update_upload_status(
    db: Session, upload_id: int, status: str, error_message: str = None
) -> None:
    vals = {"status": status}
    if error_message is not None:
        vals["error_message"] = error_message
    db.query(UploadRecord).filter(UploadRecord.id == upload_id).update(vals)
    db.commit()


# ─── Analysis Results ──────────────────────────────────────────────────────

def create_analysis_result(db: Session, upload_id: int, mode: str) -> AnalysisResult:
    task_id = f"img_{uuid.uuid4().hex}"
    result = AnalysisResult(upload_id=upload_id, task_id=task_id, mode=mode)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_analysis_result_by_task(db: Session, task_id: str) -> Optional[AnalysisResult]:
    return db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()


def update_analysis_result(db: Session, task_id: str, **kwargs) -> None:
    for key in ["detected_objects", "detected_signs", "ocr_text", "confidence_info", "raw_results"]:
        if key in kwargs and isinstance(kwargs[key], (dict, list)):
            kwargs[key] = json.dumps(kwargs[key])
    db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).update(kwargs)
    db.commit()


# ─── Document Results ──────────────────────────────────────────────────────

def create_document_result(db: Session, upload_id: int, mode: str) -> DocumentResult:
    task_id = f"doc_{uuid.uuid4().hex}"
    result = DocumentResult(upload_id=upload_id, task_id=task_id, mode=mode)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_document_result_by_task(db: Session, task_id: str) -> Optional[DocumentResult]:
    return db.query(DocumentResult).filter(DocumentResult.task_id == task_id).first()


def update_document_result(db: Session, task_id: str, **kwargs) -> None:
    for key in ["extracted_text", "headings", "tables", "embedded_visuals"]:
        if key in kwargs and isinstance(kwargs[key], (dict, list)):
            kwargs[key] = json.dumps(kwargs[key])
    db.query(DocumentResult).filter(DocumentResult.task_id == task_id).update(kwargs)
    db.commit()


# ─── Audio Records ─────────────────────────────────────────────────────────

def create_audio_record(
    db: Session, upload_id: int, audio_path: str,
    voice: str, speed: float, duration: float = None,
    audio_id: Optional[str] = None,
) -> AudioRecord:
    if not audio_id:
        audio_id = f"audio_{uuid.uuid4().hex}"
    record = AudioRecord(
        audio_id=audio_id, upload_id=upload_id,
        audio_path=audio_path, voice=voice,
        speed=speed, duration=duration
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_audio_record(db: Session, audio_id: str) -> Optional[AudioRecord]:
    return db.query(AudioRecord).filter(AudioRecord.audio_id == audio_id).first()


# ─── History ───────────────────────────────────────────────────────────────

def get_history(
    db: Session, page: int = 1, page_size: int = 20
) -> Tuple[List[UploadRecord], int]:
    offset = (page - 1) * page_size
    total = db.query(func.count(UploadRecord.id)).scalar() or 0
    records = (
        db.query(UploadRecord)
        .order_by(UploadRecord.upload_time.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return records, total


def delete_history_item(db: Session, upload_id: int) -> bool:
    record = get_upload(db, upload_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def cleanup_old_records(db: Session, retention_days: int) -> int:
    if retention_days <= 0:
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    records = db.query(UploadRecord).filter(UploadRecord.upload_time < cutoff).all()
    count = 0
    for rec in records:
        db.delete(rec)
        count += 1
    if count:
        db.commit()
    return count


# ─── Settings ──────────────────────────────────────────────────────────────

def get_settings(db: Session) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.id == 1).first()
    if not settings:
        settings = UserSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, **kwargs) -> UserSettings:
    kwargs["updated_at"] = datetime.now(timezone.utc)
    db.query(UserSettings).filter(UserSettings.id == 1).update(kwargs)
    db.commit()
    return get_settings(db)
