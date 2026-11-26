"""
Annotation Validation Tool
===========================
Validates YOLO-format annotations for the campus signs dataset.
Checks for common annotation errors and reports issues.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image
except ImportError:
    Image = None

CLASS_NAMES = {
    0: "directional_sign",
    1: "department_sign",
    2: "safety_sign",
    3: "exit_sign",
    4: "information_sign"
}

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


class ValidationResult:
    """Stores validation results."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.total_images = 0
        self.total_labels = 0
        self.total_annotations = 0
        self.valid_annotations = 0
        self.invalid_annotations = 0
        self.images_without_labels = []
        self.labels_without_images = []
        self.empty_labels = []
        self.class_counts = {name: 0 for name in CLASS_NAMES.values()}
    
    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
    
    def print_report(self):
        print("\n" + "=" * 60)
        print("ANNOTATION VALIDATION REPORT")
        print("=" * 60)
        
        print(f"\nTotal images: {self.total_images}")
        print(f"Total label files: {self.total_labels}")
        print(f"Total annotations: {self.total_annotations}")
        print(f"Valid annotations: {self.valid_annotations}")
        print(f"Invalid annotations: {self.invalid_annotations}")
        
        print(f"\nClass distribution:")
        for cls_name, count in self.class_counts.items():
            pct = (count / max(self.total_annotations, 1)) * 100
            bar = "█" * int(pct / 2)
            print(f"  {cls_name:20s}: {count:5d} ({pct:5.1f}%) {bar}")
        
        if self.images_without_labels:
            print(f"\nImages without labels ({len(self.images_without_labels)}):")
            for img in self.images_without_labels[:10]:
                print(f"  - {img}")
            if len(self.images_without_labels) > 10:
                print(f"  ... and {len(self.images_without_labels) - 10} more")
        
        if self.labels_without_images:
            print(f"\nLabels without images ({len(self.labels_without_images)}):")
            for lbl in self.labels_without_images[:10]:
                print(f"  - {lbl}")
            if len(self.labels_without_images) > 10:
                print(f"  ... and {len(self.labels_without_images) - 10} more")
        
        if self.empty_labels:
            print(f"\nEmpty label files ({len(self.empty_labels)}):")
            for lbl in self.empty_labels[:10]:
                print(f"  - {lbl}")
        
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for err in self.errors[:20]:
                print(f"  ✗ {err}")
            if len(self.errors) > 20:
                print(f"  ... and {len(self.errors) - 20} more errors")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warn in self.warnings[:20]:
                print(f"  ⚠ {warn}")
            if len(self.warnings) > 20:
                print(f"  ... and {len(self.warnings) - 20} more warnings")
        
        print("\n" + "=" * 60)
        if self.is_valid:
            print("✓ VALIDATION PASSED — No critical errors found")
        else:
            print("✗ VALIDATION FAILED — Fix errors before training")
        print("=" * 60)


def validate_yolo_line(line: str, line_num: int, filename: str, 
                        num_classes: int = 5) -> Tuple[bool, str]:
    """Validate a single YOLO annotation line."""
    parts = line.strip().split()
    
    if len(parts) != 5:
        return False, f"{filename}:{line_num}: Expected 5 values, got {len(parts)}: '{line.strip()}'"
    
    try:
        class_id = int(parts[0])
    except ValueError:
        return False, f"{filename}:{line_num}: Class ID '{parts[0]}' is not an integer"
    
    if class_id < 0 or class_id >= num_classes:
        return False, f"{filename}:{line_num}: Class ID {class_id} out of range [0, {num_classes - 1}]"
    
    try:
        cx, cy, w, h = [float(x) for x in parts[1:5]]
    except ValueError:
        return False, f"{filename}:{line_num}: Non-numeric coordinate values"
    
    issues = []
    if not (0 <= cx <= 1):
        issues.append(f"center_x={cx:.4f} out of [0,1]")
    if not (0 <= cy <= 1):
        issues.append(f"center_y={cy:.4f} out of [0,1]")
    if not (0 < w <= 1):
        issues.append(f"width={w:.4f} out of (0,1]")
    if not (0 < h <= 1):
        issues.append(f"height={h:.4f} out of (0,1]")
    
    # Check for very small bounding boxes (likely errors)
    if w * h < 0.0001:
        issues.append(f"bbox area {w*h:.6f} is extremely small")
    
    # Check for bounding boxes extending beyond image
    if cx - w/2 < -0.01 or cx + w/2 > 1.01 or cy - h/2 < -0.01 or cy + h/2 > 1.01:
        issues.append("bbox extends beyond image boundaries")
    
    if issues:
        return False, f"{filename}:{line_num}: " + "; ".join(issues)
    
    return True, ""


