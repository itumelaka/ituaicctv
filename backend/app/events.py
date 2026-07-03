from datetime import datetime, timezone
from app.config import settings
from app.detection import run_person_detection, run_person_snapshot_jpeg
from app.event_log import append_event_log, read_latest_event_logs, save_evidence_image


def evaluate_person_event() -> dict:
    detection_result = run_person_detection()

    detections_count = detection_result["detections_count"]
    person_detected = detection_result["person_detected"]
    timestamp = datetime.now(timezone.utc).isoformat()

    evidence_path = None

    if person_detected:
        event_type = "person_detected"
        severity = "medium"
        message = "Person detected in CCTV frame."

        image_bytes = run_person_snapshot_jpeg()
        filename = f"person_detected_{timestamp}.jpg"
        evidence_path = save_evidence_image(image_bytes, filename)
    else:
        event_type = "no_person"
        severity = "none"
        message = "No person detected in CCTV frame."

    event = {
        "status": "ok",
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "timestamp": timestamp,
        "camera": {
            "host": settings.cctv_host,
            "channel": settings.cctv_channel,
            "frame_width": detection_result["camera"]["frame_width"],
            "frame_height": detection_result["camera"]["frame_height"]
        },
        "person_detected": person_detected,
        "detections_count": detections_count,
        "detections": detection_result["detections"],
        "evidence_path": evidence_path
    }

    append_event_log(event)

    return event


def get_latest_events(limit: int = 20) -> dict:
    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    events = read_latest_event_logs(limit=limit)

    return {
        "status": "ok",
        "limit": limit,
        "events_count": len(events),
        "events": events
    }
