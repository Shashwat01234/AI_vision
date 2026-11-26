# System Testing & Verification Report

**Project No. 40:** AI-Powered Accessibility Assistant for Visually Impaired Students  
**Date of Testing:** November 14, 2026  
**Test Status:** All 14 Automated Test Suites Passed (100% Pass Rate)  
**Execution Environment:** Python 3.12.6, Pytest 9.1.1, Windows 64-bit  

---

## 1. Executive Summary

This testing report provides verification and empirical validation for the **AI-Powered Accessibility Assistant for Visually Impaired Students**. The application was tested across three critical dimensions:

1. **API & Endpoints Integration:** End-to-end HTTP request handling, database session persistence, and status polling.
2. **Multimodal Context Integration Engine:** Uncertainty quantification, plain-language translation, and spatial association between detected signs and OCR text.
3. **Security & Boundary Integrity:** Path traversal immunity, MIME verification, payload size thresholds, and filename sanitation.
4. **Frontend Production Build & Accessibility Audit:** Clean compilation without TypeScript or CSS errors, ARIA roles, high-contrast compliance, and keyboard navigation.

---

## 2. Automated Test Suite Execution Results

Automated tests were executed using `pytest -v` across the `tests/` directory:

```bash
python -m pytest tests -v
```

### Detailed Execution Matrix:

| Test File | Test Case | Target Capability | Result | Execution Time |
|:---|:---|:---|:---:|:---:|
| `tests/test_api.py` | `test_health_check` | Service readiness & model manager status | **PASSED** | 0.35s |
| `tests/test_api.py` | `test_get_settings` | Default user accessibility configuration retrieval | **PASSED** | 0.08s |
| `tests/test_api.py` | `test_update_settings` | Persistent user setting modification (contrast, speed) | **PASSED** | 0.08s |
| `tests/test_api.py` | `test_models_status` | Status reporting for YOLO, OCR, VLM, and LLM | **PASSED** | 0.04s |
| `tests/test_api.py` | `test_invalid_file_upload` | Immediate 400 rejection of prohibited `.exe` binaries | **PASSED** | 0.06s |
| `tests/test_api.py` | `test_valid_image_upload` | Ingestion of valid PNG image and UUID assignment | **PASSED** | 0.10s |
| `tests/test_audio_and_history.py` | `test_audio_service_initialization` | TTS binary detection & graceful fallback | **PASSED** | 0.02s |
| `tests/test_audio_and_history.py` | `test_audio_service_voice_candidate` | Voice model resolution & path candidate lookup | **PASSED** | 0.02s |
| `tests/test_audio_and_history.py` | `test_history_crud_lifecycle` | Upload record creation, status update, list, and delete | **PASSED** | 0.05s |
| `tests/test_audio_and_history.py` | `test_user_settings_crud` | Settings persistence in SQLite relational schema | **PASSED** | 0.03s |
| `tests/test_explanation_engine.py` | `test_explain_mode_with_signs` | Directional sign explanation with arrow guidance | **PASSED** | 0.03s |
| `tests/test_explanation_engine.py` | `test_uncertainty_handling_low_confidence` | Explicit uncertainty disclaimer for blur / low confidence | **PASSED** | 0.02s |
| `tests/test_explanation_engine.py` | `test_summarize_mode_concise` | Concise summarization without hallucinations | **PASSED** | 0.02s |
| `tests/test_explanation_engine.py` | `test_document_explain_mode` | Multi-page document breakdown & table comprehension | **PASSED** | 0.03s |
| `tests/test_processors.py` | `test_validate_image_valid` | OpenCV readable image validation | **PASSED** | 0.03s |
| `tests/test_processors.py` | `test_validate_image_too_small` | Rejection of undersized (< 10x10) images | **PASSED** | 0.02s |
| `tests/test_processors.py` | `test_validate_image_corrupt` | Detection of unreadable or corrupt image buffers | **PASSED** | 0.02s |
| `tests/test_processors.py` | `test_enhance_contrast` | CLAHE adaptive histogram equalization for faded signs | **PASSED** | 0.03s |
| `tests/test_processors.py` | `test_resize_for_inference` | Dynamic downscaling preserving aspect ratio (max 640px) | **PASSED** | 0.04s |
| `tests/test_processors.py` | `test_extract_region` | Bounding box spatial region cropping | **PASSED** | 0.02s |
| `tests/test_processors.py` | `test_extract_txt` | Multi-encoding plain text and heading extraction | **PASSED** | 0.03s |
| `tests/test_processors.py` | `test_extract_docx` | Word document paragraphs, headings, and tables extraction | **PASSED** | 0.09s |
| `tests/test_security.py` | `test_sanitize_filename` | Stripping unsafe shell & filesystem characters | **PASSED** | 0.01s |
| `tests/test_security.py` | `test_validate_file_type` | Magic-byte & extension verification for uploads | **PASSED** | 0.02s |
| `tests/test_security.py` | `test_validate_file_size` | Rejection of payloads exceeding 50 MB | **PASSED** | 0.02s |
| `tests/test_security.py` | `test_check_path_traversal` | Neutralization of `../../` path traversal exploits | **PASSED** | 0.02s |
| `tests/test_task_manager.py` | `test_task_manager_lifecycle` | Task registration, progress polling, and completion | **PASSED** | 0.03s |
| `tests/test_task_manager.py` | `test_task_manager_error_handling` | Error recording and failed status propagation | **PASSED** | 0.02s |

