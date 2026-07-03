# ITU AI CCTV - Project Status

Last updated: 2026-07-03

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
- Dashboard UI includes auto-refresh every 30 seconds, last updated time, next refresh countdown, quick links/buttons, improved badges, clickable evidence thumbnails, Health card, and per-camera health badges.
- backend/app/dashboard_health.py exists.
- tests/test_dashboard_health.py exists.
- Unit test passed with: python -m unittest discover -s tests -p "test_*.py" -v
- Compile passed with: python -m compileall backend/app
- sambung.txt is a private local handoff note and should not be committed.

Next recommended work:

1. Improve block_f_cam_8 metadata if not already committed
2. Add camera health from scheduler log
3. Enhance dashboard health card
4. Investigate block_f_cam_8 network/IP issue
5. Later: face detection planning
6. Later: number plate recognition planning

## Current Project Goal

Build an internal AI CCTV backend system using existing Hikvision CCTV infrastructure at ITU Melaka.

The long-term target is to create a self-managed AI CCTV system with:

- Multi-camera CCTV monitoring
- Person detection
- Event logging
- Evidence snapshot storage
- Face detection and recognition
- Vehicle and number plate recognition
- Dashboard and alerting system

## Current Working Foundation

The backend is currently running on FastAPI and has been tested locally using a Hikvision CCTV RTSP stream.

## Current Status Snapshot

Completed foundation and dashboard features:

- RTSP frame capture
- YOLOv8n person detection
- Person snapshot endpoint
- Event logging
- Evidence image save and view
- Event stats
- Multi-camera registry
- Camera audit
- Check-all monitor
- Dashboard summary API
- Dashboard health API
- Per-camera dashboard event endpoints
- Lightweight browser dashboard
- Dashboard auto-refresh and status UI polish
- Dashboard health card with per-camera health badges

Current camera status:

- Total cameras: 10
- Enabled cameras: 9
- Disabled cameras: 1
- Disabled camera: block_f_cam_8 / 192.168.40.20
- Status: offline
- Reason: ping and RTSP port 554 are not reachable

Important dashboard URLs:

- /dashboard-ui
- /dashboard/summary
- /dashboard/health
- /dashboard/cameras
- /dashboard/events/latest
- /dashboard/evidence
- /dashboard/cameras/{camera_id}/latest-event
- /dashboard/cameras/{camera_id}/stats

Current scheduler status:

- Task name: ITU AI CCTV Person Monitor
- State: intentionally Disabled
- BAT launcher returns 0 to Task Scheduler
- Main script: backend/scripts/monitor_person_all_once.py
- BAT launcher: backend/scripts/run_monitor_person_all_once.bat
- Hidden VBS launcher: backend/scripts/run_monitor_person_all_once_hidden.vbs
- Runtime log: backend/data/task-logs/monitor_person_all.log

## Confirmed Working Camera

| Camera ID | Name | IP Address | Channel | Status |
|---|---|---:|---:|---|
| block_f_cam_9 | ITU BLOCK F CAM9 | 192.168.40.21 | 102 | Confirmed working |
| block_e_cam_2 | ITU BLOCK E CAM2 | 192.168.40.14 | 102 | Person detection confirmed |

## Camera Stream Configuration

Recommended CCTV stream for AI processing:

| Setting | Value |
|---|---|
| Stream Type | Sub-stream |
| Codec | H.264 |
| Resolution | 640x360 |
| RTSP Channel | 102 |
| Bitrate | Around 512 Kbps |

Avoid H.265 / HEVC for backend AI processing because OpenCV may timeout or fail to decode the stream reliably on Windows.

## Working Backend Features

### Camera

- GET /cameras/list
- GET /cameras/enabled
- GET /cameras/test
- GET /cameras/snapshot
- GET /cameras/{camera_id}/test

### Detection

- GET /detections/test
- GET /detections/yolo
- GET /detections/yolo/snapshot
- GET /detections/person
- GET /detections/person/snapshot
- GET /detections/{camera_id}/person
- GET /detections/{camera_id}/person/snapshot

### Events

- GET /events/person
- GET /events/logs
- GET /events/stats
- GET /events/evidence/{filename}

### Monitor

- GET /monitor/person/check
- GET /monitor/{camera_id}/person/check
- GET /monitor/person/check-all

### Dashboard

- GET /dashboard-ui
- GET /dashboard/summary
- GET /dashboard/cameras
- GET /dashboard/events/latest
- GET /dashboard/evidence
- GET /dashboard/cameras/{camera_id}/latest-event
- GET /dashboard/cameras/{camera_id}/stats

## Local Scheduler Status

Windows Task Scheduler pilot has been created:

Task name:

ITU AI CCTV Person Monitor

Current behaviour:

- Uses the multi-camera monitor launcher
- Checks enabled cameras from the camera registry
- Writes output to backend/data/task-logs/monitor_person_all.log
- Uses hidden VBS launcher to avoid CMD popup
- BAT launcher returns 0 to Task Scheduler
- Currently intentionally Disabled until operational testing is ready

## Runtime Data

Runtime files are not committed to GitHub.

Ignored runtime paths:

- backend/data/events.jsonl
- backend/data/task-logs/
- backend/data/evidence/
- *.pt YOLO model weights

## Current Development Focus

The project now has a lightweight dashboard health endpoint and health card based on existing camera config and event logs.

Next technical focus:

1. Improve block_f_cam_8 metadata if not already committed
2. Add camera health from scheduler log
3. Enhance dashboard health card
4. Investigate block_f_cam_8 network/IP issue
5. Later: face detection planning
6. Later: number plate recognition planning

## Latest Milestone - Multi-Camera Scheduler

