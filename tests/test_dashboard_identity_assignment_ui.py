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
        self.assertIn("personTargetsFromEvent(event)", dashboard_ui)
        self.assertIn("person_rank", dashboard_ui)
        self.assertIn("person_confidence", dashboard_ui)
        self.assertIn("person_bbox", dashboard_ui)
        self.assertIn("person_target_label", dashboard_ui)
        self.assertIn("identity_person_target", dashboard_ui)
        self.assertIn("event?.person_detections", dashboard_ui)
        self.assertIn("PERSON ${rank}", dashboard_ui)
        self.assertIn("targetCount > 1", dashboard_ui)
        self.assertNotIn("batch-enroll", dashboard_ui)
        self.assertNotIn("enroll_lbph_from_csv", dashboard_ui)

    def test_tv_dashboard_contains_webrtc_smooth_mjpeg_fallback_and_hd_snapshot_controls(self):
        dashboard_ui = DASHBOARD_UI_PATH.read_text(encoding="utf-8")

        self.assertIn('let selectedLiveMode = "webrtc"', dashboard_ui)
        self.assertIn('let selectedLiveQuality = "standard"', dashboard_ui)
        self.assertIn('id="modeWebrtcButton"', dashboard_ui)
        self.assertIn('id="modeMjpegButton"', dashboard_ui)
        self.assertIn("WebRTC Smooth", dashboard_ui)
        self.assertIn("MJPEG Fallback", dashboard_ui)
        self.assertIn("mediamtxWebrtcUrl(camera.camera_id)", dashboard_ui)
        self.assertIn("window.location.hostname", dashboard_ui)
        self.assertIn(":8889", dashboard_ui)
        self.assertIn('id="qualitySmoothButton"', dashboard_ui)
        self.assertIn('id="qualityHdButton"', dashboard_ui)
        self.assertIn("Smooth Live", dashboard_ui)
        self.assertIn("HD Live", dashboard_ui)
        self.assertIn('id="snapshotButton"', dashboard_ui)
        self.assertIn('id="fullscreenLiveButton"', dashboard_ui)
        self.assertIn("Reconnecting", dashboard_ui)
        self.assertIn("snapshot.jpg?quality=hd", dashboard_ui)
        self.assertIn("Snapshot: HD", dashboard_ui)
        self.assertIn("Evidence/Crops: HD when available", dashboard_ui)
        self.assertIn("selected camera only", dashboard_ui)
        self.assertNotIn("13-camera", dashboard_ui)
        self.assertNotIn("rtsp" + "://", dashboard_ui)
        self.assertNotIn("CCTV" + "_PASSWORD", dashboard_ui)
        self.assertNotIn("TELEGRAM" + "_BOT_TOKEN", dashboard_ui)
        self.assertNotIn("http://192.168.1.254:8889", dashboard_ui)

    def test_tv_dashboard_mode_badge_and_hd_tags(self):
        dashboard_ui = DASHBOARD_UI_PATH.read_text(encoding="utf-8")

        self.assertIn('id="liveModeBadge"', dashboard_ui)
        self.assertIn('id="liveCameraIdentity"', dashboard_ui)
        self.assertIn("function updateModeBadge(camera)", dashboard_ui)
        self.assertIn("WebRTC smooth", dashboard_ui)
        self.assertIn("MJPEG fallback", dashboard_ui)
        self.assertIn("Snapshot (HD)", dashboard_ui)
        self.assertIn("Latest AI Evidence", dashboard_ui)

    def test_tv_dashboard_shows_disabled_camera_in_selector_not_hidden(self):
        dashboard_ui = DASHBOARD_UI_PATH.read_text(encoding="utf-8")

        # The dropdown must always be built from the full camera list, not a
        # selectable-only subset, so disabled/offline cameras (eg block_f_cam_8)
        # still appear as a visibly disabled option instead of being dropped.
        self.assertNotIn(
            "const dropdownCameras = selectableCameras.length ? selectableCameras : cameras;",
            dashboard_ui,
        )
        self.assertIn("cameras.forEach((camera) => {", dashboard_ui)
        self.assertIn("- disabled/offline`", dashboard_ui)
        self.assertIn("option.disabled = !selectable;", dashboard_ui)

    def test_tv_dashboard_degrades_gracefully_with_zero_selectable_cameras(self):
        dashboard_ui = DASHBOARD_UI_PATH.read_text(encoding="utf-8")

        self.assertIn("const anySelectable = cameras.some((camera) => cameraIsSelectable(camera));", dashboard_ui)
        self.assertIn("No camera available (all disabled/offline)", dashboard_ui)
        self.assertIn("No cameras configured", dashboard_ui)
        self.assertIn("selector.disabled = true;", dashboard_ui)

    def test_tv_dashboard_makmal_cam_13_hint(self):
        dashboard_ui = DASHBOARD_UI_PATH.read_text(encoding="utf-8")

        self.assertIn('id="makmalHint"', dashboard_ui)
        self.assertIn("makmal_cam_13", dashboard_ui)
        self.assertIn("may need MJPEG Fallback", dashboard_ui)
        self.assertIn('camera.camera_id === "makmal_cam_13"', dashboard_ui)
        self.assertIn("TODO: remove this hint once makmal_cam_13", dashboard_ui)

    def test_tv_dashboard_webrtc_fallback_banner(self):
        dashboard_ui = DASHBOARD_UI_PATH.read_text(encoding="utf-8")

        self.assertIn('id="webrtcFallbackBanner"', dashboard_ui)
        self.assertIn('id="webrtcFallbackSwitchButton"', dashboard_ui)
        self.assertIn('id="webrtcFallbackDismissButton"', dashboard_ui)
        self.assertIn("Smooth live unavailable for this camera. Switch to MJPEG fallback.", dashboard_ui)
        self.assertIn("function hideWebrtcFallbackBanner()", dashboard_ui)
        self.assertIn("}, 9000);", dashboard_ui)
        self.assertNotIn("rtsp" + "://", dashboard_ui)

    def test_tv_dashboard_footer_hint(self):
        dashboard_ui = DASHBOARD_UI_PATH.read_text(encoding="utf-8")

        self.assertIn("Smooth live via MediaMTX (port 8889)", dashboard_ui)


if __name__ == "__main__":
    unittest.main()
