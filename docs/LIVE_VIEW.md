# ITU AI CCTV - Live View

The dashboard live view is a backend MJPEG proxy for one selected camera at a time. It is for viewing only and does not run YOLO, save evidence, write event logs, send Telegram alerts, change event review, change ignore zones, or affect the live monitor loop.

## Endpoints

```text
GET /dashboard/live/{camera_id}/stream.mjpg?quality=standard
GET /dashboard/live/{camera_id}/stream.mjpg?quality=hd
GET /dashboard/live/{camera_id}/snapshot.jpg?quality=standard
GET /dashboard/live/{camera_id}/snapshot.jpg?quality=hd
```

Missing `quality` defaults to `standard`.

Invalid `quality` values return HTTP 400.

## Quality Modes

- `standard`: uses the configured camera channel, usually Hikvision sub-stream `102`.
- `hd`: uses Hikvision channel `101`.

HD snapshot can preserve full source resolution where the camera provides it. A production test on `block_f_cam_7` confirmed an HD snapshot at 3200x1800. Actual resolution still depends on the camera main-stream settings and may be lower.

MJPEG live stream output is capped for browser performance. HD allows a larger max width than Standard, but it is still intended for one selected camera/viewer, not all cameras at once.

## Audio

MJPEG has no audio. Some Hikvision cameras may have microphone/audio streams, but dashboard audio is not implemented.

Future audio requires a different media path such as HLS, WebRTC, or an FFmpeg-backed proxy.

## Security

Browsers never receive RTSP URLs, CCTV usernames, or CCTV passwords. The backend opens RTSP and serves MJPEG frames to the dashboard.
