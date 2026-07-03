from datetime import datetime, timezone
from app.config import settings
from app.detection import run_person_detection


def evaluate_person_event() -> dict:
    detection_result = run_person_detection()

    detections_count = detection_result["detections_count"]
    person_detected = detection_result["person_detected"]

    if person_detected:
        event_type = "person_detected"
        severity = "medium"
        message = "Person detected in CCTV frame."
    else:
        event_type = "no_person"
        severity = "none"
        message = "No person detected in CCTV frame."

    return {
        "status": "ok",
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "camera": {
            "host": settings.cctv_host,
            "channel": settings.cctv_channel,
            "frame_width": detection_result["camera"]["frame_width"],
            "frame_height": detection_result["camera"]["frame_height"]
        },
        "person_detected": person_detected,
        "detections_count": detections_count,
        "detections": detection_result["detections"]
    }
