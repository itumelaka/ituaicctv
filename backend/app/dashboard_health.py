from typing import Any


def _get_camera_id_from_event(event: dict[str, Any]) -> str | None:
    camera = event.get("camera") or {}
    return camera.get("id") or event.get("camera_id")


def _is_person_event(event: dict[str, Any]) -> bool:
    return (
        event.get("person_detected") is True
        or event.get("event_type") == "person_detected"
        or event.get("event_type") == "person"
    )


def _is_failed_event(event: dict[str, Any]) -> bool:
    status = str(event.get("status") or "").lower()
    event_type = str(event.get("event_type") or "").lower()
    action = str(event.get("action") or "").lower()

    return (
        status in {"failed", "error", "failing", "warning"}
        or event_type in {"failed", "camera_failed", "camera_error"}
        or action in {"failed", "error"}
        or event.get("failed") is True
    )


def build_dashboard_health(
    cameras: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    enabled_cameras = [
        camera for camera in cameras
        if camera.get("enabled", True)
    ]
    disabled_cameras = [
        camera for camera in cameras
        if not camera.get("enabled", True)
    ]

    camera_events: dict[str, list[dict[str, Any]]] = {
        str(camera.get("id")): []
        for camera in cameras
        if camera.get("id")
    }
    latest_event_time = None
    latest_event_camera_id = None
    latest_person_event_time = None

    for event in events:
        timestamp = event.get("timestamp")
        camera_id = _get_camera_id_from_event(event)

        if timestamp:
            latest_event_time = timestamp
            latest_event_camera_id = camera_id

        if _is_person_event(event) and timestamp:
            latest_person_event_time = timestamp

        if camera_id in camera_events:
            camera_events[camera_id].append(event)

    per_camera = []

    for camera in cameras:
        camera_id = camera.get("id")
        events_for_camera = camera_events.get(str(camera_id), [])
        enabled = camera.get("enabled", True)
        last_event_time = None
        last_person_event_time = None
        person_events = 0
        has_failed_event = False

        for event in events_for_camera:
            if event.get("timestamp"):
                last_event_time = event.get("timestamp")

            if _is_person_event(event):
                person_events += 1
                if event.get("timestamp"):
                    last_person_event_time = event.get("timestamp")

            if _is_failed_event(event):
                has_failed_event = True

        if not enabled:
            health_status = "disabled"
        elif has_failed_event:
            health_status = "warning"
        elif last_event_time:
            health_status = "active"
        else:
            health_status = "no_recent_event"

        per_camera.append({
            "camera_id": camera_id,
            "name": camera.get("name"),
            "enabled": enabled,
            "health_status": health_status,
            "last_event_time": last_event_time,
            "last_person_event_time": last_person_event_time,
            "total_events": len(events_for_camera),
            "person_events": person_events,
            "notes": camera.get("notes"),
            "status": camera.get("status"),
            "health_note": camera.get("health_note"),
        })

    return {
        "status": "ok",
        "cameras": {
            "total": len(cameras),
            "enabled": len(enabled_cameras),
            "disabled": len(disabled_cameras),
            "disabled_cameras": [
                {
                    "camera_id": camera.get("id"),
                    "name": camera.get("name"),
                    "enabled": camera.get("enabled", True),
                    "health_status": "disabled",
                    "notes": camera.get("notes"),
                    "status": camera.get("status"),
                    "health_note": camera.get("health_note"),
                }
                for camera in disabled_cameras
            ],
        },
        "events": {
            "total_events": len(events),
            "latest_event_time": latest_event_time,
            "latest_event_camera_id": latest_event_camera_id,
            "latest_person_event_time": latest_person_event_time,
        },
        "per_camera": per_camera,
    }
