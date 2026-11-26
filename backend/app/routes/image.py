"""
Image Analysis API Routes
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import crud
from app.schemas.analysis import AnalysisRequest, ImageAnalysisResponse
from app.services.task_manager import task_manager, TaskStatus
from app.services.image_service import analyze_image_task

router = APIRouter(prefix="/image", tags=["Image Analysis"])
logger = logging.getLogger(__name__)


@router.post("/analyze")
async def start_image_analysis(
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

    if upload.file_type != "image":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload ID {req.upload_id} is a {upload.file_type}, not an image.",
        )

    mode = req.mode.lower() if req.mode else "explain"
    if mode not in {"read", "explain", "summarize"}:
        mode = "explain"

    analysis_rec = crud.create_analysis_result(db, req.upload_id, mode)
    task_id = analysis_rec.task_id

    # Register in task manager
    await task_manager.register(task_id, req.upload_id)

    background_tasks.add_task(
        analyze_image_task,
        upload_id=req.upload_id,
        task_id=task_id,
        mode=mode,
    )

    logger.info(f"Started image analysis: task_id={task_id}, upload_id={req.upload_id}")

    return {
        "task_id": task_id,
        "upload_id": req.upload_id,
        "mode": mode,
        "status": "processing",
        "message": "Image analysis started in background",
    }


@router.get("/result/{task_id}", response_model=ImageAnalysisResponse)
async def get_image_analysis_result(
    task_id: str,
    db: Session = Depends(get_db),
):
    analysis_rec = crud.get_analysis_result_by_task(db, task_id)
    if not analysis_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis task {task_id} not found.",
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

    detected_signs = parse_json(analysis_rec.detected_signs, [])
    detected_objects = parse_json(analysis_rec.detected_objects, [])
    ocr_results = parse_json(analysis_rec.ocr_text, [])
    confidence_info = parse_json(analysis_rec.confidence_info, None)

    return ImageAnalysisResponse(
        task_id=task_id,
        upload_id=analysis_rec.upload_id,
        status=current_status,
        mode=analysis_rec.mode,
        scene_description=analysis_rec.scene_description,
        detected_signs=detected_signs,
        detected_objects=detected_objects,
        ocr_results=ocr_results,
        explanation=analysis_rec.explanation,
        confidence_info=confidence_info,
        audio_id=analysis_rec.audio_id,
        error_message=task_info.error if task_info else None,
    )
