# ITU AI CCTV Backend

FastAPI backend for CCTV RTSP testing, snapshot capture, YOLO detection, person-only detection, event decision, local logging, evidence snapshot, multi-camera monitoring, and dashboard UI.

For public project overview, use the root `README.md`. Detailed operator notes are split into:

- `docs/OPERATIONS.md`
- `docs/LIVE_VIEW.md`
- `docs/EVENT_REVIEW.md`
- `docs/IGNORE_ZONES.md`
- `docs/FACE_RECOGNITION.md`

## Current Production Runtime

- Production path: `C:\ituaicctv`
- Development path: `C:\Users\burnk\OneDrive\Documents-assets\ai-cctv-detection`
- Production dashboard: `http://192.168.1.254:8000/dashboard-ui`
- TV command center: `http://192.168.1.254:8000/dashboard-tv`
- Backend service: `ITUAICCTVBackend`, confirmed `Running`, `Automatic`
- Primary monitor task: `ITU AI CCTV Live Monitor`, confirmed `Running`
- Old batch monitor task: `ITU AI CCTV Person Monitor`, confirmed `Disabled` and retained as backup
- Live monitor command: `C:\ituaicctv\.venv312\Scripts\python.exe C:\ituaicctv\scripts\monitor_person_live.py`
- Live monitor status file: `backend/data/task-logs/live_monitor_status.json`
- `/dashboard/health` prefers `live_monitor_status.json` and falls back to the old `monitor_person_all.log` for backward compatibility.
- Live monitor scans enabled cameras sequentially. Configured interval is 10 seconds, with real observed full-cycle time around 30 seconds for 12 enabled cameras.
- Latest observed live monitor summary: `enabled=12 attention=0 failed=0 next_scan=10s`
- Total known cameras: 13
- Enabled cameras: 12
- Disabled/offline camera: `block_f_cam_8 / ITU BLOCK F CAM8 / 192.168.40.20`
- Evidence share: `\\192.168.1.254\ituaicctv-evidence`

Verify after server restart:

```powershell
Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType
Get-ScheduledTask |
  Where-Object { $_.TaskName -like "ITU AI CCTV*" } |
  Select-Object TaskName, State
Invoke-RestMethod http://127.0.0.1:8000/dashboard/health | ConvertTo-Json -Depth 6
```

## Latest Evidence Behavior

Person evidence remains one saved JPEG using the existing filename pattern:

```text
person_detected_<camera_id>_<timestamp>.jpg
```

For new detections, the evidence image is a clearer composite:

- full CCTV frame with bounding boxes
- up to three right-panel person crops ordered by confidence
- crop labels such as `PERSON 1`, confidence, and active threshold where useful
- metadata in new event JSON synced to the rendered crops through `person_detections`
- `person_detections` includes `crop_rank`, `confidence`, and `bbox`
- `evidence_source` records whether evidence used `hd_redetect`, `hd_scaled_bbox`, or `detection_frame`
- fallback to boxed full-frame evidence if composite generation fails

Telegram sends the saved evidence image, so new alerts use the clearer composite image automatically.

Existing old events are not migrated. New events after deployment include synced multi-person evidence metadata. If YOLO detects only one person in a crowded or overlapping scene, the dashboard can only assign the detected `PERSON 1`; future tuning may require a stronger local model or tracker for selected cameras.

HD evidence flow:

1. Detect person on the configured camera stream, usually sub-stream `102`.
2. Try HD/main-stream re-detection on channel `101`.
3. If HD re-detection finds valid persons, use HD detections.
4. If HD re-detection finds no person but the HD frame exists, scale the original detection boxes to the HD frame and use valid scaled crops.
5. If scaled crops are invalid, fall back to the original detection frame.

The scaled HD fallback can improve face readiness from `not_suitable` to `possible` or `suitable` when the sub-stream crop was too small. Recognition can still return `UNKNOWN` if the local model does not match.

## False Positive Review and Ignore Zones

- Global person confidence remains 0.60 unless a camera overrides it.
- makmal_cam_13 and kuarantin_cam_11 currently use 0.75 because of known static false positives.
- Camera configs may define optional `ignore_zones` polygon masks with normalized points from 0.0 to 1.0.
- Placeholder zones for makmal_cam_13 and kuarantin_cam_11 are present but disabled until calibrated against reviewed frames.
- When an ignore zone is enabled, detections with a bounding-box center inside the polygon are suppressed before event logging, evidence saving, and Telegram alerting.
- Event reviews are stored locally in ignored runtime data under `backend/data/event-reviews/`.
- Production verification confirmed `/events/reviews`, `/events/latest-with-reviews`, `/dashboard/cameras`, and the `/dashboard-ui` review buttons.
- Review statuses are `unreviewed`, `valid`, `false_positive`, `needs_follow_up`, `ignored`, and `reviewed`.

