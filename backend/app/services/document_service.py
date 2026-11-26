"""
Document Analysis Service — full document pipeline orchestrator.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict

from app.config import settings
from app.ai_models.model_manager import model_manager
from app.services.explanation_engine import ExplanationEngine, ExplanationInput
from app.services.task_manager import task_manager, TaskStatus
from app.database.database import SessionLocal
from app.database import crud

logger = logging.getLogger(__name__)
_engine = ExplanationEngine()


async def analyze_document_task(upload_id: int, task_id: str, mode: str) -> None:
    db = SessionLocal()
    try:
        await task_manager.update(task_id, TaskStatus.PROCESSING, 10, "Loading document...")
        crud.update_upload_status(db, upload_id, "processing")

        upload = crud.get_upload(db, upload_id)
        if not upload:
            raise ValueError(f"Upload {upload_id} not found")

        doc_path = str(upload.file_path)
        if not Path(doc_path).exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")

        mime = upload.mime_type
        original_name = upload.original_filename

        await task_manager.update(task_id, TaskStatus.PROCESSING, 25, "Extracting text...")

        pages: List[Dict] = []
        headings: List[str] = []
        tables: List[Dict] = []
        images_extracted: List[Dict] = []
        total_pages = 0
        img_output_dir = str(settings.get_processed_dir() / f"doc_{upload_id}_imgs")

        if mime == "application/pdf" or doc_path.endswith(".pdf"):
            from app.processors.pdf_processor import (
                extract_text_by_page, extract_tables, extract_images,
                extract_metadata, is_scanned
            )
            metadata = extract_metadata(doc_path)
            total_pages = metadata.get("num_pages", 0)

            pages = extract_text_by_page(doc_path)

            if is_scanned(doc_path):
                logger.info(f"Scanned PDF detected: {doc_path}")
                await task_manager.update(task_id, TaskStatus.PROCESSING, 35, "Running OCR on scanned pages...")
                from app.processors.scanned_doc_processor import process_scanned_pdf
                ocr_pages = process_scanned_pdf(doc_path, img_output_dir)
                for op in ocr_pages:
                    pg_num = op["page"]
                    native = next((p for p in pages if p["page"] == pg_num), None)
                    if native and native["char_count"] < 50:
                        native.update(op)
                    elif not native:
                        pages.append(op)

            tables = extract_tables(doc_path)
            images_extracted = extract_images(doc_path, img_output_dir)
            for p in pages:
                headings.extend(p.get("headings", []))

        elif mime in {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        } or doc_path.endswith((".docx", ".doc")):
            from app.processors.docx_processor import (
                extract_text, extract_tables, extract_images
            )
            result = extract_text(doc_path)
            pages = [{
                "page": 1, "text": result["text"],
                "headings": result["headings"], "is_ocr": False,
                "char_count": len(result["text"])
            }]
            headings = result["headings"]
            tables = extract_tables(doc_path)
            images_extracted = extract_images(doc_path, img_output_dir)
            total_pages = 1

        elif mime in {
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint"
        } or doc_path.endswith((".pptx", ".ppt")):
            from app.processors.pptx_processor import (
                extract_slides, extract_tables, extract_images
            )
            slides = extract_slides(doc_path)
            pages = slides
            tables = extract_tables(doc_path)
            images_extracted = extract_images(doc_path, img_output_dir)
            total_pages = len(slides)
            for s in slides:
                headings.extend(s.get("headings", []))

        elif mime == "text/plain" or doc_path.endswith(".txt"):
            from app.processors.txt_processor import extract_text
            result = extract_text(doc_path)
            pages = [{
                "page": 1, "text": result["text"],
                "headings": result["headings"], "is_ocr": False,
                "char_count": len(result["text"])
            }]
            headings = result["headings"]
            total_pages = 1

        else:
            raise ValueError(f"Unsupported document type: {mime}")

        await task_manager.update(task_id, TaskStatus.PROCESSING, 60, "Analysing document structure and visuals...")
        vlm = model_manager.get_vlm()
        embedded_visuals = []

        # In "read" mode, prioritize verbatim text reading; in other modes, summarize visuals
        for idx, img_data in enumerate(images_extracted[:3]):
            img_path = img_data.get("image_path")
            pg = img_data.get("page", 1)
            desc = None
            if mode != "read" and idx == 0 and vlm.is_available:
                try:
                    desc = vlm.describe_image(img_path)
                except Exception as vlm_err:
                    logger.warning(f"VLM visual description skipped: {vlm_err}")

            embedded_visuals.append({
                "page": pg,
                "image_path": img_path,
                "description": desc or f"Visual diagram/figure on Page {pg}.",
                "type": img_data.get("type", "image"),
            })

        await task_manager.update(task_id, TaskStatus.GENERATING_EXPLANATION, 75, "Formulating accessible explanation...")
        inp = ExplanationInput(
            file_type="document",
            document_pages=pages,
            document_headings=list(dict.fromkeys(headings))[:20],
            document_tables=tables,
            embedded_visual_descriptions=embedded_visuals,
            filename=original_name,
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
                logger.warning(f"Document audio generation skipped: {audio_err}")

        crud.update_document_result(
            db, task_id,
            total_pages=total_pages or len(pages),
            extracted_text=pages,
            headings=list(dict.fromkeys(headings))[:30],
            tables=tables,
            embedded_visuals=embedded_visuals,
            explanation=explanation,
            summary=output.main_explanation if mode == "summarize" else None,
            audio_id=audio_id,
        )
        crud.update_upload_status(db, upload_id, "completed")
        await task_manager.update(task_id, TaskStatus.COMPLETED, 100, "Analysis complete")
        logger.info(f"Document analysis complete: upload={upload_id} task={task_id} audio={audio_id}")

    except Exception as e:
        logger.exception(f"Document analysis failed: upload={upload_id}")
        err_msg = str(e)
        await task_manager.update(task_id, TaskStatus.FAILED, 0, "Analysis failed", error=err_msg)
        try:
            crud.update_upload_status(db, upload_id, "failed", error_message=err_msg)
        except Exception:
            pass
    finally:
        db.close()
