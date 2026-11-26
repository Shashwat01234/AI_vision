"""Pydantic v2 schemas for image and document analysis."""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class DetectedSign(BaseModel):
    label: str
    confidence: float
    bbox: Optional[List[float]] = None
    ocr_text: Optional[str] = None
    class_id: Optional[int] = None


class DetectedObject(BaseModel):
    label: str
    confidence: float
    bbox: Optional[List[float]] = None


class OcrResult(BaseModel):
    text: str
    confidence: float
    bbox: Optional[List[float]] = None
    page: Optional[int] = None


class ConfidenceInfo(BaseModel):
    overall_confidence: str = "medium"
    notes: List[str] = []
    uncertain_detections: List[str] = []


class AnalysisRequest(BaseModel):
    upload_id: int
    mode: str = "explain"  # read / explain / summarize


class ImageAnalysisResponse(BaseModel):
    task_id: str
    upload_id: int
    status: str
    mode: str
    scene_description: Optional[str] = None
    detected_signs: Optional[List[DetectedSign]] = None
    detected_objects: Optional[List[DetectedObject]] = None
    ocr_results: Optional[List[OcrResult]] = None
    explanation: Optional[str] = None
    confidence_info: Optional[ConfidenceInfo] = None
    audio_id: Optional[str] = None
    error_message: Optional[str] = None


class PageContent(BaseModel):
    page: int
    text: str
    headings: List[str] = []
    is_ocr: bool = False


class TableData(BaseModel):
    page: int
    headers: List[str] = []
    rows: List[List[str]] = []


class EmbeddedVisual(BaseModel):
    page: int
    image_path: Optional[str] = None
    description: Optional[str] = None
    type: str = "image"  # image / chart / diagram


class DocumentAnalysisResponse(BaseModel):
    task_id: str
    upload_id: int
    status: str
    mode: str
    total_pages: Optional[int] = None
    pages: Optional[List[PageContent]] = None
    headings: Optional[List[str]] = None
    tables: Optional[List[TableData]] = None
    embedded_visuals: Optional[List[EmbeddedVisual]] = None
    explanation: Optional[str] = None
    summary: Optional[str] = None
    audio_id: Optional[str] = None
    error_message: Optional[str] = None
