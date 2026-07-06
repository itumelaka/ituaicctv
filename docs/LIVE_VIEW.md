# ITU AI CCTV - Live View

The dashboard live view is for one selected camera at a time. `/dashboard-tv` defaults to MediaMTX WebRTC Smooth mode for display and keeps the backend MJPEG proxy as fallback. It is for viewing only and does not run YOLO, save evidence, write event logs, send Telegram alerts, change event review, change identity assignment, change ignore zones, or affect the live monitor loop.

Assign Identity and multi-person targets come from saved event metadata, not from live-view pixels.

`/dashboard-tv` uses an iVMS-style single-camera live monitor layout. It keeps the camera dropdown/selection model and intentionally does not show a 13-camera simultaneous grid.

## Endpoints

```text
GET /dashboard/live/{camera_id}/stream.mjpg?quality=standard
GET /dashboard/live/{camera_id}/stream.mjpg?quality=hd
GET /dashboard/live/{camera_id}/snapshot.jpg?quality=standard
GET /dashboard/live/{camera_id}/snapshot.jpg?quality=hd
```

Missing `quality` defaults to `standard`.

Invalid `quality` values return HTTP 400.

The TV dashboard defaults its selected live stream to WebRTC Smooth. It also provides MJPEG Fallback with a Smooth Live / HD Live toggle. Changing camera, live mode, or fallback quality restarts the selected stream with a cache-busting query parameter or refreshed viewer URL and shows a reconnecting state.

## WebRTC Smooth Mode

The TV dashboard defaults to WebRTC Smooth mode through a local MediaMTX gateway on port `8889`. The browser URL is built from the current dashboard hostname:

```text
http://<dashboard-host>:8889/{camera_id}/
```

The MediaMTX path name should match the dashboard `camera_id`. RTSP source URLs and camera credentials remain server-side and are not exposed to the browser. If a selected camera path is not configured in MediaMTX yet, use MJPEG Fallback.

WebRTC quality is controlled by the MediaMTX/camera path for now. The Smooth Live / HD Live quality toggle applies only to MJPEG Fallback mode.

Production MediaMTX notes:

- Tested version: `v1.19.2`
- Windows service name: `MediaMTX`
- Display name: `MediaMTX WebRTC Gateway`
- Install folder: `C:\Tools\mediamtx`
- Config file: `C:\Tools\mediamtx\mediamtx.yml`
- Logs: `C:\Tools\mediamtx\logs\mediamtx.out.log` and `C:\Tools\mediamtx\logs\mediamtx.err.log`
- Service wrapper: NSSM at `C:\Tools\nssm\win64\nssm.exe`

MediaMTX ports:

- TCP `8889`: WebRTC HTTP/player used by `/dashboard-tv`
- UDP `8189`: WebRTC ICE
- TCP `8888`: HLS listener
- TCP `8554`: RTSP listener

Firewall rules must allow LAN access to TCP `8889` and UDP `8189` for WebRTC viewing.

## Camera Paths

MediaMTX path names should match backend `camera_id` values. Enabled production camera paths should exclude disabled/offline `block_f_cam_8`.

Current enabled camera host/channel inventory for MediaMTX path setup:

| MediaMTX path / camera_id | Host | Channel |
| --- | --- | --- |
| `block_e_cam_1` | `192.168.40.13` | `102` |
| `block_e_cam_2` | `192.168.40.14` | `102` |
| `block_e_cam_3` | `192.168.40.15` | `102` |
| `block_e_cam_4` | `192.168.40.16` | `102` |
| `block_e_cam_5` | `192.168.40.17` | `102` |
| `block_f_cam_6` | `192.168.40.18` | `102` |
| `block_f_cam_7` | `192.168.40.19` | `102` |
| `block_f_cam_9` | `192.168.40.21` | `102` |
| `block_f_cam_10` | `192.168.40.22` | `102` |
| `kuarantin_cam_11` | `192.168.40.23` | `102` |
| `biosekuriti_cam_12` | `192.168.40.24` | `102` |
| `makmal_cam_13` | `192.168.40.25` | `102` |

Use placeholder-only source examples. To avoid committing credential-shaped URLs, document the source structure as: RTSP scheme, `USERNAME`, `ENCODED_PASSWORD`, `HOST`, port `554`, and `/Streaming/Channels/102`.

Do not document real usernames or passwords. Password symbols must be URL-encoded; for example `@` becomes `%40`, `#` becomes `%23`, and `!` becomes `%21`.

## Codec Requirements

