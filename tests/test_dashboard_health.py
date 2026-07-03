import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.dashboard_health import build_dashboard_health


class DashboardHealthTests(unittest.TestCase):
    def test_builds_camera_health_from_config_and_events(self):
        cameras = [
            {
                "id": "cam_active",
                "name": "Active Camera",
                "enabled": True,
                "notes": "Working camera.",
            },
            {
                "id": "cam_new",
                "name": "New Camera",
                "enabled": True,
                "notes": "No checks yet.",
            },
            {
                "id": "block_f_cam_8",
                "name": "ITU BLOCK F CAM8",
                "enabled": False,
                "notes": "Ping and RTSP port 554 not reachable.",
            },
        ]
        events = [
            {
                "timestamp": "2026-07-03T01:00:00+00:00",
                "event_type": "no_person",
                "person_detected": False,
                "camera": {"id": "cam_active"},
            },
            {
                "timestamp": "2026-07-03T01:05:00+00:00",
                "event_type": "person_detected",
                "person_detected": True,
                "camera": {"id": "cam_active"},
            },
        ]

        health = build_dashboard_health(cameras, events)

        self.assertEqual(health["status"], "ok")
        self.assertEqual(health["cameras"]["total"], 3)
        self.assertEqual(health["cameras"]["enabled"], 2)
        self.assertEqual(health["cameras"]["disabled"], 1)
        self.assertEqual(health["events"]["total_events"], 2)
        self.assertEqual(health["events"]["latest_event_time"], "2026-07-03T01:05:00+00:00")
        self.assertEqual(health["events"]["latest_event_camera_id"], "cam_active")
        self.assertEqual(health["events"]["latest_person_event_time"], "2026-07-03T01:05:00+00:00")

        per_camera = {
            camera["camera_id"]: camera
            for camera in health["per_camera"]
        }

        self.assertEqual(per_camera["cam_active"]["health_status"], "active")
        self.assertEqual(per_camera["cam_active"]["total_events"], 2)
        self.assertEqual(per_camera["cam_active"]["person_events"], 1)
        self.assertEqual(per_camera["cam_active"]["last_event_time"], "2026-07-03T01:05:00+00:00")
        self.assertEqual(per_camera["cam_active"]["last_person_event_time"], "2026-07-03T01:05:00+00:00")

        self.assertEqual(per_camera["cam_new"]["health_status"], "no_recent_event")
        self.assertIsNone(per_camera["cam_new"]["last_event_time"])

        self.assertEqual(per_camera["block_f_cam_8"]["health_status"], "disabled")
        self.assertFalse(per_camera["block_f_cam_8"]["enabled"])
        self.assertIn("not reachable", per_camera["block_f_cam_8"]["notes"])
        self.assertEqual(
            health["cameras"]["disabled_cameras"][0]["camera_id"],
            "block_f_cam_8",
        )


if __name__ == "__main__":
    unittest.main()
