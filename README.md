# ITU AI CCTV

Backend AI CCTV detection project for ITU Melaka using existing Hikvision CCTV infrastructure.

The project is currently focused on local backend development, RTSP camera access, YOLO detection, person-only detection, event decision, event logging, and evidence snapshot preparation.

## Current Checkpoint

Latest confirmed commit:

8352f37

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
- Scheduler summary in GET /dashboard/health is usable.
- Stale camera health logic in GET /dashboard/health is usable.
- Scheduler BAT resolves the project root from its own script location.
- Scheduler BAT uses .venv312 first, then .venv, then python from PATH.
- backend/app/dashboard_health.py exists.
- tests/test_dashboard_health.py exists.
- Unit tests pass with: python -m unittest discover -s tests -p "test_*.py" -v
- Compile check passes with: python -m compileall backend/app
- sambung.txt is a private local handoff note and should not be committed.

Next recommended work:

1. Scheduler task enable decision
2. Investigate block_f_cam_8 network/IP
3. Later: face detection planning
4. Later: number plate recognition planning

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
- Dashboard stale/offline visual polish
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

GET /dashboard/health currently includes:

- camera totals
- disabled/offline camera list
- event health
- scheduler summary
- per-camera active/stale/no_recent_event/disabled/offline status
- stale threshold minutes
- stale_minutes
- last_seen_source

Current health status logic:

- offline for disabled cameras with status offline
- disabled for disabled cameras
- active for enabled cameras with recent event/check
- stale for enabled cameras with old event/check
- no_recent_event for enabled cameras with no event/check yet

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

Health endpoint:

http://127.0.0.1:8000/dashboard/health

The dashboard UI is a simple browser page that consumes the dashboard API endpoints only. It shows camera totals, disabled cameras, latest events, clickable evidence thumbnails, camera status badges, per-camera event counts, a health card, scheduler latest run and summary, per-camera health badges, stale/offline counts, last seen source, stale minutes, health notes, last updated time, and a 30-second auto-refresh countdown.

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
- BAT launcher resolves the project root dynamically from its script location
- Python selection order:
  1. .venv312\Scripts\python.exe
  2. .venv\Scripts\python.exe
  3. python from PATH
- This supports laptop environments where the old .venv is missing or broken but .venv312 exists

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

Current expected healthy dashboard state after a successful scheduler run:

- total cameras: 10
- enabled: 9
- disabled/offline: 1
- active: 9
- stale: 0
- latest scheduler summary: status=ok, mode=check_all, enabled=9, person=0, no_person=9, failed=0

Known camera note:

- block_f_cam_8 / ITU BLOCK F CAM8 remains disabled/offline.
- IP: 192.168.40.20.
- Ping and RTSP port 554 are not reachable.
- Do not treat this camera as a system failure unless it is intentionally re-enabled later.

## Scheduler PowerShell Commands

Check task state:

Get-ScheduledTask -TaskName "ITU AI CCTV Person Monitor" | Select-Object TaskName, State

Show task info:

Get-ScheduledTaskInfo -TaskName "ITU AI CCTV Person Monitor"

Enable the task:

Enable-ScheduledTask -TaskName "ITU AI CCTV Person Monitor"

Disable the task:

Disable-ScheduledTask -TaskName "ITU AI CCTV Person Monitor"

Start the task manually:

Start-ScheduledTask -TaskName "ITU AI CCTV Person Monitor"

Operational notes:

- RTSP timeouts may happen temporarily if the CCTV network is unstable.
- Avoid overlapping scheduler runs if check-all takes too long.
- When working inside OneDrive, pause sync during coding or Git work if Git, virtualenv, or project files are being modified.
- Never commit backend/.env, virtualenv folders, logs, evidence images, or local handoff notes.

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

1. Scheduler task enable decision
2. Investigate block_f_cam_8 network/IP
3. Later: face detection planning
4. Later: number plate recognition planning

## Repository

https://github.com/itumelaka/ituaicctv

## GitHub Pages Dashboard

Live dashboard URL:

https://itumelaka.github.io/ituaicctv/

The GitHub Pages site serves the full dashboard UI as a static PWA from the `docs/` folder.
It is installable as a PWA on desktop and mobile (Add to Home Screen).

The dashboard connects to the FastAPI backend over the LAN.
Set the Backend URL in the dashboard header to your server IP, for example:

```
http://192.168.x.x:8000
```

The backend URL is saved in the browser's localStorage and remembered on next visit.

CORS is enabled on the backend (`allow_origins=["*"]`) so any browser on the LAN can connect.

## Windows Server Deployment

Recommended setup for production:

```
CCTV LAN
  → Hikvision NVR / cameras
  → Windows Server (bilik server)
       → FastAPI backend (port 8000)
       → Windows Task Scheduler (monitor every 5 min)
  → Staff browser → https://itumelaka.github.io/ituaicctv/
       → Backend URL set to http://<server-ip>:8000
```

Steps to deploy on Windows Server:

1. Install Python 3.12 on Windows Server.

2. Clone the repository:
   ```powershell
   git clone https://github.com/itumelaka/ituaicctv.git
   cd ituaicctv
   ```

3. Create virtual environment and install dependencies:
   ```powershell
   python -m venv .venv312
   .\.venv312\Scripts\Activate.ps1
   pip install -r backend\requirements.txt
   ```

4. Create `backend\.env` from example:
   ```powershell
   Copy-Item backend\.env.example backend\.env
   ```
   Fill in CCTV credentials, Telegram token, and chat ID.

5. Allow port 8000 through Windows Firewall (LAN only):
   ```powershell
   New-NetFirewallRule -DisplayName "ITU AI CCTV Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
   ```

6. Run backend:
   ```powershell
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

7. Run deployment scripts (as Administrator):

   ```powershell
   # Install backend as Windows Service (auto-start on boot)
   .\scripts\server\install_backend_service.ps1

   # Open port 8000 in Windows Firewall (LAN only)
   .\scripts\server\setup_firewall.ps1

   # Setup Task Scheduler for periodic monitoring (every 5 min)
   .\scripts\server\setup_task_scheduler.ps1
   ```

   Scripts require NSSM for the service installer.
   Download NSSM: https://nssm.cc/download — place `nssm.exe` at `C:\nssm\nssm.exe`.

8. Enable the monitoring task when ready:

   ```powershell
   Enable-ScheduledTask -TaskName "ITU AI CCTV Person Monitor"
   ```

9. Check server health anytime:

   ```powershell
   .\scripts\server\check_server.ps1
   ```

10. Open GitHub Pages dashboard in any browser on the LAN:
    ```
    https://itumelaka.github.io/ituaicctv/
    ```
    Set Backend URL to `http://<windows-server-ip>:8000`.

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
