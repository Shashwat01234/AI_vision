"""
Image Analysis Service — full image pipeline orchestrator.
"""
import json
import logging
import os
from pathlib import Path
import cv2

from app.config import settings
from app.ai_models.model_manager import model_manager
from app.processors.image_processor import validate_image, preprocess, extract_region
from app.services.explanation_engine import ExplanationEngine, ExplanationInput
from app.services.task_manager import task_manager, TaskStatus
from app.database.database import SessionLocal
from app.database import crud

logger = logging.getLogger(__name__)
_engine = ExplanationEngine()


async def analyze_image_task(upload_id: int, task_id: str, mode: str) -> None:
    db = SessionLocal()
    try:
        await task_manager.update(task_id, TaskStatus.PROCESSING, 10, "Loading image...")
        crud.update_upload_status(db, upload_id, "processing")

        upload = crud.get_upload(db, upload_id)
        if not upload:
            raise ValueError(f"Upload {upload_id} not found")

        image_path = str(upload.file_path)
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # 2. Validate & preprocess
        await task_manager.update(task_id, TaskStatus.VALIDATING, 15, "Validating image...")
        valid, msg = validate_image(image_path)
        if not valid:
            raise ValueError(f"Invalid image: {msg}")

        processed_path = str(settings.get_processed_dir() / f"proc_{Path(image_path).name}")
        preprocess(image_path, processed_path)

        # 3. YOLO detection
        await task_manager.update(task_id, TaskStatus.PROCESSING, 30, "Detecting signs and objects...")
        yolo = model_manager.get_yolo()
        detections = []
        if yolo.is_available:
            raw_detections = yolo.detect(processed_path, settings.YOLO_CONFIDENCE_THRESHOLD)
            detections = [d.to_dict() for d in raw_detections]

            # OCR on detected sign regions
            ocr_engine = model_manager.get_ocr()
            if ocr_engine.is_available:
                img_cv = cv2.imread(processed_path)
                if img_cv is not None:
                    for det in detections:
                        if "sign" in det.get("label", ""):
                            region_text = ocr_engine.extract_text_from_region(
                                img_cv, det.get("bbox", [0, 0, 0, 0])
                            )
                            if region_text:
                                det["ocr_text"] = region_text

        # 4. OCR on full image
        await task_manager.update(task_id, TaskStatus.PROCESSING, 50, "Extracting text...")
        ocr_engine = model_manager.get_ocr()
        ocr_results = []
        if ocr_engine.is_available:
            raw_ocr = ocr_engine.extract_text(processed_path)
            ocr_results = [r.to_dict() for r in raw_ocr]

        # 5. VLM scene description (with safety timeout)
        scene_description = None
        vlm = model_manager.get_vlm()
        if vlm.is_available:
            await task_manager.update(task_id, TaskStatus.PROCESSING, 65, "Analysing scene context...")
            try:
                import asyncio
                timeout_sec = getattr(settings, "VLM_TIMEOUT_SECONDS", 15)
                scene_description = await asyncio.wait_for(
                    asyncio.to_thread(vlm.describe_image, processed_path),
                    timeout=timeout_sec
                )
            except asyncio.TimeoutError:
                logger.warning(f"VLM inference timed out after {timeout_sec}s; proceeding with YOLO + OCR explanation")
            except Exception as vlm_err:
                logger.warning(f"VLM inference skipped: {vlm_err}")

        # 6. Build explanation
        await task_manager.update(task_id, TaskStatus.GENERATING_EXPLANATION, 80, "Generating explanation...")
        inp = ExplanationInput(
            yolo_detections=detections,
            ocr_results=ocr_results,
            vlm_description=scene_description,
            file_type="image",
            filename=upload.original_filename,
            mode=mode,
        )
        output = _engine.build_explanation(inp)

        llm = model_manager.get_llm()
        explanation = output.main_explanation
        if llm.is_available:
            explanation = llm.enhance(explanation, {}, mode)

        # Generate audio narration automatically
        await task_manager.update(task_id, TaskStatus.GENERATING_AUDIO, 85, "Generating audio narration...")
        audio_id = None
        if explanation:
            try:
                from app.services.audio_service import audio_service
                audio_id = await audio_service.generate(
                    text=explanation,
                    upload_id=upload_id,
                    voice=settings.PIPER_VOICE,
                    speed=1.0,
                )
                if audio_id:
                    audio_path = audio_service.get_audio_path(audio_id)
                    if audio_path:
                        crud.create_audio_record(
                            db=db,
                            upload_id=upload_id,
                            audio_path=audio_path,
                            voice=settings.PIPER_VOICE,
                            speed=1.0,
                            audio_id=audio_id,
                        )
            except Exception as audio_err:
                logger.warning(f"Image audio generation skipped: {audio_err}")

        # 7. Save results
        crud.update_analysis_result(
            db, task_id,
            scene_description=scene_description or "",
            detected_objects=output.object_details,
            detected_signs=output.sign_details,
            ocr_text=ocr_results,
            explanation=explanation,
            confidence_info={"notes": output.confidence_notes, "sources": output.sources},
            audio_id=audio_id,
        )
        crud.update_upload_status(db, upload_id, "completed")
        await task_manager.update(task_id, TaskStatus.COMPLETED, 100, "Analysis complete")
        logger.info(f"Image analysis complete: upload={upload_id} task={task_id}")

    except Exception as e:
        logger.exception(f"Image analysis failed: upload={upload_id}")
        err_msg = str(e)
        await task_manager.update(task_id, TaskStatus.FAILED, 0, "Analysis failed", error=err_msg)
        try:
            crud.update_upload_status(db, upload_id, "failed", error_message=err_msg)
        except Exception:
            pass
    finally:
        db.close()
