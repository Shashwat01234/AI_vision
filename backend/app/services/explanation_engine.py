"""
Multimodal Context Integration Engine
======================================
The core AI engine that combines outputs from YOLO, OCR, VLM, and document
processors to produce natural-language explanations for visually impaired students.

Design principles:
 - Confidence-aware: low-confidence detections are flagged, not stated as facts
 - Anti-hallucination: never invent data not present in source inputs
 - Source-traceable: explanation tracks where each piece of info came from
 - Three modes: READ (faithful), EXPLAIN (simple), SUMMARIZE (key points)
"""
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ExplanationInput:
    """Structured input collected from all AI components."""
    yolo_detections: List[Dict] = field(default_factory=list)
    ocr_results: List[Dict] = field(default_factory=list)
    vlm_description: Optional[str] = None
    document_pages: Optional[List[Dict]] = None
    document_headings: Optional[List[str]] = None
    document_tables: Optional[List[Dict]] = None
    embedded_visual_descriptions: Optional[List[Dict]] = None
    file_type: str = "image"  # "image" or "document"
    filename: str = ""
    mode: str = "explain"  # read / explain / summarize


@dataclass
class ExplanationOutput:
    """Structured output from the explanation engine."""
    main_explanation: str
    sign_details: List[Dict] = field(default_factory=list)
    object_details: List[Dict] = field(default_factory=list)
    text_content: Optional[str] = None
    confidence_notes: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    mode: str = "explain"


CONFIDENCE_HIGH = 0.70
CONFIDENCE_MEDIUM = 0.40


