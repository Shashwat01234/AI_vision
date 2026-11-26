"""DOCX processor using python-docx."""
import logging
import os
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


def extract_text(docx_path: str) -> Dict:
    """Extract structured text, headings, paragraphs from DOCX."""
    try:
        from docx import Document
        from docx.oxml.ns import qn
        doc = Document(str(docx_path))
        headings, paragraphs, all_text = [], [], []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            style = para.style.name if para.style else ""
            if style.startswith("Heading"):
                headings.append(text)
            all_text.append(text)
            paragraphs.append({"style": style, "text": text})

        return {
            "text": "\n".join(all_text),
            "headings": headings,
            "paragraphs": paragraphs,
            "page_count": None,  # DOCX doesn't expose pages easily
        }
    except ImportError:
        logger.error("python-docx not installed")
        return {"text": "", "headings": [], "paragraphs": []}
    except Exception as e:
        logger.error(f"DOCX text extraction error: {e}")
        return {"text": "", "headings": [], "paragraphs": []}


def extract_tables(docx_path: str) -> List[Dict]:
    """Extract all tables from DOCX."""
    try:
        from docx import Document
        doc = Document(str(docx_path))
        tables = []
        for i, table in enumerate(doc.tables):
            if not table.rows:
                continue
            headers = [cell.text.strip() for cell in table.rows[0].cells]
            rows = []
            for row in table.rows[1:21]:  # cap at 20 data rows
                rows.append([cell.text.strip() for cell in row.cells])
            tables.append({"table_index": i + 1, "headers": headers, "rows": rows})
        return tables
    except Exception as e:
        logger.warning(f"DOCX table extraction error: {e}")
        return []


def extract_images(docx_path: str, output_dir: str) -> List[Dict]:
    """Extract embedded images from DOCX."""
    try:
        from docx import Document
        import zipfile
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        extracted = []
        # DOCX is a ZIP — extract image parts
        with zipfile.ZipFile(str(docx_path), "r") as z:
            for name in z.namelist():
                if name.startswith("word/media/"):
                    ext = Path(name).suffix.lower()
                    if ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp"}:
                        out_name = Path(name).name
                        out_path = os.path.join(output_dir, out_name)
                        with z.open(name) as src, open(out_path, "wb") as dst:
                            dst.write(src.read())
                        extracted.append({
                            "page": None,
                            "image_path": out_path,
                            "type": "image",
                            "description": None,
                        })
        return extracted
    except Exception as e:
        logger.warning(f"DOCX image extraction error: {e}")
        return []

