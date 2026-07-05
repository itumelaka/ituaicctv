import time

import cv2
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from app.camera import (
    _open_rtsp_stream,
    capture_frame_for_camera,
    capture_frame_for_camera_channel,
)
from app.camera_registry import build_rtsp_url, get_camera_by_id, load_cameras, list_enabled_cameras
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
from app.live_view import (
    InvalidLiveViewQuality,
    LIVE_VIEW_STANDARD_QUALITY,
    live_view_channel_for_quality,
    live_view_max_width_for_quality,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

TV_MJPEG_FPS = 4
TV_MJPEG_FRAME_DELAY_SECONDS = 1 / TV_MJPEG_FPS
TV_MJPEG_MAX_READ_FAILURES = 30


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
                "status": camera.get("status"),
                "ignore_zones_count": len(camera.get("ignore_zones", [])),
                "ignore_zones_enabled": len([
                    zone for zone in camera.get("ignore_zones", [])
                    if zone.get("enabled")
                ])
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


@router.get("/live/{camera_id}/snapshot.jpg")
def dashboard_live_camera_snapshot(
    camera_id: str,
    quality: str = Query(default=LIVE_VIEW_STANDARD_QUALITY),
):
    try:
        camera = get_camera_by_id(camera_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Camera not found: {camera_id}"
        )

    if not camera.get("enabled", True):
        raise HTTPException(
            status_code=409,
            detail=f"Camera is disabled: {camera_id}"
        )

    channel = _live_view_channel_or_400(quality)

    try:
        if channel:
            frame = capture_frame_for_camera_channel(camera, channel)
        else:
            frame = capture_frame_for_camera(camera)
        success, buffer = cv2.imencode(".jpg", frame)
    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Live snapshot unavailable for {camera_id} "
                f"quality={quality}: {error}"
            )
        )

    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to encode live snapshot for {camera_id}"
        )

    return Response(
        content=buffer.tobytes(),
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"}
    )


def _get_enabled_dashboard_camera(camera_id: str) -> dict:
    try:
        camera = get_camera_by_id(camera_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Camera not found: {camera_id}"
        )

    if not camera.get("enabled", True):
        raise HTTPException(
            status_code=409,
            detail=f"Camera is disabled: {camera_id}"
        )

    return camera


def _live_view_channel_or_400(quality: str) -> str | None:
    try:
        return live_view_channel_for_quality(quality)
    except InvalidLiveViewQuality as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


def _live_view_max_width_or_400(quality: str) -> int:
    try:
        return live_view_max_width_for_quality(quality)
    except InvalidLiveViewQuality as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


def _resize_for_tv_mjpeg(frame, max_width: int):
    height, width = frame.shape[:2]

    if width <= max_width:
        return frame

    scale = max_width / width
    resized_height = max(1, int(height * scale))
    return cv2.resize(
        frame,
        (max_width, resized_height),
        interpolation=cv2.INTER_AREA
    )


def _mjpeg_frame_generator(cap, max_width: int):
    # MJPEG is intended for one selected TV camera, not all cameras at once.
    failures = 0

    try:
        while True:
            ok, frame = cap.read()

            if not ok or frame is None:
                failures += 1
                if failures >= TV_MJPEG_MAX_READ_FAILURES:
                    break
                time.sleep(TV_MJPEG_FRAME_DELAY_SECONDS)
                continue

            failures = 0
            frame = _resize_for_tv_mjpeg(frame, max_width=max_width)
            success, buffer = cv2.imencode(".jpg", frame)

            if not success:
                time.sleep(TV_MJPEG_FRAME_DELAY_SECONDS)
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Cache-Control: no-store\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )
            time.sleep(TV_MJPEG_FRAME_DELAY_SECONDS)
    except GeneratorExit:
        pass
    finally:
        cap.release()


@router.get("/live/{camera_id}/stream.mjpg")
def dashboard_live_camera_stream(
    camera_id: str,
    quality: str = Query(default=LIVE_VIEW_STANDARD_QUALITY),
):
    camera = _get_enabled_dashboard_camera(camera_id)
    channel = _live_view_channel_or_400(quality)
    max_width = _live_view_max_width_or_400(quality)
    rtsp_url = build_rtsp_url(camera, channel_override=channel)
    cap = _open_rtsp_stream(rtsp_url)

    if not cap.isOpened():
        cap.release()
        raise HTTPException(
            status_code=503,
            detail=f"Live stream unavailable for {camera_id} quality={quality}"
        )

    return StreamingResponse(
        _mjpeg_frame_generator(cap, max_width=max_width),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store"}
    )
