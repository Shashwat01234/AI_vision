"""
PDF document processor using PyMuPDF.
"""
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def extract_text_by_page(pdf_path: str) -> List[Dict]:
    """Extract text from each page. Returns list of {page, text, is_ocr=False}."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf_path))
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            headings = []
            # Try to detect headings by font size
            blocks = page.get_text("dict").get("blocks", [])
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span.get("size", 0) > 14 and span.get("text", "").strip():
                            headings.append(span["text"].strip())

            pages.append({
                "page": page_num + 1,
                "text": text,
                "headings": headings[:10],
                "is_ocr": False,
                "char_count": len(text),
            })
        doc.close()
        return pages
    except ImportError:
        logger.error("PyMuPDF not installed")
        return []
    except Exception as e:
        logger.error(f"PDF text extraction error: {e}")
        return []


def extract_images(pdf_path: str, output_dir: str) -> List[Dict]:
    """Extract embedded images from PDF."""
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        extracted = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            img_list = page.get_images(full=True)
            for img_idx, img_info in enumerate(img_list):
                xref = img_info[0]
                try:
                    base_image = doc.extract_image(xref)
                    img_bytes = base_image["image"]
                    ext = base_image.get("ext", "png")
                    img_name = f"p{page_num+1}_img{img_idx+1}.{ext}"
                    img_path = os.path.join(output_dir, img_name)
                    with open(img_path, "wb") as f:
                        f.write(img_bytes)
                    extracted.append({
                        "page": page_num + 1,
                        "image_path": img_path,
                        "type": "image",
                        "description": None,
                    })
                except Exception as ex:
                    logger.warning(f"Could not extract image {xref}: {ex}")
        doc.close()
        return extracted
    except Exception as e:
        logger.error(f"PDF image extraction error: {e}")
        return []


def extract_tables(pdf_path: str) -> List[Dict]:
    """Extract tables from PDF using PyMuPDF table detection."""
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        tables = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            # PyMuPDF 1.23+ has find_tables()
            if hasattr(page, "find_tables"):
                try:
                    table_list = page.find_tables()
                    for tbl in table_list.tables:
                        df = tbl.to_pandas()
                        headers = list(df.columns)
                        rows = df.astype(str).values.tolist()
                        tables.append({
                            "page": page_num + 1,
                            "headers": headers,
                            "rows": rows[:20],  # cap rows
                        })
                except Exception:
                    pass
        doc.close()
        return tables
    except Exception as e:
        logger.warning(f"PDF table extraction error: {e}")
        return []


def extract_metadata(pdf_path: str) -> Dict:
    """Extract document metadata."""
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        meta = doc.metadata or {}
        num_pages = len(doc)
        doc.close()
        return {"num_pages": num_pages, **meta}
    except Exception as e:
        return {"error": str(e)}


def is_scanned(pdf_path: str, threshold: int = 50) -> bool:
    """Return True if PDF appears scanned (pages have < threshold chars of text)."""
    pages = extract_text_by_page(pdf_path)
    if not pages:
        return True
    avg_chars = sum(p["char_count"] for p in pages) / max(len(pages), 1)
    return avg_chars < threshold

