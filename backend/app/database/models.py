"""
Database models using SQLAlchemy ORM (declarative base style).
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    DateTime, ForeignKey, BigInteger
)
from sqlalchemy.orm import DeclarativeBase, relationship


def utc_now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class UploadRecord(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(512), nullable=False)          # Safe stored filename
    original_filename = Column(String(512), nullable=False)  # User's original filename
    file_type = Column(String(20), nullable=False)           # "image" or "document"
    mime_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_path = Column(String(1024), nullable=False)
    upload_time = Column(DateTime, default=utc_now, nullable=False)
    status = Column(String(50), default="uploaded", nullable=False)
    error_message = Column(Text, nullable=True)

    analysis_results = relationship("AnalysisResult", back_populates="upload", cascade="all, delete-orphan")
    document_results = relationship("DocumentResult", back_populates="upload", cascade="all, delete-orphan")
    audio_records = relationship("AudioRecord", back_populates="upload", cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(100), unique=True, index=True, nullable=False)
    mode = Column(String(20), nullable=False, default="explain")  # read/explain/summarize
    scene_description = Column(Text, nullable=True)
    detected_objects = Column(Text, nullable=True)   # JSON string
    detected_signs = Column(Text, nullable=True)     # JSON string
    ocr_text = Column(Text, nullable=True)           # JSON string
    explanation = Column(Text, nullable=True)
    confidence_info = Column(Text, nullable=True)    # JSON string
    raw_results = Column(Text, nullable=True)        # JSON string
    audio_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    upload = relationship("UploadRecord", back_populates="analysis_results")


class DocumentResult(Base):
    __tablename__ = "document_results"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(100), unique=True, index=True, nullable=False)
    mode = Column(String(20), nullable=False, default="explain")
    total_pages = Column(Integer, nullable=True)
    extracted_text = Column(Text, nullable=True)     # JSON: list of {page, text}
    headings = Column(Text, nullable=True)           # JSON
    tables = Column(Text, nullable=True)             # JSON
    embedded_visuals = Column(Text, nullable=True)   # JSON
    explanation = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    audio_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    upload = relationship("UploadRecord", back_populates="document_results")


class AudioRecord(Base):
    __tablename__ = "audio_records"

    id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(String(100), unique=True, index=True, nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    audio_path = Column(String(1024), nullable=False)
    duration = Column(Float, nullable=True)
    voice = Column(String(100), nullable=True)
    speed = Column(Float, default=1.0)
    created_at = Column(DateTime, default=utc_now)

    upload = relationship("UploadRecord", back_populates="audio_records")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, default=1)
    voice = Column(String(100), default="en_US-lessac-medium")
    speech_speed = Column(Float, default=1.0)
    text_size = Column(String(10), default="md")
    high_contrast = Column(Boolean, default=False)
    reduced_motion = Column(Boolean, default=False)
    screen_reader_optimized = Column(Boolean, default=True)
    data_retention_days = Column(Integer, default=30)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
