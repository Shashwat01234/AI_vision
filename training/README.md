# Campus Signs Detection — Training Guide

## Overview

This directory contains the complete training pipeline for fine-tuning a YOLO model to detect campus signs. The trained model is integrated into the AI Accessibility Assistant to help visually impaired students identify and understand signs in their environment.

## Target Classes

| ID | Class | Description | Examples |
|----|-------|-------------|----------|
| 0 | `directional_sign` | Signs with arrows indicating directions | "→ Library", "← Parking" |
| 1 | `department_sign` | Department, room, office labels | "Computer Science Dept.", "Room 101" |
| 2 | `safety_sign` | Warning and hazard symbols | ⚠ Caution, ☣ Biohazard |
| 3 | `exit_sign` | Emergency exit signs | EXIT, 🚪 Emergency Exit |
| 4 | `information_sign` | Information boards, notice boards | Maps, schedules, announcements |

## Quick Start

### 1. Prepare Dataset Structure

```bash
cd training
python dataset_tools/prepare_dataset.py create --path ./datasets/campus_signs
```

### 2. Add Your Data

Place annotated images in `datasets/campus_signs/raw/`:
- Images → `raw/images/`
- YOLO-format labels → `raw/labels/`

**Or import from Roboflow:**
```bash
python dataset_tools/prepare_dataset.py import-roboflow \
  --export-dir /path/to/roboflow/export \
  --target ./datasets/campus_signs
```

### 3. Validate Annotations

```bash
python dataset_tools/validate_annotations.py --path ./datasets/campus_signs
```

### 4. Split Dataset

```bash
python dataset_tools/split_dataset.py --path ./datasets/campus_signs \
  --train 0.7 --val 0.2 --test 0.1 --seed 42
```

### 5. Visualize Annotations

```bash
python dataset_tools/visualize_annotations.py --path ./datasets/campus_signs \
  --split train --max-images 20
```

### 6. Train

**Option A: Google Colab (recommended — free GPU)**
1. Open `notebooks/yolo_campus_sign_training.ipynb` in Google Colab
2. Enable GPU runtime
3. Upload your dataset or connect to Roboflow
4. Run all cells
5. Download `best.pt` to `models/custom/`

**Option B: Local training (requires GPU)**
```bash
python scripts/train.py --data configs/campus_signs.yaml \
  --config configs/training_config.yaml --device auto
```

### 7. Evaluate

```bash
python scripts/evaluate.py --model ../models/custom/best.pt \
  --data configs/campus_signs.yaml --split test
```

### 8. Export

```bash
python scripts/export_model.py --model ../models/custom/best.pt \
  --format torchscript
```

## Dataset Requirements

### Target Size
- **Minimum:** 500 images
- **Recommended:** 1,000–1,500 images
- **Per class:** At least 100 images per class

### Image Guidelines
- Various sign designs and styles
- Different lighting conditions (daylight, artificial, dim)
- Different distances (close-up, medium, far)
- Different camera angles
- Indoor and outdoor settings
- Some partially obscured signs
- Negative samples (images without any signs): ~10-15% of dataset

### Annotation Format
YOLO format: one `.txt` file per image, each line:
```
class_id center_x center_y width height
```
All coordinates normalized to [0, 1].

## Training Configuration

Edit `configs/training_config.yaml` to adjust:
- Base model (default: YOLO11n)
- Epochs (default: 80)
- Image size (default: 640)
- Batch size (default: 16, auto-reduces on OOM)
- Augmentation parameters
- Early stopping patience

## Output Files

After training, find these in `runs/campus_signs/`:
- `weights/best.pt` — Best model weights (copy to `models/custom/`)
- `weights/last.pt` — Last checkpoint
- `results.csv` — Training metrics per epoch
- `results.png` — Training curves
- `confusion_matrix.png` — Confusion matrix
- `P_curve.png`, `R_curve.png`, `PR_curve.png` — Evaluation curves

## Directory Structure

```
training/
├── configs/
│   ├── campus_signs.yaml          # Dataset class config
│   └── training_config.yaml       # Hyperparameters
├── dataset_tools/
│   ├── prepare_dataset.py         # Create structure, import data
│   ├── validate_annotations.py    # Validate YOLO annotations
│   ├── split_dataset.py           # Train/val/test split
│   ├── augment_data.py            # Offline augmentation
│   └── visualize_annotations.py   # Draw boxes on images
├── scripts/
│   ├── train.py                   # Training script
│   ├── evaluate.py                # Evaluation script
│   └── export_model.py            # Model export
├── evaluation/
│   └── generate_report.py         # Generate training report
├── notebooks/
│   └── yolo_campus_sign_training.ipynb  # Google Colab notebook
└── README.md                      # This file
```

