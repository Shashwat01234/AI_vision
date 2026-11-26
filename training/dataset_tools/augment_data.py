"""
Data Augmentation Tool
======================
Applies augmentations to training images to increase dataset diversity.
Uses OpenCV and Pillow for image transformations.
"""

import os
import sys
import random
import argparse
from pathlib import Path
from typing import List, Tuple

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def adjust_brightness(image: np.ndarray, factor: float) -> np.ndarray:
    """Adjust image brightness. Factor > 1 brightens, < 1 darkens."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * factor, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def add_gaussian_noise(image: np.ndarray, mean: float = 0, std: float = 25) -> np.ndarray:
    """Add Gaussian noise to simulate camera noise."""
    noise = np.random.normal(mean, std, image.shape).astype(np.float32)
    noisy = np.clip(image.astype(np.float32) + noise, 0, 255)
    return noisy.astype(np.uint8)


def random_crop_and_resize(
    image: np.ndarray,
    labels: List[str],
    crop_ratio: float = 0.8
) -> Tuple[np.ndarray, List[str]]:
    """
    Random crop that adjusts bounding box annotations.
    Only keeps annotations that remain at least 50% visible.
    """
    h, w = image.shape[:2]
    crop_h = int(h * crop_ratio)
    crop_w = int(w * crop_ratio)
    
    y1 = random.randint(0, h - crop_h)
    x1 = random.randint(0, w - crop_w)
    y2 = y1 + crop_h
    x2 = x1 + crop_w
    
    cropped = image[y1:y2, x1:x2]
    
    # Adjust labels
    new_labels = []
    for label_line in labels:
        parts = label_line.strip().split()
        if len(parts) != 5:
            continue
        
        class_id = parts[0]
        cx, cy, bw, bh = [float(x) for x in parts[1:5]]
        
        # Convert from normalized to absolute
        abs_cx = cx * w
        abs_cy = cy * h
        abs_bw = bw * w
        abs_bh = bh * h
        
        # Clip to crop region
        box_x1 = max(abs_cx - abs_bw / 2, x1) - x1
        box_y1 = max(abs_cy - abs_bh / 2, y1) - y1
        box_x2 = min(abs_cx + abs_bw / 2, x2) - x1
        box_y2 = min(abs_cy + abs_bh / 2, y2) - y1
        
        new_w = box_x2 - box_x1
        new_h = box_y2 - box_y1
        
        # Check if at least 50% of the original box is visible
        orig_area = abs_bw * abs_bh
        new_area = new_w * new_h
        
        if orig_area > 0 and new_area / orig_area < 0.5:
            continue
        
        if new_w <= 0 or new_h <= 0:
            continue
        
        # Normalize to crop dimensions
        new_cx = (box_x1 + new_w / 2) / crop_w
        new_cy = (box_y1 + new_h / 2) / crop_h
        new_bw = new_w / crop_w
        new_bh = new_h / crop_h
        
        # Clamp
        new_cx = max(0, min(1, new_cx))
        new_cy = max(0, min(1, new_cy))
        new_bw = max(0.001, min(1, new_bw))
        new_bh = max(0.001, min(1, new_bh))
        
        new_labels.append(f"{class_id} {new_cx:.6f} {new_cy:.6f} {new_bw:.6f} {new_bh:.6f}")
    
    # Resize back to original dimensions
    cropped = cv2.resize(cropped, (w, h))
    
    return cropped, new_labels


def horizontal_flip(
    image: np.ndarray,
    labels: List[str]
) -> Tuple[np.ndarray, List[str]]:
    """Horizontal flip with label adjustment."""
    flipped = cv2.flip(image, 1)
    
    new_labels = []
    for label_line in labels:
        parts = label_line.strip().split()
        if len(parts) != 5:
            continue
        class_id = parts[0]
        cx, cy, bw, bh = [float(x) for x in parts[1:5]]
        cx = 1.0 - cx  # Mirror center x
        new_labels.append(f"{class_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
    
    return flipped, new_labels


def augment_image(
    image_path: Path,
    label_path: Path,
    output_img_dir: Path,
    output_lbl_dir: Path,
    num_augmentations: int = 3,
    seed: int = None
) -> int:
    """Generate augmented versions of a single image."""
    if not HAS_CV2:
        print("Error: OpenCV (cv2) is required for augmentation")
        return 0
    
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"  Warning: Could not read {image_path.name}")
        return 0
    
    # Read labels
    labels = []
    if label_path.exists():
        with open(label_path, "r") as f:
            labels = [line.strip() for line in f if line.strip()]
    
    generated = 0
    stem = image_path.stem
    ext = image_path.suffix
    
    augmentations = [
        ("bright", lambda img, lbl: (adjust_brightness(img, random.uniform(1.2, 1.5)), lbl)),
        ("dark", lambda img, lbl: (adjust_brightness(img, random.uniform(0.5, 0.8)), lbl)),
        ("noise", lambda img, lbl: (add_gaussian_noise(img, std=random.uniform(15, 40)), lbl)),
        ("flip", lambda img, lbl: horizontal_flip(img, lbl)),
        ("crop", lambda img, lbl: random_crop_and_resize(img, lbl, random.uniform(0.7, 0.9))),
        ("blur", lambda img, lbl: (cv2.GaussianBlur(img, (5, 5), 0), lbl)),
        ("contrast", lambda img, lbl: (
            cv2.convertScaleAbs(img, alpha=random.uniform(1.2, 1.8), beta=0), lbl
        )),
    ]
    
    # Randomly select augmentations
    selected = random.sample(augmentations, min(num_augmentations, len(augmentations)))
    
    for aug_name, aug_fn in selected:
        try:
            aug_img, aug_labels = aug_fn(image.copy(), labels.copy())
            
            out_name = f"{stem}_aug_{aug_name}{ext}"
            out_img_path = output_img_dir / out_name
            out_lbl_path = output_lbl_dir / f"{stem}_aug_{aug_name}.txt"
            
            cv2.imwrite(str(out_img_path), aug_img)
            with open(out_lbl_path, "w") as f:
                f.write("\n".join(aug_labels))
            
            generated += 1
        except Exception as e:
            print(f"  Warning: Augmentation '{aug_name}' failed for {stem}: {e}")
    
    return generated


def main():
    parser = argparse.ArgumentParser(
        description="Augment training images for campus signs detection"
    )
    parser.add_argument(
        "--path", default="./datasets/campus_signs",
        help="Base path to dataset"
    )
    parser.add_argument(
        "--split", default="train",
        help="Which split to augment (default: train)"
    )
    parser.add_argument(
        "--num-aug", type=int, default=3,
        help="Number of augmentations per image (default: 3)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    if not HAS_CV2:
        print("Error: OpenCV is required. Install with: pip install opencv-python-headless")
        sys.exit(1)
    
    base = Path(args.path)
    img_dir = base / "images" / args.split
    lbl_dir = base / "labels" / args.split
    
    if not img_dir.exists():
        print(f"Error: Image directory not found: {img_dir}")
        sys.exit(1)
    
    images = [f for f in img_dir.iterdir() 
              if f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
              and "_aug_" not in f.stem]  # Don't augment augmented images
    
    print(f"\nAugmenting {len(images)} images from {args.split}/")
    print(f"Generating up to {args.num_aug} augmentations per image")
    
    total = 0
    for i, img_path in enumerate(images):
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        count = augment_image(
            img_path, lbl_path, img_dir, lbl_dir,
            num_augmentations=args.num_aug,
            seed=args.seed + i
        )
        total += count
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(images)} images...")
    
    print(f"\n✓ Generated {total} augmented images")
    print(f"Total training images: {len(images) + total}")


if __name__ == "__main__":
    main()

