# ITU AI CCTV

Backend AI CCTV detection project for ITU Melaka using existing Hikvision CCTV infrastructure.

The project is currently focused on local backend development, RTSP camera access, YOLO detection, person-only detection, event decision, event logging, and evidence snapshot preparation.

## Current Checkpoint

Latest confirmed commit:

d18747e feat: add dashboard health endpoint

Confirmed at this checkpoint:

- Backend FastAPI works.
- Hikvision RTSP works.
- Multi-camera config has 10 cameras.
- 9 cameras are enabled.
- 1 camera is disabled: block_f_cam_8 / 192.168.40.20.
- Disabled camera reason: ping and RTSP port 554 are not reachable.
- GET /dashboard-ui is usable.
- GET /dashboard/health is usable.
- Dashboard UI includes auto-refresh, last updated time, next refresh countdown, quick links, improved badges, clickable evidence thumbnails, Health card, and per-camera health badges.
- GET /dashboard/health includes a scheduler log summary from backend/data/task-logs/monitor_person_all.log when available.
- backend/app/dashboard_health.py exists.
- tests/test_dashboard_health.py exists.
- Unit tests pass with: python -m unittest discover -s tests -p "test_*.py" -v
- Compile check passes with: python -m compileall backend/app
- sambung.txt is a private local handoff note and should not be committed.

Next recommended work:

1. Improve block_f_cam_8 metadata if not already committed
2. Add camera health from scheduler log
3. Enhance dashboard health card
4. Investigate block_f_cam_8 network/IP issue
5. Later: face detection planning
6. Later: number plate recognition planning

## Current Status

Completed:

- FastAPI backend setup
- Health check endpoint
- RTSP frame capture
- RTSP camera test endpoint
- CCTV snapshot endpoint
- YOLOv8n person detection
- YOLO detection endpoint
- YOLO snapshot endpoint with bounding boxes
- Person-only detection endpoint
- Person-only snapshot endpoint / person snapshot
- Person event decision endpoint
- Local event logging using JSONL
- Evidence snapshot logic for person events
- Evidence image save and view endpoint
- Event stats endpoint
- Multi-camera registry
- Camera audit endpoint
- Check-all monitor endpoint
- Dashboard summary API
- Dashboard health API
- Scheduler-log health summary in GET /dashboard/health
- Stale camera health logic in GET /dashboard/health
- Lightweight dashboard API endpoints for cameras, latest events, and evidence
- Per-camera dashboard endpoints for latest event and event stats
- Simple browser dashboard UI
- Dashboard auto-refresh and status UI polish
- Dashboard health card with per-camera health badges
- CCTV sub-stream configured to H.264 for OpenCV compatibility
- YOLOv8n running in CPU mode

## Camera Status Summary

Current configured camera status:

- Total cameras: 10
- Enabled cameras: 9
- Disabled cameras: 1
- Disabled camera: block_f_cam_8 / 192.168.40.20
- Status: offline
- Reason: ping and RTSP port 554 are not reachable

## Current Working Camera

Camera Host : 192.168.40.21
RTSP Port   : 554
Channel     : 102
Stream      : Sub-stream
Codec       : H.264
Resolution  : 640x360
Bitrate     : 512 Kbps

Do not use the high-resolution H.265 main stream for backend AI processing because OpenCV may fail to decode it reliably on Windows.

## Backend Endpoints

Health:

GET /health

Camera:

GET /cameras/test
GET /cameras/snapshot

Detection:

GET /detections/test
GET /detections/yolo
GET /detections/yolo/snapshot
GET /detections/person
GET /detections/person/snapshot

Events:

GET /events/person
GET /events/logs
GET /events/logs?limit=5
GET /events/stats
GET /events/evidence/{filename}

Dashboard:

GET /dashboard-ui
GET /dashboard/summary
GET /dashboard/health
GET /dashboard/evidence
GET /dashboard/evidence?limit=20
GET /dashboard/cameras
GET /dashboard/cameras/{camera_id}/latest-event
GET /dashboard/cameras/{camera_id}/stats
GET /dashboard/events/latest
GET /dashboard/events/latest?limit=10

Dashboard endpoints are lightweight read-only endpoints. They read existing camera configuration, event logs, and evidence image metadata only. They do not run YOLO detection. Per-camera dashboard endpoints validate camera_id against the configured camera list.

GET /dashboard/health also marks enabled cameras as active, stale, or no_recent_event based on the latest event/check time in backend/data/events.jsonl. The default stale threshold is 120 minutes. Disabled cameras with status offline are reported as offline.

