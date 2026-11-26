"""
Unit tests for Multimodal Explanation Engine
Tests Read, Explain, Summarize modes, confidence weighting, uncertainty handling, anti-hallucination.
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest
from app.services.explanation_engine import ExplanationEngine, ExplanationInput


@pytest.fixture
def engine():
    return ExplanationEngine()


def test_explain_mode_with_signs(engine):
    inp = ExplanationInput(
        file_type="image",
        mode="explain",
        yolo_detections=[
            {"label": "directional_sign", "confidence": 0.88, "ocr_text": "Library & Computer Lab"},
            {"label": "exit_sign", "confidence": 0.92, "ocr_text": "Emergency Exit"},
        ],
        ocr_results=[
            {"text": "Library & Computer Lab", "confidence": 0.95},
            {"text": "Emergency Exit", "confidence": 0.98},
        ],
        vlm_description="A university corridor with tiled floors and well-lit ceilings.",
    )
    output = engine.build_explanation(inp)

    assert "Library & Computer Lab" in output.main_explanation
    assert "exit sign" in output.main_explanation.lower()
    assert len(output.sign_details) == 2
    assert output.mode == "explain"


def test_uncertainty_handling_low_confidence(engine):
    inp = ExplanationInput(
        file_type="image",
        mode="explain",
        yolo_detections=[
            {"label": "safety_sign", "confidence": 0.35, "ocr_text": None},
        ],
        ocr_results=[],
        vlm_description="A dim hallway.",
    )
    output = engine.build_explanation(inp)

    assert len(output.confidence_notes) > 0
    assert "low confidence" in output.confidence_notes[0].lower() or "uncertain" in output.confidence_notes[0].lower()


def test_summarize_mode_concise(engine):
    inp = ExplanationInput(
        file_type="image",
        mode="summarize",
        yolo_detections=[
            {"label": "department_sign", "confidence": 0.90, "ocr_text": "Department of Artificial Intelligence"},
        ],
        ocr_results=[{"text": "Department of Artificial Intelligence", "confidence": 0.92}],
    )
    output = engine.build_explanation(inp)

    assert output.mode == "summarize"
    assert "Key findings:" in output.main_explanation
    assert "Department of Artificial Intelligence" in output.main_explanation


def test_document_explain_mode(engine):
    inp = ExplanationInput(
        file_type="document",
        mode="explain",
        filename="lecture_syllabus.pdf",
        document_pages=[
            {"page": 1, "text": "CS401: Advanced Artificial Intelligence and Neural Networks.", "headings": ["Course Introduction"]},
        ],
        document_headings=["Course Introduction", "Grading Criteria"],
        document_tables=[{"page": 1, "headers": ["Week", "Topic"], "rows": [["1", "Deep Learning"]]}],
    )
    output = engine.build_explanation(inp)

    assert "lecture_syllabus.pdf" in output.main_explanation
    assert "Course Introduction" in output.main_explanation
    assert "table" in output.main_explanation.lower()
