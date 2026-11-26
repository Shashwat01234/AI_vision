"""
YOLO Fine-Tuning Script for Traffic / Campus Signs
Trains on the converted dataset, evaluates metrics, and exports best.pt to models/custom/best.pt.
"""
import os
import shutil
from pathlib import Path

# Set local YOLO config directory to prevent Windows AppData permission issues
config_dir = Path(__file__).resolve().parent.parent.parent / "models" / ".ultralytics"
config_dir.mkdir(parents=True, exist_ok=True)
os.environ["YOLO_CONFIG_DIR"] = str(config_dir)

from ultralytics import YOLO

def train_and_export(
    data_yaml: str = "training/configs/traffic_signs_local.yaml",
    epochs: int = 25,
    imgsz: int = 320,
    batch: int = 16,
    base_model: str = "models/pretrained/yolo11n.pt",
    output_model_dir: str = "models/custom",
):
    print("=" * 60)
    print("STARTING YOLO FINE-TUNING ON SIGNS DATASET")
    print("=" * 60)
    print(f"Data config: {data_yaml}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch}")
    print(f"Image size: {imgsz}")
    print(f"Base model: {base_model}")

    model = YOLO(base_model)

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device="cpu",
        workers=2,
        fliplr=0.0,  # CRITICAL: Do not horizontally mirror directional and arrow signs
        project="training/runs",
        name="traffic_signs_local",
        exist_ok=True,
        plots=True,
        save=True,
        val=True,
        verbose=True,
    )

    print("\n" + "=" * 60)
    print("TRAINING COMPLETED. EXPORTING WEIGHTS...")
    print("=" * 60)

    run_dir = Path("runs/detect/training/runs/traffic_signs_local")
    if not run_dir.exists():
        run_dir = Path("training/runs/traffic_signs_local")
    best_weights = run_dir / "weights" / "best.pt"
    if not best_weights.exists():
        best_weights = run_dir / "weights" / "last.pt"

    dest_dir = Path(output_model_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    final_dest = dest_dir / "best.pt"

    if best_weights.exists():
        shutil.copy2(best_weights, final_dest)
        print(f"SUCCESS: Exported custom-trained model to {final_dest} ({final_dest.stat().st_size / 1024 / 1024:.2f} MB)")
    else:
        print("WARNING: best.pt weights file not found in run directory.")

    # Run quick validation on the test/val set
    print("\nRunning Validation Evaluation...")
    metrics = model.val(data=data_yaml, imgsz=imgsz, batch=batch, device="cpu")
    print(f"Validation mAP50: {metrics.box.map50:.4f}")
    print(f"Validation mAP50-95: {metrics.box.map:.4f}")
    print(f"Validation Precision: {metrics.box.p.mean():.4f}" if len(metrics.box.p) else "Validation Precision: N/A")
    print(f"Validation Recall: {metrics.box.r.mean():.4f}" if len(metrics.box.r) else "Validation Recall: N/A")

    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--data", default="training/configs/traffic_signs_local.yaml")
    args = parser.parse_args()

    train_and_export(data_yaml=args.data, epochs=args.epochs)