Important dashboard URLs:

- /dashboard-ui
- /dashboard/summary
- /dashboard/health
- /dashboard/cameras
- /dashboard/events/latest
- /dashboard/evidence
- /dashboard/cameras/{camera_id}/latest-event
- /dashboard/cameras/{camera_id}/stats

Dashboard UI:

Open this URL after starting the backend:

http://127.0.0.1:8000/dashboard-ui

The dashboard UI is a simple browser page that consumes the dashboard API endpoints only. It shows camera totals, disabled cameras, latest events, clickable evidence thumbnails, camera status badges, per-camera event counts, a health card, scheduler latest run and summary, per-camera health badges, last updated time, and a 30-second auto-refresh countdown.

The page also includes quick links for:

- Refresh now
- /dashboard/health
- /dashboard/summary
- /dashboard/cameras
- /dashboard/events/latest
- /dashboard/evidence

## Scheduler Status

Windows Task Scheduler task:

ITU AI CCTV Person Monitor

Current status:

- Intentionally Disabled
- Uses the multi-camera monitor launcher
- BAT launcher returns 0 to Task Scheduler so attention events are not marked as task failures

Scheduler script paths:

- backend/scripts/monitor_person_all_once.py
- backend/scripts/run_monitor_person_all_once.bat
- backend/scripts/run_monitor_person_all_once_hidden.vbs

Scheduler log path:

backend/data/task-logs/monitor_person_all.log

GET /dashboard/health reads this log lightly and returns a scheduler block with:

- status
- latest_run_time
- latest_summary
- failed_count
- person_detected_count
- no_person_count
- log_path
- recent_lines

Per-camera dashboard health includes:

- health_status
- last_event_time
- stale_minutes
- stale_threshold_minutes
- last_seen_source

## Event Flow

Current event flow:

CCTV RTSP stream
? Capture frame
? Run YOLO person detection
? Decide event type
? Save event log
? Save evidence snapshot only when person_detected is true

Event log file:

backend/data/events.jsonl

Evidence folder:

backend/data/evidence/

Runtime logs and evidence images are ignored from Git.

## Environment File

Create local environment file:

Copy-Item backend\.env.example backend\.env

Example backend/.env:

APP_NAME=ITU AI CCTV Backend
APP_ENV=development

CCTV_HOST=192.168.40.21
CCTV_PORT=554
CCTV_USERNAME=your_username
CCTV_PASSWORD=your_password
CCTV_CHANNEL=102

Never commit real CCTV usernames or passwords.

Security reminders:

- backend/.env is local only
- Never commit camera passwords
- Dashboard responses must not expose RTSP credentials
- Evidence images may contain real CCTV footage and must be handled carefully

## Local Development

Create virtual environment:

python -m venv .venv

Activate virtual environment:

.\.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r backend\requirements.txt

Run backend:

cd backend
python -m uvicorn app.main:app --reload

Open API docs:

http://127.0.0.1:8000/docs

## Important Notes

The original camera main stream used H.265 / HEVC at high resolution. OpenCV produced HEVC decode errors such as:

PPS id out of range
VPS does not exist
SPS does not exist
Stream timeout triggered

Stable backend configuration:

Video Encoding : H.264
Resolution     : 640x360
Channel        : 102

This is lighter and more suitable for AI detection.

## Next Milestones

1. Improve block_f_cam_8 metadata if not already committed
2. Investigate block_f_cam_8 network/IP issue
3. Later: face detection planning
4. Later: number plate recognition planning

## Repository

https://github.com/itumelaka/ituaicctv

## Monitor Endpoint

Manual monitor check endpoint:

GET /monitor/person/check

This endpoint runs a complete person monitoring check:

CCTV RTSP stream
? Capture frame
? Run person-only YOLO detection
? Create event decision
? Save event log
? Save evidence snapshot if person_detected is true
? Return recommended action

Example no-person response:

status          : ok
monitor         : person
action          : no_action
next_step       : Continue monitoring.
person_detected : false

Example person-detected response:

status          : ok
monitor         : person
action          : attention_required
next_step       : Review evidence image and consider alert notification.
person_detected : true
evidence_path   : data/evidence/...

## Project Documentation

Additional project documentation:

- docs/PROJECT_STATUS.md
- docs/TODO.md
- docs/ROADMAP.md
- docs/SECURITY_NOTES.md
- docs/WINDOWS_TASK_SCHEDULER.md