## Telegram Group Alerts

- Production Telegram alerts currently go to the internal `itunetmonitor` group.
- Set `TELEGRAM_CHAT_ID` to the Telegram group chat ID in private `.env`; do not commit bot tokens or numeric chat IDs.
- Use Telegram `getUpdates` after posting a message in the group to find the group chat ID.
- Telegram group delivery was verified after deployment.

Face readiness and internal recognition status:

- Face readiness / face quality assessment is implemented and conservative. It is not identity recognition by itself.
- OpenCV LBPH is available on production through `opencv-contrib-python 5.0.0.93`; `cv2.face` and `LBPHFaceRecognizer_create` are available.
- Production currently enables `FACE_RECOGNITION_ENABLED=true` and `FACE_RECOGNITION_BACKEND=opencv_lbph` in private `.env`.
- Approved internal test labels can be enrolled using private local samples. Generated LBPH model and label files live under the ignored `backend/data/face-embeddings/` directory and must never be committed.
- `UNKNOWN` means no reliable internal match and does not mean suspicious.
- Face Enrollment Manager supports local placeholder CSV templates, reviewed draft CSV generation, batch OpenCV/LBPH enrollment, and JSON reject reports through `scripts/manage_face_enrollment.py`.
- Real enrollment CSV files, face images, identity data, reject reports with private paths, and generated model files must stay private and out of Git.

## Scheduler Exit Codes

- `0` = ok / no attention required / no person detected
- `2` = attention required / person detected, not a crash
- Other non-zero failures should be checked in `C:\ituaicctv\backend\data\task-logs\monitor_person_all.log`

## API Endpoints

### Health

```
GET /health
```

### Camera

```
GET /cameras/test
GET /cameras/snapshot
GET /cameras/audit
```

### Detection

```
GET /detections/test
GET /detections/yolo
GET /detections/yolo/snapshot
GET /detections/person
GET /detections/person/snapshot
```

### Events

```
GET /events/person
GET /events/logs
GET /events/logs?limit=5
GET /events/latest-with-reviews
GET /events/stats
GET /events/reviews
GET /events/reviews/{event_id}
PUT /events/reviews/{event_id}
POST /events/reviews/{event_id}
GET /events/evidence/{filename}
```

### Monitor

```
GET /monitor/person/check
GET /monitor/person/check-all
GET /monitor/person/summary
GET /{camera_id}/person/check
```

### Dashboard

```
GET /dashboard/summary
GET /dashboard/health
GET /dashboard/cameras
GET /dashboard/cameras/{camera_id}/latest-event
GET /dashboard/cameras/{camera_id}/stats
GET /dashboard/events/latest
GET /dashboard/events/latest?limit=10
GET /dashboard/evidence
GET /dashboard/evidence?limit=20
GET /dashboard/live/{camera_id}/stream.mjpg
GET /dashboard/live/{camera_id}/stream.mjpg?quality=standard
GET /dashboard/live/{camera_id}/stream.mjpg?quality=hd
GET /dashboard/live/{camera_id}/snapshot.jpg
GET /dashboard/live/{camera_id}/snapshot.jpg?quality=standard
GET /dashboard/live/{camera_id}/snapshot.jpg?quality=hd
```

### Dashboard UI

```
GET /dashboard-ui
GET /dashboard-tv
```

### Face Enrollment

```
GET /faces/enrollment/template
POST /faces/enrollment/identity-assignment
GET /faces/enrollment/identity-assignments
```

Face enrollment helpers are local-only. They expose template, assignment, and readback metadata only; they do not upload face images, call paid APIs, or call cloud recognition services.

Local CLI helpers:

```powershell
python scripts\manage_face_enrollment.py template --output private-face-enrollment-template.csv
python scripts\manage_face_enrollment.py draft --source-dir C:\private\approved-face-reference --output C:\private\face-enrollment-draft.csv
python scripts\manage_face_enrollment.py batch-enroll --csv C:\private\face-enrollment-reviewed.csv --reject-report C:\private\face-enrollment-reject-report.json
```

Private runtime storage:

```text
backend/data/face-enrollment/
backend/data/face-enrollment/identity-assignments/identity_assignments.json
backend/data/face-embeddings/
```

Do not commit enrollment CSVs, crops, assignments, face images, embeddings, recognition models, evidence, logs, `.env`, `.venv`, or `.venv312`.

If an older path bug creates an accidental `backend/backend/` runtime folder, treat it as private runtime output. Do not commit it. Stop the service first, verify no current process is writing there, move any needed private runtime files to the correct `backend/data/` location, then remove the stray folder locally.

