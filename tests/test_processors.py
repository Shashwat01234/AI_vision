"""
Unit tests for Image and Document processors
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import os
import tempfile
import cv2
import numpy as np
import pytest

from app.processors.image_processor import (
    validate_image,
    preprocess,
    resize_for_inference,
    enhance_contrast,
    extract_region,
)
from app.processors.txt_processor import extract_text as extract_txt
from app.processors.docx_processor import extract_text as extract_docx, extract_tables as extract_docx_tables
from app.processors.pdf_processor import extract_text_by_page as extract_pdf_pages


def test_validate_image_valid(tmp_path):
    img_path = tmp_path / "test.png"
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(img_path), dummy_img)

    valid, msg = validate_image(str(img_path))
    assert valid is True
    assert msg == ""


def test_validate_image_too_small(tmp_path):
    img_path = tmp_path / "tiny.png"
    tiny_img = np.zeros((5, 5, 3), dtype=np.uint8)
    cv2.imwrite(str(img_path), tiny_img)

    valid, msg = validate_image(str(img_path))
    assert valid is False
    assert "too small" in msg.lower()


def test_validate_image_corrupt(tmp_path):
    corrupt_path = tmp_path / "corrupt.png"
    corrupt_path.write_bytes(b"not an image data string")

    valid, msg = validate_image(str(corrupt_path))
    assert valid is False


def test_enhance_contrast():
    img = np.full((64, 64, 3), 128, dtype=np.uint8)
    enhanced = enhance_contrast(img)
    assert enhanced.shape == img.shape
    assert enhanced.dtype == np.uint8


def test_resize_for_inference():
    large_img = np.zeros((1200, 800, 3), dtype=np.uint8)
    resized = resize_for_inference(large_img, max_size=640)
    assert max(resized.shape[:2]) == 640


def test_extract_region():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Bbox: [x1, y1, x2, y2]
    bbox = [20, 30, 80, 100]
    cropped = extract_region(img, bbox)
    assert cropped.shape == (70, 60, 3)  # height=100-30=70, width=80-20=60


def test_extract_txt(tmp_path):
    txt_file = tmp_path / "notes.txt"
    content = "CHAPTER 1: INTRODUCTION\nThis is a test paragraph for visually impaired students.\nCHAPTER 2: METHODS\n"
    txt_file.write_text(content, encoding="utf-8")

    result = extract_txt(str(txt_file))
    assert "text" in result
    assert result["char_count"] == len(content)
    assert len(result["headings"]) >= 2
    assert "CHAPTER 1: INTRODUCTION" in result["headings"]


def test_extract_docx(tmp_path):
    from docx import Document
    docx_file = tmp_path / "sample.docx"
    doc = Document()
    doc.add_heading("Course Syllabus", level=1)
    doc.add_paragraph("Welcome to Computer Science 101.")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Week"
    table.cell(0, 1).text = "Topic"
    table.cell(1, 0).text = "1"
    table.cell(1, 1).text = "Algorithms"
    doc.save(str(docx_file))

    extracted = extract_docx(str(docx_file))
    assert "Course Syllabus" in extracted["headings"]
    assert "Welcome to Computer Science 101." in extracted["text"]

    tables = extract_docx_tables(str(docx_file))
    assert len(tables) == 1
    assert tables[0]["headers"] == ["Week", "Topic"]

