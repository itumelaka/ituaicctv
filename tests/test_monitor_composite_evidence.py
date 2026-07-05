import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))


fake_detection = types.ModuleType("app.detection")


def _detection_result():
    return {
        "status": "ok",
        "person_detected": True,
        "detections_count": 1,
        "detections": [
            {
                "class_name": "person",
                "confidence": 0.91,
                "box": {"x1": 10, "y1": 20, "x2": 110, "y2": 220},
            }
        ],
        "confidence_threshold": 0.60,
        "camera": {"frame_width": 640, "frame_height": 360},
    }


def _with_frame(*_args, **_kwargs):
    return _detection_result(), object()


fake_detection.build_person_evidence_from_detection = (
    lambda _frame, _result, camera=None: (
        b"composite-image",
        {
            "face_detection_available": False,
            "face_detected": False,
            "face_count": 0,
            "best_face_box": None,
            "face_quality": "unknown",
            "face_readiness": "not_available",
            "reasons": ["face_detection_unavailable"],
        },
        {
            "face_recognition_enabled": False,
            "face_recognition_available": False,
            "recognition_attempted": False,
            "recognized_label": None,
            "recognition_confidence": None,
            "recognition_reason": "disabled",
        },
    )
)
fake_detection.run_person_detection_with_frame = _with_frame
fake_detection.run_person_detection_with_frame_for_camera = _with_frame
fake_detection.run_person_snapshot_jpeg = lambda: b"fallback-image"
fake_detection.run_person_snapshot_jpeg_for_camera = lambda _camera: b"fallback-image"

sys.modules["app.detection"] = fake_detection
sys.modules.setdefault("requests", types.ModuleType("requests"))
fake_dotenv = types.ModuleType("dotenv")
fake_dotenv.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", fake_dotenv)

from app.monitor import run_person_monitor_check_for_camera


class MonitorCompositeEvidenceTests(unittest.TestCase):
    def test_monitor_person_event_saves_composite_evidence_bytes(self):
        camera = {
            "id": "test_cam",
            "name": "Test Camera",
            "host": "192.168.40.99",
            "channel": "102",
        }

        with (
            patch("app.events._is_person_event_in_cooldown", return_value=False),
            patch("app.events.append_event_log"),
            patch("app.events.save_evidence_image", return_value="data/evidence/test.jpg") as save_image,
            patch("app.monitor.send_person_alert", return_value=True),
        ):
            result = run_person_monitor_check_for_camera(
                camera,
                log_no_person=False,
            )

        self.assertEqual(result["action"], "attention_required")
        self.assertTrue(result["event"]["person_detected"])
        self.assertEqual(result["event"]["evidence_path"], "data/evidence/test.jpg")
        self.assertEqual(result["event"]["face_readiness"]["face_readiness"], "not_available")
        save_image.assert_called_once()
        self.assertEqual(save_image.call_args.args[0], b"composite-image")


if __name__ == "__main__":
    unittest.main()
