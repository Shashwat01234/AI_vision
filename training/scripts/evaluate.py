"""
Model Evaluation Script
=======================
Evaluates a trained YOLO model on the test set and generates a comprehensive report.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CLASS_NAMES = {
    0: "directional_sign",
    1: "department_sign",
    2: "safety_sign",
    3: "exit_sign",
    4: "information_sign"
}


def evaluate(
    model_path: str,
    dataset_config: str,
    split: str = "test",
    conf: float = 0.25,
    iou: float = 0.45,
    device: str = "auto",
    output_dir: str = "evaluation/results",
):
    """Evaluate model on specified dataset split."""
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("Ultralytics not installed. Install with: pip install ultralytics")
        sys.exit(1)
    
    import torch
    if device == "auto":
        device = "0" if torch.cuda.is_available() else "cpu"
    
    # Load model
    model = YOLO(model_path)
    logger.info(f"Loaded model: {model_path}")

    # Load dataset classes dynamically
    import yaml
    class_names = {}
    try:
        with open(dataset_config, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            names_entry = cfg.get("names", {})
            if isinstance(names_entry, list):
                class_names = {i: n for i, n in enumerate(names_entry)}
            elif isinstance(names_entry, dict):
                class_names = {int(k): str(v) for k, v in names_entry.items()}
    except Exception:
        pass
    if not class_names:
        class_names = getattr(model, "names", CLASS_NAMES)
    
    # Run validation
    results = model.val(
        data=dataset_config,
        split=split,
        conf=conf,
        iou=iou,
        device=device,
        plots=True,
        verbose=True,
    )
    
    # Extract metrics
    metrics = {
        "model_path": str(model_path),
        "dataset_config": str(dataset_config),
        "split": split,
        "evaluation_date": datetime.now().isoformat(),
        "device": device,
        "confidence_threshold": conf,
        "iou_threshold": iou,
        "overall": {
            "mAP50": float(results.box.map50) if hasattr(results.box, 'map50') else None,
            "mAP50-95": float(results.box.map) if hasattr(results.box, 'map') else None,
            "precision": float(results.box.mp) if hasattr(results.box, 'mp') else None,
            "recall": float(results.box.mr) if hasattr(results.box, 'mr') else None,
        },
        "per_class": {}
    }
    
    # Per-class metrics
    if hasattr(results.box, 'maps') and results.box.maps is not None:
        for i, map_val in enumerate(results.box.maps):
            class_name = class_names.get(i, f"class_{i}")
            metrics["per_class"][class_name] = {
                "mAP50-95": float(map_val),
            }
    
    # Save metrics
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    metrics_file = output / "evaluation_metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"Metrics saved to: {metrics_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"Model: {model_path}")
    print(f"Split: {split}")
    print(f"\nOverall Metrics:")
    print(f"  mAP@0.5:      {metrics['overall']['mAP50']:.4f}" if metrics['overall']['mAP50'] else "  mAP@0.5:      N/A")
    print(f"  mAP@0.5:0.95:  {metrics['overall']['mAP50-95']:.4f}" if metrics['overall']['mAP50-95'] else "  mAP@0.5:0.95:  N/A")
    print(f"  Precision:     {metrics['overall']['precision']:.4f}" if metrics['overall']['precision'] else "  Precision:     N/A")
    print(f"  Recall:        {metrics['overall']['recall']:.4f}" if metrics['overall']['recall'] else "  Recall:        N/A")
    
    if metrics["per_class"]:
        print(f"\nPer-Class mAP@0.5:0.95:")
        for cls_name, cls_metrics in metrics["per_class"].items():
            print(f"  {cls_name:20s}: {cls_metrics['mAP50-95']:.4f}")
    
    print("=" * 60)
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate trained YOLO model")
    parser.add_argument("--model", required=True, help="Path to trained model weights")
    parser.add_argument("--data", default="configs/campus_signs.yaml", help="Dataset config")
    parser.add_argument("--split", default="test", help="Dataset split (test/val)")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold")
    parser.add_argument("--device", default="auto", help="Device")
    parser.add_argument("--output", default="evaluation/results", help="Output directory")
    
    args = parser.parse_args()
    evaluate(
        model_path=args.model,
        dataset_config=args.data,
        split=args.split,
        conf=args.conf,
        iou=args.iou,
        device=args.device,
        output_dir=args.output,
    )


if __name__ == "__main__":
    main()

