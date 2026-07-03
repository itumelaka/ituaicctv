import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
EVENT_LOG_FILE = DATA_DIR / "events.jsonl"


def append_event_log(event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with EVENT_LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_latest_event_logs(limit: int = 20) -> list[dict[str, Any]]:
    if not EVENT_LOG_FILE.exists():
        return []

    with EVENT_LOG_FILE.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    latest_lines = lines[-limit:]
    events = []

    for line in latest_lines:
        line = line.strip()

        if not line:
            continue

        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    events.reverse()
    return events
