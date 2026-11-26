# REST API Reference — AI Accessibility Assistant

The backend exposes a high-performance RESTful API adhering to OpenAPI 3.1 specifications. Interactive Swagger documentation is available at `http://localhost:8000/api/docs` and ReDoc at `http://localhost:8000/api/redoc`.

**Base URL:** `http://localhost:8000/api`

---

## 1. System & Health Endpoints

### 1.1 Health Check
- **Endpoint:** `GET /health` or `GET /api/health`
- **Description:** Verifies service health, active version, and AI model availability.
- **Response (200 OK):**
```json
{
  "status": "healthy",
  "app": "AI Accessibility Assistant API",
  "version": "1.0.0",
  "models": {
    "yolo": {
      "available": true,
      "is_custom": false,
      "model_path": "C:\\visual_impaired\\models\\pretrained\\yolo11n.pt"
    },
    "ocr": {
      "available": false
    },
    "vlm": {
      "available": true,
      "model": "vikhyatk/moondream2"
    },
    "llm": {
      "available": true,
      "provider": "none"
    }
  }
}
```

---

## 2. File Upload

### 2.1 Upload File
- **Endpoint:** `POST /api/upload`
- **Content-Type:** `multipart/form-data`
- **Supported Formats:**
  - Images: `.jpg`, `.jpeg`, `.png`, `.webp`
  - Documents: `.pdf`, `.docx`, `.pptx`, `.txt`
- **Max File Size:** 50 MB
- **Request Parameters:**
  - `file`: Binary file upload.
- **Response (200 OK):**
```json
{
  "upload_id": 1,
  "filename": "a1b2c3d4_campus_sign.png",
  "original_filename": "campus_sign.png",
  "file_type": "image",
  "mime_type": "image/png",
  "file_size": 204800,
  "file_url": "/static/uploads/a1b2c3d4_campus_sign.png",
  "upload_time": "2026-11-14T09:30:00Z",
  "status": "uploaded"
}
```
- **Error Responses:**
  - `400 Bad Request`: Disallowed extension or MIME mismatch.
  - `413 Payload Too Large`: File exceeds 50 MB.

---

## 3. Image Understanding Pipeline

