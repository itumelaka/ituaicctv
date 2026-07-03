# ITU AI CCTV Backend

FastAPI backend for CCTV RTSP testing, snapshot capture, YOLO detection, person-only detection, event decision, local logging, evidence snapshot, multi-camera monitoring, and dashboard UI.

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
GET /events/stats
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
```

### Dashboard UI

```
GET /dashboard-ui
```

Full HTML dashboard served directly by the backend. Auto-refreshes every 30 seconds. Loads data from all dashboard endpoints.

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
    task-logs/
      monitor_person_all.log
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
PERSON_EVENT_COOLDOWN_SECONDS=300
```

Never commit `backend/.env`.

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

Cameras are configured in `backend/data/cameras.json`. Each camera entry:

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
