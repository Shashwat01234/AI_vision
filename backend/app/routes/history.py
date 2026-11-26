"""
History API Routes
"""
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import crud
from app.schemas.history import HistoryItem, HistoryList

router = APIRouter(prefix="/history", tags=["History"])
logger = logging.getLogger(__name__)


@router.get("", response_model=HistoryList)
def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    records, total = crud.get_history(db, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    items = []
    for r in records:
        items.append(
            HistoryItem(
                id=r.id,
                filename=r.filename,
                original_filename=r.original_filename,
                file_type=r.file_type,
                mime_type=r.mime_type,
                file_size=r.file_size,
                upload_time=r.upload_time,
                status=r.status,
                error_message=r.error_message,
                has_analysis=bool(r.analysis_results),
                has_document_result=bool(r.document_results),
                has_audio=bool(r.audio_records),
            )
        )

    return HistoryList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


import json

def _parse_json(val, default):
    if not val:
        return default
    if isinstance(val, (dict, list)):
        return val
    try:
        return json.loads(val)
    except Exception:
        return default


@router.get("/{id}")
def get_history_detail(
    id: int,
    db: Session = Depends(get_db),
):
    upload = crud.get_upload(db, id)
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History item {id} not found.",
        )

    image_analysis = upload.analysis_results[-1] if upload.analysis_results else None
    doc_analysis = upload.document_results[-1] if upload.document_results else None
    audio = upload.audio_records[-1] if upload.audio_records else None

    return {
        "upload": {
            "id": upload.id,
            "filename": upload.filename,
            "original_filename": upload.original_filename,
            "file_type": upload.file_type,
            "mime_type": upload.mime_type,
            "file_size": upload.file_size,
            "status": upload.status,
            "upload_time": upload.upload_time,
            "error_message": upload.error_message,
        },
        "image_analysis": {
            "task_id": image_analysis.task_id,
            "mode": image_analysis.mode,
            "explanation": image_analysis.explanation,
            "scene_description": image_analysis.scene_description,
            "detected_signs": _parse_json(image_analysis.detected_signs, []),
            "detected_objects": _parse_json(image_analysis.detected_objects, []),
            "ocr_results": _parse_json(image_analysis.ocr_text, []),
            "confidence_info": _parse_json(image_analysis.confidence_info, None),
            "audio_id": image_analysis.audio_id,
        } if image_analysis else None,
        "document_analysis": {
            "task_id": doc_analysis.task_id,
            "mode": doc_analysis.mode,
            "explanation": doc_analysis.explanation,
            "summary": doc_analysis.summary,
            "total_pages": doc_analysis.total_pages,
            "extracted_text": _parse_json(doc_analysis.extracted_text, []),
            "headings": _parse_json(doc_analysis.headings, []),
            "tables": _parse_json(doc_analysis.tables, []),
            "embedded_visuals": _parse_json(doc_analysis.embedded_visuals, []),
            "audio_id": doc_analysis.audio_id,
        } if doc_analysis else None,
        "audio": {
            "audio_id": audio.audio_id,
            "audio_url": f"/api/audio/{audio.audio_id}",
            "voice": audio.voice,
            "speed": audio.speed,
        } if audio else None,
    }


@router.delete("/{id}")
def delete_history_item(
    id: int,
    db: Session = Depends(get_db),
):
    upload = crud.get_upload(db, id)
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History item {id} not found.",
        )

    file_path = Path(upload.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete file {file_path}: {e}")

    for a in upload.audio_records:
        ap = Path(a.audio_path)
        if ap.exists():
            try:
                ap.unlink()
            except Exception:
                pass

    crud.delete_history_item(db, id)
    logger.info(f"Deleted history item {id}")

    return {"message": f"History item {id} deleted successfully."}
