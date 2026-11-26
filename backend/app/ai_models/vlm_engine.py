"""
Vision-Language Model Engine — wraps moondream2 for scene description.
Loads lazily upon first inference request and handles unavailability gracefully.
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class VLMEngine:
    """Wrapper for moondream2 vision-language model."""

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._available: Optional[bool] = None
        self._model_name = "vikhyatk/moondream2"

    @property
    def is_available(self) -> bool:
        """Check if VLM is enabled in configuration and required dependencies are present."""
        from app.config import settings
        if not getattr(settings, "ENABLE_VLM", False):
            return False

        if self._available is not None:
            return self._available
        import importlib.util
        self._available = (
            importlib.util.find_spec("torch") is not None
            and importlib.util.find_spec("transformers") is not None
            and importlib.util.find_spec("PIL") is not None
        )
        return self._available

    def _ensure_loaded(self) -> bool:
        """Load model into memory on first actual inference call."""
        if self._model is not None:
            return True
        if not self.is_available:
            return False

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            logger.info(f"Loading VLM model: {self._model_name}...")
            self._tokenizer = AutoTokenizer.from_pretrained(
                self._model_name,
                trust_remote_code=True,
                local_files_only=False,
            )
            self._model = AutoModelForCausalLM.from_pretrained(
                self._model_name,
                trust_remote_code=True,
                torch_dtype=torch.float32,
                local_files_only=False,
            )
            self._model.eval()
            logger.info(f"VLM model {self._model_name} loaded successfully")
            return True
        except Exception as e:
            logger.warning(f"VLM model load failed: {e}. VLM inference unavailable.")
            return False

    def describe_image(self, image_path: str) -> Optional[str]:
        """Generate a natural-language description of an image."""
        if not self._ensure_loaded():
            return None

        try:
            from PIL import Image
            img = Image.open(image_path).convert("RGB")

            if hasattr(self._model, "answer_question"):
                enc_image = self._model.encode_image(img)
                description = self._model.answer_question(
                    enc_image,
                    "Describe this image in detail for a visually impaired person. "
                    "Include all visible signs, text, people, objects, and the overall environment.",
                    self._tokenizer,
                )
            else:
                inputs = self._tokenizer(
                    images=img,
                    text="Describe this image in detail.",
                    return_tensors="pt",
                )
                import torch
                with torch.no_grad():
                    outputs = self._model.generate(**inputs, max_new_tokens=200)
                description = self._tokenizer.decode(outputs[0], skip_special_tokens=True)

            logger.info(f"VLM described image: {image_path[:50]}")
            return str(description).strip() if description else None

        except Exception as e:
            logger.error(f"VLM describe_image error: {e}")
            return None

    def answer_question(self, image_path: str, question: str) -> Optional[str]:
        """Answer a question about an image."""
        if not self._ensure_loaded():
            return None

        try:
            from PIL import Image
            img = Image.open(image_path).convert("RGB")

            if hasattr(self._model, "answer_question"):
                enc_image = self._model.encode_image(img)
                answer = self._model.answer_question(enc_image, question, self._tokenizer)
                return str(answer).strip() if answer else None
            return None
        except Exception as e:
            logger.error(f"VLM answer_question error: {e}")
            return None
