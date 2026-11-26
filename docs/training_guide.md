# AI Model Training & Fine-Tuning Guide — Campus Sign Detection

## 1. Project Training Strategy & Objectives

A primary engineering requirement of the **AI-Powered Accessibility Assistant (Project No. 40)** is the inclusion of a genuinely fine-tuned visual AI model. General-purpose object detectors (trained on COCO) detect generic objects like chairs, people, and cars, but cannot categorize the specialized signages essential for visually impaired campus navigation.

Our hybrid strategy combines:
1. **Fine-tuned Custom YOLO Detector:** Specialized in detecting and classifying campus signs and accessibility markers.
2. **Pretrained PaddleOCR:** Reads verbatim alphanumeric text and symbol codes.
3. **Pretrained Vision-Language Model (Moondream2):** Evaluates overall surroundings, architecture, and lighting.
4. **Multimodal Integration Engine:** Fuses bounding boxes, text transcriptions, and scene context into natural navigation guidance.

---

## 2. Target Classes & Annotation Standards

The detector is designed for 5 distinct campus accessibility sign classes:

| Class ID | Class Label | Description | Real-World Campus Examples |
|:---:|:---|:---|:---|
| **0** | `directional_sign` | Wayfinding signs containing arrows indicating directions | "→ Central Library", "↑ Main Auditorium", "← Restrooms" |
| **1** | `department_sign` | Academic departments, laboratories, lecture halls, and faculty office plaques | "Dept. of Computer Science", "Lab 204", "Dean's Office" |
| **2** | `safety_sign` | Hazard warnings, laboratory precautions, and emergency equipment locations | ⚠ High Voltage, ☣ Biohazard, Fire Extinguisher, Eye Wash |
| **3** | `exit_sign` | Emergency exits and building egress markers | "EXIT", "Emergency Exit Only", Green Running Person glyph |
| **4** | `information_sign` | Information boards, campus maps, bulletin boards, and notices | Campus directory, event schedule, notice board |

### YOLO Annotation Format
Each annotation `.txt` file corresponding to an image must follow the standard normalized format:
```
<class_id> <x_center> <y_center> <width> <height>
```
Where all coordinates are float values in the range `[0.0, 1.0]`, normalized by image width and height.

---

## 3. Dataset Infrastructure & Tooling

The repository includes a complete dataset management suite located in `training/dataset_tools/`:

### 3.1 Initializing Dataset Structure
```bash
python training/dataset_tools/prepare_dataset.py create --path training/datasets/campus_signs
```
Creates the standard layout:
```
training/datasets/campus_signs/
├── raw/
│   ├── images/
│   └── labels/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

### 3.2 Validating Annotations
Validates bounding box boundaries, checks for NaN/out-of-range coordinates, unmapped class IDs, and orphaned labels:
```bash
python training/dataset_tools/validate_annotations.py --path training/datasets/campus_signs
```

### 3.3 Data Leakage Prevention & Dataset Splitting
Generates deterministic 70/20/10 train/val/test splits using a fixed random seed (`--seed 42`):
```bash
python training/dataset_tools/split_dataset.py \
  --path training/datasets/campus_signs \
  --train 0.7 --val 0.2 --test 0.1 --seed 42
```

### 3.4 Data Augmentation
To improve model generalization across varied campus lighting and weather conditions, use the augmentation script:
```bash
python training/dataset_tools/augment_data.py \
  --input training/datasets/campus_signs/train \
  --output training/datasets/campus_signs/train_aug \
  --techniques blur,brightness,contrast,rotate
```

---

## 4. Google Colab GPU Training Workflow

Because local development machines may lack dedicated NVIDIA CUDA hardware, a fully reproducible Google Colab notebook is provided at:
[`training/notebooks/yolo_campus_sign_training.ipynb`](file:///c:/visual_impaired/training/notebooks/yolo_campus_sign_training.ipynb).

### Step-by-Step Training in Colab:

1. **Open Google Colab:** Navigate to [Google Colab](https://colab.research.google.com/) and upload `yolo_campus_sign_training.ipynb`.
2. **Select GPU Runtime:** Go to **Runtime → Change runtime type** and select **T4 GPU** (or A100 if subscribed to Colab Pro).
3. **Mount Google Drive (for Checkpoint Persistence):**
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
4. **Clone or Upload Dataset:**
   Upload the prepared `campus_signs` dataset or download it directly from your Roboflow workspace.
5. **Execute Training Cell:**
   The training script executes Ultralytics YOLO with early stopping, dynamic image sizing (640px), and automatic mixed precision (AMP):
   ```python
   from ultralytics import YOLO

   # Initialize lightweight YOLO11n backbone
   model = YOLO('yolo11n.pt')

   # Fine-tune on custom dataset
   results = model.train(
       data='training/configs/campus_signs.yaml',
       epochs=80,
       patience=15,
       imgsz=640,
       batch=16,
       device=0,
       project='/content/drive/MyDrive/campus_signs_run',
       name='yolo_campus_signs_v1',
       save=True,
       val=True,
       plots=True
   )
   ```
6. **Automatic OOM Fallback:**
   If GPU VRAM is constrained, the notebook automatically catches CUDA Out-of-Memory exceptions and restarts with a halved batch size (`batch=8` or `batch=4`).

---

## 5. Model Evaluation & Export

Once training reaches convergence or early stopping triggers:

### 5.1 Metric Targets:
- **mAP@50:** Target $\ge 0.75$ across all sign categories.
- **mAP@50-95:** Target $\ge 0.50$.
- **Inference Latency:** $\le 25\text{ ms}$ on GPU; $\le 80\text{ ms}$ on modern CPU.

### 5.2 Artifact Outputs:
Training generates:
- `best.pt`: Model weights with the highest validation mAP.
- `last.pt`: Final epoch checkpoint.
- `confusion_matrix.png`: Matrix showing inter-class classification accuracy.
- `results.png`: Precision, recall, and loss curves across epochs.

### 5.3 Exporting & Deploying to Backend:
Copy the trained `best.pt` file into the backend's designated custom model path:
```bash
cp /path/to/best.pt c:/visual_impaired/models/custom/best.pt
```

The FastAPI backend automatically checks `models/custom/best.pt` on startup:
```python
if Path("./models/custom/best.pt").exists():
    # Automatically loads custom campus sign detector
```
No code modifications or backend reconfigurations are required. If `best.pt` is not present, the backend gracefully falls back to `models/pretrained/yolo11n.pt`.

