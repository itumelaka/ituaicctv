import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.live_view import (
    InvalidLiveViewQuality,
    live_view_channel_for_quality,
    live_view_max_width_for_quality,
    normalize_live_view_quality,
)


class DashboardLiveQualityTests(unittest.TestCase):
    def test_standard_quality_uses_configured_camera_channel(self):
        camera = {"id": "cam_1", "channel": "102"}

        channel = live_view_channel_for_quality("standard")

        self.assertIsNone(channel)
        self.assertEqual(camera["channel"], "102")

    def test_hd_quality_uses_main_stream_channel_without_mutating_camera(self):
        camera = {"id": "cam_1", "channel": "102"}

        channel = live_view_channel_for_quality("hd")

        self.assertEqual(channel, "101")
        self.assertEqual(camera["channel"], "102")

    def test_quality_is_case_and_whitespace_tolerant(self):
        self.assertEqual(normalize_live_view_quality(" HD "), "hd")
        self.assertEqual(live_view_channel_for_quality(" STANDARD "), None)

    def test_live_view_max_width_is_quality_aware(self):
        self.assertEqual(live_view_max_width_for_quality("standard"), 960)
        self.assertEqual(live_view_max_width_for_quality("hd"), 1920)

    def test_invalid_quality_is_rejected(self):
        with self.assertRaises(InvalidLiveViewQuality):
            live_view_channel_for_quality("ultra")


if __name__ == "__main__":
    unittest.main()
