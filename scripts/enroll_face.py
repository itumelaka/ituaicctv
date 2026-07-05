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


def _safe_label(label: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", label.strip().upper())
    return cleaned.strip("_")


def _embedding_library():
    try:
        return importlib.import_module("face_recognition")
    except Exception:
        return None


def _load_image(path: Path):
    import cv2

    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Cannot read image: {path}")

    return image


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Enroll approved internal staff/student face embeddings locally. "
            "Raw reference images are not copied by this script."
        )
    )
    parser.add_argument("--label", required=True, help="Approved internal label, for example BURN")
    parser.add_argument("--images", nargs="+", required=True, help="One or more local image paths")
    args = parser.parse_args()

    label = _safe_label(args.label)
    if not label:
        print("ERROR: Label is empty after sanitizing.")
        return 1

    library = _embedding_library()
    if library is None:
        print(
            "ERROR: face_recognition library is not installed. "
            "Install and approve a local embedding dependency before enrollment."
        )
        return 2

    embeddings = []
    rejected = []

    for image_arg in args.images:
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
                "embedding_model": "face_recognition",
                "embeddings": embeddings,
                "source_image_count": len(args.images),
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


if __name__ == "__main__":
    raise SystemExit(main())

