from fastapi import APIRouter, HTTPException, Query
from app.camera_registry import get_camera_by_id, load_cameras, list_enabled_cameras
from app.dashboard_health import build_dashboard_health
from app.event_log import list_evidence_images
from app.event_log import read_all_event_logs
from app.events import (
    get_dashboard_camera_event_stats,
    get_event_stats,
    get_latest_events,
    get_latest_dashboard_event_for_camera,
    get_latest_dashboard_events,
)

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


@router.get("/health")
def dashboard_health():
    return build_dashboard_health(
        cameras=load_cameras(),
        events=read_all_event_logs()
    )


@router.get("/evidence")
def dashboard_evidence(limit: int = Query(default=20, ge=1, le=100)):
    evidence_images = list_evidence_images(limit=limit)

    return {
        "status": "ok",
        "limit": limit,
        "evidence_count": len(evidence_images),
        "evidence": evidence_images
    }


@router.get("/cameras")
def dashboard_cameras():
    cameras = load_cameras()
    enabled_cameras = [
        camera for camera in cameras
        if camera.get("enabled", True)
    ]
    disabled_cameras = [
        camera for camera in cameras
        if not camera.get("enabled", True)
    ]

    return {
        "status": "ok",
        "totals": {
            "total": len(cameras),
            "enabled": len(enabled_cameras),
            "disabled": len(disabled_cameras)
        },
        "cameras": [
            {
                "camera_id": camera.get("id"),
                "name": camera.get("name"),
                "location": camera.get("location"),
                "block": camera.get("block"),
                "ip": camera.get("host"),
                "channel": camera.get("channel"),
                "enabled": camera.get("enabled", True),
                "notes": camera.get("notes"),
                "status": camera.get("status")
            }
            for camera in cameras
        ]
    }


@router.get("/events/latest")
def dashboard_latest_events(limit: int = Query(default=10, ge=1, le=100)):
    return get_latest_dashboard_events(limit=limit)


def _validate_dashboard_camera(camera_id: str) -> None:
    try:
        get_camera_by_id(camera_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Camera not found: {camera_id}"
        )


@router.get("/cameras/{camera_id}/latest-event")
def dashboard_camera_latest_event(camera_id: str):
    _validate_dashboard_camera(camera_id)
    return get_latest_dashboard_event_for_camera(camera_id)


@router.get("/cameras/{camera_id}/stats")
def dashboard_camera_stats(camera_id: str):
    _validate_dashboard_camera(camera_id)
    return get_dashboard_camera_event_stats(camera_id)
