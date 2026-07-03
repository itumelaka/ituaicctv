# ITU AI CCTV

Backend AI CCTV detection project for ITU Melaka using existing Hikvision CCTV infrastructure.

The project is currently focused on local backend development, RTSP camera access, YOLO detection, person-only detection, event decision, event logging, and evidence snapshot preparation.

## Current Status

Completed:

- FastAPI backend setup
- Health check endpoint
- RTSP camera test endpoint
- CCTV snapshot endpoint
- YOLO detection endpoint
- YOLO snapshot endpoint with bounding boxes
- Person-only detection endpoint
- Person-only snapshot endpoint
- Person event decision endpoint
- Local event logging using JSONL
- Evidence snapshot logic for person events
- Lightweight dashboard API endpoints for cameras, latest events, and evidence
- CCTV sub-stream configured to H.264 for OpenCV compatibility
- YOLOv8n running in CPU mode

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

GET /dashboard/summary
GET /dashboard/evidence
GET /dashboard/evidence?limit=20
GET /dashboard/cameras
GET /dashboard/events/latest
GET /dashboard/events/latest?limit=10

Dashboard endpoints are lightweight read-only endpoints. They read existing camera configuration, event logs, and evidence image metadata only. They do not run YOLO detection.

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

1. Add configurable confidence threshold
2. Add per-camera event statistics
3. Add retention cleanup for evidence images
4. Add alert integration such as Telegram
5. Add dashboard preview

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
