import json
import sys
from pathlib import Path

# Allow script to import app modules when run from backend folder.
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.monitor import run_person_monitor_check


def main():
    result = run_person_monitor_check()

    print(json.dumps(result, indent=2, ensure_ascii=False))

    event = result.get("event", {})
    person_detected = event.get("person_detected", False)

    if person_detected:
        # Exit code 2 means attention required.
        sys.exit(2)

    # Exit code 0 means normal/no action.
    sys.exit(0)


if __name__ == "__main__":
    main()
