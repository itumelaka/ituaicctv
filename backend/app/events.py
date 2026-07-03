from datetime import datetime, timezone
from app.config import settings
from app.detection import run_person_detection, run_person_snapshot_jpeg
from app.event_log import (
    append_event_log,
    read_latest_event_logs,
    read_all_event_logs,
    save_evidence_image,
)


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


def get_event_stats() -> dict:
    events = read_all_event_logs()

    total_events = len(events)
    person_detected_count = 0
    no_person_count = 0
    evidence_count = 0

    for event in events:
        if event.get("person_detected") is True:
            person_detected_count += 1

        if event.get("event_type") == "no_person":
            no_person_count += 1

        if event.get("evidence_path"):
            evidence_count += 1

    latest_event = events[-1] if events else None

    return {
        "status": "ok",
        "total_events": total_events,
        "person_detected_count": person_detected_count,
        "no_person_count": no_person_count,
        "evidence_count": evidence_count,
        "latest_event": {
            "timestamp": latest_event.get("timestamp"),
            "event_type": latest_event.get("event_type"),
            "severity": latest_event.get("severity"),
            "person_detected": latest_event.get("person_detected")
        } if latest_event else None
    }
