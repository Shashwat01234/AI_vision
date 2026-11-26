"""
Document Analysis API Routes
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import crud
from app.schemas.analysis import AnalysisRequest, DocumentAnalysisResponse
from app.services.task_manager import task_manager, TaskStatus
from app.services.document_service import analyze_document_task

router = APIRouter(prefix="/document", tags=["Document Analysis"])
logger = logging.getLogger(__name__)


@router.post("/analyze")
async def start_document_analysis(
    req: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    upload = crud.get_upload(db, req.upload_id)
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload with ID {req.upload_id} not found.",
        )

    if upload.file_type != "document":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload ID {req.upload_id} is a {upload.file_type}, not a document.",
        )

    mode = req.mode.lower() if req.mode else "explain"
    if mode not in {"read", "explain", "summarize"}:
        mode = "explain"

    doc_rec = crud.create_document_result(db, req.upload_id, mode)
    task_id = doc_rec.task_id

    await task_manager.register(task_id, req.upload_id)

    background_tasks.add_task(
        analyze_document_task,
        upload_id=req.upload_id,
        task_id=task_id,
        mode=mode,
    )

    logger.info(f"Started document analysis: task_id={task_id}, upload_id={req.upload_id}")

    return {
        "task_id": task_id,
        "upload_id": req.upload_id,
        "mode": mode,
        "status": "processing",
        "message": "Document analysis started in background",
    }


@router.get("/result/{task_id}", response_model=DocumentAnalysisResponse)
async def get_document_analysis_result(
    task_id: str,
    db: Session = Depends(get_db),
):
    doc_rec = crud.get_document_result_by_task(db, task_id)
    if not doc_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document analysis task {task_id} not found.",
        )

    task_info = await task_manager.get(task_id)
    current_status = task_info.status.value if task_info else "completed"

    def parse_json(val, default):
        if not val:
            return default
        if isinstance(val, (dict, list)):
            return val
        try:
            return json.loads(val)
        except Exception:
            return default

    pages = parse_json(doc_rec.extracted_text, [])
    headings = parse_json(doc_rec.headings, [])
    tables = parse_json(doc_rec.tables, [])
    embedded_visuals = parse_json(doc_rec.embedded_visuals, [])

    return DocumentAnalysisResponse(
        task_id=task_id,
        upload_id=doc_rec.upload_id,
        status=current_status,
        mode=doc_rec.mode,
        total_pages=doc_rec.total_pages or (len(pages) if pages else 1),
        pages=pages,
        headings=headings,
        tables=tables,
        embedded_visuals=embedded_visuals,
        explanation=doc_rec.explanation,
        summary=doc_rec.summary,
        audio_id=doc_rec.audio_id,
        error_message=task_info.error if task_info else None,
    )
