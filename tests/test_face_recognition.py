import sys
import unittest
from pathlib import Path


BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app import face_recognition as recognition


class FaceRecognitionTests(unittest.TestCase):
    def setUp(self):
        self.original_enabled = recognition.settings.face_recognition_enabled
        self.original_threshold = recognition.settings.face_match_threshold
        self.original_library = recognition._embedding_library
        self.original_load_embeddings = recognition._load_embeddings

    def tearDown(self):
        recognition.settings.face_recognition_enabled = self.original_enabled
        recognition.settings.face_match_threshold = self.original_threshold
        recognition._embedding_library = self.original_library
        recognition._load_embeddings = self.original_load_embeddings

    def test_face_recognition_enabled_default_false(self):
        self.assertFalse(recognition.settings.face_recognition_enabled)

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
        self.assertTrue(result["recognition_attempted"])
        self.assertEqual(result["recognized_label"], "BURN")
        self.assertEqual(result["recognition_reason"], "matched")


if __name__ == "__main__":
    unittest.main()

