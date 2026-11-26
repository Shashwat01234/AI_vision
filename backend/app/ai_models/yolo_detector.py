"""
YOLO Sign Detector — wraps Ultralytics YOLO for campus sign detection.
"""
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

CAMPUS_SIGN_CLASS_NAMES = {
    0: "directional_sign",
    1: "department_sign",
    2: "safety_sign",
    3: "exit_sign",
    4: "information_sign",
}


class Detection:
    def __init__(self, label: str, confidence: float, bbox: List[float],
                 class_id: int, ocr_text: Optional[str] = None):
        self.label = label
        self.confidence = confidence
        self.bbox = bbox  # [x1, y1, x2, y2] absolute pixels
        self.class_id = class_id
        self.ocr_text = ocr_text

    def to_dict(self) -> Dict:
        return {
            "label": self.label,
            "confidence": round(self.confidence, 4),
            "bbox": self.bbox,
            "class_id": self.class_id,
            "ocr_text": self.ocr_text,
        }


class YOLODetector:
    """Wrapper around Ultralytics YOLO model."""

    def __init__(self):
        self._model = None
        self._model_path: Optional[str] = None
        self._is_custom = False
        self._available = False

    def load_model(self, custom_path: str, pretrained_path: str) -> bool:
        """Resolve model paths and check availability lazily."""
        import importlib.util
        if importlib.util.find_spec("ultralytics") is None:
            self._available = False
            return False

        custom = Path(custom_path)
        pretrained = Path(pretrained_path)

        if custom.exists():
            self._model_path = str(custom)
            self._is_custom = True
            self._available = True
        elif pretrained.exists():
            self._model_path = str(pretrained)
            self._is_custom = False
            self._available = True
        else:
            self._model_path = "yolo11n.pt"
            self._is_custom = False
            self._available = True

        return True

    def _ensure_loaded(self) -> bool:
        """Load the YOLO model weights into memory if not already loaded."""
        if self._model is not None:
            return True
        if not self._available or not self._model_path:
            return False
        try:
            import os
            os.environ["YOLO_VERBOSE"] = "False"
            os.environ["ULTRALYTICS_AUTOINSTALL"] = "False"
            config_dir = Path(__file__).resolve().parent.parent.parent.parent / "models" / ".ultralytics"
            config_dir.mkdir(parents=True, exist_ok=True)
            os.environ["YOLO_CONFIG_DIR"] = str(config_dir)
            from ultralytics import YOLO

            logger.info(f"Loading YOLO model weights: {self._model_path}...")
            self._model = YOLO(self._model_path)
            return True
        except Exception as e:
            logger.error(f"Failed to load YOLO weights from {self._model_path}: {e}")
            self._available = False
            return False

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def is_custom(self) -> bool:
        return self._is_custom

    def detect(self, image_path: str, confidence_threshold: float = 0.25) -> List[Detection]:
        """Run detection on image. Returns list of Detections."""
        if not self._ensure_loaded() or self._model is None:
            return []

        try:
            results = self._model.predict(
                source=image_path,
                conf=confidence_threshold,
                verbose=False,
                device="cpu",
            )

            detections = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()

                    # Use model's internal class names or fallback to class dictionary
                    if result.names and class_id in result.names:
                        label = result.names[class_id]
                    elif self._is_custom:
                        label = CAMPUS_SIGN_CLASS_NAMES.get(class_id, f"sign_{class_id}")
                    else:
                        label = f"object_{class_id}"

                    detections.append(Detection(
                        label=label,
                        confidence=confidence,
                        bbox=[round(x, 1) for x in bbox],
                        class_id=class_id,
                    ))

            logger.info(f"YOLO detected {len(detections)} objects in {image_path}")
            return detections

        except Exception as e:
            logger.error(f"YOLO detection error: {e}")
            return []
