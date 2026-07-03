# ITU AI CCTV Backend

FastAPI backend for CCTV RTSP testing, snapshot capture, YOLO detection, person-only detection, event decision, local logging, and evidence snapshot preparation.

## Current Features

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

## Folder Structure

backend/
  app/
    main.py
    config.py
    camera.py
    detection.py
    events.py
    event_log.py
    routes/
      health.py
      cameras.py
      detections.py
      events.py
  data/
    events.jsonl
    evidence/
  .env.example
  requirements.txt
  README.md

Runtime files under backend/data are ignored from Git.

## Run Backend

From project root:

.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000/docs

## CCTV Configuration

Recommended stream for AI processing:

Stream Type      : Sub-stream
RTSP Channel     : 102
Video Encoding   : H.264
Resolution       : 640x360
Bitrate          : 512 Kbps
Frame Rate       : 10-20 fps

Avoid H.265 / HEVC for OpenCV snapshot and AI processing on Windows.

## Environment

Local backend/.env example:

APP_NAME=ITU AI CCTV Backend
APP_ENV=development

CCTV_HOST=192.168.40.21
CCTV_PORT=554
CCTV_USERNAME=your_username
CCTV_PASSWORD=your_password
CCTV_CHANNEL=102

Never commit backend/.env.

## Event Logging

When GET /events/person is called, the backend:

1. Captures one CCTV frame
2. Runs person-only YOLO detection
3. Creates event decision
4. Saves the event to backend/data/events.jsonl
5. Saves evidence image only if person_detected is true

No-person event example:

event_type      : no_person
severity        : none
person_detected : false
evidence_path   : null

Person event example:

event_type      : person_detected
severity        : medium
person_detected : true
evidence_path   : data/evidence/person_detected_timestamp.jpg

## Troubleshooting

If uvicorn is not recognized, use:

python -m uvicorn app.main:app --reload

If RTSP connects but snapshot fails, check whether the stream is H.265. Change CCTV sub-stream to H.264 and use channel 102.

Check RTSP port:

Test-NetConnection 192.168.40.21 -Port 554

Check HTTPS camera web UI:

Test-NetConnection 192.168.40.21 -Port 443

Open camera web UI:

https://192.168.40.21
