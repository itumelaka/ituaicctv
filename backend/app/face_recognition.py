import importlib
import json
import math
from pathlib import Path

from app.config import settings


RECOGNITION_DISABLED = {
    "face_recognition_enabled": False,
    "face_recognition_available": False,
    "recognition_attempted": False,
    "recognized_label": None,
    "recognition_confidence": None,
    "recognition_reason": "disabled",
}


def _disabled_result() -> dict:
    return dict(RECOGNITION_DISABLED)


def _result(
    *,
    enabled: bool,
    available: bool,
    attempted: bool,
    label: str | None = None,
    confidence: float | None = None,
    reason: str,
) -> dict:
    return {
        "face_recognition_enabled": enabled,
        "face_recognition_available": available,
        "recognition_attempted": attempted,
        "recognized_label": label,
        "recognition_confidence": confidence,
        "recognition_reason": reason,
    }


def recognition_is_enabled() -> bool:
    return bool(settings.face_recognition_enabled)


def _embedding_library():
    try:
        return importlib.import_module("face_recognition")
    except Exception:
        return None


def recognition_available() -> bool:
    return _embedding_library() is not None


def _face_is_ready(face_readiness: dict | None) -> bool:
    if not face_readiness:
        return False

    return face_readiness.get("face_readiness") in {"possible", "suitable"}


def _load_embeddings() -> list[dict]:
    embeddings_dir = Path(settings.face_embeddings_dir)

    if not embeddings_dir.exists():
        return []

    embeddings = []
    for path in embeddings_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            label = data.get("label") or path.stem
            vectors = data.get("embeddings") or []

            for vector in vectors:
                if isinstance(vector, list) and vector:
                    embeddings.append({"label": label, "embedding": [float(v) for v in vector]})
        except Exception:
            continue

    return embeddings


def _distance(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return math.inf

    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def recognize_face(face_crop, face_readiness: dict | None) -> dict:
    if not recognition_is_enabled():
        return _disabled_result()

    if not _face_is_ready(face_readiness):
        return _result(
            enabled=True,
            available=False,
            attempted=False,
            reason="face_readiness_not_suitable",
        )

    library = _embedding_library()
    if library is None:
        return _result(
            enabled=True,
            available=False,
            attempted=False,
            reason="embedding_library_unavailable",
        )

    embeddings = _load_embeddings()
    if not embeddings:
        return _result(
            enabled=True,
            available=True,
            attempted=False,
            reason="no_enrolled_embeddings",
        )

    try:
        face_encodings = library.face_encodings(face_crop)
    except Exception:
        return _result(
            enabled=True,
            available=True,
            attempted=False,
            reason="embedding_generation_failed",
        )

    if not face_encodings:
        return _result(
            enabled=True,
            available=True,
            attempted=False,
            reason="no_face_embedding",
        )

    query_embedding = [float(value) for value in face_encodings[0]]
    best_label = None
    best_distance = math.inf

    for item in embeddings:
        distance = _distance(query_embedding, item["embedding"])
        if distance < best_distance:
            best_distance = distance
            best_label = item["label"]

    threshold = float(settings.face_match_threshold)
    confidence = max(0.0, min(1.0, 1.0 - best_distance))

    if best_label is not None and best_distance <= threshold:
        return _result(
            enabled=True,
            available=True,
            attempted=True,
            label=best_label,
            confidence=round(confidence, 4),
            reason="matched",
        )

    return _result(
        enabled=True,
        available=True,
        attempted=True,
        label="UNKNOWN",
        confidence=round(confidence, 4),
        reason="no_match",
    )

