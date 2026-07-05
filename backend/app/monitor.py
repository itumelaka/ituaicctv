from app.alert import send_person_alert
from app.camera_registry import list_enabled_cameras
from app.events import evaluate_person_event, evaluate_person_event_for_camera


def run_person_monitor_check(log_no_person: bool = True) -> dict:
    event = evaluate_person_event(log_no_person=log_no_person)
    alert_sent = False

    if event.get("person_detected"):
        action = "attention_required"
        next_step = "Alert sent via Telegram." if not event.get("cooldown_active") else "Cooldown active — alert skipped."

        if not event.get("cooldown_active"):
            alert_sent = send_person_alert(event)
    else:
        action = "no_action"
        next_step = "No person detected. Continue monitoring."

    return {
        "status": "ok",
        "monitor": "person",
        "action": action,
        "next_step": next_step,
        "alert_sent": alert_sent,
        "event": event
    }


def run_person_monitor_check_for_camera(camera: dict, log_no_person: bool = True) -> dict:
    event = evaluate_person_event_for_camera(camera, log_no_person=log_no_person)
    alert_sent = False

    if event.get("person_detected"):
        action = "attention_required"
        next_step = "Alert sent via Telegram." if not event.get("cooldown_active") else "Cooldown active — alert skipped."

        if not event.get("cooldown_active"):
            alert_sent = send_person_alert(event)
    else:
        action = "no_action"
        next_step = "No person detected. Continue monitoring."

    return {
        "status": "ok",
        "monitor": "person",
        "action": action,
        "next_step": next_step,
        "alert_sent": alert_sent,
        "event": event,
        "camera_id": camera.get("id")
    }


def run_person_monitor_check_all(log_no_person: bool = True) -> dict:
    cameras = list_enabled_cameras()
    results = []

    for camera in cameras:
        try:
            result = run_person_monitor_check_for_camera(
                camera,
                log_no_person=log_no_person,
            )
        except Exception as error:
            result = {
                "status": "failed",
                "monitor": "person",
                "action": "error",
                "next_step": "Review camera configuration or RTSP connection.",
                "camera_id": camera.get("id"),
                "camera_name": camera.get("name"),
                "camera_host": camera.get("host"),
                "channel": camera.get("channel"),
                "error": str(error)
            }

        results.append(result)

    attention_required_count = len([
        item for item in results
        if item.get("action") == "attention_required"
    ])

    failed_count = len([
        item for item in results
        if item.get("status") == "failed"
    ])

    no_action_count = len([
        item for item in results
        if item.get("action") == "no_action"
    ])

    return {
        "status": "ok",
        "monitor": "person",
        "mode": "check_all",
        "enabled_cameras_count": len(cameras),
        "attention_required_count": attention_required_count,
        "no_action_count": no_action_count,
        "failed_count": failed_count,
        "results": results
    }


def run_person_monitor_summary() -> dict:
    result = run_person_monitor_check_all()
    cameras = []

    for item in result.get("results", []):
        event = item.get("event") or {}
        camera = event.get("camera") or {}

        if item.get("status") == "failed":
            cameras.append({
                "camera_id": item.get("camera_id"),
                "camera_name": item.get("camera_name"),
                "camera_host": item.get("camera_host"),
                "channel": item.get("channel"),
                "status": "failed",
                "action": item.get("action"),
                "person_detected": False,
                "detections_count": 0,
                "evidence_path": None,
                "cooldown_active": False,
                "timestamp": None,
                "error": item.get("error")
            })
            continue

        cameras.append({
            "camera_id": item.get("camera_id"),
            "camera_name": camera.get("name"),
            "camera_host": camera.get("host"),
            "channel": camera.get("channel"),
            "status": item.get("status"),
            "action": item.get("action"),
            "person_detected": event.get("person_detected"),
            "detections_count": event.get("detections_count"),
            "evidence_path": event.get("evidence_path"),
            "cooldown_active": event.get("cooldown_active"),
            "timestamp": event.get("timestamp")
        })

    attention_cameras = [
        camera for camera in cameras
        if camera.get("action") == "attention_required"
    ]

    failed_cameras = [
        camera for camera in cameras
        if camera.get("status") == "failed"
    ]

    return {
        "status": "ok",
        "monitor": "person",
        "mode": "summary",
        "enabled_cameras_count": result.get("enabled_cameras_count"),
        "attention_required_count": result.get("attention_required_count"),
        "no_action_count": result.get("no_action_count"),
        "failed_count": result.get("failed_count"),
        "attention_cameras": attention_cameras,
        "failed_cameras": failed_cameras,
        "cameras": cameras
    }
