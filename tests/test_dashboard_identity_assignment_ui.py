import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DASHBOARD_UI_PATH = ROOT_DIR / "backend" / "app" / "routes" / "dashboard_ui.py"


class DashboardIdentityAssignmentUiTests(unittest.TestCase):
    def test_dashboard_ui_contains_identity_assignment_flow_without_training(self):
        dashboard_ui = DASHBOARD_UI_PATH.read_text(encoding="utf-8")

        self.assertIn("Assign Identity", dashboard_ui)
        self.assertIn("/faces/enrollment/identity-assignment", dashboard_ui)
        self.assertIn("assigned_label", dashboard_ui)
        self.assertIn("approved_for_training", dashboard_ui)
        self.assertIn("canAssignIdentity(event)", dashboard_ui)
        self.assertNotIn("batch-enroll", dashboard_ui)
        self.assertNotIn("enroll_lbph_from_csv", dashboard_ui)


if __name__ == "__main__":
    unittest.main()
