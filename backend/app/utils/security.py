"""
Security utilities: file type validation, path traversal prevention.
"""
import os
from pathlib import Path

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt"}
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/webp",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-powerpoint",
    "text/plain",
}


def validate_file_type(filename: str, content_type: str) -> tuple[bool, str]:
    """Validate file type by both extension and MIME type.
    Returns (is_valid, reason).
    """
    ext = Path(filename).suffix.lower()
    all_allowed_ext = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS

    if ext not in all_allowed_ext:
        return False, f"File extension '{ext}' is not allowed. Supported: {', '.join(sorted(all_allowed_ext))}"

    # Be lenient with MIME type — browsers sometimes send wrong MIME
    # but we still flag obviously wrong types
    if content_type and content_type != "application/octet-stream":
        # Mismatch between image ext and document MIME (and vice versa)
        is_image_ext = ext in ALLOWED_IMAGE_EXTENSIONS
        is_image_mime = content_type.startswith("image/")
        if is_image_ext and not is_image_mime and content_type not in ALLOWED_MIME_TYPES:
            return False, f"Content type '{content_type}' does not match image extension '{ext}'"

    return True, ""


def check_path_traversal(base_dir: str, file_path: str) -> bool:
    """Return True if file_path is safely within base_dir (no traversal)."""
    try:
        base = Path(base_dir).resolve()
        target = Path(file_path).resolve()
        return target.is_relative_to(base)
    except Exception:
        return False


def validate_file_size(size_bytes: int, max_mb: int) -> tuple[bool, str]:
    """Check file size is within limit."""
    max_bytes = max_mb * 1024 * 1024
    if size_bytes > max_bytes:
        return False, f"File size {size_bytes / (1024*1024):.1f} MB exceeds limit of {max_mb} MB"
    return True, ""
