"""
YOLO Training Script
====================
Trains a YOLO model for campus sign detection.
Can be run locally (with GPU) or as part of a Colab workflow.
"""

import os
import sys
import yaml
import argparse
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def check_environment():
    """Check training environment and report capabilities."""
    info = {"gpu_available": False, "gpu_name": None, "gpu_memory": None}
    
    try:
        import torch
        info["torch_version"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        
        if torch.cuda.is_available():
            info["gpu_available"] = True
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory"] = f"{torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB"
            info["cuda_version"] = torch.version.cuda
        
    except ImportError:
        info["torch_version"] = "NOT INSTALLED"
        info["cuda_available"] = False
    
    try:
        import ultralytics
        info["ultralytics_version"] = ultralytics.__version__
    except ImportError:
        info["ultralytics_version"] = "NOT INSTALLED"
    
    return info


def load_training_config(config_path: str) -> dict:
    """Load training configuration from YAML file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def train(
    dataset_config: str,
    training_config: str = None,
    base_model: str = "yolo11n.pt",
    epochs: int = 80,
    imgsz: int = 640,
    batch_size: int = 16,
    device: str = "auto",
    project: str = "runs/campus_signs",
    name: str = "train",
    resume: bool = False,
    weights_dir: str = "../../models/custom",
):
    """Run YOLO training."""
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("Ultralytics not installed. Install with: pip install ultralytics")
        sys.exit(1)
    
    # Load training config if provided
    if training_config:
        config = load_training_config(training_config)
        train_cfg = config.get("training", {})
        epochs = train_cfg.get("epochs", epochs)
        imgsz = train_cfg.get("imgsz", imgsz)
        batch_size = train_cfg.get("batch_size", batch_size)
        base_model = config.get("model", {}).get("base_model", base_model)
    
    # Determine device
    if device == "auto":
        import torch
        device = "0" if torch.cuda.is_available() else "cpu"
    
    logger.info(f"Training configuration:")
    logger.info(f"  Base model: {base_model}")
    logger.info(f"  Dataset config: {dataset_config}")
    logger.info(f"  Epochs: {epochs}")
    logger.info(f"  Image size: {imgsz}")
    logger.info(f"  Batch size: {batch_size}")
    logger.info(f"  Device: {device}")
    logger.info(f"  Project: {project}")
    
    # Load model
    try:
        model = YOLO(base_model)
        logger.info(f"Loaded base model: {base_model}")
    except Exception as e:
        logger.warning(f"Could not load {base_model}: {e}")
        fallback = "yolov8n.pt"
        logger.info(f"Trying fallback model: {fallback}")
        model = YOLO(fallback)
    
    # Train
    try:
        results = model.train(
            data=dataset_config,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch_size,
            device=device,
            project=project,
            name=name,
            exist_ok=True,
            patience=15,
            save=True,
            save_period=10,
            plots=True,
            verbose=True,
            seed=42,
            deterministic=True,
            cos_lr=True,
            close_mosaic=10,
            resume=resume,
        )
        
        logger.info("Training completed successfully!")
        
        # Copy best weights to models directory
        best_weights = Path(project) / name / "weights" / "best.pt"
        last_weights = Path(project) / name / "weights" / "last.pt"
        weights_out = Path(weights_dir)
        weights_out.mkdir(parents=True, exist_ok=True)
        
        import shutil
        if best_weights.exists():
            shutil.copy2(best_weights, weights_out / "best.pt")
            logger.info(f"Best weights saved to: {weights_out / 'best.pt'}")
        
        if last_weights.exists():
            shutil.copy2(last_weights, weights_out / "last.pt")
            logger.info(f"Last weights saved to: {weights_out / 'last.pt'}")
        
        return results
        
    except RuntimeError as e:
        if "out of memory" in str(e).lower() or "CUDA" in str(e):
            logger.warning(f"OOM error with batch_size={batch_size}. Reducing to {batch_size // 2}")
            
            if batch_size > 1:
                import torch
                torch.cuda.empty_cache()
                return train(
                    dataset_config=dataset_config,
                    training_config=None,
                    base_model=base_model,
                    epochs=epochs,
                    imgsz=imgsz,
                    batch_size=batch_size // 2,
                    device=device,
                    project=project,
                    name=name,
                    resume=resume,
                    weights_dir=weights_dir,
                )
            else:
                logger.error("Cannot reduce batch size further. Training failed.")
                raise
        else:
            raise


def main():
    parser = argparse.ArgumentParser(description="Train YOLO campus sign detector")
    parser.add_argument("--data", default="configs/campus_signs.yaml", help="Dataset YAML config")
    parser.add_argument("--config", default="configs/training_config.yaml", help="Training config")
    parser.add_argument("--model", default=None, help="Override base model")
    parser.add_argument("--epochs", type=int, default=None, help="Override epochs")
    parser.add_argument("--batch", type=int, default=None, help="Override batch size")
    parser.add_argument("--imgsz", type=int, default=None, help="Override image size")
    parser.add_argument("--device", default="auto", help="Device: auto/cpu/0")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--check-env", action="store_true", help="Check environment only")
    
    args = parser.parse_args()
    
    if args.check_env:
        info = check_environment()
        print("\n=== Training Environment ===")
        for k, v in info.items():
            print(f"  {k}: {v}")
        if not info.get("gpu_available"):
            print("\n  ⚠ No GPU available. Training will be very slow on CPU.")
            print("  Consider using Google Colab (see notebooks/yolo_campus_sign_training.ipynb)")
        return
    
    # Load config and apply overrides
    config = load_training_config(args.config) if Path(args.config).exists() else {}
    train_cfg = config.get("training", {})
    
    train(
        dataset_config=args.data,
        training_config=args.config if Path(args.config).exists() else None,
        base_model=args.model or config.get("model", {}).get("base_model", "yolo11n.pt"),
        epochs=args.epochs or train_cfg.get("epochs", 80),
        imgsz=args.imgsz or train_cfg.get("imgsz", 640),
        batch_size=args.batch or train_cfg.get("batch_size", 16),
        device=args.device,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()