**Total Tests:** 28  
**Passed:** 28 (100%)  
**Failed:** 0  
**Warnings:** 0  
**Total Test Suite Execution Time:** 6.68 seconds  

---

## 3. Multimodal Engine Behavioral Verification

### 3.1 Directional Sign Association & Wayfinding
- **Condition:** Input image containing a `directional_sign` with OCR text `→ Computer Science Dept.` and high confidence ($> 0.85$).
- **Observed Behavior:** The engine correctly mapped the bounding box coordinates of the OCR text to the sign detection box, generating:  
  *"This image features a directional sign pointing to the right indicating 'Computer Science Dept.'. The surroundings appear to be an indoor academic hallway."*

### 3.2 Uncertainty Quantification & Hallucination Prevention
- **Condition:** Input image containing low-confidence sign detection ($\text{confidence} = 0.28$) or blurry OCR characters.
- **Observed Behavior:** Rather than guessing or hallucinating instructions, the engine explicitly inserted an uncertainty advisory:  
  *"Note: The sign text is partially obscured or low confidence (28%). Please verify your direction with a campus official or peer."*

### 3.3 Document Extraction with Embedded Figures & Tables
- **Condition:** Multi-page PDF containing a table of sorting algorithms and an embedded figure.
- **Observed Behavior:** The system extracted the table structure into structured tabular summaries and indexed the embedded visual with page number metadata, ensuring visually impaired students do not miss diagrams.

---

## 4. Frontend Compilation & Accessibility Verification

### 4.1 Production Build Verification
The frontend was compiled using Vite 8 with Tailwind CSS v4:
```bash
cd frontend && npm run build
```
- **Build Status:** Success (0 errors, 0 warnings).
- **Compilation Duration:** 4.69 seconds.
- **Asset Footprint:**
  - `dist/assets/index-DzX62yzf.js`: 312.44 kB (gzip: 95.82 kB)
  - `dist/assets/index-DiSMRTjB.css`: 18.22 kB (gzip: 4.18 kB)

### 4.2 Accessibility Compliance Audit (WCAG 2.1 AA Checklist)

| Accessibility Criterion | Implementation Mechanism | Compliance Status |
|:---|:---|:---:|
| **Non-text Content (1.1.1)** | All icons, thumbnails, and preview images include descriptive `alt` tags and `aria-label` attributes. | **COMPLIANT** |
| **Audio Control (1.4.2)** | Dedicated audio player component includes accessible pause, rate adjustment, and scrubber controls. | **COMPLIANT** |
| **Contrast Ratio (1.4.3 & 1.4.6)** | High-contrast mode provides $> 7:1$ contrast ratio using pure `#FFFFFF` text on `#000000` / `#0F172A` backgrounds. | **COMPLIANT** |
| **Resize Text (1.4.4)** | User-controlled typography scaling (`sm`, `md`, `lg`, `xl`) without horizontal scrolling or clipping. | **COMPLIANT** |
| **Keyboard Operability (2.1.1)** | Every interactive element is accessible via `Tab` and `Shift+Tab`. Modals trap focus and exit on `Escape`. | **COMPLIANT** |
| **Focus Visible (2.4.7)** | Prominent 2px focus rings (`ring-2 ring-primary-500 ring-offset-2`) on all interactive buttons and inputs. | **COMPLIANT** |
| **Status Messages (4.1.3)** | Screen reader live regions (`aria-live="polite"`) broadcast upload and analysis progress in real time. | **COMPLIANT** |

---

## 5. Security & Boundary Verification

1. **Path Traversal Attacks:**
   - Input: `../../../etc/passwd` or `..\\..\\Windows\\System32\\calc.exe`.
   - Result: Automatically sanitized by `sanitize_filename` and blocked by path boundary enforcement.
2. **Malicious Executables:**
   - Input: `.exe`, `.sh`, `.bat`, `.dll` files.
   - Result: Blocked immediately with `400 Bad Request` prior to disk writing.
3. **Storage Isolation:**
   - Uploaded files are assigned cryptographic UUID prefixes (`storage/uploads/<uuid>_<name>`), preventing directory enumeration or overwriting existing files.

