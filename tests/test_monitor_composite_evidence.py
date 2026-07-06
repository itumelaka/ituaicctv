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
        "detections_count": 3,
        "detections": [
            {
                "class_name": "person",
                "confidence": 0.91,
                "box": {"x1": 10, "y1": 20, "x2": 110, "y2": 220},
            },
            {
                "class_name": "person",
                "confidence": 0.84,
                "box": {"x1": 140, "y1": 25, "x2": 230, "y2": 210},
            },
            {
                "class_name": "person",
                "confidence": 0.73,
                "box": {"x1": 260, "y1": 40, "x2": 330, "y2": 205},
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
        self.assertEqual(result["event"]["detections_count"], 3)
        self.assertEqual(len(result["event"]["person_detections"]), 3)
        self.assertEqual(result["event"]["person_detections"][0]["crop_rank"], 1)
        self.assertEqual(result["event"]["person_detections"][0]["confidence"], 0.91)
        self.assertEqual(
            result["event"]["person_detections"][0]["bbox"],
            {"x1": 10, "y1": 20, "x2": 110, "y2": 220},
        )
        self.assertEqual(result["event"]["evidence_path"], "data/evidence/test.jpg")
        self.assertEqual(result["event"]["face_readiness"]["face_readiness"], "not_available")
        save_image.assert_called_once()
        self.assertEqual(save_image.call_args.args[0], b"composite-image")

    def test_monitor_event_logs_person_targets_returned_by_evidence_builder(self):
        camera = {
            "id": "test_cam",
            "name": "Test Camera",
            "host": "192.168.40.99",
            "channel": "102",
        }
        evidence_metadata = {
            "detections_count": 2,
            "evidence_source": "hd_scaled_bbox",
            "detections": [
                {
                    "class_name": "person",
                    "confidence": 0.95,
                    "box": {"x1": 500, "y1": 300, "x2": 900, "y2": 980},
                },
                {
                    "class_name": "person",
                    "confidence": 0.82,
                    "box": {"x1": 920, "y1": 320, "x2": 1200, "y2": 960},
                },
            ],
            "person_detections": [
                {
                    "crop_rank": 1,
                    "confidence": 0.95,
                    "bbox": {"x1": 500, "y1": 300, "x2": 900, "y2": 980},
                },
                {
                    "crop_rank": 2,
                    "confidence": 0.82,
                    "bbox": {"x1": 920, "y1": 320, "x2": 1200, "y2": 960},
                },
            ],
        }
        appended_events = []

        def fake_evidence_builder(_frame, _result, camera=None):
            return (
                b"composite-image",
                {"face_readiness": "not_available"},
                {"face_recognition_enabled": False},
                evidence_metadata,
            )

        with (
            patch("app.events._is_person_event_in_cooldown", return_value=False),
            patch("app.events.build_person_evidence_from_detection", side_effect=fake_evidence_builder),
            patch("app.events.append_event_log", side_effect=appended_events.append),
            patch("app.events.save_evidence_image", return_value="data/evidence/test.jpg"),
            patch("app.monitor.send_person_alert", return_value=True),
        ):
            result = run_person_monitor_check_for_camera(
                camera,
                log_no_person=False,
            )

        self.assertEqual(result["event"]["detections_count"], 2)
        self.assertEqual(len(result["event"]["person_detections"]), 2)
        self.assertEqual(result["event"]["person_detections"][1]["crop_rank"], 2)
        self.assertEqual(
            result["event"]["person_detections"][1]["bbox"],
            {"x1": 920, "y1": 320, "x2": 1200, "y2": 960},
        )
        self.assertEqual(result["event"]["detections"], evidence_metadata["detections"])
        self.assertEqual(result["event"]["evidence_source"], "hd_scaled_bbox")
        self.assertEqual(result["event"]["message"], "Person detected in CCTV frame (2 detection(s)).")
        self.assertEqual(appended_events[0]["person_detections"], evidence_metadata["person_detections"])


if __name__ == "__main__":
    unittest.main()
