"""
Dataset Splitting Tool
======================
Splits raw annotated images into train/val/test sets
with stratified sampling to maintain class balance.
"""

import os
import sys
import json
import shutil
import random
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

CLASS_NAMES = {
    0: "directional_sign",
    1: "department_sign",
    2: "safety_sign",
    3: "exit_sign",
    4: "information_sign"
}


def get_image_classes(label_path: Path) -> Set[int]:
    """Get the set of class IDs present in a label file."""
    classes = set()
    if not label_path.exists():
        return classes
    
    with open(label_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        classes.add(int(parts[0]))
                    except ValueError:
                        pass
    return classes


def stratified_split(
    image_stems: List[str],
    label_dir: Path,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42
) -> Tuple[List[str], List[str], List[str]]:
    """
    Split images into train/val/test with stratification.
    
    Ensures each class is proportionally represented in all splits.
    Images with multiple classes are assigned based on their rarest class.
    """
    random.seed(seed)
    
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, \
        f"Ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}"
    
    # Group images by their primary (rarest) class
    class_to_images: Dict[int, List[str]] = defaultdict(list)
    no_class_images: List[str] = []
    
    # Count global class frequencies
    global_class_counts = defaultdict(int)
    image_classes_map = {}
    
    for stem in image_stems:
        lbl_path = label_dir / f"{stem}.txt"
        classes = get_image_classes(lbl_path)
        image_classes_map[stem] = classes
        for c in classes:
            global_class_counts[c] += 1
    
    # Assign each image to its rarest class for stratification
    for stem in image_stems:
        classes = image_classes_map[stem]
        if not classes:
            no_class_images.append(stem)
        else:
            rarest_class = min(classes, key=lambda c: global_class_counts[c])
            class_to_images[rarest_class].append(stem)
    
    train, val, test = [], [], []
    
    # Split each class group
    for class_id in sorted(class_to_images.keys()):
        images = class_to_images[class_id]
        random.shuffle(images)
        
        n = len(images)
        n_train = max(1, int(n * train_ratio))
        n_val = max(1, int(n * val_ratio))
        n_test = n - n_train - n_val
        
        if n_test < 0:
            n_test = 0
            n_val = n - n_train
        
        train.extend(images[:n_train])
        val.extend(images[n_train:n_train + n_val])
        test.extend(images[n_train + n_val:])
    
    # Distribute no-class images (negative samples)
    random.shuffle(no_class_images)
    n = len(no_class_images)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    train.extend(no_class_images[:n_train])
    val.extend(no_class_images[n_train:n_train + n_val])
    test.extend(no_class_images[n_train + n_val:])
    
    # Shuffle final splits
    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)
    
    return train, val, test


def copy_split(
    stems: List[str],
    src_img_dir: Path,
    src_lbl_dir: Path,
    dst_img_dir: Path,
    dst_lbl_dir: Path
) -> int:
    """Copy image and label files for a split."""
    dst_img_dir.mkdir(parents=True, exist_ok=True)
    dst_lbl_dir.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    for stem in stems:
        # Find image file (could be any supported extension)
        img_found = False
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            src_img = src_img_dir / f"{stem}{ext}"
            if src_img.exists():
                shutil.copy2(src_img, dst_img_dir / src_img.name)
                img_found = True
                break
        
        if not img_found:
            print(f"  Warning: Image not found for {stem}")
            continue
        
        # Copy label file
        src_lbl = src_lbl_dir / f"{stem}.txt"
        if src_lbl.exists():
            shutil.copy2(src_lbl, dst_lbl_dir / src_lbl.name)
        
        copied += 1
    
    return copied


def verify_no_leakage(train: List[str], val: List[str], test: List[str]) -> bool:
    """Verify there is no data leakage between splits."""
    train_set = set(train)
    val_set = set(val)
    test_set = set(test)
    
    train_val = train_set & val_set
    train_test = train_set & test_set
    val_test = val_set & test_set
    
    is_clean = True
    
    if train_val:
        print(f"  ERROR: {len(train_val)} images appear in both train and val!")
        is_clean = False
    if train_test:
        print(f"  ERROR: {len(train_test)} images appear in both train and test!")
        is_clean = False
    if val_test:
        print(f"  ERROR: {len(val_test)} images appear in both val and test!")
        is_clean = False
    
    if is_clean:
        print("  ✓ No data leakage detected between splits")
    
    return is_clean


def main():
    parser = argparse.ArgumentParser(
        description="Split dataset into train/val/test sets"
    )
    parser.add_argument(
        "--path", default="./datasets/campus_signs",
        help="Base path to dataset"
    )
    parser.add_argument("--train", type=float, default=0.7, help="Training ratio (default: 0.7)")
    parser.add_argument("--val", type=float, default=0.2, help="Validation ratio (default: 0.2)")
    parser.add_argument("--test", type=float, default=0.1, help="Test ratio (default: 0.1)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument(
        "--clear", action="store_true",
        help="Clear existing splits before creating new ones"
    )
    
    args = parser.parse_args()
    
    base = Path(args.path)
    raw_img = base / "raw" / "images"
    raw_lbl = base / "raw" / "labels"
    
    if not raw_img.exists():
        print(f"Error: Raw images directory not found: {raw_img}")
        print("Place your annotated images and labels in the 'raw/' directory first.")
        sys.exit(1)
    
    # Get all image stems
    image_stems = [
        f.stem for f in raw_img.iterdir()
        if f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]
    
    if not image_stems:
        print(f"Error: No images found in {raw_img}")
        sys.exit(1)
    
    print(f"\nFound {len(image_stems)} images in raw/")
    print(f"Split ratios: train={args.train}, val={args.val}, test={args.test}")
    print(f"Random seed: {args.seed}")
    
    # Clear existing splits if requested
    if args.clear:
        for split in ["train", "val", "test"]:
            for subdir in ["images", "labels"]:
                split_dir = base / subdir / split
                if split_dir.exists():
                    shutil.rmtree(split_dir)
                    print(f"  Cleared: {split_dir}")
    
    # Perform stratified split
    train, val, test = stratified_split(
        image_stems, raw_lbl,
        train_ratio=args.train,
        val_ratio=args.val,
        test_ratio=args.test,
        seed=args.seed
    )
    
    print(f"\nSplit results:")
    print(f"  Train: {len(train)} images")
    print(f"  Val:   {len(val)} images")
    print(f"  Test:  {len(test)} images")
    
    # Verify no leakage
    verify_no_leakage(train, val, test)
    
    # Copy files
    print("\nCopying files...")
    for split_name, split_stems in [("train", train), ("val", val), ("test", test)]:
        copied = copy_split(
            split_stems, raw_img, raw_lbl,
            base / "images" / split_name,
            base / "labels" / split_name
        )
        print(f"  {split_name}: {copied} images copied")
    
    # Save split info
    split_info = {
        "seed": args.seed,
        "ratios": {"train": args.train, "val": args.val, "test": args.test},
        "counts": {"train": len(train), "val": len(val), "test": len(test)},
        "train_stems": train,
        "val_stems": val,
        "test_stems": test,
    }
    
    info_path = base / "metadata" / "split_info.json"
    info_path.parent.mkdir(parents=True, exist_ok=True)
    with open(info_path, "w") as f:
        json.dump(split_info, f, indent=2)
    print(f"\nSplit info saved to: {info_path}")
    
    print("\n✓ Dataset splitting complete!")
    print("\nNext steps:")
    print("  1. Run 'python validate_annotations.py --path <dataset_path> --all'")
    print("  2. Run training with the YOLO config pointing to this dataset")


if __name__ == "__main__":
    main()

