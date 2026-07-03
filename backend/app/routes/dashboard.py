from fastapi import APIRouter
from app.camera_registry import load_cameras, list_enabled_cameras
from app.events import get_event_stats, get_latest_events

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary():
    cameras = load_cameras()
    enabled_cameras = list_enabled_cameras()
    stats = get_event_stats()
    latest_events = get_latest_events(limit=10)

    disabled_cameras = [
        camera for camera in cameras
        if not camera.get("enabled", True)
    ]

    latest_event = stats.get("latest_event")

    return {
        "status": "ok",
        "dashboard": "summary",
        "cameras_total": len(cameras),
        "cameras_enabled": len(enabled_cameras),
        "cameras_disabled": len(disabled_cameras),
        "disabled_cameras": [
            {
                "camera_id": camera.get("id"),
                "camera_name": camera.get("name"),
                "camera_host": camera.get("host"),
                "channel": camera.get("channel"),
                "notes": camera.get("notes")
            }
            for camera in disabled_cameras
        ],
        "events": {
            "total_events": stats.get("total_events"),
            "person_detected_count": stats.get("person_detected_count"),
            "no_person_count": stats.get("no_person_count"),
            "evidence_count": stats.get("evidence_count"),
            "cooldown_skipped_count": stats.get("cooldown_skipped_count"),
            "latest_event": latest_event,
            "latest_events_count": latest_events.get("events_count"),
            "latest_events": latest_events.get("events")
        },
        "links": {
            "camera_audit": "/cameras/audit",
            "monitor_summary": "/monitor/person/summary",
            "monitor_check_all": "/monitor/person/check-all",
            "events_logs": "/events/logs",
            "events_stats": "/events/stats"
        }
    }
