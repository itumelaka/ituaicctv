import json
import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
SCHEDULER_LOG_FILE = BASE_DIR / "data" / "task-logs" / "monitor_person_all.log"


def _empty_scheduler_summary(status: str) -> dict[str, Any]:
    return {
        "status": status,
        "latest_run_time": None,
        "latest_summary": None,
        "failed_count": None,
        "person_detected_count": None,
        "no_person_count": None,
        "log_path": "data/task-logs/monitor_person_all.log",
        "recent_lines": [],
    }


def _safe_log_line(line: str) -> str:
    safe_line = re.sub(r"rtsp://\S+", "rtsp://***", line)
    safe_line = re.sub(
        r'("?(?:username|password|credential|credentials)"?\s*[:=]\s*)("[^"]*"|\S+)',
        r"\1***",
        safe_line,
        flags=re.IGNORECASE,
    )
    return safe_line


def _read_scheduler_log_lines(log_path: Path) -> list[str]:
    if not log_path.exists() or not log_path.is_file():
        return []

    return log_path.read_text(encoding="utf-8", errors="ignore").splitlines()


def _extract_last_json_object(lines: list[str]) -> dict[str, Any] | None:
    text = "\n".join(lines)
    decoder = json.JSONDecoder()
    latest_object = None
    index = 0

    while index < len(text):
        start = text.find("{", index)

        if start == -1:
            break

        try:
            parsed, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue

        if isinstance(parsed, dict):
            latest_object = parsed

        index = start + max(end, 1)

    return latest_object


def _get_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())

    return None


def _extract_labeled_count(lines: list[str], label: str) -> int | None:
    pattern = re.compile(rf"^{re.escape(label)}\s*:\s*(\d+)\s*$", re.IGNORECASE)

    for line in reversed(lines):
        match = pattern.search(line.strip())

        if match:
            return int(match.group(1))

    return None


def _extract_latest_run_time(lines: list[str]) -> str | None:
    pattern = re.compile(r"^Run started:\s*(.+?)\s*$", re.IGNORECASE)

    for line in reversed(lines):
        match = pattern.search(line.strip())

        if match:
            return match.group(1)

    return None


def _build_latest_summary(
    latest_json: dict[str, Any] | None,
    failed_count: int | None,
    person_detected_count: int | None,
    no_person_count: int | None,
) -> str | None:
    if latest_json:
        parts = []

        status = latest_json.get("status")
        mode = latest_json.get("mode") or latest_json.get("monitor")
        enabled_count = latest_json.get("enabled_cameras_count")

        if status:
            parts.append(f"status={status}")

        if mode:
            parts.append(f"mode={mode}")

        if enabled_count is not None:
            parts.append(f"enabled={enabled_count}")

        if person_detected_count is not None:
            parts.append(f"person={person_detected_count}")

        if no_person_count is not None:
            parts.append(f"no_person={no_person_count}")

        if failed_count is not None:
            parts.append(f"failed={failed_count}")

        if parts:
            return ", ".join(parts)

    if failed_count is None and person_detected_count is None and no_person_count is None:
        return None

    return (
        f"person={person_detected_count if person_detected_count is not None else 'unknown'}, "
        f"no_person={no_person_count if no_person_count is not None else 'unknown'}, "
        f"failed={failed_count if failed_count is not None else 'unknown'}"
    )


def parse_scheduler_log_summary(
    log_path: Path = SCHEDULER_LOG_FILE,
    recent_line_count: int = 8,
) -> dict[str, Any]:
    lines = _read_scheduler_log_lines(log_path)

    if not lines:
        return _empty_scheduler_summary("missing")

    non_empty_lines = [
        _safe_log_line(line.strip())
        for line in lines
        if line.strip()
    ]
    latest_json = _extract_last_json_object(lines)

    failed_count = None
    person_detected_count = None
    no_person_count = None

    if latest_json:
        failed_count = _get_int(latest_json.get("failed_count"))
        person_detected_count = _get_int(latest_json.get("attention_required_count"))

        if person_detected_count is None:
            person_detected_count = _get_int(latest_json.get("person_detected_count"))

        no_person_count = _get_int(latest_json.get("no_action_count"))

        if no_person_count is None:
            no_person_count = _get_int(latest_json.get("no_person_count"))

    if failed_count is None:
        failed_count = _extract_labeled_count(lines, "Failed")

    if person_detected_count is None:
        person_detected_count = _extract_labeled_count(lines, "Attention required")

    if no_person_count is None:
        no_person_count = _extract_labeled_count(lines, "No action")

    latest_summary = _build_latest_summary(
        latest_json=latest_json,
        failed_count=failed_count,
        person_detected_count=person_detected_count,
        no_person_count=no_person_count,
    )

    return {
        "status": latest_json.get("status", "unknown") if latest_json else "unknown",
        "latest_run_time": _extract_latest_run_time(lines),
        "latest_summary": latest_summary,
        "failed_count": failed_count,
        "person_detected_count": person_detected_count,
        "no_person_count": no_person_count,
        "log_path": "data/task-logs/monitor_person_all.log",
        "recent_lines": non_empty_lines[-recent_line_count:],
    }


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
    scheduler = parse_scheduler_log_summary()
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
        "scheduler": scheduler,
        "per_camera": per_camera,
    }
