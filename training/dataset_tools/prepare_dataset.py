"""
Dataset Preparation Tool for Campus Signs Detection
====================================================
Creates the required directory structure and provides utilities for
organizing images and annotations in YOLO format.
"""

import os
import sys
import json
import shutil
import argparse
import random
from pathlib import Path
from datetime import datetime


# YOLO annotation format:
# Each image has a corresponding .txt file with the same name
# Each line: class_id center_x center_y width height (normalized 0-1)

CLASS_NAMES = {
    0: "directional_sign",
    1: "department_sign", 
    2: "safety_sign",
    3: "exit_sign",
    4: "information_sign"
}

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def create_dataset_structure(base_path: str) -> dict:
    """Create the YOLO dataset directory structure.
    
    Structure:
        datasets/campus_signs/
        ├── images/
        │   ├── train/
        │   ├── val/
        │   └── test/
        ├── labels/
        │   ├── train/
        │   ├── val/
        │   └── test/
        ├── raw/           # Unsplit raw images + labels
        │   ├── images/
        │   └── labels/
        └── metadata/
            ├── classes.txt
            └── dataset_info.json
    """
    base = Path(base_path)
    
    dirs = {
        "images_train": base / "images" / "train",
        "images_val": base / "images" / "val",
        "images_test": base / "images" / "test",
        "labels_train": base / "labels" / "train",
        "labels_val": base / "labels" / "val",
        "labels_test": base / "labels" / "test",
        "raw_images": base / "raw" / "images",
        "raw_labels": base / "raw" / "labels",
        "metadata": base / "metadata",
    }
    
    for name, dir_path in dirs.items():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {dir_path}")
    
    # Create classes.txt
    classes_file = dirs["metadata"] / "classes.txt"
    with open(classes_file, "w") as f:
        for class_id in sorted(CLASS_NAMES.keys()):
            f.write(f"{CLASS_NAMES[class_id]}\n")
    print(f"  Created: {classes_file}")
    
    # Create dataset_info.json
    info = {
        "name": "Campus Signs Detection Dataset",
        "version": "1.0.0",
        "created": datetime.now().isoformat(),
        "classes": CLASS_NAMES,
        "num_classes": len(CLASS_NAMES),
        "annotation_format": "YOLO",
        "description": "Dataset for detecting campus signs including directional, "
                       "department, safety, exit, and information signs.",
        "notes": [
            "Images should include various sign designs, lighting conditions, "
            "distances, angles, indoor and outdoor settings.",
            "Include some images without any signs (negative samples).",
            "Annotations use YOLO format: class_id center_x center_y width height (normalized)."
        ]
    }
    info_file = dirs["metadata"] / "dataset_info.json"
    with open(info_file, "w") as f:
        json.dump(info, f, indent=2)
    print(f"  Created: {info_file}")
    
    return dirs