### 3.1 Submit Image for Analysis
- **Endpoint:** `POST /api/image/analyze`
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "upload_id": 1,
  "mode": "explain"
}
```
*Valid modes:* `"read"`, `"explain"`, `"summarize"`.
- **Response (200 OK):**
```json
{
  "task_id": "img-task-9f8a7b6c-5d4e-3f2a-1b0c-9d8e7f6a5b4c",
  "upload_id": 1,
  "status": "queued",
  "message": "Image analysis started."
}
```

### 3.2 Poll Image Task Progress
- **Endpoint:** `GET /api/image/task/{task_id}`
- **Response (200 OK):**
```json
{
  "task_id": "img-task-9f8a7b6c-5d4e-3f2a-1b0c-9d8e7f6a5b4c",
  "status": "processing",
  "progress": 65,
  "step": "Detecting signs and reading text...",
  "error": null
}
```
*Statuses:* `"queued"`, `"validating"`, `"processing"`, `"completed"`, `"failed"`.

### 3.3 Get Image Analysis Result
- **Endpoint:** `GET /api/image/result/{upload_id}`
- **Response (200 OK):**
```json
{
  "id": 1,
  "upload_id": 1,
  "mode": "explain",
  "scene_description": "An indoor well-lit college hallway with classrooms along the right side.",
  "detected_objects": [
    {
      "label": "directional_sign",
      "confidence": 0.89,
      "bbox": [120, 85, 340, 210],
      "class_id": 0,
      "ocr_text": "→ Computer Science Dept."
    }
  ],
  "detected_signs": [
    {
      "class_name": "directional_sign",
      "confidence": 0.89,
      "bbox": [120, 85, 340, 210],
      "ocr_text": "→ Computer Science Dept."
    }
  ],
  "ocr_text": [
    {
      "text": "→ Computer Science Dept.",
      "confidence": 0.94,
      "bbox": [[125, 90], [335, 90], [335, 205], [125, 205]]
    }
  ],
  "explanation": "This image features a directional sign pointing to the right indicating 'Computer Science Dept.'. The surroundings appear to be an indoor academic hallway.",
  "confidence_info": {
    "detection_confidence": 0.89,
    "ocr_confidence": 0.94,
    "has_uncertainty": false
  },
  "audio_id": "audio-550e8400-e29b-41d4-a716-446655440000",
  "audio_url": "/static/audio/audio-550e8400-e29b-41d4-a716-446655440000.wav"
}
```

---

## 4. Document Understanding Pipeline

### 4.1 Submit Document for Analysis
- **Endpoint:** `POST /api/document/analyze`
- **Request Body:**
```json
{
  "upload_id": 2,
  "mode": "summarize"
}
```
- **Response (200 OK):**
```json
{
  "task_id": "doc-task-1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "upload_id": 2,
  "status": "queued",
  "message": "Document analysis started."
}
```

### 4.2 Poll Document Task Progress
- **Endpoint:** `GET /api/document/task/{task_id}`

### 4.3 Get Document Analysis Result
- **Endpoint:** `GET /api/document/result/{upload_id}`
- **Response (200 OK):**
```json
{
  "id": 2,
  "upload_id": 2,
  "mode": "summarize",
  "total_pages": 4,
  "headings": ["1. Introduction to Algorithms", "2. Asymptotic Complexity"],
  "tables": [
    {
      "page": 2,
      "rows": [["Algorithm", "Best Case", "Worst Case"], ["QuickSort", "O(n log n)", "O(n^2)"]]
    }
  ],
  "embedded_visuals": [
    {
      "page": 3,
      "type": "figure",
      "description": "Chart illustrating growth rates of standard complexities."
    }
  ],
  "summary": "This document outlines algorithmic complexity principles, detailing sorting benchmarks across 4 pages.",
  "audio_url": "/static/audio/doc-audio-123.wav"
}
```

---

## 5. Audio Narration

### 5.1 Generate Speech for Text
- **Endpoint:** `POST /api/audio/generate`
- **Request Body:**
```json
{
  "upload_id": 1,
  "text": "This image features a directional sign pointing towards the Library.",
  "voice": "en_US-lessac-medium",
  "speed": 1.0
}
```
- **Response (200 OK):**
```json
{
  "audio_id": "aud-1a2b3c",
  "audio_url": "/static/audio/aud-1a2b3c.wav",
  "duration": 4.2,
  "voice": "en_US-lessac-medium",
  "speed": 1.0
}
```

---

## 6. History & User Settings

### 6.1 List History
- **Endpoint:** `GET /api/history?page=1&page_size=20`
- **Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "filename": "a1b2c3d4_campus_sign.png",
      "original_filename": "campus_sign.png",
      "file_type": "image",
      "mime_type": "image/png",
      "file_size": 204800,
      "upload_time": "2026-11-14T09:30:00Z",
      "status": "completed",
      "has_analysis": true,
      "has_audio": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### 6.2 Delete History Record
- **Endpoint:** `DELETE /api/history/{id}`
- **Response (200 OK):**
```json
{
  "detail": "Record deleted successfully."
}
```

### 6.3 Get User Settings
- **Endpoint:** `GET /api/settings`
- **Response (200 OK):**
```json
{
  "voice": "en_US-lessac-medium",
  "speech_speed": 1.0,
  "text_size": "md",
  "high_contrast": false,
  "reduced_motion": false,
  "screen_reader_optimized": true,
  "data_retention_days": 30
}
```

### 6.4 Update User Settings
- **Endpoint:** `PUT /api/settings`
- **Request Body:**
```json
{
  "speech_speed": 1.25,
  "high_contrast": true,
  "text_size": "lg"
}
```

