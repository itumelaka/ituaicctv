import logging
from pathlib import Path

import requests

from app.config import settings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]


def _is_configured() -> bool:
    return bool(settings.telegram_bot_token and settings.telegram_chat_id)


def _resolve_evidence_path(evidence_path: str | None) -> Path | None:
    if not evidence_path:
        return None

    path = Path(evidence_path)

    if path.is_absolute():
        return path if path.exists() else None

    resolved = BASE_DIR / path
    return resolved if resolved.exists() else None


def _send_photo(caption: str, image_path: Path | None) -> bool:
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    base_url = f"https://api.telegram.org/bot{token}"

    try:
        if image_path:
            with open(image_path, "rb") as photo:
                response = requests.post(
                    f"{base_url}/sendPhoto",
                    data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
                    files={"photo": photo},
                    timeout=15,
                )
        else:
            response = requests.post(
                f"{base_url}/sendMessage",
                json={"chat_id": chat_id, "text": caption, "parse_mode": "HTML"},
                timeout=15,
            )

        response.raise_for_status()
        return True

    except Exception as error:
        logger.warning("Telegram alert failed: %s", error)
        return False


def send_person_alert(event: dict) -> bool:
    if not _is_configured():
        logger.debug("Telegram alert skipped: not configured.")
        return False

    camera = event.get("camera") or {}
    camera_name = camera.get("name") or camera.get("id") or "Unknown camera"
    camera_host = camera.get("host", "")
    timestamp = event.get("timestamp", "")
    detections_count = event.get("detections_count", 0)
    detections = event.get("detections") or []
    confidences = [
        detection.get("confidence")
        for detection in detections
        if isinstance(detection.get("confidence"), (int, float))
    ]
    max_confidence = max(confidences) if confidences else None
    confidence_threshold = event.get("confidence_threshold")
    face_readiness = event.get("face_readiness") or {}
    evidence_path = _resolve_evidence_path(event.get("evidence_path"))

    caption = f"<b>Person Detected</b>\nCamera: {camera_name}"

    if camera_host:
        caption += f" ({camera_host})"

    caption += f"\nTime: {timestamp}"

    if detections_count:
        caption += f"\nDetections: {detections_count}"

    if max_confidence is not None:
        caption += f"\nConfidence: {max_confidence:.2f}"

    if confidence_threshold is not None:
        caption += f"\nThreshold: {float(confidence_threshold):.2f}"

    if face_readiness:
        readiness = face_readiness.get("face_readiness", "unknown")
        reasons = face_readiness.get("reasons") or []
        caption += f"\nFace readiness: {readiness}"

        if reasons:
            caption += f"\nReason: {', '.join(reasons[:3])}"

    if event.get("face_recognition_enabled") and event.get("recognition_attempted"):
        label = event.get("recognized_label") or "UNKNOWN"
        caption += f"\nRecognized: {label}"

        confidence = event.get("recognition_confidence")
        if isinstance(confidence, (int, float)) and label != "UNKNOWN":
            caption += f" ({float(confidence):.2f})"

    sent = _send_photo(caption=caption, image_path=evidence_path)

    if sent:
        logger.info("Telegram alert sent for camera %s.", camera_name)

    return sent
