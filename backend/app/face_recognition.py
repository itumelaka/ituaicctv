import importlib
import json
import math
from pathlib import Path

from app.config import settings


LBPH_MODEL_FILENAME = "opencv_lbph_model.yml"
LBPH_LABELS_FILENAME = "opencv_lbph_labels.json"
LBPH_FACE_SIZE = (160, 160)

RECOGNITION_DISABLED = {
    "face_recognition_enabled": False,
    "face_recognition_available": False,
    "face_recognition_backend": _backend if (_backend := getattr(settings, "face_recognition_backend", "auto")) else "auto",
    "recognition_attempted": False,
    "recognized_label": None,
    "recognition_confidence": None,
    "recognition_reason": "disabled",
}


def _disabled_result() -> dict:
    result = dict(RECOGNITION_DISABLED)
    result["face_recognition_backend"] = _configured_backend()
    return result


def _result(
    *,
    enabled: bool,
    available: bool,
    attempted: bool,
    backend: str | None = None,
    label: str | None = None,
    confidence: float | None = None,
    reason: str,
) -> dict:
    return {
        "face_recognition_enabled": enabled,
        "face_recognition_available": available,
        "face_recognition_backend": backend or _configured_backend(),
        "recognition_attempted": attempted,
        "recognized_label": label,
        "recognition_confidence": confidence,
        "recognition_reason": reason,
    }


def recognition_is_enabled() -> bool:
    return bool(settings.face_recognition_enabled)


def _configured_backend() -> str:
    backend = getattr(settings, "face_recognition_backend", "auto") or "auto"
    backend = backend.strip().lower()

    if backend not in {"auto", "face_recognition", "opencv_lbph"}:
        return "auto"

    return backend


def _embedding_library():
    try:
        return importlib.import_module("face_recognition")
    except Exception:
        return None


def _cv2_module():
    try:
        return importlib.import_module("cv2")
    except Exception:
        return None


def _lbph_factory():
    cv2 = _cv2_module()
    face_module = getattr(cv2, "face", None) if cv2 else None
    factory = getattr(face_module, "LBPHFaceRecognizer_create", None)

    if callable(factory):
        return factory

    return None


def _lbph_available() -> bool:
    return _lbph_factory() is not None


def _select_backend() -> tuple[str | None, str | None]:
    configured = _configured_backend()

    if configured == "face_recognition":
        if _embedding_library() is None:
            return None, "embedding_library_unavailable"
        return "face_recognition", None

    if configured == "opencv_lbph":
        if not _lbph_available():
            return None, "opencv_lbph_unavailable"
        return "opencv_lbph", None

    if _embedding_library() is not None:
        return "face_recognition", None

    if _lbph_available():
        return "opencv_lbph", None

    return None, "no_supported_backend"


def recognition_available() -> bool:
    backend, _reason = _select_backend()
    return backend is not None


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
        if path.name == LBPH_LABELS_FILENAME:
            continue

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


def _recognize_with_embedding_library(face_crop, backend: str) -> dict:
    library = _embedding_library()
    if library is None:
        return _result(
            enabled=True,
            available=False,
            attempted=False,
            backend=backend,
            reason="embedding_library_unavailable",
        )

    embeddings = _load_embeddings()
    if not embeddings:
        return _result(
            enabled=True,
            available=True,
            attempted=False,
            backend=backend,
            reason="no_enrolled_embeddings",
        )

    try:
        face_encodings = library.face_encodings(face_crop)
    except Exception:
        return _result(
            enabled=True,
            available=True,
            attempted=False,
            backend=backend,
            reason="embedding_generation_failed",
        )

    if not face_encodings:
        return _result(
            enabled=True,
            available=True,
            attempted=False,
            backend=backend,
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
            backend=backend,
            label=best_label,
            confidence=round(confidence, 4),
            reason="matched",
        )

    return _result(
        enabled=True,
        available=True,
        attempted=True,
        backend=backend,
        label="UNKNOWN",
        confidence=round(confidence, 4),
        reason="no_match",
    )


def _lbph_paths() -> tuple[Path, Path]:
    embeddings_dir = Path(settings.face_embeddings_dir)
    return embeddings_dir / LBPH_MODEL_FILENAME, embeddings_dir / LBPH_LABELS_FILENAME


def _load_lbph_labels(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}

    data = json.loads(path.read_text(encoding="utf-8"))
    labels = data.get("labels", data)
    return {int(key): str(value) for key, value in labels.items()}


def _prepare_lbph_face(face_crop):
    cv2 = _cv2_module()
    if cv2 is None:
        return None

    try:
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    except Exception:
        gray = face_crop

    return cv2.resize(gray, LBPH_FACE_SIZE)


def _recognize_with_lbph(face_crop, backend: str) -> dict:
    factory = _lbph_factory()
    if factory is None:
        return _result(
            enabled=True,
            available=False,
            attempted=False,
            backend=backend,
            reason="opencv_lbph_unavailable",
        )

    model_path, labels_path = _lbph_paths()
    if not model_path.exists() or not labels_path.exists():
        return _result(
            enabled=True,
            available=True,
            attempted=False,
            backend=backend,
            reason="no_enrolled_lbph_model",
        )

    try:
        labels = _load_lbph_labels(labels_path)
        recognizer = factory()
        recognizer.read(str(model_path))
        prepared_face = _prepare_lbph_face(face_crop)
        label_id, distance = recognizer.predict(prepared_face)
    except Exception:
        return _result(
            enabled=True,
            available=True,
            attempted=False,
            backend=backend,
            reason="lbph_prediction_failed",
        )

    label = labels.get(int(label_id))
    threshold = float(settings.face_match_threshold)
    confidence = max(0.0, min(1.0, 1.0 - (float(distance) / max(threshold, 1.0))))

    if label and float(distance) <= threshold:
        return _result(
            enabled=True,
            available=True,
            attempted=True,
            backend=backend,
            label=label,
            confidence=round(confidence, 4),
            reason="matched",
        )

    return _result(
        enabled=True,
        available=True,
        attempted=True,
        backend=backend,
        label="UNKNOWN",
        confidence=round(confidence, 4),
        reason="no_match",
    )


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

    backend, unavailable_reason = _select_backend()
    if backend is None:
        return _result(
            enabled=True,
            available=False,
            attempted=False,
            reason=unavailable_reason or "no_supported_backend",
        )

    if backend == "opencv_lbph":
        return _recognize_with_lbph(face_crop, backend)

    return _recognize_with_embedding_library(face_crop, backend)