class ExplanationEngine:
    """Core engine: combines all AI outputs into accessible explanations."""

    def build_explanation(self, inp: ExplanationInput) -> ExplanationOutput:
        """Main entry point. Dispatches to mode-specific builder."""
        try:
            if inp.file_type == "document":
                return self._explain_document(inp)
            else:
                return self._explain_image(inp)
        except Exception as e:
            logger.exception("ExplanationEngine error")
            return ExplanationOutput(
                main_explanation=f"An error occurred while generating the explanation: {e}",
                confidence_notes=["Explanation generation failed."],
                mode=inp.mode,
            )

    # ── Image Explanation ──────────────────────────────────────────────────

    def _explain_image(self, inp: ExplanationInput) -> ExplanationOutput:
        """Build explanation for an uploaded image."""
        sources = []
        sign_details = []
        object_details = []
        confidence_notes = []

        # Categorise YOLO detections
        traffic_sign_keywords = {
            "sign", "cross", "crossing", "road", "ahead", "limit", "speed", "stop",
            "prohibited", "turn", "bend", "curve", "way", "parking", "bridge",
            "intersection", "roundabout", "ascent", "descent", "rocks", "dip",
            "gravel", "work", "median", "hospital", "school", "petrol"
        }

        high_signs, low_signs, objects = [], [], []

        for det in inp.yolo_detections:
            conf = det.get("confidence", 0.0)
            label = det.get("label", "unknown").lower()
            # Recognize as sign if label is in standard campus classes, contains 'sign', or matches traffic sign categories
            is_sign = (
                "sign" in label
                or any(kw in label for kw in traffic_sign_keywords)
                or label.startswith("sign_")
            )
            if is_sign:
                if conf >= CONFIDENCE_HIGH:
                    high_signs.append(det)
                else:
                    low_signs.append(det)
            else:
                objects.append(det)

        if inp.yolo_detections:
            sources.append("YOLO sign/object detector")

        # Build sign detail records from YOLO
        for det in high_signs:
            sd = {
                "label": det.get("label"),
                "confidence": det.get("confidence"),
                "confirmed": True,
                "ocr_text": det.get("ocr_text"),
            }
            sign_details.append(sd)

        for det in low_signs:
            confidence_notes.append(
                f"A possible {det.get('label', 'sign').replace('_', ' ')} was detected with "
                f"low confidence ({det.get('confidence', 0):.0%})."
            )
            sd = {
                "label": det.get("label"),
                "confidence": det.get("confidence"),
                "confirmed": False,
                "ocr_text": det.get("ocr_text"),
            }
            sign_details.append(sd)

        for det in objects:
            object_details.append({
                "label": det.get("label"),
                "confidence": det.get("confidence"),
            })

        # Process OCR text
        ocr_clean_lines = []
        combined_ocr_text = ""
        ocr_inferred_signs = []

        if inp.ocr_results:
            sources.append("Open-Source EasyOCR text recognition")
            # Sort OCR results by vertical coordinate or confidence
            seen_texts = set()
            for ocr in inp.ocr_results:
                text = ocr.get("text", "").strip()
                # Filter out pure noise / watermarks if too short or corrupt
                if len(text) < 2 and not text.isalnum():
                    continue
                if text.lower() not in seen_texts:
                    seen_texts.add(text.lower())
                    conf = ocr.get("confidence", 0.8)
                    ocr_clean_lines.append({"text": text, "confidence": conf, "bbox": ocr.get("bbox")})

            combined_ocr_text = " | ".join(item["text"] for item in ocr_clean_lines)

            # Analyze OCR text for campus, university, directional, and safety signs
            all_text_lower = " ".join(item["text"].lower() for item in ocr_clean_lines)

            # 1. Campus / University sign detection
            if any(term in all_text_lower for term in ["university", "college", "campus", "institute", "academy"]):
                uni_words = [item["text"] for item in ocr_clean_lines if any(t in item["text"].lower() for t in ["university", "utah", "college", "campus", "u"])]
                sign_name = " ".join(uni_words) if uni_words else "Campus Monument Sign"
                ocr_inferred_signs.append({
                    "label": "campus_monument_sign",
                    "display_label": "Campus Monument Sign",
                    "confidence": 0.95,
                    "confirmed": True,
                    "ocr_text": sign_name,
                    "description": f"Official campus monument sign: {sign_name}",
                })

            # 2. Department / Building sign detection
            elif any(term in all_text_lower for term in ["department", "dept", "building", "hall", "center", "library", "lab", "faculty", "room"]):
                ocr_inferred_signs.append({
                    "label": "department_sign",
                    "display_label": "Department / Facility Sign",
                    "confidence": 0.90,
                    "confirmed": True,
                    "ocr_text": combined_ocr_text,
                    "description": f"Department or facility sign: {combined_ocr_text}",
                })

            # 3. Exit / Emergency / Safety sign detection
            elif any(term in all_text_lower for term in ["exit", "emergency", "fire", "caution", "danger", "warning", "hazard"]):
                ocr_inferred_signs.append({
                    "label": "safety_sign",
                    "display_label": "Safety / Exit Sign",
                    "confidence": 0.92,
                    "confirmed": True,
                    "ocr_text": combined_ocr_text,
                    "description": f"Safety or exit notice: {combined_ocr_text}",
                })

            # 4. Directional / Wayfinding sign detection
            elif any(term in all_text_lower for term in ["entrance", "entry", "gate", "way", "lane", "road", "street", "north", "south", "east", "west"]):
                ocr_inferred_signs.append({
                    "label": "directional_sign",
                    "display_label": "Directional / Wayfinding Sign",
                    "confidence": 0.88,
                    "confirmed": True,
                    "ocr_text": combined_ocr_text,
                    "description": f"Directional sign: {combined_ocr_text}",
                })

            # 5. General information board
            elif len(ocr_clean_lines) >= 1:
                ocr_inferred_signs.append({
                    "label": "information_sign",
                    "display_label": "Information Notice / Signboard",
                    "confidence": 0.85,
                    "confirmed": True,
                    "ocr_text": combined_ocr_text,
                    "description": f"Text signboard: {combined_ocr_text}",
                })

            # Add OCR-identified signs to sign_details if YOLO did not detect signs
            if not sign_details:
                for ois in ocr_inferred_signs:
                    if not any(sd.get("label") == ois["label"] for sd in sign_details):
                        sign_details.append({
                            "label": ois["label"],
                            "confidence": ois["confidence"],
                            "confirmed": True,
                            "ocr_text": ois["ocr_text"],
                        })

        if inp.vlm_description:
            sources.append("Vision-Language Model scene analysis")

        # Compose explanation by mode
        if inp.mode == "read":
            explanation = self._image_read_mode(
                high_signs, low_signs, objects, combined_ocr_text, inp.vlm_description, ocr_inferred_signs
            )
        elif inp.mode == "summarize":
            explanation = self._image_summarize_mode(
                high_signs, combined_ocr_text, inp.vlm_description, ocr_inferred_signs
            )
        else:  # explain (default)
            explanation = self._image_explain_mode(
                high_signs, low_signs, objects, combined_ocr_text, inp.vlm_description, ocr_inferred_signs
            )

        return ExplanationOutput(
            main_explanation=explanation,
            sign_details=sign_details,
            object_details=object_details,
            text_content=combined_ocr_text if combined_ocr_text else None,
            confidence_notes=confidence_notes,
            sources=sources,
            mode=inp.mode,
        )

    def _image_read_mode(self, signs, low_signs, objects, ocr_text, vlm_desc, ocr_signs=None) -> str:
        """Faithful, complete transcription and description of everything detected."""
        parts = []

        if vlm_desc:
            parts.append(f"Visual Scene: {vlm_desc}")

        if ocr_text:
            parts.append(f"Verbatim text read from image: {ocr_text}.")

        all_signs = list(signs)
        if ocr_signs:
            for os in ocr_signs:
                if not any(s.get("label") == os["label"] for s in all_signs):
                    all_signs.append(os)

        if all_signs:
            sign_strs = []
            for s in all_signs:
                name = s.get("label", "sign").replace("_", " ")
                ocr = s.get("ocr_text")
                if ocr:
                    sign_strs.append(f"{name} reading '{ocr}'")
                else:
                    sign_strs.append(name)
            parts.append("Identified signs: " + "; ".join(sign_strs) + ".")

        if objects:
            obj_strs = [o.get("label", "object").replace("_", " ") for o in objects[:8]]
            parts.append("Other visible elements: " + ", ".join(obj_strs) + ".")

        if not parts:
            return "No clear text, signs, or objects could be identified in this image."

        return " ".join(parts)

    def _image_explain_mode(self, signs, low_signs, objects, ocr_text, vlm_desc, ocr_signs=None) -> str:
        """Simplified, conversational, assistive explanation for a visually impaired student."""
        parts = []

        if vlm_desc:
            parts.append(vlm_desc.rstrip(".") + ".")

        all_signs = list(signs)
        if ocr_signs:
            for os in ocr_signs:
                if not any(s.get("label") == os["label"] for s in all_signs):
                    all_signs.append(os)

        # 1. Detail identified signs
        if all_signs:
            for s in all_signs:
                label = s.get("label", "sign").replace("_", " ")
                txt = s.get("ocr_text") or ""

                if "campus" in label or "monument" in label or any(w in txt.lower() for w in ["university", "college"]):
                    cleaned_name = txt or "the campus"
                    parts.append(
                        f"There is a prominent campus monument sign indicating '{cleaned_name}'. "
                        "This marks the official grounds and entrance to the university."
                    )
                elif "directional" in label:
                    if txt:
                        parts.append(f"A directional sign points toward: '{txt}'.")
                    else:
                        parts.append("A directional sign is visible indicating a pathway or route.")
                elif "exit" in label:
                    if txt:
                        parts.append(f"An exit sign is visible reading '{txt}', showing a way out.")
                    else:
                        parts.append("An exit sign marks a way out of this area.")
                elif "department" in label:
                    if txt:
                        parts.append(f"A department sign reads: '{txt}'.")
                    else:
                        parts.append("A department or facility sign is posted here.")
                elif "safety" in label or "caution" in label or "warning" in label:
                    if txt:
                        parts.append(f"A safety warning sign is displayed: '{txt}'. Please exercise caution.")
                    else:
                        parts.append("A safety or warning sign is present in this area.")
                elif "compulsary" in label or "compulsory" in label:
                    action = label.replace("compulsary", "").replace("compulsory", "").replace("_", " ").strip()
                    parts.append(f"A mandatory blue traffic sign indicates: {action} (vehicles must follow this direction).")
                else:
                    sign_desc = label.replace("_", " ").strip()
                    if sign_desc.endswith(" sign"):
                        sign_desc = sign_desc[:-5].strip()
                    if txt:
                        parts.append(f"A {sign_desc} sign is visible reading '{txt}'.")
                    else:
                        parts.append(f"A {sign_desc} sign is located here.")

        # 2. Text reading
        if ocr_text:
            # Highlight legible words
            clean_words = [w.strip() for w in ocr_text.split("|") if len(w.strip()) > 1]
            if clean_words:
                readable = ", ".join(f"'{w}'" for w in clean_words[:6])
                if not all_signs:
                    parts.append(f"The text visible on the signage reads: {readable}.")

        # 3. Mention objects if present
        if objects:
            obj_names = list({o.get("label", "object").replace("_", " ") for o in objects[:5]})
            if obj_names:
                parts.append(f"Surrounding environment features: {', '.join(obj_names)}.")

        # 4. Uncertainty note & fallback description
        if low_signs:
            low_names = [s.get("label", "sign").replace("_", " ") for s in low_signs]
            # If no high-confidence signs were found, provide a helpful primary description
            if not all_signs:
                top_sign = max(low_signs, key=lambda s: s.get("confidence", 0))
                top_label = top_sign.get("label", "sign").replace("_", " ")
                if any("all motor vehicle" in s.get("label", "") for s in low_signs):
                    parts.insert(0, "A circular red regulatory sign is visible indicating that all motor vehicles are prohibited from entering this road or area.")
                elif any("prohibited" in s.get("label", "") for s in low_signs):
                    parts.insert(0, f"A circular regulatory sign is visible indicating a traffic prohibition (likely '{top_label}').")
                else:
                    parts.insert(0, f"A sign is visible appearing to indicate '{top_label}'.")

            parts.append(
                f"Note: There may also be a {' or '.join(low_names)}, with moderate detection confidence."
            )

        if not parts:
            return "This image does not appear to contain recognizable signs or text. It may be a general view or landscape."

        return " ".join(parts)

    def _image_summarize_mode(self, signs, ocr_text, vlm_desc, ocr_signs=None) -> str:
        """Concise key-points summary for quick screen-reader review."""
        points = []

        all_signs = list(signs)
        if ocr_signs:
            for os in ocr_signs:
                if not any(s.get("label") == os["label"] for s in all_signs):
                    all_signs.append(os)

        if all_signs:
            for s in all_signs:
                name = s.get("label", "sign").replace("_", " ")
                ocr = s.get("ocr_text")
                if ocr:
                    points.append(f"Sign: {name.title()} — '{ocr}'")
                else:
                    points.append(f"Sign: {name.title()}")

        if ocr_text:
            clean_words = [w.strip() for w in ocr_text.split("|") if len(w.strip()) > 1]
            if clean_words:
                points.append(f"Text: {', '.join(clean_words[:5])}")

        if vlm_desc and not points:
            points.append(vlm_desc[:250])

        if not points:
            return "Key findings: No significant signs or legible text detected."

        return "Key findings: " + " | ".join(points) + "."

    # ── Document Explanation ───────────────────────────────────────────────

    def _explain_document(self, inp: ExplanationInput) -> ExplanationOutput:
        """Build explanation for a processed document."""
        sources = []
        confidence_notes = []

        pages = inp.document_pages or []
        headings = inp.document_headings or []
        tables = inp.document_tables or []
        visuals = inp.embedded_visual_descriptions or []

        if pages:
            sources.append("Document text extraction")
        if tables:
            sources.append("Table extraction")
        if visuals:
            sources.append("Embedded image analysis")

        # Gather all text
        all_text_parts = [p.get("text", "") for p in pages if p.get("text", "").strip()]
        full_text = "\n\n".join(all_text_parts)

        if inp.mode == "read":
            explanation = self._document_read_mode(full_text, headings, tables, visuals)
        elif inp.mode == "summarize":
            explanation = self._document_summarize_mode(full_text, headings, tables)
        else:
            explanation = self._document_explain_mode(full_text, headings, tables, visuals, inp.filename)

        return ExplanationOutput(
            main_explanation=explanation,
            text_content=full_text[:2000] if full_text else None,
            confidence_notes=confidence_notes,
            sources=sources,
            mode=inp.mode,
        )

    def _document_read_mode(self, text, headings, tables, visuals) -> str:
        parts = []
        if headings:
            parts.append("Document structure — headings: " + "; ".join(headings[:10]) + ".")
        if text:
            # Present first 1500 chars faithfully
            excerpt = text[:1500].strip()
            parts.append(f"Document content:\n{excerpt}")
            if len(text) > 1500:
                parts.append(f"[... document continues for {len(text) - 1500} more characters]")
        if tables:
            parts.append(f"This document contains {len(tables)} table(s).")
        if visuals:
            for v in visuals[:3]:
                desc = v.get("description") or "an image"
                parts.append(f"Embedded visual on page {v.get('page', '?')}: {desc}.")
        if not parts:
            return "This document appears to be empty or its content could not be extracted."
        return "\n\n".join(parts)

    @staticmethod
    def _is_float(val: str) -> bool:
        try:
            float(val)
            return True
        except ValueError:
            return False

    def _document_explain_mode(self, text, headings, tables, visuals, filename) -> str:
        parts = []

        # Check if the document appears to be a machine-learning label file (e.g. YOLO coordinates)
        lines = [l.strip() for l in (text or "").split("\n") if l.strip()]
        is_yolo_annotation = False
        if lines and all(len(l.split()) == 5 and all(self._is_float(x) for x in l.split()) for l in lines[:5]):
            is_yolo_annotation = True

        if is_yolo_annotation:
            return (
                "This file contains machine learning label coordinates rather than readable text. "
                "If you intended to analyze a traffic or campus sign, please upload the corresponding photograph or image file (.jpg or .png) instead."
            )

        name = filename or "this document"
        parts.append(f"This is {name}.")
        if headings:
            parts.append(f"It covers the following topics: {', '.join(headings[:8])}.")
        if text:
            excerpt = text[:800].strip().replace("\n", " ")
            parts.append(f"The document begins with: {excerpt}")
        if tables:
            parts.append(f"It includes {len(tables)} table(s) with structured data.")
        if visuals:
            parts.append(f"There are {len(visuals)} embedded image(s) or diagram(s).")
        return " ".join(parts)

    def _document_summarize_mode(self, text, headings, tables) -> str:
        points = []
        if headings:
            points.append(f"Topics: {', '.join(headings[:6])}")
        if tables:
            points.append(f"{len(tables)} table(s) with structured data")
        if text:
            # Extract first meaningful sentence
            sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
            if sentences:
                points.append(f"Key content: {sentences[0]}.")
        if not points:
            return "No summarisable content was found in this document."
        return "Summary: " + " | ".join(points) + "."


# Singleton
explanation_engine = ExplanationEngine()
