"""
API Integration tests for FastAPI endpoints — uses FastAPI TestClient
for reliable in-process testing.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _get(path, **kw):
    return client.get(path, **kw)


def _post(path, **kw):
    return client.post(path, **kw)


def _put(path, **kw):
    return client.put(path, **kw)



# ── Health ──────────────────────────────────────────────────────────────────

def test_health_check():
    response = _get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models" in data


# ── Settings ─────────────────────────────────────────────────────────────────

def test_get_settings():
    response = _get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "voice" in data
    assert "speech_speed" in data
    assert "high_contrast" in data


def test_update_settings():
    update_payload = {
        "speech_speed": 1.25,
        "high_contrast": True,
        "text_size": "lg",
    }
    response = _put("/api/settings", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["speech_speed"] == 1.25
    assert data["high_contrast"] is True
    assert data["text_size"] == "lg"


# ── Models Status ─────────────────────────────────────────────────────────────

def test_models_status():
    response = _get("/api/settings/models-status")
    assert response.status_code == 200
    data = response.json()
    assert "yolo" in data
    assert "ocr" in data
    assert "vlm" in data


# ── Upload ───────────────────────────────────────────────────────────────────

def test_invalid_file_upload():
    response = _post(
        "/api/upload",
        files={"file": ("malicious.exe", b"binarycontent", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()


def test_valid_image_upload():
    dummy_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x02"
        b"\x00\x00\x00\x02\x90\x01\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00"
        b"\x05\xfe\x02\xfe\xa7\xbf\xba\x8e\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    response = _post(
        "/api/upload",
        files={"file": ("campus_sign.png", dummy_png, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["file_type"] == "image"
    assert data["original_filename"] == "campus_sign.png"
    assert "upload_id" in data
