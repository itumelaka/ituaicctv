# ITU AI CCTV

Backend AI CCTV detection project for ITU Melaka using existing Hikvision CCTV infrastructure.

The project is currently focused on local backend development, RTSP camera access, YOLO detection, person-only detection, event decision, event logging, and evidence snapshot preparation.

## Current Production Status

Repository and runtime:

- GitHub repo: https://github.com/itumelaka/ituaicctv
- Production server path: C:\ituaicctv
- Local laptop development path: C:\Users\burnk\OneDrive\Documents-assets\ai-cctv-detection
- Production dashboard: http://192.168.1.254:8000/dashboard-ui
- Fullscreen TV command center: http://192.168.1.254:8000/dashboard-tv
- GitHub Pages is no longer the primary production dashboard. Daily operation uses the backend-served /dashboard-ui page.

Latest deployed checkpoints:

- a04f8b6 feat: add live dashboard effects and zoomed evidence
- 9ac95c5 feat: redesign dashboard command center UI
- a65e817 docs: add safe face detection and recognition roadmap
- 016cc02 feat: add person detection confidence threshold
- 657f110 feat: make dashboard nav scroll to sections

Production server status:

- Windows Service: ITUAICCTVBackend
- Service status: Running
- Service StartType: Automatic
- Backend listens on port 8000 and should auto-start after Windows Server reboot.
- Task Scheduler task: ITU AI CCTV Person Monitor
- Task state: Ready
- Scheduler Python: C:\ituaicctv\.venv312\Scripts\python.exe
- Scheduler scans 9 enabled cameras. Latest logs show status ok, enabled=9, failed=0.

Camera and network status:

- Total cameras: 10
- Enabled cameras: 9
- Disabled/offline cameras: 1
- Disabled/offline: block_f_cam_8 / ITU BLOCK F CAM8, because ping and RTSP port 554 are not reachable.
- All 9 enabled cameras are active based on recent health checks.
- Production server LAN IP: 192.168.1.254
- GOVNET NIC: 10.65.28.254
- CCTV subnet: 192.168.40.0/24
- UDM Pro allows server 192.168.1.254 to CCTV subnet 192.168.40.0/24 on TCP 554.
- Windows Firewall allows inbound TCP 8000 for dashboard/API.

## Verify After Server Restart

Run these on the Windows Server:

```powershell
Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType
Get-ScheduledTask -TaskName "ITU AI CCTV Person Monitor" | Select-Object TaskName, State
Invoke-RestMethod http://127.0.0.1:8000/dashboard/health | ConvertTo-Json -Depth 6
```

Expected:

- ITUAICCTVBackend is Running and Automatic.
- ITU AI CCTV Person Monitor is Ready.
- /dashboard/health returns camera totals, scheduler latest run/summary, and per-camera health.

## Evidence Share Usage

Production evidence:

- Server folder: C:\ituaicctv\backend\data\evidence
- SMB share: \\192.168.1.254\ituaicctv-evidence
- Normal share access is read-only for Everyone.
- Backend/server can still save evidence locally.
- Use File Explorer for browsing if the browser shows a directory index.

Open from laptop:

```powershell
explorer "\\192.168.1.254\ituaicctv-evidence"
```

Copy laptop evidence to server only during a controlled maintenance window:

```powershell
$source = "C:\Users\burnk\OneDrive\Documents-assets\ai-cctv-detection\backend\data\evidence"
$dest = "\\192.168.1.254\ituaicctv-evidence"
robocopy $source $dest *.jpg /E /XO /R:2 /W:2
```

Temporary server-side write access, then revert to read-only:

```powershell
Grant-SmbShareAccess -Name "ituaicctv-evidence" -AccountName "Everyone" -AccessRight Change -Force
icacls "C:\ituaicctv\backend\data\evidence" /grant "*S-1-1-0:(OI)(CI)M"

Revoke-SmbShareAccess -Name "ituaicctv-evidence" -AccountName "Everyone" -Force
Grant-SmbShareAccess -Name "ituaicctv-evidence" -AccountName "Everyone" -AccessRight Read -Force
icacls "C:\ituaicctv\backend\data\evidence" /remove:g "*S-1-1-0"
Get-SmbShareAccess -Name "ituaicctv-evidence"
```

## Exit Codes

- 0 = ok / no attention required / no person detected.
- 2 = attention required / person detected; this is an operational alert, not a crash.
- Other non-zero failures should be checked in backend/data/task-logs/monitor_person_all.log.

## Latest AI Features

- YOLO person detection from Hikvision RTSP streams.
- PERSON_CONFIDENCE_THRESHOLD defaults to 0.60. This reduces false positives but can miss distant or low-light people.
- Telegram person alerts include confidence and active threshold when available.
- New person evidence uses a clearer composite image: full CCTV frame with bounding boxes plus a zoom crop of the highest-confidence person.
- The crop is labelled as person review evidence, not face identity evidence. Low-resolution sub-stream crops may be marked LOW-RES CROP / FACE ID NOT SUITABLE.
- Face recognition readiness is false by default until a face is detected from suitable high-resolution evidence. No identity recognition or face database is implemented.
- Future reliable face recognition should capture a high-resolution main-stream or snapshot frame after person_detected=True while keeping fast person detection on the sub-stream.
- Composite evidence keeps the existing filename pattern: person_detected_<camera_id>_<timestamp>.jpg
- If composite generation fails, the fallback is the boxed full-frame evidence image.
- Telegram sends the saved evidence image, so new detections use the clearer composite.

