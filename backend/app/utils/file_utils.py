"""
File utilities: safe naming, MIME detection, cleanup.
"""
import os
import uuid
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta


ALLOWED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_DOCUMENT_TYPES = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt"}
IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
DOCUMENT_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-powerpoint",
    "text/plain",
}


def sanitize_filename(name: str) -> str:
    """Remove unsafe characters from filename, keeping alphanumeric, dots, dashes, underscores."""
    import re
    base = Path(name).stem
    ext = Path(name).suffix.lower()
    safe_base = re.sub(r"[^\w\-]", "_", base)[:64]
    return f"{safe_base}{ext}"


def generate_unique_filename(original_name: str) -> str:
    """Generate a UUID-based unique filename preserving the extension."""
    ext = Path(original_name).suffix.lower()
    return f"{uuid.uuid4().hex}{ext}"


def get_mime_type(path: str) -> str:
    """Guess MIME type from file path."""
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"


def get_file_category(mime_type: str, filename: str = "") -> str:
    """Return 'image', 'document', or 'unknown' based on MIME type."""
    if mime_type in IMAGE_MIME_TYPES:
        return "image"
    ext = Path(filename).suffix.lower()
    if ext in ALLOWED_IMAGE_TYPES:
        return "image"
    if mime_type in DOCUMENT_MIME_TYPES or ext in ALLOWED_DOCUMENT_TYPES:
        return "document"
    return "unknown"


def format_file_size(size_bytes: int) -> str:
    """Human-readable file size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def cleanup_old_files(directory: str, days: int) -> int:
    """Delete files older than `days` days. Returns count deleted."""
    if days <= 0:
        return 0
    cutoff = datetime.now() - timedelta(days=days)
    count = 0
    dir_path = Path(directory)
    if not dir_path.exists():
        return 0
    for f in dir_path.iterdir():
        if f.is_file():
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                try:
                    f.unlink()
                    count += 1
                except OSError:
                    pass
    return count
