# Installation & Setup Guide — AI Accessibility Assistant

This guide provides complete, step-by-step instructions for installing, configuring, and running the **AI-Powered Accessibility Assistant** on Windows, Linux, and macOS.

---

## 1. System Requirements & Prerequisites

### Minimum Hardware Requirements:
- **Processor:** 4-core 64-bit CPU (Intel Core i5 / AMD Ryzen 5 or Apple Silicon M-series).
- **Memory (RAM):** 8 GB minimum (16 GB recommended for local VLM inference).
- **Disk Storage:** At least 5 GB of free space for dependencies, models, and audio cache.
- **GPU:** Optional. The application operates in CPU-only mode by default. CUDA-enabled NVIDIA GPUs (>= 4GB VRAM) will automatically be used if available.

### Software Prerequisites:
- **Python:** Version 3.10, 3.11, or 3.12 (64-bit).
- **Node.js:** Version 18.x or higher with `npm` (Node 20+ LTS recommended).
- **Git:** Latest stable release.

---

## 2. Repository Cloning & Directory Layout

Clone the repository and inspect the directory structure:

```bash
git clone https://github.com/your-org/visual_impaired.git
cd visual_impaired
```

The workspace structure:
```
visual_impaired/
├── backend/            # FastAPI REST backend & AI integration engine
├── frontend/           # React 19 + Vite + Tailwind CSS accessibility client
├── training/           # YOLO sign detection training suite & Colab notebook
├── models/             # Local models directory (pretrained & custom checkpoints)
├── storage/            # SQLite database & local uploads / audio storage
├── tests/              # Pytest automated test suite
└── docs/               # System architecture and user manuals
```

---

## 3. Backend Setup & Configuration

### Step 3.1: Create and Activate a Python Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS (Bash/Zsh):**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3.2: Install Backend Dependencies

Upgrade pip and install the required Python packages:

```bash
python -m pip install --upgrade pip
pip install fastapi uvicorn[standard] pydantic pydantic-settings sqlalchemy aiosqlite python-multipart
pip install PyMuPDF python-docx python-pptx opencv-python Pillow numpy
pip install ultralytics gTTS pytest httpx
```

*Optional packages for local VLM and Piper TTS:*
```bash
pip install torch torchvision transformers piper-tts
```

### Step 3.3: Configure Environment Variables

Copy the sample environment file and configure local paths:

```bash
cp backend/.env.example backend/.env
```

Review or edit `backend/.env`:
```ini
# Application Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO

# Database & Storage
DATABASE_URL=sqlite:///./storage/accessibility.db
UPLOAD_DIR=./storage/uploads
PROCESSED_DIR=./storage/processed
AUDIO_DIR=./storage/audio

# YOLO Model Configuration
YOLO_MODEL_PATH=./models/custom/best.pt
YOLO_PRETRAINED_PATH=./models/pretrained/yolo11n.pt
YOLO_CONFIDENCE_THRESHOLD=0.25

# OCR & VLM Settings
OCR_LANG=en
OCR_USE_GPU=False
VLM_MODEL_NAME=vikhyatk/moondream2
VLM_DEVICE=cpu

# LLM Enhancement (optional: "none", "local", "external")
LLM_PROVIDER=none
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama

# Text-to-Speech
PIPER_VOICE=en_US-lessac-medium
AUDIO_FALLBACK_GTTS=True
```

### Step 3.4: Verify Pretrained Models

Ensure the default pretrained YOLO model is present:

```bash
# Verify model file exists at models/pretrained/yolo11n.pt (5.4 MB)
python -c "from pathlib import Path; print('Pretrained YOLO exists:', Path('models/pretrained/yolo11n.pt').exists())"
```

If missing, the system will automatically download `yolo11n.pt` on first startup, or you can download it directly:
```bash
python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"
```

---

## 4. Frontend Setup & Configuration

### Step 4.1: Install Node Dependencies

Navigate to the `frontend/` directory and install packages:

```bash
cd frontend
npm install
```

### Step 4.2: Configure Frontend Environment

Create a `.env` file in `frontend/` if connecting to a custom backend address:

```ini
VITE_API_BASE_URL=http://localhost:8000/api
```

By default, Vite's development server includes a proxy in `vite.config.js` redirecting `/api` and `/static` requests directly to `http://localhost:8000`.

### Step 4.3: Verify or Build Frontend

To compile the production build:
```bash
npm run build
```
This produces an optimized, accessibility-tested static bundle in `frontend/dist/`.

---

## 5. Running the Application

### Option A: Development Mode (Two Terminals)

**Terminal 1 — Backend API:**
```bash
# From workspace root
python backend/run.py
```
*The FastAPI server will start on `http://localhost:8000`. Interactive OpenAPI documentation will be available at `http://localhost:8000/api/docs`.*

**Terminal 2 — Frontend UI:**
```bash
# In frontend directory
cd frontend
npm run dev
```
*The React application will launch on `http://localhost:5173`.*

### Option B: Production Preview Mode

1. Start backend:
```bash
python backend/run.py
```
2. In a second terminal, serve the production frontend:
```bash
cd frontend
npm run preview
```

---

## 6. Running the Automated Test Suite

Execute the full suite of automated unit, integration, and security tests:

```bash
python -m pytest tests -v
```

Expected output:
```
tests/test_api.py::test_health_check PASSED                              [  7%]
tests/test_api.py::test_get_settings PASSED                              [ 14%]
tests/test_api.py::test_update_settings PASSED                           [ 21%]
tests/test_api.py::test_models_status PASSED                             [ 28%]
tests/test_api.py::test_invalid_file_upload PASSED                       [ 35%]
tests/test_api.py::test_valid_image_upload PASSED                        [ 42%]
tests/test_explanation_engine.py::test_explain_mode_with_signs PASSED    [ 50%]
tests/test_explanation_engine.py::test_uncertainty_handling_low_confidence PASSED [ 57%]
tests/test_explanation_engine.py::test_summarize_mode_concise PASSED     [ 64%]
tests/test_explanation_engine.py::test_document_explain_mode PASSED      [ 71%]
tests/test_security.py::test_sanitize_filename PASSED                    [ 78%]
tests/test_security.py::test_validate_file_type PASSED                   [ 85%]
tests/test_security.py::test_validate_file_size PASSED                   [ 92%]
tests/test_security.py::test_check_path_traversal PASSED                 [100%]
============================= 14 passed in 3.92s ==============================
```

---

## 7. Troubleshooting & FAQ

| Symptom | Cause | Solution |
|---------|-------|----------|
| `ModuleNotFoundError: No module named 'app'` | Python path not including backend | Run tests using `python -m pytest tests` from the repository root (conftest handles path injection). |
| Port 8000 in use | Another service is using port 8000 | Set `PORT=8001` in `backend/.env` and adjust the proxy target in `frontend/vite.config.js`. |
| Piper TTS executable not found | Piper binary not installed | System automatically falls back to `gTTS` (Google Text-to-Speech) with zero configuration required. |
| YOLO loading takes 10+ seconds on CPU | PyTorch CPU layer scanning | Normal on cold start. Models are loaded lazily and cached in memory for all subsequent requests. |
| CORS issues in development | Mismatched ports | Ensure `CORS_ORIGINS` in `backend/.env` includes `http://localhost:5173`. |

