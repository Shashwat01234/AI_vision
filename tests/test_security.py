"""
Unit tests for security and validation functions
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.utils.security import (
    validate_file_type,
    validate_file_size,
    check_path_traversal,
)
from app.utils.file_utils import sanitize_filename, generate_unique_filename


def test_sanitize_filename():
    assert sanitize_filename("safe_file.png") == "safe_file.png"
    # Removes traversal attempts and dangerous characters
    unsafe = "../../etc/passwd%00.jpg"
    sanitized = sanitize_filename(unsafe)
    assert "/" not in sanitized
    assert "\\" not in sanitized
    assert sanitized.endswith(".jpg")


def test_validate_file_type():
    # Valid types
    ok, _ = validate_file_type("test.jpg", "image/jpeg")
    assert ok is True

    ok, _ = validate_file_type("notes.pdf", "application/pdf")
    assert ok is True

    ok, _ = validate_file_type("presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
    assert ok is True

    # Invalid extensions
    bad, reason = validate_file_type("virus.exe", "application/x-msdownload")
    assert bad is False
    assert "not allowed" in reason

    bad2, _ = validate_file_type("script.sh", "text/x-sh")
    assert bad2 is False


def test_validate_file_size():
    # 5MB within 50MB limit
    ok, _ = validate_file_size(5 * 1024 * 1024, max_mb=50)
    assert ok is True

    # 55MB exceeds 50MB limit
    bad, reason = validate_file_size(55 * 1024 * 1024, max_mb=50)
    assert bad is False
    assert "exceeds limit" in reason


def test_check_path_traversal():
    base = Path("c:/visual_impaired/storage/uploads").resolve()
    safe_child = base / "abc_123.jpg"
    assert check_path_traversal(str(base), str(safe_child)) is True

    unsafe_child = base / ".." / ".." / "windows" / "system32"
    assert check_path_traversal(str(base), str(unsafe_child)) is False

