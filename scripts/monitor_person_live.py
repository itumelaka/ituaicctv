import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import settings
from app.monitor import run_person_monitor_check_all


def _positive_int(value: int, default: int) -> int:
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default

    return value if value > 0 else default


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _print_cycle_summary(result: dict, interval_seconds: int) -> None:
    print(
        "[{timestamp}] enabled={enabled} attention={attention} "
        "failed={failed} next_scan={interval}s".format(
            timestamp=_utc_timestamp(),
            enabled=result.get("enabled_cameras_count", 0),
            attention=result.get("attention_required_count", 0),
            failed=result.get("failed_count", 0),
            interval=interval_seconds,
        ),
        flush=True,
    )

    attention_items = [
        item for item in result.get("results", [])
        if item.get("action") == "attention_required"
    ]

    for item in attention_items:
        event = item.get("event") or {}
        camera = event.get("camera") or {}
        cooldown = " cooldown=active" if event.get("cooldown_active") else ""
        evidence = " evidence=yes" if event.get("evidence_path") else " evidence=no"
        print(
            "  attention camera={camera_id} name={camera_name}{cooldown}{evidence}".format(
                camera_id=item.get("camera_id"),
                camera_name=camera.get("name") or item.get("camera_name") or "-",
                cooldown=cooldown,
                evidence=evidence,
            ),
            flush=True,
        )

    failed_items = [
        item for item in result.get("results", [])
        if item.get("status") == "failed"
    ]

    for item in failed_items:
        print(
            "  failed camera={camera_id} name={camera_name} error={error}".format(
                camera_id=item.get("camera_id"),
                camera_name=item.get("camera_name") or "-",
                error=item.get("error") or "unknown",
            ),
            flush=True,
        )


def _sleep_interruptibly(seconds: int) -> None:
    for _ in range(seconds):
        time.sleep(1)


def main() -> int:
    interval_seconds = _positive_int(
        settings.live_monitor_interval_seconds,
        default=10,
    )
    cooldown_seconds = _positive_int(
        settings.live_monitor_alert_cooldown_seconds,
        default=300,
    )

    settings.person_event_cooldown_seconds = cooldown_seconds

    print("ITU AI CCTV - Near-Live Person Monitor", flush=True)
    print(
        "interval={interval}s alert_cooldown={cooldown}s mode=sequential".format(
            interval=interval_seconds,
            cooldown=cooldown_seconds,
        ),
        flush=True,
    )
    print("Press Ctrl+C to stop cleanly.", flush=True)

    try:
        while True:
            try:
                result = run_person_monitor_check_all(log_no_person=False)
                _print_cycle_summary(result, interval_seconds)
            except Exception as error:
                print(
                    "[{timestamp}] live_monitor_cycle_failed error={error} next_scan={interval}s".format(
                        timestamp=_utc_timestamp(),
                        error=error,
                        interval=interval_seconds,
                    ),
                    flush=True,
                )

            _sleep_interruptibly(interval_seconds)

    except KeyboardInterrupt:
        print("\nLive monitor stopped cleanly.", flush=True)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
