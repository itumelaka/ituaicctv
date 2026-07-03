# ITU AI CCTV

Backend AI CCTV detection project for ITU Melaka using existing Hikvision CCTV infrastructure.

The project is currently focused on local backend development, RTSP camera access, YOLO detection, person-only detection, event decision, event logging, and evidence snapshot preparation.

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

The dashboard UI is a simple browser page that consumes the dashboard API endpoints only. It shows camera totals, disabled cameras, latest events, clickable evidence thumbnails, camera status badges, per-camera event counts, a health card, per-camera health badges, last updated time, and a 30-second auto-refresh countdown.

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

1. Improve latest successful check tracking per camera
2. Investigate block_f_cam_8 network/RTSP issue
3. Add dashboard filters and search
4. Add evidence retention cleanup
5. Later: face detection planning
6. Later: number plate recognition planning

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
