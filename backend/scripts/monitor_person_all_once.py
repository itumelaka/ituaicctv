import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.monitor import run_person_monitor_check_all


def print_summary(result: dict):
    print("ITU AI CCTV - Multi-Camera Person Monitor")
    print("=" * 50)
    print(f"Status              : {result.get('status')}")
    print(f"Mode                : {result.get('mode')}")
    print(f"Enabled cameras     : {result.get('enabled_cameras_count')}")
    print(f"Attention required  : {result.get('attention_required_count')}")
    print(f"No action           : {result.get('no_action_count')}")
    print(f"Failed              : {result.get('failed_count')}")
    print("")

    attention_items = [
        item for item in result.get("results", [])
        if item.get("action") == "attention_required"
    ]

    failed_items = [
        item for item in result.get("results", [])
        if item.get("status") == "failed"
    ]

    if attention_items:
        print("Attention cameras:")
        for item in attention_items:
            event = item.get("event") or {}
            camera = event.get("camera") or {}
            evidence_path = event.get("evidence_path")
            cooldown_active = event.get("cooldown_active")

            if evidence_path:
                evidence_status = "evidence saved"
            elif cooldown_active:
                evidence_status = "evidence skipped by cooldown"
            else:
                evidence_status = "no evidence"

            print(
                f"- {item.get('camera_id')} | "
                f"{camera.get('name')} | "
                f"detections={event.get('detections_count')} | "
                f"{evidence_status}"
            )
    else:
        print("Attention cameras: none")

    print("")

    if failed_items:
        print("Failed cameras:")
        for item in failed_items:
            print(
                f"- {item.get('camera_id')} | "
                f"{item.get('camera_name')} | "
                f"{item.get('error')}"
            )
    else:
        print("Failed cameras: none")


def main():
    result = run_person_monitor_check_all()

    print_summary(result)

    print("")
    print("Compact JSON:")
    print(json.dumps({
        "status": result.get("status"),
        "mode": result.get("mode"),
        "enabled_cameras_count": result.get("enabled_cameras_count"),
        "attention_required_count": result.get("attention_required_count"),
        "no_action_count": result.get("no_action_count"),
        "failed_count": result.get("failed_count"),
    }, indent=2, ensure_ascii=False))

    if result.get("failed_count", 0) > 0:
        return 1

    if result.get("attention_required_count", 0) > 0:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
