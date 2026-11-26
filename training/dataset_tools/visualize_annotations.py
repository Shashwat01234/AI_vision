"""
Annotation Visualization Tool
==============================
Draws bounding boxes on images to visually verify annotations.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

CLASS_NAMES = {
    0: "directional_sign",
    1: "department_sign",
    2: "safety_sign",
    3: "exit_sign",
    4: "information_sign"
}

# Distinct colors for each class (BGR format)
CLASS_COLORS = {
    0: (255, 100, 0),    # Blue-ish - directional
    1: (0, 200, 0),      # Green - department
    2: (0, 0, 255),      # Red - safety
    3: (0, 255, 255),    # Yellow - exit
    4: (255, 0, 200),    # Purple - information
}


def draw_annotations(
    image_path: Path,
    label_path: Path,
    output_path: Path = None,
    show: bool = False
) -> bool:
    """Draw YOLO annotations on an image."""
    if not HAS_CV2:
        print("Error: OpenCV required for visualization")
        return False
    
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"  Could not read: {image_path}")
        return False
    
    h, w = image.shape[:2]
    
    if not label_path.exists():
        print(f"  No labels for: {image_path.name}")
        if output_path:
            cv2.imwrite(str(output_path), image)
        return True
    
    with open(label_path, "r") as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        if len(parts) != 5:
            continue
        
        class_id = int(parts[0])
        cx, cy, bw, bh = [float(x) for x in parts[1:5]]
        
        # Convert normalized to absolute coordinates
        x1 = int((cx - bw / 2) * w)
        y1 = int((cy - bh / 2) * h)
        x2 = int((cx + bw / 2) * w)
        y2 = int((cy + bh / 2) * h)
        
        color = CLASS_COLORS.get(class_id, (128, 128, 128))
        label = CLASS_NAMES.get(class_id, f"class_{class_id}")
        
        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Draw label background
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        cv2.rectangle(image, (x1, y1 - text_size[1] - 8), 
                     (x1 + text_size[0] + 4, y1), color, -1)
        
        # Draw label text
        cv2.putText(image, label, (x1 + 2, y1 - 4),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image)
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Visualize YOLO annotations on images"
    )
    parser.add_argument(
        "--path", default="./datasets/campus_signs",
        help="Base path to dataset"
    )
    parser.add_argument(
        "--split", default="train",
        help="Split to visualize (train/val/test/raw)"
    )
    parser.add_argument(
        "--output", default="./datasets/campus_signs/visualized",
        help="Output directory for annotated images"
    )
    parser.add_argument(
        "--max-images", type=int, default=50,
        help="Maximum number of images to visualize"
    )
    
    args = parser.parse_args()
    
    if not HAS_CV2:
        print("Error: OpenCV required. Install: pip install opencv-python-headless")
        sys.exit(1)
    
    base = Path(args.path)
    
    if args.split == "raw":
        img_dir = base / "raw" / "images"
        lbl_dir = base / "raw" / "labels"
    else:
        img_dir = base / "images" / args.split
        lbl_dir = base / "labels" / args.split
    
    if not img_dir.exists():
        print(f"Error: Image directory not found: {img_dir}")
        sys.exit(1)
    
    output_dir = Path(args.output) / args.split
    output_dir.mkdir(parents=True, exist_ok=True)
    
    images = sorted([
        f for f in img_dir.iterdir()
        if f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ])[:args.max_images]
    
    print(f"\nVisualizing {len(images)} images from {args.split}/")
    
    success = 0
    for img_path in images:
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        out_path = output_dir / img_path.name
        
        if draw_annotations(img_path, lbl_path, out_path):
            success += 1
    
    print(f"\n✓ Visualized {success}/{len(images)} images")
    print(f"Output saved to: {output_dir}")


if __name__ == "__main__":
    main()

