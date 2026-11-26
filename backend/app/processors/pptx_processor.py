"""PPTX processor using python-pptx."""
import logging
import os
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


def extract_slides(pptx_path: str) -> List[Dict]:
    """Extract text and titles from each slide."""
    try:
        from pptx import Presentation
        prs = Presentation(str(pptx_path))
        slides = []
        for i, slide in enumerate(prs.slides):
            title = ""
            text_parts = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    if shape.shape_type == 13:  # Picture
                        continue
                    if shape.name and "title" in shape.name.lower():
                        title = shape.text.strip()
                    text_parts.append(shape.text.strip())
            notes = ""
            if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                notes = slide.notes_slide.notes_text_frame.text.strip()
            slides.append({
                "page": i + 1,
                "title": title,
                "text": "\n".join(text_parts),
                "notes": notes,
                "headings": [title] if title else [],
                "is_ocr": False,
            })
        return slides
    except ImportError:
        logger.error("python-pptx not installed")
        return []
    except Exception as e:
        logger.error(f"PPTX slide extraction error: {e}")
        return []


def extract_tables(pptx_path: str) -> List[Dict]:
    """Extract tables from all slides."""
    try:
        from pptx import Presentation
        from pptx.util import Pt
        prs = Presentation(str(pptx_path))
        tables = []
        for slide_num, slide in enumerate(prs.slides):
            for shape in slide.shapes:
                if shape.has_table:
                    tbl = shape.table
                    if tbl.rows:
                        headers = [tbl.cell(0, c).text.strip() for c in range(len(tbl.columns))]
                        rows = []
                        for r in range(1, min(len(tbl.rows), 21)):
                            rows.append([tbl.cell(r, c).text.strip() for c in range(len(tbl.columns))])
                        tables.append({
                            "page": slide_num + 1,
                            "headers": headers,
                            "rows": rows,
                        })
        return tables
    except Exception as e:
        logger.warning(f"PPTX table extraction error: {e}")
        return []


def extract_images(pptx_path: str, output_dir: str) -> List[Dict]:
    """Extract embedded images from PPTX."""
    try:
        from pptx import Presentation
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        prs = Presentation(str(pptx_path))
        extracted = []
        for slide_num, slide in enumerate(prs.slides):
            for shape in slide.shapes:
                if shape.shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
                    try:
                        img = shape.image
                        ext = img.ext
                        img_name = f"slide{slide_num+1}_img{shape.shape_id}.{ext}"
                        out_path = os.path.join(output_dir, img_name)
                        with open(out_path, "wb") as f:
                            f.write(img.blob)
                        extracted.append({
                            "page": slide_num + 1,
                            "image_path": out_path,
                            "type": "image",
                            "description": None,
                        })
                    except Exception:
                        pass
        return extracted
    except Exception as e:
        logger.warning(f"PPTX image extraction error: {e}")
        return []

