import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app import face_recognition as recognition


class FaceRecognitionTests(unittest.TestCase):
    def setUp(self):
        self.original_enabled = recognition.settings.face_recognition_enabled
        self.original_threshold = recognition.settings.face_match_threshold
        self.original_backend = recognition.settings.face_recognition_backend
        self.original_embeddings_dir = recognition.settings.face_embeddings_dir
        self.original_library = recognition._embedding_library
        self.original_load_embeddings = recognition._load_embeddings
        self.original_lbph_factory = recognition._lbph_factory
        self.original_prepare_lbph_face = recognition._prepare_lbph_face

    def tearDown(self):
        recognition.settings.face_recognition_enabled = self.original_enabled
        recognition.settings.face_match_threshold = self.original_threshold
        recognition.settings.face_recognition_backend = self.original_backend
        recognition.settings.face_embeddings_dir = self.original_embeddings_dir
        recognition._embedding_library = self.original_library
        recognition._load_embeddings = self.original_load_embeddings
        recognition._lbph_factory = self.original_lbph_factory
        recognition._prepare_lbph_face = self.original_prepare_lbph_face

    def test_face_recognition_enabled_default_false(self):
        self.assertFalse(recognition.settings.face_recognition_enabled)
        self.assertEqual(recognition.settings.face_recognition_backend, "auto")

    def test_enrollment_cli_accepts_backend_option(self):
        script_path = Path(__file__).resolve().parents[1] / "scripts" / "enroll_face.py"
        script = script_path.read_text(encoding="utf-8")

        self.assertIn('"--backend"', script)
        self.assertIn('"opencv_lbph"', script)
        self.assertIn('"face_recognition"', script)

    def test_recognition_metadata_disabled_when_flag_false(self):
        recognition.settings.face_recognition_enabled = False

        result = recognition.recognize_face(
            object(),
            {"face_readiness": "suitable"},
        )

        self.assertFalse(result["face_recognition_enabled"])
        self.assertFalse(result["recognition_attempted"])
        self.assertEqual(result["recognition_reason"], "disabled")

    def test_recognition_does_not_run_when_face_not_suitable(self):
        recognition.settings.face_recognition_enabled = True
        recognition.settings.face_recognition_backend = "auto"
        recognition._embedding_library = lambda: self.fail("embedding library should not load")

        result = recognition.recognize_face(
            object(),
            {"face_readiness": "not_suitable"},
        )

        self.assertTrue(result["face_recognition_enabled"])
        self.assertFalse(result["recognition_attempted"])
        self.assertEqual(result["recognition_reason"], "face_readiness_not_suitable")

    def test_recognition_can_return_internal_label_with_mock_matcher(self):
        class FakeLibrary:
            @staticmethod
            def face_encodings(_image):
                return [[0.1, 0.2, 0.3]]

        recognition.settings.face_recognition_enabled = True
        recognition.settings.face_recognition_backend = "face_recognition"
        recognition.settings.face_match_threshold = 0.60
        recognition._embedding_library = lambda: FakeLibrary
        recognition._load_embeddings = lambda: [
            {"label": "BURN", "embedding": [0.1, 0.2, 0.3]},
        ]

        result = recognition.recognize_face(
            object(),
            {"face_readiness": "suitable"},
        )

        self.assertTrue(result["face_recognition_enabled"])
        self.assertTrue(result["face_recognition_available"])
        self.assertEqual(result["face_recognition_backend"], "face_recognition")
        self.assertTrue(result["recognition_attempted"])
        self.assertEqual(result["recognized_label"], "BURN")
        self.assertEqual(result["recognition_reason"], "matched")

    def test_auto_backend_returns_unavailable_when_no_backend_exists(self):
        recognition.settings.face_recognition_enabled = True
        recognition.settings.face_recognition_backend = "auto"
        recognition._embedding_library = lambda: None
        recognition._lbph_factory = lambda: None

        result = recognition.recognize_face(
            object(),
            {"face_readiness": "suitable"},
        )

        self.assertFalse(result["face_recognition_available"])
        self.assertFalse(result["recognition_attempted"])
        self.assertEqual(result["recognition_reason"], "no_supported_backend")

    def test_opencv_lbph_backend_unavailable_when_cv2_face_missing(self):
        recognition.settings.face_recognition_enabled = True
        recognition.settings.face_recognition_backend = "opencv_lbph"
        recognition._lbph_factory = lambda: None

        result = recognition.recognize_face(
            object(),
            {"face_readiness": "suitable"},
        )

        self.assertFalse(result["face_recognition_available"])
        self.assertFalse(result["recognition_attempted"])
        self.assertEqual(result["face_recognition_backend"], "opencv_lbph")
        self.assertEqual(result["recognition_reason"], "opencv_lbph_unavailable")

    def test_mocked_opencv_lbph_recognizer_can_return_internal_label(self):
        class FakeRecognizer:
            def read(self, _path):
                pass

            def predict(self, _image):
                return 1, 20.0

        with tempfile.TemporaryDirectory() as temp_dir:
            embeddings_dir = Path(temp_dir)
            (embeddings_dir / recognition.LBPH_MODEL_FILENAME).write_text("model", encoding="utf-8")
            (embeddings_dir / recognition.LBPH_LABELS_FILENAME).write_text(
                '{"labels": {"1": "BURN"}}',
                encoding="utf-8",
            )

            recognition.settings.face_recognition_enabled = True
            recognition.settings.face_recognition_backend = "opencv_lbph"
            recognition.settings.face_match_threshold = 60.0
            recognition.settings.face_embeddings_dir = str(embeddings_dir)
            recognition._lbph_factory = lambda: FakeRecognizer
            recognition._prepare_lbph_face = lambda image: image

            result = recognition.recognize_face(
                object(),
                {"face_readiness": "suitable"},
            )

        self.assertTrue(result["face_recognition_available"])
        self.assertEqual(result["face_recognition_backend"], "opencv_lbph")
        self.assertTrue(result["recognition_attempted"])
        self.assertEqual(result["recognized_label"], "BURN")
        self.assertEqual(result["recognition_reason"], "matched")


if __name__ == "__main__":
    unittest.main()
