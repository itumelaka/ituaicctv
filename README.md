# ITU AI CCTV

Backend AI CCTV monitoring project for ITU Melaka using existing Hikvision CCTV cameras, YOLO person detection, evidence capture, Telegram alerting, and dashboard-based review.

## Current Status

- Production uses the backend-served dashboard for daily operation.
- GitHub Pages is no longer the primary production dashboard.
- Backend service: `ITUAICCTVBackend`
- Primary monitor: `ITU AI CCTV Live Monitor`
- Old 5-minute monitor: `ITU AI CCTV Person Monitor`, retained as disabled backup
- Camera inventory: 13 known cameras, 12 enabled, 1 disabled/offline
- Event review, ignore-zone groundwork, Telegram group alerting, Standard/HD live view, live monitor health, and local face enrollment tools are deployed.

## Key Features

- RTSP camera access through the backend, without exposing CCTV credentials to browsers.
- Near-live sequential person monitoring using YOLO.
- Person evidence images with full-frame context, all detected person boxes, and up to three top-confidence person crops.
- HD evidence fallback can use scaled main-stream crops when HD re-detection misses a person.
- Telegram alerts for person detections.
- Normal dashboard for operators and evidence review.
- Fullscreen TV Command Center for wall display.
- Event review / acknowledgement statuses.
- Per-camera confidence thresholds and disabled placeholder ignore-zone polygons for known static false positives.
- Optional internal face-recognition foundation, privacy-gated and not identity proof.
- Local-only Face Enrollment Manager for approved CSV/LBPH enrollment and reject reports.
- Dashboard Assign Identity workflow for unknown/unrecognized evidence events, including person-specific targets for multi-person evidence.

## Dashboards

Production LAN examples:

- Normal dashboard: `http://192.168.1.254:8000/dashboard-ui`
- TV dashboard: `http://192.168.1.254:8000/dashboard-tv`

The TV dashboard includes one selected MJPEG live camera stream at a time. Live view supports:

- `quality=standard`: configured camera channel, usually Hikvision sub-stream `102`
- `quality=hd`: Hikvision channel `101`, where available

Invalid live-view quality values return HTTP 400. MJPEG is video-only and does not include audio.

## Architecture Overview

```text
Hikvision CCTV cameras
        |
        v
FastAPI backend on Windows Server
        |
        +-- YOLO person detection and evidence capture
        +-- Near-live monitor task
        +-- Telegram alert helper
        +-- Dashboard APIs and MJPEG proxy
        +-- Local event logs and review metadata
        +-- Local-only face enrollment and identity assignment records
        |
        v
Dashboard UI / TV Command Center / Telegram group
```

The browser connects to the backend only. RTSP URLs, CCTV usernames, and CCTV passwords are not exposed in frontend code.

## Quick Start For Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend\requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

Create local environment files from the examples and keep real secrets private. Do not commit `.env`, camera credentials, Telegram tokens, evidence, face data, embeddings, or models.

## Production Operations

Detailed production and operator notes live in the docs folder:

- [Project status](docs/PROJECT_STATUS.md)
- [Operations](docs/OPERATIONS.md)
- [Live view](docs/LIVE_VIEW.md)
- [Event review](docs/EVENT_REVIEW.md)
- [Ignore zones](docs/IGNORE_ZONES.md)
- [Face recognition](docs/FACE_RECOGNITION.md)
- [Security notes](docs/SECURITY_NOTES.md)
- [Windows Task Scheduler](docs/WINDOWS_TASK_SCHEDULER.md)
- [Roadmap](docs/ROADMAP.md)
- [TODO](docs/TODO.md)

Backend-specific endpoint and runtime notes are in [backend/README.md](backend/README.md).

## Security And Privacy

- Evidence, event review data, face images, face embeddings, and recognition models are private runtime data and ignored by Git.
- Face enrollment CSVs, face crops, identity assignments, and generated LBPH files are private runtime data and must not be committed.
- Telegram bot tokens and numeric chat IDs must stay in private `.env` files.
- CCTV credentials and RTSP URLs with credentials must never be committed.
- Face recognition is optional, internal, privacy-gated, and not high-security identity proof.
- `UNKNOWN` recognition means no reliable internal match; it does not mean suspicious.
- Face Enrollment Manager and identity assignment are local-only. They do not use paid APIs, cloud recognition, or external image upload.

## License

Internal ITU Melaka operational project. Confirm sharing and deployment policy with the project owner before publishing sensitive operational details.
