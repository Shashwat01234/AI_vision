"""
Pydantic v2 schemas for uploads.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    upload_id: int
    task_id: Optional[str] = None
    filename: str
    original_filename: str
    file_type: str
    mime_type: str
    file_size: int
    status: str
    upload_time: datetime
    message: str = "File uploaded successfully"


class FileInfo(BaseModel):
    filename: str
    file_type: str
    mime_type: str
    file_size: int
    is_image: bool
    is_document: bool


class UploadStatus(BaseModel):
    upload_id: int
    status: str
    error_message: Optional[str] = None