def count_dataset_stats(base_path: str) -> dict:
    """Count images and annotations in each split."""
    base = Path(base_path)
    stats = {}
    
    for split in ["train", "val", "test", "raw"]:
        if split == "raw":
            img_dir = base / "raw" / "images"
            lbl_dir = base / "raw" / "labels"
        else:
            img_dir = base / "images" / split
            lbl_dir = base / "labels" / split
        
        images = [f for f in img_dir.iterdir() if f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS] if img_dir.exists() else []
        labels = list(lbl_dir.glob("*.txt")) if lbl_dir.exists() else []
        
        # Count annotations per class
        class_counts = {name: 0 for name in CLASS_NAMES.values()}
        total_annotations = 0
        for lbl_file in labels:
            with open(lbl_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            if class_id in CLASS_NAMES:
                                class_counts[CLASS_NAMES[class_id]] += 1
                            total_annotations += 1
        
        stats[split] = {
            "images": len(images),
            "labels": len(labels),
            "total_annotations": total_annotations,
            "class_distribution": class_counts,
            "images_without_labels": len(images) - len(labels),
        }
    
    return stats


def import_from_roboflow(export_dir: str, target_dir: str):
    """Import a Roboflow YOLO-format export into our dataset structure.
    
    Roboflow exports typically have:
        export_dir/
        ├── train/
        │   ├── images/
        │   └── labels/
        ├── valid/
        │   ├── images/
        │   └── labels/
        └── test/
            ├── images/
            └── labels/
    """
    export = Path(export_dir)
    target = Path(target_dir)
    
    mapping = {
        "train": "train",
        "valid": "val",
        "val": "val",
        "test": "test",
    }
    
    total_copied = 0
    
    for src_split, dst_split in mapping.items():
        src_img = export / src_split / "images"
        src_lbl = export / src_split / "labels"
        
        if not src_img.exists():
            continue
        
        dst_img = target / "images" / dst_split
        dst_lbl = target / "labels" / dst_split
        dst_img.mkdir(parents=True, exist_ok=True)
        dst_lbl.mkdir(parents=True, exist_ok=True)
        
        for img_file in src_img.iterdir():
            if img_file.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                shutil.copy2(img_file, dst_img / img_file.name)
                total_copied += 1
                
                # Copy corresponding label
                lbl_file = src_lbl / (img_file.stem + ".txt")
                if lbl_file.exists():
                    shutil.copy2(lbl_file, dst_lbl / lbl_file.name)
    
    print(f"Imported {total_copied} images from Roboflow export")
    return total_copied


def import_from_cvat(annotations_xml: str, images_dir: str, target_dir: str):
    """Import CVAT XML annotations and convert to YOLO format.
    
    This handles CVAT's XML export format (CVAT for images 1.1).
    """
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        print("Error: xml.etree.ElementTree required")
        return 0
    
    target = Path(target_dir)
    raw_images = target / "raw" / "images"
    raw_labels = target / "raw" / "labels"
    raw_images.mkdir(parents=True, exist_ok=True)
    raw_labels.mkdir(parents=True, exist_ok=True)
    
    tree = ET.parse(annotations_xml)
    root = tree.getroot()
    
    # Build class name to ID mapping
    name_to_id = {v: k for k, v in CLASS_NAMES.items()}
    
    total_images = 0
    total_annotations = 0
    
    for image_elem in root.findall(".//image"):
        img_name = image_elem.get("name")
        img_width = int(image_elem.get("width"))
        img_height = int(image_elem.get("height"))
        
        # Copy image
        src_img = Path(images_dir) / img_name
        if src_img.exists():
            shutil.copy2(src_img, raw_images / img_name)
            total_images += 1
        
        # Convert annotations to YOLO format
        yolo_lines = []
        for box in image_elem.findall("box"):
            label = box.get("label")
            if label not in name_to_id:
                print(f"  Warning: Unknown label '{label}' in {img_name}, skipping")
                continue
            
            class_id = name_to_id[label]
            xtl = float(box.get("xtl"))
            ytl = float(box.get("ytl"))
            xbr = float(box.get("xbr"))
            ybr = float(box.get("ybr"))
            
            # Convert to YOLO format (normalized center x, y, width, height)
            cx = ((xtl + xbr) / 2) / img_width
            cy = ((ytl + ybr) / 2) / img_height
            w = (xbr - xtl) / img_width
            h = (ybr - ytl) / img_height
            
            yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
            total_annotations += 1
        
        # Write YOLO label file
        lbl_name = Path(img_name).stem + ".txt"
        with open(raw_labels / lbl_name, "w") as f:
            f.write("\n".join(yolo_lines))
    
    print(f"Imported {total_images} images with {total_annotations} annotations from CVAT")
    return total_images


def main():
    parser = argparse.ArgumentParser(
        description="Dataset Preparation Tool for Campus Signs Detection"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create structure
    create_parser = subparsers.add_parser("create", help="Create dataset directory structure")
    create_parser.add_argument(
        "--path", default="./datasets/campus_signs",
        help="Base path for the dataset (default: ./datasets/campus_signs)"
    )
    
    # Show stats
    stats_parser = subparsers.add_parser("stats", help="Show dataset statistics")
    stats_parser.add_argument(
        "--path", default="./datasets/campus_signs",
        help="Base path for the dataset"
    )
    
    # Import from Roboflow
    roboflow_parser = subparsers.add_parser("import-roboflow", help="Import Roboflow YOLO export")
    roboflow_parser.add_argument("--export-dir", required=True, help="Path to Roboflow export")
    roboflow_parser.add_argument(
        "--target", default="./datasets/campus_signs",
        help="Target dataset path"
    )
    
    # Import from CVAT
    cvat_parser = subparsers.add_parser("import-cvat", help="Import CVAT XML annotations")
    cvat_parser.add_argument("--xml", required=True, help="Path to CVAT annotations XML")
    cvat_parser.add_argument("--images", required=True, help="Path to images directory")
    cvat_parser.add_argument(
        "--target", default="./datasets/campus_signs",
        help="Target dataset path"
    )
    
    args = parser.parse_args()
    
    if args.command == "create":
        print(f"\nCreating dataset structure at: {args.path}")
        create_dataset_structure(args.path)
        print("\nDataset structure created successfully!")
        print("\nNext steps:")
        print("  1. Place your annotated images in the 'raw/' directory")
        print("  2. Run 'python validate_annotations.py --path <dataset_path>'")
        print("  3. Run 'python split_dataset.py --path <dataset_path>'")
        
    elif args.command == "stats":
        print(f"\nDataset statistics for: {args.path}")
        stats = count_dataset_stats(args.path)
        for split, data in stats.items():
            print(f"\n  {split.upper()}:")
            print(f"    Images: {data['images']}")
            print(f"    Labels: {data['labels']}")
            print(f"    Total annotations: {data['total_annotations']}")
            print(f"    Images without labels: {data['images_without_labels']}")
            if data['total_annotations'] > 0:
                print(f"    Class distribution:")
                for cls_name, count in data['class_distribution'].items():
                    print(f"      {cls_name}: {count}")
                    
    elif args.command == "import-roboflow":
        import_from_roboflow(args.export_dir, args.target)
        
    elif args.command == "import-cvat":
        import_from_cvat(args.xml, args.images, args.target)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