def validate_directory(dir_path: str, split_name: str = "") -> ValidationResult:
    """Validate all annotations in a directory pair (images/ + labels/)."""
    result = ValidationResult()
    base = Path(dir_path)
    
    if split_name:
        img_dir = base / "images" / split_name
        lbl_dir = base / "labels" / split_name
    else:
        img_dir = base / "images" if (base / "images").exists() else base / "raw" / "images"
        lbl_dir = base / "labels" if (base / "labels").exists() else base / "raw" / "labels"
    
    if not img_dir.exists():
        result.errors.append(f"Image directory not found: {img_dir}")
        return result
    
    if not lbl_dir.exists():
        result.errors.append(f"Label directory not found: {lbl_dir}")
        return result
    
    # Collect image and label stems
    image_files = {f.stem: f for f in img_dir.iterdir() 
                   if f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS}
    label_files = {f.stem: f for f in lbl_dir.glob("*.txt")}
    
    result.total_images = len(image_files)
    result.total_labels = len(label_files)
    
    # Check for mismatches
    image_stems = set(image_files.keys())
    label_stems = set(label_files.keys())
    
    result.images_without_labels = sorted(image_stems - label_stems)
    result.labels_without_images = sorted(label_stems - image_stems)
    
    if result.labels_without_images:
        for orphan in result.labels_without_images:
            result.errors.append(f"Label file has no matching image: {orphan}.txt")
    
    if result.images_without_labels:
        for orphan in result.images_without_labels:
            result.warnings.append(
                f"Image has no label file: {orphan} (OK if negative sample)"
            )
    
    # Validate each label file
    for stem, lbl_path in sorted(label_files.items()):
        with open(lbl_path, "r") as f:
            lines = f.readlines()
        
        if not lines or all(line.strip() == "" for line in lines):
            result.empty_labels.append(str(lbl_path.name))
            result.warnings.append(f"Empty label file: {lbl_path.name}")
            continue
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            result.total_annotations += 1
            valid, message = validate_yolo_line(line, line_num, lbl_path.name)
            
            if valid:
                result.valid_annotations += 1
                class_id = int(line.split()[0])
                if class_id in CLASS_NAMES:
                    result.class_counts[CLASS_NAMES[class_id]] += 1
            else:
                result.invalid_annotations += 1
                result.errors.append(message)
    
    # Validate image readability if PIL available
    if Image is not None:
        for stem, img_path in sorted(image_files.items()):
            try:
                with Image.open(img_path) as img:
                    img.verify()
            except Exception as e:
                result.errors.append(f"Corrupt image: {img_path.name}: {e}")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Validate YOLO annotations for campus signs dataset"
    )
    parser.add_argument(
        "--path", default="./datasets/campus_signs",
        help="Base path to dataset"
    )
    parser.add_argument(
        "--split", default="",
        help="Specific split to validate (train/val/test). Empty = validate raw/"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Validate all splits (train, val, test)"
    )
    
    args = parser.parse_args()
    
    if args.all:
        for split in ["train", "val", "test"]:
            print(f"\nValidating {split.upper()} split...")
            result = validate_directory(args.path, split)
            result.print_report()
    elif args.split:
        print(f"\nValidating {args.split.upper()} split...")
        result = validate_directory(args.path, args.split)
        result.print_report()
    else:
        print(f"\nValidating raw annotations...")
        result = validate_directory(args.path, "")
        result.print_report()
    
    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()

