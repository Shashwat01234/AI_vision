"""
Upload API Route
Handles file validation, safe storage, and DB record creation.
"""
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.database import crud
from app.schemas.upload import UploadResponse
from app.utils.file_utils import (
    sanitize_filename,
    generate_unique_filename,
    get_file_category,
    get_mime_type,
)
from app.utils.security import validate_file_type, validate_file_size

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = logging.getLogger(__name__)


@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload an image or document for accessibility processing.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    # 1. Validate file extension and MIME type
    is_valid, reason = validate_file_type(file.filename, file.content_type or "")
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )

    # 2. Read contents to check size and save
    try:
        contents = await file.read()
        file_size = len(contents)
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read uploaded file.",
        )

    # Validate size against config limit
    size_valid, size_reason = validate_file_size(file_size, settings.MAX_UPLOAD_SIZE_MB)
    if not size_valid:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=size_reason,
        )

    # 3. Determine safe unique file storage path
    original_filename = sanitize_filename(file.filename)
    unique_filename = generate_unique_filename(original_filename)
    upload_dir = settings.get_upload_dir()
    destination_path = upload_dir / unique_filename

    # Save to disk
    try:
        with open(destination_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"Failed to save file to disk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save uploaded file.",
        )

    # 4. Determine category: image or document
    mime_type = file.content_type or get_mime_type(str(destination_path))
    file_type = get_file_category(mime_type, original_filename)

    # 5. Create database record
    upload_record = crud.create_upload(
        db=db,
        filename=unique_filename,
        original_filename=original_filename,
        file_type=file_type,
        mime_type=mime_type,
        file_size=file_size,
        file_path=str(destination_path),
        status="uploaded",
    )

    logger.info(f"File uploaded successfully: ID={upload_record.id}, file={unique_filename}")

    return UploadResponse(
        upload_id=upload_record.id,
        filename=unique_filename,
        original_filename=original_filename,
        file_type=file_type,
        mime_type=mime_type,
        file_size=file_size,
        status="uploaded",
        upload_time=upload_record.upload_time,
        message="File uploaded successfully",
    )