Full HTML dashboard served directly by the backend. Auto-refreshes every 30 seconds. Loads data from all dashboard endpoints.

Production dashboard:

```
http://192.168.1.254:8000/dashboard-ui
```

TV command center:

```
http://192.168.1.254:8000/dashboard-tv
```

The TV dashboard includes a selectable MJPEG Live Camera View. The browser connects only to the backend; the backend proxies the selected camera RTSP stream and does not expose RTSP URLs, CCTV usernames, or CCTV passwords. The MJPEG stream is limited to 4 FPS and is intended for one selected camera/viewer, not all cameras simultaneously.

Live view quality:

- `quality=standard` uses the camera configured channel, usually Hikvision sub-stream `102`.
- `quality=hd` uses Hikvision main-stream channel `101` where available. HD MJPEG allows a larger 1920px max width, but actual resolution depends on the camera main-stream settings and may still be 720p.
- Invalid quality values return HTTP 400.
- Quality selection is live-view only. It does not change detection channel, scheduler/live monitor behavior, evidence, Telegram alerts, event review, or ignore zones.
- HD can increase CPU, bandwidth, and camera load.
- MJPEG does not support audio. Audio requires camera audio support plus a future HLS/WebRTC/FFmpeg proxy.

Live stream test URL:

```
http://192.168.1.254:8000/dashboard/live/kuarantin_cam_11/stream.mjpg
http://192.168.1.254:8000/dashboard/live/kuarantin_cam_11/stream.mjpg?quality=hd
http://192.168.1.254:8000/dashboard/live/biosekuriti_cam_12/stream.mjpg
http://192.168.1.254:8000/dashboard/live/makmal_cam_13/stream.mjpg
```

Snapshot fallback test URL:

```
http://192.168.1.254:8000/dashboard/live/kuarantin_cam_11/snapshot.jpg
http://192.168.1.254:8000/dashboard/live/kuarantin_cam_11/snapshot.jpg?quality=hd
```

The live stream and snapshot fallback do not run YOLO, write event logs, save evidence images, or send Telegram alerts. Latest evidence in `/dashboard-tv` remains a separate historical evidence panel.

Use `http://127.0.0.1:8000/dashboard-ui` only when browsing on the machine running the backend. The production backend runs from `C:\ituaicctv` on the Windows Server. GitHub Pages may remain useful for static/demo/client work, but daily operation uses the backend dashboard served by FastAPI.

Evidence images are saved only for `person_detected=True` events. `no_person` events usually have `evidence_path=null`.

Production runtime paths:

```
C:\ituaicctv\backend\data\evidence
C:\ituaicctv\backend\data\task-logs
C:\ituaicctv\backend\data\service-logs
```

Evidence SMB share:

```
\\192.168.1.254\ituaicctv-evidence
```

The dashboard includes Refresh Evidence and Copy Evidence Folder Path actions. If browser security blocks direct folder links, paste the UNC path into File Explorer.

## Folder Structure

```
backend/
  app/
    main.py
    config.py
    camera.py
    camera_registry.py
    detection.py
    monitor.py
    events.py
    event_log.py
    dashboard_health.py
    routes/
      health.py
      cameras.py
      detections.py
      events.py
      monitor.py
      dashboard.py
      dashboard_ui.py
  data/
    events.jsonl
    evidence/
    face-enrollment/
      identity-assignments/
    face-embeddings/
    task-logs/
      monitor_person_all.log
      live_monitor_status.json
  .env.example
  requirements.txt
  README.md
```

Runtime files under `backend/data` are ignored from Git.

## Run Backend

From project root:

```powershell
.\.venv312\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload
```

Open Swagger docs:

```
http://127.0.0.1:8000/docs
```

Open dashboard UI:

```
http://127.0.0.1:8000/dashboard-ui
```

## CCTV Configuration

Recommended stream for AI processing:

```
Stream Type      : Sub-stream
RTSP Channel     : 102
Video Encoding   : H.264
Resolution       : 640x360
Bitrate          : 512 Kbps
Frame Rate       : 10-20 fps
```

Avoid H.265 / HEVC for OpenCV snapshot and AI processing on Windows.

## Environment

Local `backend/.env` example:

```env
APP_NAME=ITU AI CCTV Backend
APP_ENV=development

CCTV_HOST=192.168.40.21
CCTV_PORT=554
CCTV_USERNAME=your_username
CCTV_PASSWORD=your_password
CCTV_CHANNEL=102

YOLO_CONFIDENCE=0.35
PERSON_CONFIDENCE_THRESHOLD=0.60
PERSON_EVENT_COOLDOWN_SECONDS=300

TELEGRAM_BOT_TOKEN=<TELEGRAM_BOT_TOKEN>
TELEGRAM_CHAT_ID=<TELEGRAM_CHAT_ID_OR_GROUP_CHAT_ID>
```

