import sys
import types
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))


fake_dotenv = types.ModuleType("dotenv")
fake_dotenv.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", fake_dotenv)

fake_cv2 = types.ModuleType("cv2")
fake_cv2.CAP_FFMPEG = 0
fake_cv2.CAP_PROP_BUFFERSIZE = 0
fake_cv2.IMWRITE_JPEG_QUALITY = 1
fake_cv2.VideoCapture = lambda *_args, **_kwargs: None
fake_cv2.FONT_HERSHEY_SIMPLEX = 0
fake_cv2.COLOR_BGR2GRAY = 0
fake_cv2.CV_64F = 0
fake_cv2.imencode = lambda *_args, **_kwargs: (True, types.SimpleNamespace(tobytes=lambda: b"jpg"))
fake_cv2.cvtColor = lambda image, _mode: image
fake_cv2.CascadeClassifier = lambda _path: types.SimpleNamespace(empty=lambda: True)
sys.modules.setdefault("cv2", fake_cv2)

fake_ultralytics = types.ModuleType("ultralytics")
fake_ultralytics.YOLO = lambda *_args, **_kwargs: None
sys.modules.setdefault("ultralytics", fake_ultralytics)

from app import detection


class _Frame:
    def __init__(self, width, height):
        self.shape = (height, width, 3)


class DetectionCameraConfigTests(unittest.TestCase):
    def test_camera_person_threshold_overrides_global_default(self):
        self.assertEqual(
            detection._person_confidence_threshold(
                {"id": "makmal_cam_13", "person_confidence_threshold": 0.75}
            ),
            0.75,
        )

    def test_missing_camera_threshold_uses_global_default(self):
        self.assertEqual(
            detection._person_confidence_threshold({"id": "other_cam"}),
            detection.settings.person_confidence_threshold,
        )

    def test_high_resolution_evidence_uses_high_res_detection_boxes(self):
        original_detection = {
            "person_detected": True,
            "detections": [
                {
                    "class_name": "person",
                    "confidence": 0.91,
                    "box": {"x1": 10, "y1": 20, "x2": 110, "y2": 220},
                }
            ],
        }
        high_res_detection = [
            {
                "class_name": "person",
                "confidence": 0.93,
                "box": {"x1": 500, "y1": 300, "x2": 900, "y2": 980},
            }
        ]
        captured = {}

        original_capture = detection.capture_frame_for_camera_channel
        original_detect = detection.detect_objects
        original_build = detection._build_person_evidence_frame
        original_assess = detection.assess_face_readiness
        original_crop = detection._crop_detection

        try:
            detection.capture_frame_for_camera_channel = (
                lambda _camera, _channel: _Frame(width=1920, height=1080)
            )
            detection.detect_objects = lambda *_args, **_kwargs: high_res_detection
            detection._crop_detection = lambda frame, _detection: frame
            detection.assess_face_readiness = lambda _image: {"face_readiness": "not_available"}
            detection._build_person_evidence_frame = (
                lambda frame, detections, face_readiness=None, face_recognition=None: captured.update(
                    {"frame": frame, "detections": detections}
                ) or frame
            )

            detection.build_person_evidence_from_detection(
                _Frame(width=640, height=360),
                original_detection,
                camera={"id": "cam_1", "channel": "102"},
            )
        finally:
            detection.capture_frame_for_camera_channel = original_capture
            detection.detect_objects = original_detect
            detection._build_person_evidence_frame = original_build
            detection.assess_face_readiness = original_assess
            detection._crop_detection = original_crop

        self.assertEqual(
            captured["detections"][0]["box"],
            {"x1": 500, "y1": 300, "x2": 900, "y2": 980},
        )
        self.assertEqual(captured["frame"].shape, (1080, 1920, 3))

    def test_face_readiness_returns_not_available_when_cascade_missing(self):
        original_data = getattr(detection.cv2, "data", None)

        try:
            detection.cv2.data = types.SimpleNamespace(haarcascades="")
            readiness = detection.assess_face_readiness(_Frame(width=320, height=240))
        finally:
            detection.cv2.data = original_data

        self.assertFalse(readiness["face_detection_available"])
        self.assertFalse(readiness["face_detected"])
        self.assertEqual(readiness["face_quality"], "unknown")
        self.assertEqual(readiness["face_readiness"], "not_available")

    def test_face_readiness_returns_no_face_detected_on_blank_image(self):
        class FakeCascade:
            def __init__(self, _path):
                pass

            def empty(self):
                return False

            def detectMultiScale(self, *_args, **_kwargs):
                return []

        original_data = getattr(detection.cv2, "data", None)
        original_cascade = detection.cv2.CascadeClassifier

        try:
            detection.cv2.data = types.SimpleNamespace(haarcascades="C:/fake/")
            detection.cv2.CascadeClassifier = FakeCascade
            readiness = detection.assess_face_readiness(_Frame(width=320, height=240))
        finally:
            detection.cv2.data = original_data
            detection.cv2.CascadeClassifier = original_cascade

        self.assertTrue(readiness["face_detection_available"])
        self.assertFalse(readiness["face_detected"])
        self.assertEqual(readiness["face_quality"], "poor")
        self.assertEqual(readiness["face_readiness"], "not_suitable")
        self.assertIn("no_face_detected", readiness["reasons"])


if __name__ == "__main__":
    unittest.main()