## Latest Dashboard UI

/dashboard-ui is now a dark AI Command Center dashboard with:

- LIVE AI MONITORING pulsing indicator
- animated scan line
- summary cards
- AI Status / Health section
- latest AI event card
- event timeline
- evidence gallery
- camera grid cards
- section scroll navigation
- Refresh now loading state
- hover/glow effects
- person-detected pulse/glow
- prefers-reduced-motion support

/dashboard-tv is available for fullscreen office/security-monitor display. It reuses the same dashboard APIs and is optimized for 16:9 TV layouts with:

- large readable status cards
- LIVE AI MONITORING badge
- latest AI alert panel
- selectable MJPEG Live Camera View proxied by the backend for one selected camera
- latest evidence snapshot in a smaller historical evidence panel
- compact event timeline
- compact camera health strip
- 30-second auto-refresh
- Fullscreen button and F keyboard shortcut
- R keyboard shortcut for refresh

The browser does not connect to RTSP directly and never receives CCTV credentials. `/dashboard-tv` uses the backend MJPEG proxy for the selected live camera, while `/dashboard/live/{camera_id}/snapshot.jpg` remains available as a lightweight fallback/manual snapshot path. MJPEG is intended for one selected TV view, not all cameras at once; future scaling work should consider WebRTC or HLS.

Dashboard navigation:

- Refresh now reloads dashboard data.
- Summary / Health / Latest events / Evidence / Cameras scroll to same-page sections.
- Copy Evidence Folder Path may be blocked by browser clipboard permissions over HTTP; manually copy \\192.168.1.254\ituaicctv-evidence if needed.

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

First production deployment (2026-07-03):

- Backend deployed on the Windows Server as a Windows Service (ITUAICCTVBackend) via NSSM, auto-start enabled, confirmed Running.
- Production backend path: C:\ituaicctv.
- Server LAN IP: 192.168.1.254.
- Production dashboard URL on LAN / Teleport: http://192.168.1.254:8000/dashboard-ui.
- Local 127.0.0.1 dashboard URLs are only for browsing on the machine running the backend.
- GitHub Pages is no longer the primary production dashboard; daily operation uses the Windows Server backend dashboard.
- Firewall opens port 8000 for backend dashboard/API access.
- Person Monitor scheduled task is registered and confirmed Ready.
- Dashboard confirmed reachable across the LAN / Teleport.
- Server setup PowerShell scripts fixed for Windows PowerShell 5.1 (project-root path, PS7-only null-conditional operator, non-ASCII em-dash) and SETUP_GUIDE.txt rewritten for a clean-server install.

Production evidence and logs:

- Evidence images are saved only when person_detected=True.
- no_person events usually have evidence_path=null and no evidence image.
- Person detection now uses PERSON_CONFIDENCE_THRESHOLD with a safer default of 0.60 for person-only detections and monitor alerts.
- YOLO_CONFIDENCE remains available for general YOLO detection; tune PERSON_CONFIDENCE_THRESHOLD first when reducing false person alerts.
- Telegram person alerts include the highest available person confidence and active threshold when the event contains detection confidence data.
- Evidence snapshots for person events use the person snapshot path, which draws YOLO bounding boxes and confidence labels on the saved image.
- Production evidence folder: C:\ituaicctv\backend\data\evidence.
- Production task log folder: C:\ituaicctv\backend\data\task-logs.
- Production service log folder: C:\ituaicctv\backend\data\service-logs.
- Evidence SMB share: \\192.168.1.254\ituaicctv-evidence.
- Share physical path: C:\ituaicctv\backend\data\evidence.
- Dashboard includes Refresh Evidence and Copy Evidence Folder Path actions. If the browser blocks direct folder access, paste the UNC path into File Explorer.
- Laptop evidence folders are not production evidence storage, and the laptop should not run the production scheduler while the server is the production backend.

Latest successful server scheduler run:

- Task: ITU AI CCTV Person Monitor.
- Run started: Fri 03/07/2026 22:59:30.
- Run ended: Fri 03/07/2026 23:00:03.
- Enabled cameras: 9.
- Attention/person: 0.
- No action/no_person: 9.
- Failed: 0.
- Exit code: 0.
- Server uses C:\ituaicctv\.venv312\Scripts\python.exe.
- YOLOv8n downloaded successfully on the server during the first successful run.

Next recommended work:

1. Review recent person alerts at PERSON_CONFIDENCE_THRESHOLD=0.60 before lowering the threshold.
2. Dashboard production polish and evidence review workflow
3. Investigate block_f_cam_8 network/IP
4. Avoid overlapping scheduler runs if check-all takes too long
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
GET /dashboard-tv
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

1. Dashboard production polish and evidence review workflow
2. Investigate block_f_cam_8 network/IP
3. Avoid overlapping scheduler runs if check-all takes too long
4. Later: face detection planning
5. Later: number plate recognition planning

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
