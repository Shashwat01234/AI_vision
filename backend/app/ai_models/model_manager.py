"""
Model Manager — lazy-loads and caches all AI models.
Single point of access for YOLO, OCR, VLM, LLM.
"""
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._yolo = None
            cls._instance._ocr = None
            cls._instance._vlm = None
            cls._instance._llm = None
            cls._instance._initialised = True
        return cls._instance

    def initialise(self):
        self._yolo = None
        self._ocr = None
        self._vlm = None
        self._llm = None
        self._initialised = True

    # ── YOLO ──────────────────────────────────────────────────────────────

    def get_yolo(self):
        if getattr(self, "_yolo", None) is None:
            from app.ai_models.yolo_detector import YOLODetector
            det = YOLODetector()
            det.load_model(
                str(settings.get_yolo_model_path()),
                str(settings.get_yolo_pretrained_path()),
            )
            self._yolo = det
        return self._yolo

    # ── OCR ───────────────────────────────────────────────────────────────

    def get_ocr(self):
        if getattr(self, "_ocr", None) is None:
            from app.ai_models.ocr_engine import OCREngine
            self._ocr = OCREngine()
        return self._ocr

    # ── VLM ───────────────────────────────────────────────────────────────

    def get_vlm(self):
        if getattr(self, "_vlm", None) is None:
            from app.ai_models.vlm_engine import VLMEngine
            engine = VLMEngine()
            engine._model_name = settings.VLM_MODEL_NAME
            self._vlm = engine
        return self._vlm

    # ── LLM ───────────────────────────────────────────────────────────────

    def get_llm(self):
        if getattr(self, "_llm", None) is None:
            from app.ai_models.llm_engine import LLMEngine
            self._llm = LLMEngine(
                provider=settings.LLM_PROVIDER,
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                api_key=settings.EXTERNAL_LLM_API_KEY,
                external_model=settings.EXTERNAL_LLM_MODEL,
            )
        return self._llm

    def status_report(self) -> dict:
        """Return availability of all models."""
        yolo_model = self.get_yolo()
        return {
            "yolo": {
                "available": yolo_model.is_available,
                "is_custom": yolo_model.is_custom if yolo_model.is_available else False,
                "model_path": getattr(yolo_model, "_model_path", None),
            },
            "ocr": {"available": self.get_ocr().is_available},
            "vlm": {"available": self.get_vlm().is_available, "model": settings.VLM_MODEL_NAME},
            "llm": {"available": self.get_llm().is_available, "provider": settings.LLM_PROVIDER},
        }


model_manager = ModelManager()
