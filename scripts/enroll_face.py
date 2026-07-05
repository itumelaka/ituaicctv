import argparse
import importlib
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import settings  # noqa: E402
from app.detection import assess_face_readiness  # noqa: E402
from app.face_recognition import (  # noqa: E402
    LBPH_FACE_SIZE,
    LBPH_LABELS_FILENAME,
    LBPH_MODEL_FILENAME,
)


def _safe_label(label: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", label.strip().upper())
    return cleaned.strip("_")


def _embedding_library():
    try:
        return importlib.import_module("face_recognition")
    except Exception:
        return None


def _cv2_module():
    return importlib.import_module("cv2")


def _lbph_factory():
    cv2 = _cv2_module()
    face_module = getattr(cv2, "face", None)
    factory = getattr(face_module, "LBPHFaceRecognizer_create", None)

    if callable(factory):
        return factory

    return None


def _select_backend(requested: str) -> tuple[str | None, str | None]:
    backend = requested.strip().lower()

    if backend == "face_recognition":
        return ("face_recognition", None) if _embedding_library() else (None, "face_recognition library is not installed")

    if backend == "opencv_lbph":
        return ("opencv_lbph", None) if _lbph_factory() else (None, "opencv-contrib-python with cv2.face is not installed")

    if _embedding_library():
        return "face_recognition", None

    if _lbph_factory():
        return "opencv_lbph", None

    return None, "No supported local face recognition backend is available"


def _load_image(path: Path):
    cv2 = _cv2_module()
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Cannot read image: {path}")

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


def _enroll_face_recognition(label: str, images: list[str]) -> int:
    library = _embedding_library()
    if library is None:
        print("ERROR: face_recognition library is not installed.")
        return 2

    embeddings = []
    rejected = []

    for image_arg in images:
        image_path = Path(image_arg)
        try:
            image = _load_image(image_path)
            readiness = assess_face_readiness(image)

            if readiness.get("face_readiness") not in {"possible", "suitable"}:
                rejected.append(
                    {
                        "image": str(image_path),
                        "reason": ",".join(readiness.get("reasons") or ["face_not_suitable"]),
                    }
                )
                continue

            encodings = library.face_encodings(image)
            if not encodings:
                rejected.append({"image": str(image_path), "reason": "no_face_embedding"})
                continue

            embeddings.append([float(value) for value in encodings[0]])
        except Exception as error:
            rejected.append({"image": str(image_path), "reason": str(error)})

    if not embeddings:
        print("ERROR: No suitable face embeddings were created.")
        for item in rejected:
            print(f"Rejected: {item['image']} ({item['reason']})")
        return 3

    embeddings_dir = Path(settings.face_embeddings_dir)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    output_path = embeddings_dir / f"{label}.json"
    output_path.write_text(
        json.dumps(
            {
                "label": label,
                "backend": "face_recognition",
                "embedding_model": "face_recognition",
                "embeddings": embeddings,
                "source_image_count": len(images),
                "accepted_image_count": len(embeddings),
                "rejected": rejected,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Enrolled {label}: {len(embeddings)} embedding(s) saved to {output_path}")
    if rejected:
        print(f"Rejected {len(rejected)} image(s); review reasons in the JSON file.")

    return 0


def _load_lbph_labels(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}

    data = json.loads(path.read_text(encoding="utf-8"))
    labels = data.get("labels", data)
    return {int(key): str(value) for key, value in labels.items()}


def _save_lbph_labels(path: Path, labels: dict[int, str]) -> None:
    path.write_text(
        json.dumps(
            {
                "backend": "opencv_lbph",
                "labels": {str(key): value for key, value in sorted(labels.items())},
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _prepare_lbph_face(face_crop):
    cv2 = _cv2_module()
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    return cv2.resize(gray, LBPH_FACE_SIZE)


def _enroll_opencv_lbph(label: str, images: list[str]) -> int:
    factory = _lbph_factory()
    if factory is None:
        print("ERROR: OpenCV LBPH is unavailable. Install opencv-contrib-python so cv2.face exists.")
        return 2

    accepted_faces = []
    rejected = []

    for image_arg in images:
        image_path = Path(image_arg)
        try:
            image = _load_image(image_path)
            readiness = assess_face_readiness(image)

            if readiness.get("face_readiness") not in {"possible", "suitable"}:
                rejected.append(
                    {
                        "image": str(image_path),
                        "reason": ",".join(readiness.get("reasons") or ["face_not_suitable"]),
                    }
                )
                continue

            face_crop = _face_crop_from_readiness(image, readiness)
            if face_crop is None:
                rejected.append({"image": str(image_path), "reason": "no_face_box"})
                continue

            accepted_faces.append(_prepare_lbph_face(face_crop))
        except Exception as error:
            rejected.append({"image": str(image_path), "reason": str(error)})

    if not accepted_faces:
        print("ERROR: No suitable LBPH training faces were created.")
        for item in rejected:
            print(f"Rejected: {item['image']} ({item['reason']})")
        return 3

    import numpy as np

    embeddings_dir = Path(settings.face_embeddings_dir)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    model_path = embeddings_dir / LBPH_MODEL_FILENAME
    labels_path = embeddings_dir / LBPH_LABELS_FILENAME
    labels = _load_lbph_labels(labels_path)
    reverse_labels = {value: key for key, value in labels.items()}
    label_id = reverse_labels.get(label)

    if label_id is None:
        label_id = max(labels.keys(), default=0) + 1
        labels[label_id] = label

    training_labels = np.array([label_id] * len(accepted_faces), dtype=np.int32)
    recognizer = factory()

    if model_path.exists() and hasattr(recognizer, "update"):
        recognizer.read(str(model_path))
        recognizer.update(accepted_faces, training_labels)
    else:
        recognizer.train(accepted_faces, training_labels)

    recognizer.write(str(model_path))
    _save_lbph_labels(labels_path, labels)

    print(f"Enrolled {label}: {len(accepted_faces)} LBPH face sample(s) saved to {model_path}")
    if rejected:
        print(f"Rejected {len(rejected)} image(s); review quality before retrying.")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Enroll approved internal staff/student face data locally. "
            "Raw reference images are not copied by this script."
        )
    )
    parser.add_argument("--label", required=True, help="Approved internal label, for example BURN")
    parser.add_argument(
        "--backend",
        choices=["auto", "face_recognition", "opencv_lbph"],
        default="auto",
        help="Local recognition backend to enroll for.",
    )
    parser.add_argument("--images", nargs="+", required=True, help="One or more local image paths")
    args = parser.parse_args()

    label = _safe_label(args.label)
    if not label:
        print("ERROR: Label is empty after sanitizing.")
        return 1

    backend, error = _select_backend(args.backend)
    if backend is None:
        print(f"ERROR: {error}")
        return 2

    if backend == "opencv_lbph":
        return _enroll_opencv_lbph(label, args.images)

    return _enroll_face_recognition(label, args.images)


if __name__ == "__main__":
    raise SystemExit(main())

