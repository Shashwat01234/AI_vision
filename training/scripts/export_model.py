"""
Model Export Script
===================
Exports trained YOLO model to production-ready formats.
"""

import os
import sys
import shutil
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def export_model(
    model_path: str,
    output_dir: str = "../../models/custom",
    format: str = "torchscript",
    imgsz: int = 640,
    optimize: bool = True,
):
    """Export YOLO model to specified format."""
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("Ultralytics not installed.")
        sys.exit(1)
    
    model = YOLO(model_path)
    logger.info(f"Loaded model: {model_path}")
    
    # Export
    exported_path = model.export(
        format=format,
        imgsz=imgsz,
        optimize=optimize,
    )
    
    logger.info(f"Model exported to: {exported_path}")
    
    # Copy to output directory
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    exported_file = Path(exported_path)
    if exported_file.exists():
        dest = output / exported_file.name
        shutil.copy2(exported_file, dest)
        logger.info(f"Copied to: {dest}")
    
    # Also copy the .pt file for easy use
    pt_file = Path(model_path)
    if pt_file.exists():
        dest = output / "best.pt"
        shutil.copy2(pt_file, dest)
        logger.info(f"PT weights copied to: {dest}")
    
    return exported_path


def main():
    parser = argparse.ArgumentParser(description="Export trained YOLO model")
    parser.add_argument("--model", required=True, help="Path to trained model (.pt)")
    parser.add_argument("--output", default="../../models/custom", help="Output directory")
    parser.add_argument("--format", default="torchscript", 
                       choices=["torchscript", "onnx", "engine", "coreml"],
                       help="Export format")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--no-optimize", action="store_true", help="Disable optimization")
    
    args = parser.parse_args()
    export_model(
        model_path=args.model,
        output_dir=args.output,
        format=args.format,
        imgsz=args.imgsz,
        optimize=not args.no_optimize,
    )


if __name__ == "__main__":
    main()

