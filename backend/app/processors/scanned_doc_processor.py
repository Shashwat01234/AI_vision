"""
Scanned document OCR processor.
Renders PDF pages to images and runs PaddleOCR on each.
"""
import logging
import os
import tempfile
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


def process_scanned_pdf(pdf_path: str, output_dir: str = None) -> List[Dict]:
    """
    Render each PDF page as an image and extract text via OCR.
    Returns list of {page, text, is_ocr=True}.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF not installed — cannot render PDF pages")
        return []

    from app.ai_models.ocr_engine import OCREngine
    ocr = OCREngine()
    if not ocr.is_available:
        logger.warning("OCR engine unavailable — scanned PDF cannot be processed")
        return []

    work_dir = output_dir or tempfile.mkdtemp()
    Path(work_dir).mkdir(parents=True, exist_ok=True)

    try:
        doc = fitz.open(str(pdf_path))
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render at 150 DPI (mat = 150/72 ≈ 2.08)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_path = os.path.join(work_dir, f"page_{page_num+1}.png")
            pix.save(img_path)

            # OCR
            ocr_results = ocr.extract_text(img_path)
            text = " ".join(r.text for r in ocr_results if r.text.strip())

            pages.append({
                "page": page_num + 1,
                "text": text,
                "headings": [],
                "is_ocr": True,
                "char_count": len(text),
            })
            logger.info(f"OCR page {page_num+1}: {len(ocr_results)} text regions")

        doc.close()
        return pages
    except Exception as e:
        logger.error(f"Scanned PDF processing error: {e}")
        return []

