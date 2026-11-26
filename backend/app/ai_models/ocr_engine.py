"""
OCR Engine — multi-backend text extraction from images.
Uses EasyOCR (PyTorch-based) as primary open-source engine, with PaddleOCR fallback.
"""
import logging
from typing import List, Dict, Optional
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class OcrResult:
    def __init__(self, text: str, confidence: float, bbox: Optional[List] = None):
        self.text = text
        self.confidence = confidence
        self.bbox = bbox

    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "confidence": round(self.confidence, 4),
            "bbox": self.bbox,
        }


class OCREngine:
    """Multi-backend OCR engine supporting EasyOCR and PaddleOCR."""

    def __init__(self):
        self._easyocr_reader = None
        self._paddle_ocr = None
        self._backend: Optional[str] = None
        self._available: Optional[bool] = None

    @property
    def is_available(self) -> bool:
        """Check if any supported OCR library is installed."""
        if self._available is not None:
            return self._available
        import importlib.util
        has_easy = importlib.util.find_spec("easyocr") is not None
        has_paddle = importlib.util.find_spec("paddleocr") is not None
        self._available = has_easy or has_paddle
        return self._available

    def _ensure_init(self, lang: str = "en") -> bool:
        if self._easyocr_reader is not None or self._paddle_ocr is not None:
            return True
        if not self.is_available:
            return False

        # 1. Try EasyOCR first
        import importlib.util
        if importlib.util.find_spec("easyocr") is not None:
            try:
                import easyocr
                import torch
                use_gpu = torch.cuda.is_available()
                # Store EasyOCR weights inside project folder (models/ocr)
                project_root = Path(__file__).resolve().parent.parent.parent.parent
                model_dir = project_root / "models" / "ocr"
                network_dir = model_dir / "user_network"
                network_dir.mkdir(parents=True, exist_ok=True)

                has_local_weights = (model_dir / "craft_mlt_25k.pth").exists()
                logger.info(f"Initializing EasyOCR (gpu={use_gpu}, lang={lang}, dir={model_dir})...")
                self._easyocr_reader = easyocr.Reader(
                    [lang],
                    gpu=use_gpu,
                    model_storage_directory=str(model_dir),
                    user_network_directory=str(network_dir),
                    download_enabled=not has_local_weights,
                )
                self._backend = "easyocr"
                return True
            except Exception as e:
                logger.warning(f"EasyOCR init failed: {e}. Trying fallback...")

        # 2. Try PaddleOCR fallback
        if importlib.util.find_spec("paddleocr") is not None:
            try:
                import importlib
                p_mod = importlib.import_module("paddleocr")
                PaddleOCR = getattr(p_mod, "PaddleOCR")
                logger.info("Initializing PaddleOCR...")
                self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=False, show_log=False)
                self._backend = "paddleocr"
                return True
            except Exception as e:
                logger.warning(f"PaddleOCR init failed: {e}")

        return False

    def extract_text(self, image_path: str, lang: str = "en") -> List[OcrResult]:
        """Extract all text regions from an image file."""
        if not self._ensure_init(lang):
            return []

        outputs = []
        try:
            if self._backend == "easyocr":
                raw_results = self._easyocr_reader.readtext(str(image_path))
                for item in raw_results:
                    if len(item) >= 2:
                        bbox = item[0]
                        text = str(item[1]).strip()
                        conf = float(item[2]) if len(item) >= 3 else 0.8
                        # Convert numpy coordinates to plain Python ints
                        plain_bbox = [
                            [int(pt[0]), int(pt[1])] if isinstance(pt, (list, tuple, np.ndarray)) else pt
                            for pt in bbox
                        ]
                        if text:
                            outputs.append(OcrResult(text=text, confidence=conf, bbox=plain_bbox))

            elif self._backend == "paddleocr":
                result = self._paddle_ocr.ocr(str(image_path), cls=True)
                if result and result[0]:
                    for line in result[0]:
                        if line and len(line) >= 2:
                            bbox = line[0]
                            text_data = line[1]
                            if isinstance(text_data, (list, tuple)) and len(text_data) >= 2:
                                text = str(text_data[0]).strip()
                                conf = float(text_data[1])
                            else:
                                text = str(text_data).strip()
                                conf = 0.5
                            if text:
                                outputs.append(OcrResult(text=text, confidence=conf, bbox=bbox))

            logger.info(f"OCR ({self._backend}) extracted {len(outputs)} text items from {image_path}")
            return outputs

        except Exception as e:
            logger.error(f"OCR extraction error ({self._backend}): {e}")
            return []

    def extract_text_from_region(self, image: np.ndarray, bbox: List) -> str:
        """Run OCR on a cropped region of an image array."""
        if not self._ensure_init():
            return ""
        try:
            import cv2
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            region = image[y1:y2, x1:x2]
            if region.size == 0:
                return ""

            if self._backend == "easyocr":
                raw = self._easyocr_reader.readtext(region)
                words = [str(r[1]).strip() for r in raw if len(r) >= 2 and str(r[1]).strip()]
                return " ".join(words)

            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp_path = tmp.name
            cv2.imwrite(tmp_path, region)
            results = self.extract_text(tmp_path)
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            return " ".join(r.text for r in results)

        except Exception as e:
            logger.error(f"Region OCR error: {e}")
            return ""