Never commit `backend/.env`.

## Telegram Alert

Alert dihantar secara automatik apabila `person_detected=True` dan cooldown tidak aktif.

Setup:

1. Buat Telegram Bot melalui [@BotFather](https://t.me/BotFather) dan dapatkan token.
2. Dapatkan Chat ID — hantar mesej ke bot atau Telegram group anda kemudian buka:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Tambah dalam `backend/.env`:

```env
TELEGRAM_BOT_TOKEN=<TELEGRAM_BOT_TOKEN>
TELEGRAM_CHAT_ID=<TELEGRAM_CHAT_ID_OR_GROUP_CHAT_ID>
```

Untuk group alert, masukkan group chat ID ke `TELEGRAM_CHAT_ID`. Production sudah verified menghantar alert ke internal group `itunetmonitor`, tetapi numeric group chat ID dan bot token mesti kekal private.

Jika `TELEGRAM_BOT_TOKEN` atau `TELEGRAM_CHAT_ID` kosong, alert akan dilog sebagai skipped dan tidak akan crash sistem.

Alert akan hantar:
- Foto evidence (jika ada snapshot) dengan caption kamera, masa dan bilangan detections
- Confidence tertinggi dan threshold aktif jika data confidence tersedia
- Teks sahaja jika tiada evidence (contoh: cooldown skip)

Alert dihantar daripada endpoint:
- `GET /monitor/person/check`
- `GET /monitor/person/check-all`
- `GET /{camera_id}/person/check`

Response akan termasuk `"alert_sent": true/false`.

## Event Logging

When `GET /events/person` is called, the backend:

1. Captures one CCTV frame
2. Runs person-only YOLO detection
3. Creates event decision
4. Saves the event to `backend/data/events.jsonl`
5. Saves evidence image only if `person_detected` is true

No-person event example:

```
event_type      : no_person
severity        : none
person_detected : false
evidence_path   : null
```

Person event example:

```
event_type      : person_detected
severity        : medium
person_detected : true
evidence_path   : data/evidence/person_detected_timestamp.jpg
```

## Monitor

`GET /monitor/person/check` — single camera check (uses default config camera).

`GET /monitor/person/check-all` — runs check on all enabled cameras in `cameras.json`.

`GET /monitor/person/summary` — returns summary stats without triggering new checks.

`GET /{camera_id}/person/check` — check a specific camera by ID.

These endpoints are designed to be called by a scheduled task or Windows Task Scheduler on a regular interval (e.g. every 5 minutes).

Possible actions returned:

```
no_action
attention_required
```

## Dashboard Health

`GET /dashboard/health` returns per-camera health status based on last event time.

Health status values:

```
active           — event seen within stale threshold (default 120 min)
stale            — last event older than stale threshold
no_recent_event  — camera enabled but no events recorded yet
warning          — camera has a failed event in log
disabled         — camera is disabled in config
offline          — camera is disabled and marked offline in config
```

Scheduler log is read from `data/task-logs/monitor_person_all.log` to surface last run time and summary in the health endpoint.

## Camera Registry

Cameras are configured in `backend/config/cameras.json`. Current production inventory has 13 known cameras, 12 enabled cameras, and 1 disabled/offline camera (`block_f_cam_8 / 192.168.40.20`). The confirmed additional cameras are:

- `kuarantin_cam_11` / `ITU KUARANTIN CAM11` / `192.168.40.23` / channel `102`
- `biosekuriti_cam_12` / `ITU BIOSEKURITI CAM12` / `192.168.40.24` / channel `102`
- `makmal_cam_13` / `ITU MAKMAL CAM13` / `192.168.40.25` / channel `102`

Each camera entry:

```json
{
  "id": "CAM01",
  "name": "Pintu Masuk Utama",
  "host": "192.168.40.21",
  "port": 554,
  "channel": "102",
  "enabled": true,
  "location": "Block F",
  "block": "F",
  "notes": "",
  "status": "",
  "health_note": ""
}
```

## Troubleshooting

If uvicorn is not recognized:

```powershell
python -m uvicorn app.main:app --reload
```

If RTSP connects but snapshot fails, check whether the stream is H.265. Change CCTV sub-stream to H.264 and use channel 102.

Check RTSP port:

```powershell
Test-NetConnection 192.168.40.21 -Port 554
```

Check camera web UI:

```powershell
Test-NetConnection 192.168.40.21 -Port 443
```
