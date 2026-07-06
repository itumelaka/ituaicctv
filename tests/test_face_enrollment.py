import csv
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

import numpy as np


BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app import face_enrollment

try:
    from app.routes import face_enrollment as face_enrollment_route
except ModuleNotFoundError as error:
    if error.name != "fastapi":
        raise

    fake_fastapi = types.ModuleType("fastapi")

    class FakeAPIRouter:
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *args, **kwargs):
            return lambda function: function

        def post(self, *args, **kwargs):
            return lambda function: function

    class FakeHTTPException(Exception):
        def __init__(self, status_code, detail):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    fake_fastapi.APIRouter = FakeAPIRouter
    fake_fastapi.HTTPException = FakeHTTPException
    sys.modules["fastapi"] = fake_fastapi
    from app.routes import face_enrollment as face_enrollment_route


class FaceEnrollmentTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name)
        self.original_embeddings_dir = face_enrollment.settings.face_embeddings_dir
        self.original_factory = face_enrollment._lbph_factory
        self.original_load_image = face_enrollment._load_image
        self.original_assess = face_enrollment.assess_face_readiness
        self.original_prepare = face_enrollment._prepare_lbph_face
        self.original_assignments_path = face_enrollment.IDENTITY_ASSIGNMENTS_PATH
        face_enrollment.settings.face_embeddings_dir = str(self.base / "embeddings")
        face_enrollment.IDENTITY_ASSIGNMENTS_PATH = (
            self.base
            / "face-enrollment"
            / "identity-assignments"
            / "identity_assignments.json"
        )

    def tearDown(self):
        face_enrollment.settings.face_embeddings_dir = self.original_embeddings_dir
        face_enrollment._lbph_factory = self.original_factory
        face_enrollment._load_image = self.original_load_image
        face_enrollment.assess_face_readiness = self.original_assess
        face_enrollment._prepare_lbph_face = self.original_prepare
        face_enrollment.IDENTITY_ASSIGNMENTS_PATH = self.original_assignments_path
        self.temp_dir.cleanup()

    def test_csv_template_has_privacy_placeholder(self):
        output_path = self.base / "template.csv"

        result = face_enrollment.write_csv_template(output_path)

        self.assertEqual(result["status"], "ok")
        with output_path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["label"], "APPROVED_LABEL")
        self.assertIn("Do not commit", rows[0]["notes"])

    def test_generate_draft_csv_defaults_to_not_approved(self):
        source = self.base / "references" / "Person One"
        source.mkdir(parents=True)
        image_path = source / "sample.jpg"
        image_path.write_bytes(b"not a real image")
        output_path = self.base / "draft.csv"

        result = face_enrollment.generate_draft_csv(self.base / "references", output_path)

        self.assertEqual(result["rows"], 1)
        with output_path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["label"], "PERSON_ONE")
        self.assertEqual(rows[0]["approved_for_face_recognition"], "no")

    def test_batch_enrollment_rejects_unapproved_rows(self):
        class FakeRecognizer:
            def train(self, _faces, _labels):
                raise AssertionError("LBPH should not train unapproved rows")

        image_path = self.base / "person.jpg"
        image_path.write_bytes(b"placeholder")
        csv_path = self.base / "enroll.csv"
        report_path = self.base / "rejects.json"
        face_enrollment.write_csv(
            csv_path,
            [
                {
                    "label": "Person One",
                    "image_path": str(image_path),
                    "approved_for_face_recognition": "no",
                }
            ],
        )

        face_enrollment._lbph_factory = lambda: FakeRecognizer
        result = face_enrollment.enroll_lbph_from_csv(csv_path, report_path)

        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["rejected"][0]["reason"], "not_approved_for_face_recognition")

    def test_batch_enrollment_writes_model_labels_and_reject_report(self):
        class FakeRecognizer:
            def train(self, faces, labels):
                self.faces = faces
                self.labels = labels

            def write(self, path):
                Path(path).write_text("model", encoding="utf-8")

        image_path = self.base / "person.jpg"
        image_path.write_bytes(b"placeholder")
        missing_path = self.base / "missing.jpg"
        csv_path = self.base / "enroll.csv"
        report_path = self.base / "rejects.json"
        face_enrollment.write_csv(
            csv_path,
            [
                {
                    "label": "Person One",
                    "identity_id": "local-001",
                    "display_name": "Person One",
                    "image_path": str(image_path),
                    "approved_for_face_recognition": "yes",
                    "consent_reference": "policy-001",
                },
                {
                    "label": "Person Two",
                    "image_path": str(missing_path),
                    "approved_for_face_recognition": "yes",
                },
            ],
        )
        labels_path = Path(face_enrollment.settings.face_embeddings_dir) / face_enrollment.LBPH_LABELS_FILENAME
        labels_path.parent.mkdir(parents=True)
        labels_path.write_text(
            json.dumps(
                {
                    "backend": "opencv_lbph",
                    "labels": {"5": "EXISTING_PERSON"},
                    "identities": {"EXISTING_PERSON": {"identity_id": "existing-001"}},
                }
            ),
            encoding="utf-8",
        )
        face_enrollment._lbph_factory = lambda: FakeRecognizer
        face_enrollment._load_image = lambda _path: np.zeros((20, 20, 3), dtype=np.uint8)
        face_enrollment.assess_face_readiness = lambda _image: {
            "face_readiness": "suitable",
            "best_face_box": {"x": 0, "y": 0, "width": 10, "height": 10},
        }
        face_enrollment._prepare_lbph_face = lambda _crop: object()

        result = face_enrollment.enroll_lbph_from_csv(csv_path, report_path)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["accepted_count"], 1)
        self.assertEqual(result["rejected_count"], 1)
        labels = json.loads(labels_path.read_text(encoding="utf-8"))
        self.assertEqual(labels["labels"]["5"], "EXISTING_PERSON")
        self.assertEqual(labels["labels"]["6"], "PERSON_ONE")
        self.assertEqual(labels["identities"]["EXISTING_PERSON"]["identity_id"], "existing-001")
        self.assertEqual(labels["identities"]["PERSON_ONE"]["identity_id"], "local-001")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["rejected"][0]["reason"], "image_path_not_found")

    def test_identity_assignment_sanitizes_label(self):
        assignment = face_enrollment.validate_identity_assignment(
            {
                "label": "Person One!",
                "identity_id": "local-001",
                "approved_for_face_recognition": "yes",
            }
        )

        self.assertEqual(assignment["label"], "PERSON_ONE")
        self.assertTrue(assignment["approved_for_face_recognition"])

    def test_dashboard_identity_assignment_payload_is_accepted(self):
        assignment = face_enrollment.validate_identity_assignment(
            {
                "event_id": "person_detected_cam_1.jpg",
                "review_id": "person_detected_cam_1.jpg",
                "evidence_filename": "person_detected_cam_1.jpg",
                "assigned_label": "Person Two",
                "assigned_display_name": "Person Two",
                "assigned_by": "operator",
                "note": "Reviewed from dashboard.",
                "approved_for_training": True,
                "person_rank": "2",
                "person_confidence": "0.84",
                "person_bbox": {"x1": 140, "y1": 25, "x2": 230, "y2": 210},
                "person_target_label": "PERSON 2",
            }
        )

        self.assertEqual(assignment["label"], "PERSON_TWO")
        self.assertEqual(assignment["assigned_label"], "PERSON_TWO")
        self.assertEqual(assignment["assigned_display_name"], "Person Two")
        self.assertEqual(assignment["assigned_by"], "operator")
        self.assertEqual(assignment["event_id"], "person_detected_cam_1.jpg")
        self.assertEqual(assignment["review_id"], "person_detected_cam_1.jpg")
        self.assertEqual(assignment["evidence_filename"], "person_detected_cam_1.jpg")
        self.assertEqual(assignment["person_rank"], 2)
        self.assertEqual(assignment["person_confidence"], 0.84)
        self.assertEqual(assignment["person_bbox"], {"x1": 140, "y1": 25, "x2": 230, "y2": 210})
        self.assertEqual(assignment["person_target_label"], "PERSON 2")
        self.assertTrue(assignment["approved_for_training"])
        self.assertEqual(assignment["note"], "Reviewed from dashboard.")

    def test_legacy_identity_assignment_payload_still_works_without_person_target(self):
        assignment = face_enrollment.validate_identity_assignment(
            {
                "label": "Legacy Person",
                "display_name": "Legacy Person",
                "approved_for_face_recognition": "yes",
            }
        )

        self.assertEqual(assignment["label"], "LEGACY_PERSON")
        self.assertIsNone(assignment["person_rank"])
        self.assertIsNone(assignment["person_confidence"])
        self.assertIsNone(assignment["person_bbox"])
        self.assertEqual(assignment["person_target_label"], "")

    def test_identity_assignment_post_creates_storage_file_and_parent_directory(self):
        storage_path = face_enrollment.IDENTITY_ASSIGNMENTS_PATH
        self.assertFalse(storage_path.parent.exists())

        response = face_enrollment_route.face_identity_assignment(
            {
                "event_id": "event-001",
                "evidence_filename": "event-001.jpg",
                "assigned_label": "Person One",
                "assigned_display_name": "Person One",
                "assigned_by": "operator",
                "note": "Approved from dashboard.",
                "approved_for_training": True,
            }
        )

        self.assertEqual(response["status"], "ok")
        self.assertTrue(storage_path.exists())
        stored = json.loads(storage_path.read_text(encoding="utf-8"))
        self.assertEqual(len(stored["assignments"]), 1)
        self.assertEqual(stored["assignments"][0]["assigned_label"], "PERSON_ONE")
        self.assertEqual(stored["assignments"][0]["note"], "Approved from dashboard.")
        self.assertTrue(stored["assignments"][0]["approved_for_training"])
        self.assertIn("created_at", stored["assignments"][0])
        self.assertIn("updated_at", stored["assignments"][0])

    def test_identity_assignment_storage_path_is_backend_anchored(self):
        expected_path = (
            BACKEND_PATH
            / "data"
            / "face-enrollment"
            / "identity-assignments"
            / "identity_assignments.json"
        )

        self.assertTrue(self.original_assignments_path.is_absolute())
        self.assertEqual(self.original_assignments_path, expected_path)

    def test_identity_assignment_save_uses_configured_path_when_cwd_is_backend(self):
        storage_path = self.base / "runtime" / "identity_assignments.json"
        face_enrollment.IDENTITY_ASSIGNMENTS_PATH = storage_path
        original_cwd = Path.cwd()

        try:
            os.chdir(BACKEND_PATH)
            face_enrollment.save_identity_assignment(
                {
                    "event_id": "event-from-backend-cwd",
                    "evidence_filename": "event-from-backend-cwd.jpg",
                    "assigned_label": "Backend Cwd Person",
                }
            )
        finally:
            os.chdir(original_cwd)

        self.assertTrue(storage_path.exists())
        self.assertFalse((BACKEND_PATH / "runtime" / "identity_assignments.json").exists())

    def test_identity_assignment_post_preserves_person_specific_fields(self):
        response = face_enrollment_route.face_identity_assignment(
            {
                "event_id": "event-002",
                "review_id": "event-002",
                "evidence_filename": "event-002.jpg",
                "assigned_label": "Person Two",
                "assigned_display_name": "Person Two",
                "assigned_by": "operator",
                "person_rank": 2,
                "person_confidence": 0.84,
                "person_bbox": {"x1": 140, "y1": 25, "x2": 230, "y2": 210},
                "person_target_label": "PERSON 2",
            }
        )

        assignment = response["assignment"]
        self.assertEqual(assignment["person_rank"], 2)
        self.assertEqual(assignment["person_confidence"], 0.84)
        self.assertEqual(assignment["person_bbox"], {"x1": 140, "y1": 25, "x2": 230, "y2": 210})
        self.assertEqual(assignment["person_target_label"], "PERSON 2")

        stored = json.loads(face_enrollment.IDENTITY_ASSIGNMENTS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(stored["assignments"][0]["person_rank"], 2)
        self.assertEqual(stored["assignments"][0]["person_target_label"], "PERSON 2")

    def test_identity_assignment_post_upserts_same_event_person_target(self):
        first = face_enrollment_route.face_identity_assignment(
            {
                "event_id": "event-003",
                "evidence_filename": "event-003.jpg",
                "assigned_label": "Person Two",
                "person_rank": 2,
                "person_target_label": "PERSON 2",
                "note": "First review.",
            }
        )["assignment"]

        second = face_enrollment_route.face_identity_assignment(
            {
                "event_id": "event-003",
                "evidence_filename": "event-003.jpg",
                "assigned_label": "Person Two Updated",
                "person_rank": 2,
                "person_target_label": "PERSON 2",
                "note": "Updated review.",
            }
        )["assignment"]

        stored = json.loads(face_enrollment.IDENTITY_ASSIGNMENTS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(stored["assignments"]), 1)
        self.assertEqual(stored["assignments"][0]["assigned_label"], "PERSON_TWO_UPDATED")
        self.assertEqual(stored["assignments"][0]["note"], "Updated review.")
        self.assertEqual(stored["assignments"][0]["created_at"], first["created_at"])
        self.assertEqual(second["created_at"], first["created_at"])

    def test_identity_assignments_get_returns_saved_assignments(self):
        face_enrollment_route.face_identity_assignment(
            {
                "event_id": "event-004",
                "evidence_filename": "event-004.jpg",
                "assigned_label": "Person Four",
            }
        )

        response = face_enrollment_route.face_identity_assignments()

        self.assertEqual(response["status"], "ok")
        self.assertTrue(response["local_only"])
        self.assertEqual(len(response["assignments"]), 1)
        self.assertEqual(response["assignments"][0]["assigned_label"], "PERSON_FOUR")


if __name__ == "__main__":
    unittest.main()