Updated: 2026-07-03

Multi-camera monitoring is now working.

Confirmed:

- GET /cameras/audit works
- GET /monitor/person/check-all works
- 9 enabled cameras can be monitored
- 1 camera is disabled temporarily:
  - block_f_cam_8
  - 192.168.40.20
  - Reason: not reachable by ping or RTSP port 554
- Multi-camera scheduler script works:
  - backend/scripts/monitor_person_all_once.py
  - backend/scripts/run_monitor_person_all_once.bat
  - backend/scripts/run_monitor_person_all_once_hidden.vbs
- Windows Task Scheduler action has been updated to use the multi-camera hidden VBS launcher
- Task Scheduler is intentionally kept disabled until operational testing is complete

Current working monitoring flow:

Camera registry
? enabled cameras only
? person detection per camera
? event log
? evidence snapshot if person detected
? task log


## Latest Milestone - Dashboard-Ready Monitor Summary

Updated: 2026-07-03

Dashboard-ready person monitor summary endpoint has been added:

- GET /monitor/person/summary

This endpoint runs multi-camera person monitoring and returns a compact response suitable for a future dashboard.

Current summary output includes:

- enabled_cameras_count
- attention_required_count
- no_action_count
- failed_count
- attention_cameras
- failed_cameras
- cameras summary list

Confirmed test result:

- enabled_cameras_count: 9
- attention_required_count: 0
- no_action_count: 9
- failed_count: 0

Current enabled cameras:

- block_e_cam_1
- block_e_cam_2
- block_e_cam_3
- block_e_cam_4
- block_e_cam_5
- block_f_cam_6
- block_f_cam_7
- block_f_cam_9
- block_f_cam_10

Disabled camera:

- block_f_cam_8
- IP: 192.168.40.20
- Reason: not reachable by ping or RTSP port 554

Dashboard endpoint example:

GET /monitor/person/summary

## Latest Milestone - Dashboard Summary Endpoint

Updated: 2026-07-03

A new dashboard summary endpoint has been added:

- GET /dashboard/summary

This endpoint is lightweight because it reads existing camera configuration and event logs only. It does not run YOLO detection.

Current confirmed output:

- cameras_total: 10
- cameras_enabled: 9
- cameras_disabled: 1
- total_events: 114
- person_detected_count: 8
- no_person_count: 106
- evidence_count: 8
- cooldown_skipped_count: 0

Disabled camera:

- block_f_cam_8
- IP: 192.168.40.20
- Current issue: not reachable by ping or RTSP port 554

Dashboard summary links included:

- /cameras/audit
- /monitor/person/summary
- /monitor/person/check-all
- /events/logs
- /events/stats

## Latest Milestone - Lightweight Dashboard Endpoints

Updated: 2026-07-03

Additional lightweight dashboard endpoints have been added:

- GET /dashboard/evidence
- GET /dashboard/cameras
- GET /dashboard/events/latest

These endpoints read existing runtime data only:

- backend/data/evidence/
- backend/config/cameras.json
- backend/data/events.jsonl

They do not run YOLO detection or open CCTV streams.

Dashboard evidence responses include:

- filename
- url using /events/evidence/{filename}
- modified_time
- size_bytes

Dashboard camera responses include camera totals and a credential-safe camera list.

Dashboard latest events responses are sorted newest first and include evidence_url when an event has an evidence image.

## Latest Milestone - Per-Camera Dashboard Endpoints

Updated: 2026-07-03

Per-camera dashboard endpoints have been added:

- GET /dashboard/cameras/{camera_id}/latest-event
- GET /dashboard/cameras/{camera_id}/stats

These endpoints validate camera_id against backend/config/cameras.json and return 404 when the camera is unknown.

They read backend/data/events.jsonl only and do not run YOLO detection or open CCTV streams.

Dashboard latest-event response includes:

- camera_id
- latest_event, or null when no event exists
- evidence_url when the latest event has evidence

Dashboard per-camera stats response includes:

- camera_id
- total_events
- person_events
- latest_event_time
- latest_evidence_url

## Latest Milestone - Lightweight Dashboard UI

Updated: 2026-07-03

A simple browser dashboard UI has been added:

- GET /dashboard-ui

The page is mobile-friendly and uses the existing dashboard API endpoints only:

- /dashboard/summary
- /dashboard/health
- /dashboard/cameras
- /dashboard/events/latest
- /dashboard/evidence
- /dashboard/cameras/{camera_id}/stats

The dashboard UI shows:

- camera total, enabled, and disabled counts
- disabled camera list
- latest event summary
- latest 10 events
- clickable evidence thumbnails and links
- camera list with enabled or disabled badges
- per-camera total and person event counts
- health card
- per-camera health badges
- last updated time
- 30-second auto-refresh countdown
- quick links to summary, cameras, latest events, and evidence APIs

The UI does not run YOLO detection, does not open CCTV streams, and does not expose credentials or RTSP URLs.

## Latest Milestone - Dashboard Summary Endpoint

Updated: 2026-07-03

A new dashboard summary endpoint has been added:

- GET /dashboard/summary

This endpoint is lightweight because it reads existing camera configuration and event logs only. It does not run YOLO detection.

Current confirmed output:

- cameras_total: 10
- cameras_enabled: 9
- cameras_disabled: 1
- total_events: 114
- person_detected_count: 8
- no_person_count: 106
- evidence_count: 8
- cooldown_skipped_count: 0

Disabled camera:

- block_f_cam_8
- IP: 192.168.40.20
- Current issue: not reachable by ping or RTSP port 554

Dashboard summary links included:

- /cameras/audit
- /monitor/person/summary
- /monitor/person/check-all
- /events/logs
- /events/stats
