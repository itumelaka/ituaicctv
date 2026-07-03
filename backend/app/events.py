from datetime import datetime, timezone
from pathlib import Path
from app.config import settings
from app.detection import (
    run_person_detection,
    run_person_detection_for_camera,
    run_person_snapshot_jpeg,
    run_person_snapshot_jpeg_for_camera,
)
from app.event_log import append_event_log, read_latest_event_logs, read_all_event_logs, save_evidence_image


def _get_camera_id(camera_context: dict | None = None) -> str:
    if camera_context:
        return camera_context.get("id") or "unknown_camera"

    return "default_camera"


def _parse_timestamp(timestamp: str):
    try:
        return datetime.fromisoformat(timestamp)
    except Exception:
        return None


def _is_person_event_in_cooldown(camera_id: str, current_time: datetime) -> bool:
    cooldown_seconds = settings.person_event_cooldown_seconds

    if cooldown_seconds <= 0:
        return False

    latest_events = read_latest_event_logs(limit=200)

    for event in reversed(latest_events):
        if event.get("event_type") != "person_detected":
            continue

        event_camera = event.get("camera") or {}
        event_camera_id = event_camera.get("id") or "default_camera"

        if event_camera_id != camera_id:
            continue

        previous_time = _parse_timestamp(event.get("timestamp", ""))

        if previous_time is None:
            continue

        elapsed_seconds = (current_time - previous_time).total_seconds()

        return elapsed_seconds < cooldown_seconds

    return False


def _build_person_event(detection_result: dict, snapshot_func, camera_context: dict | None = None) -> dict:
    detections_count = detection_result["detections_count"]
    person_detected = detection_result["person_detected"]
    current_time = datetime.now(timezone.utc)
    timestamp = current_time.isoformat()

    evidence_path = None
    cooldown_active = False
    cooldown_seconds = settings.person_event_cooldown_seconds
    camera_id = _get_camera_id(camera_context)

    if person_detected:
        event_type = "person_detected"
        severity = "medium"

        cooldown_active = _is_person_event_in_cooldown(camera_id, current_time)

        if cooldown_active:
            message = "Person detected in CCTV frame. Evidence snapshot skipped due to cooldown."
        else:
            message = "Person detected in CCTV frame."
            image_bytes = snapshot_func()
            filename = f"person_detected_{camera_id}_{timestamp}.jpg"
            evidence_path = save_evidence_image(image_bytes, filename)
    else:
        event_type = "no_person"
        severity = "none"
        message = "No person detected in CCTV frame."

    camera_data = {
        "host": settings.cctv_host,
        "channel": settings.cctv_channel,
        "frame_width": detection_result["camera"]["frame_width"],
        "frame_height": detection_result["camera"]["frame_height"]
    }

    if camera_context:
        camera_data.update({
            "id": camera_context.get("id"),
            "name": camera_context.get("name"),
            "host": camera_context.get("host"),
            "channel": camera_context.get("channel")
        })

    event = {
        "status": "ok",
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "timestamp": timestamp,
        "camera": camera_data,
        "person_detected": person_detected,
        "detections_count": detections_count,
        "detections": detection_result["detections"],
        "evidence_path": evidence_path,
        "cooldown_active": cooldown_active,
        "cooldown_seconds": cooldown_seconds
    }

    append_event_log(event)

    return event


def evaluate_person_event() -> dict:
    detection_result = run_person_detection()
    return _build_person_event(
        detection_result=detection_result,
        snapshot_func=run_person_snapshot_jpeg
    )


def evaluate_person_event_for_camera(camera: dict) -> dict:
    detection_result = run_person_detection_for_camera(camera)

    return _build_person_event(
        detection_result=detection_result,
        snapshot_func=lambda: run_person_snapshot_jpeg_for_camera(camera),
        camera_context=camera
    )


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


def _get_evidence_filename(event: dict) -> str | None:
    evidence_filename = event.get("evidence_filename")

    if evidence_filename:
        return Path(evidence_filename).name

    evidence_path = event.get("evidence_path")

    if evidence_path:
        return Path(evidence_path).name

    return None


def add_evidence_urls(events: list[dict]) -> list[dict]:
    dashboard_events = []

    for event in events:
        dashboard_event = event.copy()
        evidence_filename = _get_evidence_filename(event)

        if evidence_filename:
            dashboard_event["evidence_filename"] = evidence_filename
            dashboard_event["evidence_url"] = f"/events/evidence/{evidence_filename}"

        dashboard_events.append(dashboard_event)

    return dashboard_events


def get_latest_dashboard_events(limit: int = 10) -> dict:
    latest_events = get_latest_events(limit=limit)
    events = add_evidence_urls(latest_events.get("events", []))

    return {
        "status": "ok",
        "limit": latest_events.get("limit"),
        "events_count": len(events),
        "events": events
    }


def get_event_stats() -> dict:
    events = read_all_event_logs()

    total_events = len(events)
    person_detected_count = 0
    no_person_count = 0
    evidence_count = 0
    cooldown_skipped_count = 0

    for event in events:
        if event.get("person_detected") is True:
            person_detected_count += 1

        if event.get("event_type") == "no_person":
            no_person_count += 1

        if event.get("evidence_path"):
            evidence_count += 1

        if event.get("cooldown_active") is True:
            cooldown_skipped_count += 1

    latest_event = events[-1] if events else None

    return {
        "status": "ok",
        "total_events": total_events,
        "person_detected_count": person_detected_count,
        "no_person_count": no_person_count,
        "evidence_count": evidence_count,
        "cooldown_skipped_count": cooldown_skipped_count,
        "latest_event": {
            "timestamp": latest_event.get("timestamp"),
            "event_type": latest_event.get("event_type"),
            "severity": latest_event.get("severity"),
            "person_detected": latest_event.get("person_detected"),
            "cooldown_active": latest_event.get("cooldown_active")
        } if latest_event else None
    }
