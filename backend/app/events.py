from datetime import datetime, timezone
from pathlib import Path
from app.config import settings
from app.detection import (
    build_person_evidence_from_detection,
    run_person_detection_with_frame,
    run_person_detection_with_frame_for_camera,
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


def _build_person_event(
    detection_result: dict,
    snapshot_func,
    camera_context: dict | None = None,
    log_no_person: bool = True,
    detection_frame=None,
) -> dict:
    detections_count = detection_result["detections_count"]
    person_detected = detection_result["person_detected"]
    current_time = datetime.now(timezone.utc)
    timestamp = current_time.isoformat()

    evidence_path = None
    face_readiness = None
    face_recognition = None
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
            try:
                if detection_frame is None:
                    raise RuntimeError("Detection frame unavailable for composite evidence.")

                image_bytes, face_readiness, face_recognition = build_person_evidence_from_detection(
                    detection_frame,
                    detection_result,
                    camera=camera_context,
                )
            except Exception as error:
                print(
                    "WARNING: Composite evidence generation failed; "
                    f"falling back to snapshot capture. Reason: {error}"
                )
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
        "confidence_threshold": detection_result.get("confidence_threshold"),
        "evidence_path": evidence_path,
        "face_readiness": face_readiness,
        "face_recognition_enabled": (
            face_recognition.get("face_recognition_enabled") if face_recognition else False
        ),
        "face_recognition_available": (
            face_recognition.get("face_recognition_available") if face_recognition else False
        ),
        "face_recognition_backend": (
            face_recognition.get("face_recognition_backend") if face_recognition else "auto"
        ),
        "recognition_attempted": (
            face_recognition.get("recognition_attempted") if face_recognition else False
        ),
        "recognized_label": (
            face_recognition.get("recognized_label") if face_recognition else None
        ),
        "recognition_confidence": (
            face_recognition.get("recognition_confidence") if face_recognition else None
        ),
        "recognition_reason": (
            face_recognition.get("recognition_reason") if face_recognition else "disabled"
        ),
        "cooldown_active": cooldown_active,
        "cooldown_seconds": cooldown_seconds
    }

    if person_detected or log_no_person:
        append_event_log(event)

    return event


def evaluate_person_event(log_no_person: bool = True) -> dict:
    detection_result, detection_frame = run_person_detection_with_frame()
    return _build_person_event(
        detection_result=detection_result,
        snapshot_func=run_person_snapshot_jpeg,
        log_no_person=log_no_person,
        detection_frame=detection_frame,
    )


def evaluate_person_event_for_camera(camera: dict, log_no_person: bool = True) -> dict:
    detection_result, detection_frame = run_person_detection_with_frame_for_camera(camera)

    return _build_person_event(
        detection_result=detection_result,
        snapshot_func=lambda: run_person_snapshot_jpeg_for_camera(camera),
        camera_context=camera,
        log_no_person=log_no_person,
        detection_frame=detection_frame,
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


def _get_event_camera_id(event: dict) -> str | None:
    camera = event.get("camera") or {}
    return camera.get("id") or event.get("camera_id")


def get_latest_dashboard_event_for_camera(camera_id: str) -> dict:
    events = [
        event for event in read_all_event_logs()
        if _get_event_camera_id(event) == camera_id
    ]

    latest_event = events[-1] if events else None
    dashboard_events = add_evidence_urls([latest_event]) if latest_event else []

    return {
        "status": "ok",
        "camera_id": camera_id,
        "latest_event": dashboard_events[0] if dashboard_events else None
    }


def get_dashboard_camera_event_stats(camera_id: str) -> dict:
    events = [
        event for event in read_all_event_logs()
        if _get_event_camera_id(event) == camera_id
    ]

    person_events = 0
    latest_event_time = None
    latest_evidence_url = None

    for event in events:
        if event.get("event_type") == "person_detected" or event.get("person_detected") is True:
            person_events += 1

        if event.get("timestamp"):
            latest_event_time = event.get("timestamp")

        evidence_filename = _get_evidence_filename(event)

        if evidence_filename:
            latest_evidence_url = f"/events/evidence/{evidence_filename}"

    return {
        "status": "ok",
        "camera_id": camera_id,
        "total_events": len(events),
        "person_events": person_events,
        "latest_event_time": latest_event_time,
        "latest_evidence_url": latest_evidence_url
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
