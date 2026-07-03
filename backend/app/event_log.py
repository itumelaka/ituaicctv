import json
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
EVENT_LOG_FILE = DATA_DIR / "events.jsonl"
EVIDENCE_DIR = DATA_DIR / "evidence"


def append_event_log(event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with EVENT_LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_all_event_logs() -> list[dict[str, Any]]:
    if not EVENT_LOG_FILE.exists():
        return []

    events = []

    with EVENT_LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return events


def read_latest_event_logs(limit: int = 20) -> list[dict[str, Any]]:
    events = read_all_event_logs()
    latest_events = events[-limit:]
    latest_events.reverse()
    return latest_events


def list_evidence_images(limit: int = 20) -> list[dict[str, Any]]:
    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    if not EVIDENCE_DIR.exists():
        return []

    evidence_files = [
        file_path for file_path in EVIDENCE_DIR.iterdir()
        if file_path.is_file()
    ]

    evidence_files.sort(
        key=lambda file_path: file_path.stat().st_mtime,
        reverse=True
    )

    images = []

    for file_path in evidence_files[:limit]:
        stat = file_path.stat()
        modified_time = datetime.fromtimestamp(
            stat.st_mtime,
            tz=timezone.utc
        ).isoformat()

        images.append({
            "filename": file_path.name,
            "url": f"/events/evidence/{file_path.name}",
            "modified_time": modified_time,
            "size_bytes": stat.st_size
        })

    return images


def save_evidence_image(image_bytes: bytes, filename: str) -> str:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    safe_filename = filename.replace(":", "-").replace("/", "-").replace("\\", "-")
    file_path = EVIDENCE_DIR / safe_filename

    with file_path.open("wb") as file:
        file.write(image_bytes)

    return str(file_path.relative_to(BASE_DIR))


def get_evidence_image_path(filename: str) -> Path:
    safe_filename = Path(filename).name
    file_path = EVIDENCE_DIR / safe_filename

    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError("Evidence image not found.")

    return file_path
