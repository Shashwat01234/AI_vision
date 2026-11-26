"""Plain text file processor."""
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def extract_text(txt_path: str) -> Dict:
    """Read text file, detect encoding, return structured content."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    text = ""
    used_encoding = "utf-8"

    for enc in encodings:
        try:
            with open(str(txt_path), "r", encoding=enc) as f:
                text = f.read()
            used_encoding = enc
            break
        except (UnicodeDecodeError, LookupError):
            continue
        except Exception as e:
            logger.error(f"TXT read error: {e}")
            break

    # Extract simple headings (ALL CAPS lines or lines ending with :)
    headings = []
    for line in text.splitlines():
        line = line.strip()
        if line and (line.isupper() or (line.endswith(":") and len(line) < 80)):
            headings.append(line)

    return {
        "text": text,
        "headings": headings[:20],
        "encoding": used_encoding,
        "char_count": len(text),
        "line_count": text.count("\n") + 1,
    }

