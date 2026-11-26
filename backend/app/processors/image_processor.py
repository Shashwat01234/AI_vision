"""
Image preprocessing with OpenCV.
"""
import logging
import os
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def validate_image(path: str) -> Tuple[bool, str]:
    """Validate that path points to a readable image."""
    try:
        img = cv2.imread(str(path))
        if img is None:
            return False, "Image file could not be read or is corrupt"
        h, w = img.shape[:2]
        if h < 10 or w < 10:
            return False, f"Image too small ({w}x{h})"
        return True, ""
    except Exception as e:
        return False, str(e)


def preprocess(image_path: str, output_path: Optional[str] = None) -> str:
    """Apply standard preprocessing pipeline and return output path."""
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    # Resize if very large (preserve aspect ratio, max 1920 on longest side)
    h, w = img.shape[:2]
    max_dim = 1920
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        logger.debug(f"Resized {w}x{h} → {new_w}x{new_h}")

    out_path = output_path or str(image_path)
    cv2.imwrite(out_path, img)
    return out_path


def resize_for_inference(image: np.ndarray, max_size: int = 640) -> np.ndarray:
    """Resize image so longest side = max_size, keeping aspect ratio."""
    h, w = image.shape[:2]
    if max(h, w) <= max_size:
        return image
    scale = max_size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def enhance_contrast(image: np.ndarray) -> np.ndarray:
    """Apply CLAHE contrast enhancement — useful for dim/faded signs."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def extract_region(image: np.ndarray, bbox: list) -> np.ndarray:
    """Crop image to bounding box [x1, y1, x2, y2]."""
    x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    h, w = image.shape[:2]
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)
    return image[y1:y2, x1:x2]

