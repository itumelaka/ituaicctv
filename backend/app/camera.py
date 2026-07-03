import os
import time
import cv2
from app.config import settings
from app.camera_registry import build_rtsp_url, build_masked_rtsp_url

def _open_rtsp_stream(rtsp_url: str):
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def _read_frame_with_retry(cap, max_attempts: int = 30):
    for _ in range(max_attempts):
        ok, frame = cap.read()

        if ok and frame is not None:
            return frame

        time.sleep(0.1)

    return None


def capture_frame_from_rtsp(rtsp_url: str):
    if not rtsp_url:
        raise RuntimeError("RTSP URL is empty.")

    cap = _open_rtsp_stream(rtsp_url)

    if not cap.isOpened():
        cap.release()
        raise RuntimeError("Cannot open RTSP stream.")

    frame = _read_frame_with_retry(cap)
    cap.release()

    if frame is None:
        raise RuntimeError("RTSP stream opened but cannot read frame after retries.")

    return frame


def capture_frame():
    if not settings.cctv_host or not settings.cctv_username or not settings.cctv_password:
        raise RuntimeError("CCTV configuration is incomplete. Check backend/.env.")

    return capture_frame_from_rtsp(settings.rtsp_url)


def capture_frame_for_camera(camera: dict):
    if not settings.cctv_username or not settings.cctv_password:
        raise RuntimeError("CCTV username/password is incomplete. Check backend/.env.")

    rtsp_url = build_rtsp_url(camera)
    return capture_frame_from_rtsp(rtsp_url)


def test_camera_connection(camera: dict) -> dict:
    try:
        frame = capture_frame_for_camera(camera)
    except RuntimeError as error:
        return {
            "status": "failed",
            "message": str(error),
            "camera_id": camera.get("id"),
            "camera_name": camera.get("name"),
            "camera_host": camera.get("host"),
            "channel": camera.get("channel"),
            "rtsp_url": build_masked_rtsp_url(camera)
        }

    height, width = frame.shape[:2]

    return {
        "status": "connected",
        "message": "RTSP stream is reachable.",
        "camera_id": camera.get("id"),
        "camera_name": camera.get("name"),
        "camera_host": camera.get("host"),
        "channel": camera.get("channel"),
        "frame_width": width,
        "frame_height": height,
        "rtsp_url": build_masked_rtsp_url(camera)
    }


def test_rtsp_connection() -> dict:
    try:
        frame = capture_frame()
    except RuntimeError as error:
        return {
            "status": "failed",
            "message": str(error),
            "camera_host": settings.cctv_host,
            "channel": settings.cctv_channel,
            "rtsp_url": settings.masked_rtsp_url
        }

    height, width = frame.shape[:2]

    return {
        "status": "connected",
        "message": "RTSP stream is reachable.",
        "camera_host": settings.cctv_host,
        "channel": settings.cctv_channel,
        "frame_width": width,
        "frame_height": height,
        "rtsp_url": settings.masked_rtsp_url
    }


def capture_snapshot_jpeg() -> bytes:
    frame = capture_frame()

    success, buffer = cv2.imencode(".jpg", frame)

    if not success:
        raise RuntimeError("Failed to encode CCTV frame as JPEG.")

    return buffer.tobytes()
