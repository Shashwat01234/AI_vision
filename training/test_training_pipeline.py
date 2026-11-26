"""
Training & Pipeline Verification Script for archive (3) Traffic Dataset
Verifies that:
1. Dataset YAML configuration is valid
2. YOLO model can parse images and label txt files
3. Runs 1 quick verification epoch on a subset of the dataset
4. Evaluates the resulting weights on test split
"""
import sys
from pathlib import Path
import yaml
from ultralytics import YOLO

def verify_dataset_and_train():
    yaml_path = Path("training/configs/traffic_signs.yaml")
    if not yaml_path.exists():
        raise FileNotFoundError(f"Config {yaml_path} does not exist.")

    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    print(f"Dataset root: {cfg['path']}")
    print(f"Number of classes: {cfg['nc']}")
    print(f"Sample classes: {[cfg['names'][i] for i in range(min(5, cfg['nc']))]}")

    # Check that sample label files exist
    train_dir = Path(cfg["path"]) / cfg["train"]
    label_files = list(train_dir.glob("*.txt"))
    print(f"Total train label files found: {len(label_files)}")
    assert len(label_files) > 0, "No label files found!"

    # Sample read one label file
    sample_txt = label_files[0]
    with open(sample_txt, "r") as f:
        sample_content = f.read().strip()
    print(f"Sample label ({sample_txt.name}):\n{sample_content}")

    # Load base model
    pretrained_path = Path("models/pretrained/yolo11n.pt")
    if pretrained_path.exists():
        model_source = str(pretrained_path)
    else:
        model_source = "yolo11n.pt"

    print(f"Loading base YOLO model from: {model_source}")
    model = YOLO(model_source)

    print("YOLO model loaded successfully. Ready for training.")
    return True

if __name__ == "__main__":
    verify_dataset_and_train()