Browser WebRTC works best with H.264. A healthy MediaMTX camera log usually shows:

```text
2 tracks (H264, G711)
```

H.265/HEVC sub-streams may fail in the browser with:

```text
codecs not supported by client
```

`makmal_cam_13` was observed as `1 track (H265)` and needs sub-stream channel `102` changed to H.264.

Recommended Hikvision sub-stream settings for WebRTC:

- Video Encoding: H.264
- H.264+ / H.265+ / Smart Codec: Off
- Resolution: 1280x720 or lower
- FPS: 15 to 20
- Bitrate: 512 to 1024 Kbps
- I-frame interval: 30 for 15 FPS, or 40 for 20 FPS

Main stream can remain HD for snapshot/evidence. H.264 is preferred, 3200x1800 can remain where supported, and H.264+ Off is recommended.

## Quality Modes

- `standard`: used by MJPEG Fallback Smooth Live. It uses the configured camera channel, usually Hikvision sub-stream `102`.
- `hd`: used by MJPEG Fallback HD Live and HD snapshots. It uses Hikvision channel `101`.

HD snapshot can preserve full source resolution where the camera provides it. A production test on `block_f_cam_7` confirmed an HD snapshot at 3200x1800. Actual resolution still depends on the camera main-stream settings and may be lower.

MJPEG live stream output is capped for browser performance. WebRTC Smooth is the default display path. MJPEG HD Live remains available for detail viewing, but can be heavier for the TV, network, or camera. HD snapshots and evidence crops use the HD evidence/snapshot paths separately from the live display mode.

## TV Controls

The TV live monitor includes:

- selected camera dropdown
- WebRTC Smooth / MJPEG Fallback live mode toggle
- Smooth Live / HD Live quality toggle for MJPEG Fallback
- camera name, camera ID, safe host metadata, selected live mode, and live status
- a compact live-mode badge ("WebRTC smooth · live" in green, or "MJPEG fallback" in amber) plus the selected camera display name and `camera_id`, shown beside the panel title
- restart stream button
- snapshot button that defaults to HD even when live display is Smooth, labeled `Snapshot (HD)`
- an `HD` tag on the Latest AI Evidence panel header
- fullscreen button when supported by the browser

### Camera Selector Behavior

The camera dropdown always lists every known camera, including disabled/offline ones (for example `block_f_cam_8`). Disabled/offline cameras appear as a visibly disabled option labeled `- disabled/offline`; they are never silently hidden from the list. Options are also tinted by health status (active/stale/offline/disabled) as a lightweight visual hint.

Default camera auto-selection always prefers a selectable camera and never lands on a disabled/offline option. If zero cameras are currently selectable (or none are configured), the dropdown shows a single disabled placeholder option and the live panel reports that no camera is available, without erroring.

### makmal_cam_13 WebRTC Hint

Because `makmal_cam_13` has a known H.265 sub-stream issue (see Codec Requirements below), the TV dashboard shows a prominent amber "may need MJPEG Fallback" notice directly in the live panel whenever `makmal_cam_13` is selected in WebRTC Smooth mode. This is a simple frontend flag hard-coded to that `camera_id`, with a `TODO` note in the source to remove it once the camera's channel `102` is confirmed re-encoded to H.264.

### WebRTC Fallback Advisory Banner

If the WebRTC player iframe has not finished loading within roughly 9 seconds, the dashboard shows a dismissible banner: "Smooth live unavailable for this camera. Switch to MJPEG fallback." with a one-click button to switch the live mode to MJPEG Fallback.

This banner is an advisory heuristic only, not a definitive stream-health check, and it has an important limitation: the WebRTC view is a cross-origin iframe into the MediaMTX player page. The iframe's `onload` event fires once that player page's HTML has loaded, which is not the same as the video track actually playing. This means the timeout banner can catch a genuinely unconfigured or unreachable MediaMTX path (the shell never loads), but it **cannot** detect the case where the player loads successfully and the video stays blank due to a codec mismatch — for example the `makmal_cam_13` H.265 sub-stream issue. That gap is why the per-camera `makmal_cam_13` hint above exists as a separate, independent notice.

## Audio

Dashboard audio is not implemented. Some Hikvision cameras may have microphone/audio streams, but this pass keeps live view video-only.

Future audio requires camera audio support plus a suitable media path.

## Security

Browsers never receive RTSP URLs, CCTV usernames, or CCTV passwords. MediaMTX and the backend handle camera sources server-side; the dashboard only receives WebRTC viewer pages or backend MJPEG/snapshot output.
