"""Pydantic v2 schemas for history."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    mime_type: str
    file_size: int
    upload_time: datetime
    status: str
    error_message: Optional[str] = None
    has_analysis: bool = False
    has_document_result: bool = False
    has_audio: bool = False


class HistoryList(BaseModel):
    items: List[HistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int
