import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from app.config import settings
from app.detection import assess_face_readiness
from app.face_recognition import (
    LBPH_FACE_SIZE,
    LBPH_LABELS_FILENAME,
    LBPH_MODEL_FILENAME,
)


CSV_HEADERS = [
    "label",
    "identity_id",
    "display_name",
    "image_path",
    "approved_for_face_recognition",
    "approved_by",
    "consent_reference",
    "notes",
]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
TRUE_VALUES = {"1", "true", "yes", "y", "on", "approved"}


def safe_label(label: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", label.strip().upper())
    return cleaned.strip("_")


def csv_template_rows() -> list[dict]:
    return [
        {
            "label": "APPROVED_LABEL",
            "identity_id": "optional-local-id",
            "display_name": "Optional Display Name",
            "image_path": r"C:\private\approved-face-reference\person-001.jpg",
            "approved_for_face_recognition": "yes",
            "approved_by": "authorized-reviewer",
            "consent_reference": "local-policy-or-consent-ref",
            "notes": "Do not commit real names, IDs, or local image paths.",
        }
    ]


def write_csv(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in CSV_HEADERS})


def write_csv_template(path: Path) -> dict:
    write_csv(path, csv_template_rows())
    return {"status": "ok", "path": str(path), "headers": CSV_HEADERS}


