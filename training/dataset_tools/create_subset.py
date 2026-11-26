"""
Ultra-fast subset creator using COCO annotations directly (0.5s execution)
"""
import json
import shutil
from pathlib import Path
import yaml
from collections import defaultdict


def create_fast_subset(
    source_dir: str = "archive (3)/traffic_dataset",
    output_dir: str = "archive (3)/traffic_subset",
    samples_per_class: int = 4,
    val_samples_per_class: int = 1,
):
    src = Path(source_dir)
    out = Path(output_dir)

    for split in ["train", "valid"]:
        (out / split).mkdir(parents=True, exist_ok=True)

    with open("training/configs/traffic_signs.yaml", "r", encoding="utf-8") as f:
        full_cfg = yaml.safe_load(f)

    # 1. Process Train
    train_json = src / "train" / "_annotations.coco.json"
    with open(train_json, "r", encoding="utf-8") as f:
        coco_train = json.load(f)

    img_map = {img["id"]: img["file_name"] for img in coco_train["images"]}
    cat_to_imgs = defaultdict(list)
    for ann in coco_train["annotations"]:
        cat_id = ann["category_id"]
        img_id = ann["image_id"]
        fname = img_map.get(img_id)
        if fname and fname not in cat_to_imgs[cat_id]:
            cat_to_imgs[cat_id].append(fname)

    copied_train = 0
    for cat_id, fnames in cat_to_imgs.items():
        for fname in fnames[:samples_per_class]:
            img_p = src / "train" / fname
            txt_p = src / "train" / (Path(fname).stem + ".txt")
            if img_p.exists() and txt_p.exists():
                shutil.copy2(img_p, out / "train" / fname)
                shutil.copy2(txt_p, out / "train" / txt_p.name)
                copied_train += 1

    print(f"Copied {copied_train} train images.")

    # 2. Process Valid
    val_json = src / "valid" / "_annotations.coco.json"
    with open(val_json, "r", encoding="utf-8") as f:
        coco_val = json.load(f)

    val_img_map = {img["id"]: img["file_name"] for img in coco_val["images"]}
    val_cat_to_imgs = defaultdict(list)
    for ann in coco_val["annotations"]:
        cat_id = ann["category_id"]
        img_id = ann["image_id"]
        fname = val_img_map.get(img_id)
        if fname and fname not in val_cat_to_imgs[cat_id]:
            val_cat_to_imgs[cat_id].append(fname)

    copied_val = 0
    for cat_id, fnames in val_cat_to_imgs.items():
        for fname in fnames[:val_samples_per_class]:
            img_p = src / "valid" / fname
            txt_p = src / "valid" / (Path(fname).stem + ".txt")
            if img_p.exists() and txt_p.exists():
                shutil.copy2(img_p, out / "valid" / fname)
                shutil.copy2(txt_p, out / "valid" / txt_p.name)
                copied_val += 1

    print(f"Copied {copied_val} valid images.")

    # Write traffic_signs_local.yaml
    local_cfg = {
        "path": str(out.resolve()).replace("\\", "/"),
        "train": "train",
        "val": "valid",
        "nc": full_cfg["nc"],
        "names": full_cfg["names"],
    }
    out_yaml = Path("training/configs/traffic_signs_local.yaml")
    with open(out_yaml, "w", encoding="utf-8") as f:
        yaml.dump(local_cfg, f, default_flow_style=False, sort_keys=False)

    print(f"Local config written to: {out_yaml}")
    return copied_train, copied_val


if __name__ == "__main__":
    create_fast_subset()
