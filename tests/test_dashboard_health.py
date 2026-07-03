import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.dashboard_health import build_dashboard_health, parse_scheduler_log_summary


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
                "id": "cam_stale",
                "name": "Stale Camera",
                "enabled": True,
                "notes": "Old check.",
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
                "status": "offline",
                "health_note": "Ping and RTSP port 554 are not reachable.",
                "notes": "Ping and RTSP port 554 not reachable.",
            },
        ]
        events = [
            {
                "timestamp": "2026-07-02T22:00:00+00:00",
                "event_type": "no_person",
                "person_detected": False,
                "camera": {"id": "cam_stale"},
            },
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

        health = build_dashboard_health(
            cameras,
            events,
            stale_threshold_minutes=120,
            now=datetime(2026, 7, 3, 1, 30, tzinfo=timezone.utc),
        )

        self.assertEqual(health["status"], "ok")
        self.assertEqual(health["cameras"]["total"], 4)
        self.assertEqual(health["cameras"]["enabled"], 3)
        self.assertEqual(health["cameras"]["disabled"], 1)
        self.assertEqual(health["events"]["total_events"], 3)
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
        self.assertEqual(per_camera["cam_active"]["stale_minutes"], 25)
        self.assertEqual(per_camera["cam_active"]["stale_threshold_minutes"], 120)
        self.assertEqual(per_camera["cam_active"]["last_seen_source"], "events_jsonl")
        self.assertEqual(per_camera["cam_active"]["last_person_event_time"], "2026-07-03T01:05:00+00:00")

        self.assertEqual(per_camera["cam_stale"]["health_status"], "stale")
        self.assertEqual(per_camera["cam_stale"]["stale_minutes"], 210)
        self.assertEqual(per_camera["cam_stale"]["stale_threshold_minutes"], 120)
        self.assertEqual(per_camera["cam_stale"]["last_seen_source"], "events_jsonl")

        self.assertEqual(per_camera["cam_new"]["health_status"], "no_recent_event")
        self.assertIsNone(per_camera["cam_new"]["last_event_time"])
        self.assertIsNone(per_camera["cam_new"]["stale_minutes"])
        self.assertEqual(per_camera["cam_new"]["stale_threshold_minutes"], 120)
        self.assertIsNone(per_camera["cam_new"]["last_seen_source"])

        self.assertEqual(per_camera["block_f_cam_8"]["health_status"], "offline")
        self.assertEqual(per_camera["block_f_cam_8"]["status"], "offline")
        self.assertIn("RTSP port 554", per_camera["block_f_cam_8"]["health_note"])
        self.assertFalse(per_camera["block_f_cam_8"]["enabled"])
        self.assertIn("not reachable", per_camera["block_f_cam_8"]["notes"])
        self.assertEqual(
            health["cameras"]["disabled_cameras"][0]["camera_id"],
            "block_f_cam_8",
        )
        self.assertEqual(
            health["cameras"]["disabled_cameras"][0]["status"],
            "offline",
        )
        self.assertEqual(
            health["cameras"]["disabled_cameras"][0]["health_status"],
            "offline",
        )
        self.assertIn(
            "RTSP port 554",
            health["cameras"]["disabled_cameras"][0]["health_note"],
        )
        self.assertIn("scheduler", health)
        self.assertIn("recent_lines", health["scheduler"])

    def test_parses_scheduler_log_summary(self):
        log_text = """Run started: Fri 03/07/2026 10:35:34.23
ITU AI CCTV - Multi-Camera Person Monitor
==================================================
Status              : ok
Mode                : check_all
Enabled cameras     : 9
Attention required  : 0
No action           : 9
Failed              : 0

Compact JSON:
{
  "status": "ok",
  "mode": "check_all",
  "enabled_cameras_count": 9,
  "attention_required_count": 0,
  "no_action_count": 9,
  "failed_count": 0
}
Exit code: 0
Run ended: Fri 03/07/2026 10:35:52.27
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "monitor_person_all.log"
            log_path.write_text(log_text, encoding="utf-8")

            scheduler = parse_scheduler_log_summary(log_path=log_path)

        self.assertEqual(scheduler["status"], "ok")
        self.assertEqual(scheduler["latest_run_time"], "Fri 03/07/2026 10:35:34.23")
        self.assertEqual(scheduler["failed_count"], 0)
        self.assertEqual(scheduler["person_detected_count"], 0)
        self.assertEqual(scheduler["no_person_count"], 9)
        self.assertEqual(scheduler["log_path"], "data/task-logs/monitor_person_all.log")
        self.assertIn("status=ok", scheduler["latest_summary"])
        self.assertIn("failed=0", scheduler["latest_summary"])
        self.assertLessEqual(len(scheduler["recent_lines"]), 8)

    def test_missing_scheduler_log_returns_unknown_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "missing.log"
            scheduler = parse_scheduler_log_summary(log_path=log_path)

        self.assertEqual(scheduler["status"], "missing")
        self.assertIsNone(scheduler["latest_run_time"])
        self.assertIsNone(scheduler["latest_summary"])
        self.assertIsNone(scheduler["failed_count"])
        self.assertIsNone(scheduler["person_detected_count"])
        self.assertIsNone(scheduler["no_person_count"])
        self.assertEqual(scheduler["recent_lines"], [])


if __name__ == "__main__":
    unittest.main()