def _image_files(source_dir: Path, recursive: bool) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    return sorted(
        path
        for path in source_dir.glob(pattern)
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def _draft_label(path: Path, source_dir: Path, label_from: str) -> str:
    if label_from == "parent":
        return safe_label(path.parent.name)

    if label_from == "filename":
        return safe_label(path.stem)

    return safe_label(source_dir.name)


def generate_draft_csv(
    source_dir: Path,
    output_path: Path,
    *,
    recursive: bool = True,
    label_from: str = "parent",
) -> dict:
    if label_from not in {"parent", "filename", "folder"}:
        raise ValueError("label_from must be one of: parent, filename, folder")

    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    rows = [
        {
            "label": _draft_label(image_path, source_dir, label_from),
            "identity_id": "",
            "display_name": "",
            "image_path": str(image_path),
            "approved_for_face_recognition": "no",
            "approved_by": "",
            "consent_reference": "",
            "notes": "Review and change approved_for_face_recognition to yes before enrollment.",
        }
        for image_path in _image_files(source_dir, recursive)
    ]
    write_csv(output_path, rows)
    return {"status": "ok", "path": str(output_path), "rows": len(rows)}


def read_enrollment_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [header for header in CSV_HEADERS if header not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV missing required column(s): {', '.join(missing)}")
        return [dict(row) for row in reader]


def _truthy(value: str) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def _cv2_module():
    import cv2

    return cv2


def _lbph_factory():
    cv2 = _cv2_module()
    face_module = getattr(cv2, "face", None)
    factory = getattr(face_module, "LBPHFaceRecognizer_create", None)

    if callable(factory):
        return factory

    return None


def _load_image(path: Path):
    image = _cv2_module().imread(str(path))
    if image is None:
        raise ValueError("image_unreadable")

    return image


def _face_crop_from_readiness(image, readiness: dict):
    box = readiness.get("best_face_box")
    if not box:
        return None

    x = max(0, int(box["x"]))
    y = max(0, int(box["y"]))
    width = max(1, int(box["width"]))
    height = max(1, int(box["height"]))
    return image[y:y + height, x:x + width]


def _prepare_lbph_face(face_crop):
    cv2 = _cv2_module()
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    return cv2.resize(gray, LBPH_FACE_SIZE)


def load_lbph_labels(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}

    data = json.loads(path.read_text(encoding="utf-8"))
    labels = data.get("labels", data)
    return {int(key): str(value) for key, value in labels.items()}


def load_lbph_identities(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}

    data = json.loads(path.read_text(encoding="utf-8"))
    identities = data.get("identities", {})
    return identities if isinstance(identities, dict) else {}


def save_lbph_labels(path: Path, labels: dict[int, str], identities: dict[str, dict] | None = None) -> None:
    payload = {
        "backend": "opencv_lbph",
        "labels": {str(key): value for key, value in sorted(labels.items())},
    }
    if identities:
        payload["identities"] = identities

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _reject(row_number: int, row: dict, reason: str) -> dict:
    return {
        "row_number": row_number,
        "label": row.get("label", ""),
        "identity_id": row.get("identity_id", ""),
        "display_name": row.get("display_name", ""),
        "image_path": row.get("image_path", ""),
        "reason": reason,
    }


def validate_identity_assignment(payload: dict) -> dict:
    label = safe_label(str(payload.get("assigned_label") or payload.get("label", "")))
    if not label:
        raise ValueError("label is required")

    return {
        "label": label,
        "assigned_label": label,
        "identity_id": str(payload.get("identity_id", "")).strip(),
        "display_name": str(payload.get("assigned_display_name") or payload.get("display_name", "")).strip(),
        "assigned_display_name": str(payload.get("assigned_display_name") or payload.get("display_name", "")).strip(),
        "assigned_by": str(payload.get("assigned_by", "")).strip(),
        "event_id": str(payload.get("event_id", "")).strip(),
        "review_id": str(payload.get("review_id", "")).strip(),
        "evidence_filename": str(payload.get("evidence_filename", "")).strip(),
        "approved_for_training": _truthy(payload.get("approved_for_training", "")),
        "approved_for_face_recognition": _truthy(payload.get("approved_for_face_recognition", "")),
        "note": str(payload.get("note", "")).strip(),
        "notes": str(payload.get("note") or payload.get("notes", "")).strip(),
    }


def enroll_lbph_from_csv(csv_path: Path, report_path: Path | None = None) -> dict:
    factory = _lbph_factory()
    if factory is None:
        raise RuntimeError("OpenCV LBPH is unavailable. Install opencv-contrib-python so cv2.face exists.")

    rows = read_enrollment_csv(csv_path)
    accepted_faces = []
    accepted_label_names = []
    accepted_rows = []
    rejected = []

    for index, row in enumerate(rows, start=2):
        label = safe_label(row.get("label", ""))
        image_path = Path(row.get("image_path", "")).expanduser()

        if not label:
            rejected.append(_reject(index, row, "label_empty"))
            continue

        if not _truthy(row.get("approved_for_face_recognition", "")):
            rejected.append(_reject(index, row, "not_approved_for_face_recognition"))
            continue

        if not image_path.exists() or not image_path.is_file():
            rejected.append(_reject(index, row, "image_path_not_found"))
            continue

        try:
            image = _load_image(image_path)
            readiness = assess_face_readiness(image)

            if readiness.get("face_readiness") not in {"possible", "suitable"}:
                reasons = readiness.get("reasons") or ["face_not_suitable"]
                rejected.append(_reject(index, row, ",".join(reasons)))
                continue

            face_crop = _face_crop_from_readiness(image, readiness)
            if face_crop is None:
                rejected.append(_reject(index, row, "no_face_box"))
                continue

            accepted_faces.append(_prepare_lbph_face(face_crop))
            accepted_label_names.append(label)
            accepted_rows.append({**row, "label": label})
        except Exception as error:
            rejected.append(_reject(index, row, str(error)))

    if not accepted_faces:
        result = {
            "status": "rejected",
            "backend": "opencv_lbph",
            "source_csv": str(csv_path),
            "accepted_count": 0,
            "rejected_count": len(rejected),
            "rejected": rejected,
        }
        if report_path:
            write_reject_report(report_path, result)
            result["report_path"] = str(report_path)
        return result

    import numpy as np

    embeddings_dir = Path(settings.face_embeddings_dir)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    model_path = embeddings_dir / LBPH_MODEL_FILENAME
    labels_path = embeddings_dir / LBPH_LABELS_FILENAME
    labels = load_lbph_labels(labels_path)
    identities = load_lbph_identities(labels_path)
    reverse_labels = {value: key for key, value in labels.items()}
    training_ids = []

    for row in accepted_rows:
        label = row["label"]
        label_id = reverse_labels.get(label)
        if label_id is None:
            label_id = max(labels.keys(), default=0) + 1
            labels[label_id] = label
            reverse_labels[label] = label_id
        training_ids.append(label_id)
        identities[label] = {
            "identity_id": row.get("identity_id", ""),
            "display_name": row.get("display_name", ""),
            "consent_reference": row.get("consent_reference", ""),
        }

    recognizer = factory()
    training_labels = np.array(training_ids, dtype=np.int32)

    if model_path.exists() and hasattr(recognizer, "update"):
        recognizer.read(str(model_path))
        recognizer.update(accepted_faces, training_labels)
    else:
        recognizer.train(accepted_faces, training_labels)

    recognizer.write(str(model_path))
    save_lbph_labels(labels_path, labels, identities=identities)

    result = {
        "status": "ok",
        "backend": "opencv_lbph",
        "source_csv": str(csv_path),
        "model_path": str(model_path),
        "labels_path": str(labels_path),
        "accepted_count": len(accepted_faces),
        "rejected_count": len(rejected),
        "accepted_labels": sorted(set(accepted_label_names)),
        "rejected": rejected,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if report_path:
        write_reject_report(report_path, result)
        result["report_path"] = str(report_path)

    return result


def write_reject_report(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
