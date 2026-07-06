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

    def __getitem__(self, _key):
        return self

    def __setitem__(self, _key, _value):
        pass


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

    def test_point_in_polygon_detects_inside_and_outside_points(self):
        polygon = [(0, 0), (10, 0), (10, 10), (0, 10)]

        self.assertTrue(detection.point_in_polygon((5, 5), polygon))
        self.assertFalse(detection.point_in_polygon((15, 5), polygon))

    def test_enabled_ignore_zone_suppresses_detection_inside_polygon(self):
        camera = {
            "id": "test_cam",
            "ignore_zones": [
                {
                    "id": "static_object",
                    "label": "Static object",
                    "type": "polygon",
                    "enabled": True,
                    "points": [[0.0, 0.0], [0.5, 0.0], [0.5, 0.5], [0.0, 0.5]],
                }
            ],
        }
        detections = [
            {
                "class_name": "person",
                "confidence": 0.80,
                "box": {"x1": 10, "y1": 10, "x2": 30, "y2": 30},
            }
        ]

        filtered, ignored = detection.filter_detections_by_ignore_zones(
            camera,
            detections,
            frame_width=100,
            frame_height=100,
        )

        self.assertEqual(filtered, [])
        self.assertEqual(len(ignored), 1)
        self.assertTrue(ignored[0]["ignored_by_zone"])
        self.assertEqual(ignored[0]["ignore_zone_id"], "static_object")

    def test_disabled_ignore_zone_does_not_suppress_detection(self):
        camera = {
            "id": "test_cam",
            "ignore_zones": [
                {
                    "id": "disabled_zone",
                    "label": "Disabled zone",
                    "type": "polygon",
                    "enabled": False,
                    "points": [[0.0, 0.0], [0.5, 0.0], [0.5, 0.5], [0.0, 0.5]],
                }
            ],
        }
        detections = [
            {
                "class_name": "person",
                "confidence": 0.80,
                "box": {"x1": 10, "y1": 10, "x2": 30, "y2": 30},
            }
        ]

        filtered, ignored = detection.filter_detections_by_ignore_zones(
            camera,
            detections,
            frame_width=100,
            frame_height=100,
        )

        self.assertEqual(filtered, detections)
        self.assertEqual(ignored, [])

    def test_detection_outside_ignore_zone_is_kept(self):
        camera = {
            "id": "test_cam",
            "ignore_zones": [
                {
                    "id": "static_object",
                    "label": "Static object",
                    "type": "polygon",
                    "enabled": True,
                    "points": [[0.0, 0.0], [0.5, 0.0], [0.5, 0.5], [0.0, 0.5]],
                }
            ],
        }
        detections = [
            {
                "class_name": "person",
                "confidence": 0.80,
                "box": {"x1": 70, "y1": 70, "x2": 90, "y2": 90},
            }
        ]

        filtered, ignored = detection.filter_detections_by_ignore_zones(
            camera,
            detections,
            frame_width=100,
            frame_height=100,
        )

        self.assertEqual(filtered, detections)
        self.assertEqual(ignored, [])

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
                lambda frame, detections, face_readiness=None, face_recognition=None, confidence_threshold=None: captured.update(
                    {"frame": frame, "detections": detections}
                ) or frame
            )

            _image, _readiness, _recognition, metadata = detection.build_person_evidence_from_detection(
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
        self.assertEqual(metadata["evidence_source"], "hd_redetect")
        self.assertEqual(metadata["person_detections"][0]["bbox"], {"x1": 500, "y1": 300, "x2": 900, "y2": 980})

    def test_high_resolution_evidence_uses_scaled_detection_boxes_when_redetect_fails(self):
        original_detection = {
            "person_detected": True,
            "detections": [
                {
                    "class_name": "person",
                    "confidence": 0.91,
                    "box": {"x1": 10, "y1": 20, "x2": 110, "y2": 220},
                },
                {
                    "class_name": "person",
                    "confidence": 0.84,
                    "box": {"x1": 200, "y1": 30, "x2": 300, "y2": 230},
                },
            ],
            "confidence_threshold": 0.60,
        }
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
            detection.detect_objects = lambda *_args, **_kwargs: []
            detection._crop_detection = lambda frame, _detection: frame
            detection.assess_face_readiness = lambda _image: {"face_readiness": "not_available"}
            detection._build_person_evidence_frame = (
                lambda frame, detections, face_readiness=None, face_recognition=None, confidence_threshold=None: captured.update(
                    {"frame": frame, "detections": detections}
                ) or frame
            )

            _image, _readiness, _recognition, metadata = detection.build_person_evidence_from_detection(
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

        self.assertEqual(captured["frame"].shape, (1080, 1920, 3))
        self.assertEqual(metadata["evidence_source"], "hd_scaled_bbox")
        self.assertEqual(metadata["detections_count"], 2)
        self.assertEqual(
            captured["detections"][0]["box"],
            {"x1": 30.0, "y1": 60.0, "x2": 330.0, "y2": 660.0},
        )
        self.assertEqual(metadata["person_detections"][0]["bbox"], captured["detections"][0]["box"])
        self.assertEqual(captured["detections"][0]["evidence_bbox_source"], "scaled_from_detection_frame")

    def test_high_resolution_evidence_falls_back_when_scaled_crop_is_invalid(self):
        original_detection = {
            "person_detected": True,
            "detections": [
                {
                    "class_name": "person",
                    "confidence": 0.91,
                    "box": {"x1": 110, "y1": 20, "x2": 10, "y2": 220},
                }
            ],
            "confidence_threshold": 0.60,
        }
        captured = {}

        original_capture = detection.capture_frame_for_camera_channel
        original_detect = detection.detect_objects
        original_build = detection._build_person_evidence_frame
        original_assess = detection.assess_face_readiness

        try:
            detection.capture_frame_for_camera_channel = (
                lambda _camera, _channel: _Frame(width=1920, height=1080)
            )
            detection.detect_objects = lambda *_args, **_kwargs: []
            detection.assess_face_readiness = lambda _image: {"face_readiness": "not_available"}
            detection._build_person_evidence_frame = (
                lambda frame, detections, face_readiness=None, face_recognition=None, confidence_threshold=None: captured.update(
                    {"frame": frame, "detections": detections}
                ) or frame
            )

            _image, _readiness, _recognition, metadata = detection.build_person_evidence_from_detection(
                _Frame(width=640, height=360),
                original_detection,
                camera={"id": "cam_1", "channel": "102"},
            )
        finally:
            detection.capture_frame_for_camera_channel = original_capture
            detection.detect_objects = original_detect
            detection._build_person_evidence_frame = original_build
            detection.assess_face_readiness = original_assess

        self.assertEqual(captured["frame"].shape, (360, 640, 3))
        self.assertEqual(metadata["evidence_source"], "detection_frame")
        self.assertEqual(metadata["person_detections"][0]["bbox"], {"x1": 110, "y1": 20, "x2": 10, "y2": 220})

    def test_person_crop_panel_shows_top_three_people_by_confidence(self):
        detections = [
            {
                "class_name": "person",
                "confidence": 0.71,
                "box": {"x1": 10, "y1": 10, "x2": 80, "y2": 180},
            },
            {
                "class_name": "person",
                "confidence": 0.93,
                "box": {"x1": 90, "y1": 10, "x2": 160, "y2": 180},
            },
            {
                "class_name": "person",
                "confidence": 0.84,
                "box": {"x1": 170, "y1": 10, "x2": 240, "y2": 180},
            },
            {
                "class_name": "person",
                "confidence": 0.66,
                "box": {"x1": 250, "y1": 10, "x2": 320, "y2": 180},
            },
        ]
        labels = []

        original_copy_make_border = getattr(detection.cv2, "copyMakeBorder", None)
        original_put_text = getattr(detection.cv2, "putText", None)
        original_line = getattr(detection.cv2, "line", None)
        original_crop = detection._crop_detection
        original_resize = detection._resize_into_panel

        try:
            detection.cv2.BORDER_CONSTANT = 0
            detection.cv2.copyMakeBorder = lambda *_args, **_kwargs: _Frame(width=320, height=360)
            detection.cv2.putText = lambda _panel, text, *_args, **_kwargs: labels.append(text)
            detection.cv2.line = lambda *_args, **_kwargs: None
            detection._crop_detection = lambda _frame, _detection: _Frame(width=60, height=120)
            detection._resize_into_panel = lambda _image, _width, panel_height: _Frame(
                width=60,
                height=panel_height,
            )

            panel = detection._build_person_crops_panel(
                _Frame(width=640, height=360),
                detections,
                confidence_threshold=0.60,
            )
        finally:
            if original_copy_make_border is None:
                delattr(detection.cv2, "copyMakeBorder")
            else:
                detection.cv2.copyMakeBorder = original_copy_make_border
            if original_put_text is None:
                delattr(detection.cv2, "putText")
            else:
                detection.cv2.putText = original_put_text
            if original_line is None:
                delattr(detection.cv2, "line")
            else:
                detection.cv2.line = original_line
            detection._crop_detection = original_crop
            detection._resize_into_panel = original_resize

        self.assertEqual(panel.shape, (360, 320, 3))
        self.assertIn("PERSON 1", labels)
        self.assertIn("PERSON 2", labels)
        self.assertIn("PERSON 3", labels)
        self.assertNotIn("PERSON 4", labels)
        self.assertIn("CONF 0.93 / THR 0.60", labels)
        self.assertIn("CONF 0.84 / THR 0.60", labels)
        self.assertIn("CONF 0.71 / THR 0.60", labels)
        self.assertNotIn("CONF 0.66 / THR 0.60", labels)

    def test_two_person_detection_input_produces_matching_evidence_metadata(self):
        detections = [
            {
                "class_name": "person",
                "confidence": 0.71,
                "box": {"x1": 10, "y1": 10, "x2": 80, "y2": 180},
            },
            {
                "class_name": "person",
                "confidence": 0.93,
                "box": {"x1": 90, "y1": 10, "x2": 160, "y2": 180},
            },
        ]

        targets = detection.evidence_person_targets(detections)

        self.assertEqual(len(targets), 2)
        self.assertEqual(targets[0]["metadata"]["crop_rank"], 1)
        self.assertEqual(targets[0]["metadata"]["confidence"], 0.93)
        self.assertEqual(targets[0]["metadata"]["bbox"], {"x1": 90, "y1": 10, "x2": 160, "y2": 180})
        self.assertEqual(targets[1]["metadata"]["crop_rank"], 2)
        self.assertEqual(targets[1]["metadata"]["confidence"], 0.71)

    def test_single_person_detection_input_produces_one_evidence_target(self):
        detections = [
            {
                "class_name": "person",
                "confidence": 0.88,
                "box": {"x1": 10, "y1": 10, "x2": 80, "y2": 180},
            }
        ]

        targets = detection.evidence_person_targets(detections)

        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]["metadata"]["crop_rank"], 1)
        self.assertEqual(targets[0]["metadata"]["confidence"], 0.88)

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
