"""
COCO to YOLO Converter Tool
Converts Roboflow COCO format (_annotations.coco.json) to standard YOLO format (.txt).
Generates traffic_signs.yaml configuration for Ultralytics YOLO training and evaluation.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def convert_coco_split_to_yolo(split_dir: Path, category_map: Dict[int, int]) -> int:
    """
    Converts _annotations.coco.json in split_dir into individual YOLO .txt files.
    """
    json_path = split_dir / "_annotations.coco.json"
    if not json_path.exists():
        logger.warning(f"No COCO annotation found at {json_path}")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        coco = json.load(f)

    # Build image lookup: id -> image info
    images = {img["id"]: img for img in coco.get("images", [])}

    # Group annotations by image_id
    img_to_anns: Dict[int, List[dict]] = {}
    for ann in coco.get("annotations", []):
        img_id = ann["image_id"]
        img_to_anns.setdefault(img_id, []).append(ann)

    converted_count = 0
    for img_id, img_info in images.items():
        file_name = img_info["file_name"]
        img_w = float(img_info["width"])
        img_h = float(img_info["height"])

        txt_name = Path(file_name).stem + ".txt"
        txt_path = split_dir / txt_name

        anns = img_to_anns.get(img_id, [])
        lines = []
        for ann in anns:
            cat_id = ann["category_id"]
            if cat_id not in category_map:
                continue

            yolo_class = category_map[cat_id]
            bbox = ann.get("bbox", [])
            if len(bbox) != 4:
                continue

            # COCO bbox: [x_min, y_min, width, height]
            x_min, y_min, w, h = bbox
            if w <= 0 or h <= 0 or img_w <= 0 or img_h <= 0:
                continue

            # Convert to normalized center_x, center_y, width, height
            x_center = (x_min + w / 2.0) / img_w
            y_center = (y_min + h / 2.0) / img_h
            norm_w = w / img_w
            norm_h = h / img_h

            # Clamp to [0, 1]
            x_center = max(0.0, min(1.0, x_center))
            y_center = max(0.0, min(1.0, y_center))
            norm_w = max(0.0, min(1.0, norm_w))
            norm_h = max(0.0, min(1.0, norm_h))

            lines.append(f"{yolo_class} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))

        converted_count += 1

    logger.info(f"Split '{split_dir.name}': converted {converted_count} images ({len(coco.get('annotations', []))} annotations)")
    return converted_count


def process_dataset(dataset_dir: str, output_yaml_path: str = None) -> Tuple[dict, int]:
    base = Path(dataset_dir)
    train_json = base / "train" / "_annotations.coco.json"
    if not train_json.exists():
        raise FileNotFoundError(f"Training annotations not found: {train_json}")

    with open(train_json, "r", encoding="utf-8") as f:
        coco_train = json.load(f)

    # Sort categories to create 0-indexed YOLO classes
    categories = coco_train.get("categories", [])
    # Filter out empty or 'none' categories if any
    sorted_cats = sorted(categories, key=lambda c: c["id"])

    # Create mapping from COCO category_id -> contiguous YOLO class index (0..N-1)
    category_map = {}
    class_names = {}
    for idx, cat in enumerate(sorted_cats):
        category_map[cat["id"]] = idx
        class_names[idx] = cat["name"]

    logger.info(f"Found {len(class_names)} unique sign classes.")

    total_images = 0
    for split in ["train", "valid", "test"]:
        split_dir = base / split
        if split_dir.exists():
            total_images += convert_coco_split_to_yolo(split_dir, category_map)

    # Generate data.yaml
    yaml_config = {
        "path": str(base.resolve()).replace("\\", "/"),
        "train": "train",
        "val": "valid",
        "test": "test",
        "nc": len(class_names),
        "names": {int(k): str(v) for k, v in class_names.items()},
    }

    if output_yaml_path is None:
        output_yaml_path = base / "traffic_signs.yaml"
    else:
        output_yaml_path = Path(output_yaml_path)

    output_yaml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_config, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Dataset YAML saved to: {output_yaml_path}")
    return yaml_config, total_images


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert Roboflow COCO dataset to YOLO")
    parser.add_argument("--dataset-dir", default="archive (3)/traffic_dataset", help="Dataset directory")
    parser.add_argument("--yaml-output", default="training/configs/traffic_signs.yaml", help="Output YAML config")
    args = parser.parse_args()

    process_dataset(args.dataset_dir, args.yaml_output)

