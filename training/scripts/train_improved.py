"""
Improved YOLO Fine-Tuning Script — better hyperparameters for higher mAP.
Key improvements over baseline:
  - imgsz 416 (larger → better small-sign detection)
  - 10 epochs (vs 3)
  - lr0=0.005, lrf=0.01, warmup 3 epochs
  - Mosaic, flipud, fliplr, hsv augmentation enabled
  - optimizer=AdamW for faster convergence
  - Runs on the FULL 7833-image dataset (not subset)
"""
import os
import shutil
from pathlib import Path
from ultralytics import YOLO


def train_improved(
    data_yaml: str = "training/configs/traffic_signs.yaml",  # full dataset
    epochs: int = 10,
    imgsz: int = 416,
    batch: int = 8,          # small batch for CPU RAM
    base_model: str = "models/custom/best.pt",   # start from existing weights
    output_model_dir: str = "models/custom",
):
    print("=" * 60)
    print("IMPROVED YOLO FINE-TUNING — 10 EPOCHS")
    print("=" * 60)
    print(f"Data:      {data_yaml}")
    print(f"Epochs:    {epochs}")
    print(f"Img size:  {imgsz}")
    print(f"Batch:     {batch}")
    print(f"Base:      {base_model}")

    model = YOLO(base_model)

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device="cpu",
        workers=2,
        project="training/runs",
        name="traffic_signs_improved",
        exist_ok=True,
        plots=True,
        save=True,
        val=True,
        verbose=True,
        # ── Optimizer ──
        optimizer="AdamW",
        lr0=0.005,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        warmup_momentum=0.8,
        # ── Augmentation ──
        mosaic=1.0,
        fliplr=0.5,
        flipud=0.0,
        degrees=5.0,          # slight rotation
        translate=0.1,
        scale=0.3,
        hsv_h=0.015,
        hsv_s=0.4,
        hsv_v=0.3,
        # ── Loss weights ──
        box=7.5,
        cls=0.5,
        dfl=1.5,
        # ── Misc ──
        patience=10,
        close_mosaic=3,
    )

    print("\n" + "=" * 60)
    print("TRAINING COMPLETED — EXPORTING WEIGHTS")
    print("=" * 60)

    run_dir = Path("training/runs/traffic_signs_improved")
    best_weights = run_dir / "weights" / "best.pt"
    if not best_weights.exists():
        best_weights = run_dir / "weights" / "last.pt"

    dest_dir = Path(output_model_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    final_dest = dest_dir / "best.pt"

    if best_weights.exists():
        shutil.copy2(best_weights, final_dest)
        size_mb = final_dest.stat().st_size / 1024 / 1024
        print(f"SUCCESS: Exported → {final_dest} ({size_mb:.2f} MB)")
    else:
        print("WARNING: Weights not found in run directory.")

    # Validation metrics
    print("\nRunning final validation...")
    metrics = model.val(data=data_yaml, imgsz=imgsz, batch=batch, device="cpu")
    map50 = metrics.box.map50
    map95 = metrics.box.map
    prec = metrics.box.p.mean() if hasattr(metrics.box, 'p') and len(metrics.box.p) > 0 else 0
    rec  = metrics.box.r.mean() if hasattr(metrics.box, 'r') and len(metrics.box.r) > 0 else 0
    print(f"\n{'='*40}")
    print(f"Final mAP50:     {map50:.4f}")
    print(f"Final mAP50-95:  {map95:.4f}")
    print(f"Final Precision: {prec:.4f}")
    print(f"Final Recall:    {rec:.4f}")
    print(f"{'='*40}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--imgsz", type=int, default=416)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--data", default="training/configs/traffic_signs.yaml")
    parser.add_argument("--base", default="models/custom/best.pt")
    args = parser.parse_args()

    train_improved(
        data_yaml=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        base_model=args.base,
    )

