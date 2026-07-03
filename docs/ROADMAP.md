# ITU AI CCTV - Roadmap

## Phase 1 - Backend Foundation

Status: Completed

- FastAPI backend
- Health check
- RTSP camera connection
- CCTV snapshot
- YOLOv8n integration
- Person detection
- Event logging
- Evidence snapshot
- Windows Task Scheduler pilot

## Phase 2 - Multi-Camera Monitoring

Status: Completed foundation

Goal:

Support all Block E and Block F CCTV cameras using a camera registry.

Completed features:

- Camera registry using backend/config/cameras.json
- Camera audit endpoint
- Camera-specific detection
- Camera-specific monitor check
- Monitor all enabled cameras
- Per-camera event log and evidence path

Current camera summary:

- Total cameras: 10
- Enabled cameras: 9
- Disabled cameras: 1
- block_f_cam_8 / 192.168.40.20 is disabled because ping and RTSP port 554 are not reachable

## Phase 3 - Stable Local Monitoring

Status: Planned

Goal:

Run AI CCTV monitoring automatically on an always-on machine.

Planned features:

- Multi-camera monitor script
- Windows Task Scheduler configuration
- Runtime cleanup script
- Log rotation
- Evidence retention policy
- Windows Server deployment guide

## Phase 4 - Face Detection and Recognition

Status: Planned

Goal:

Build a controlled face detection and recognition module.

Important note:

Face recognition involves biometric data. It must be implemented with proper policy, consent, access control, and retention rules.

Planned features:

- Face detection only
- Face crop evidence
- Authorised face enrolment
- Known person matching
- Confidence threshold
- Recognition event log

## Phase 5 - Vehicle and Number Plate Recognition

Status: Planned

Goal:

Detect vehicles and read number plates where camera angle is suitable.

Planned features:

- Vehicle detection
- Plate detection
- Plate OCR
- Plate event logging
- Evidence snapshot
- Search by plate number

## Phase 6 - Dashboard

Status: In progress

Goal:

Provide a clean web dashboard for monitoring and review.

Planned features:

- Camera list - completed
- Latest events - completed
- Event statistics - completed
- Evidence viewer - completed
- Dashboard summary API - completed
- Per-camera dashboard event endpoints - completed
- Lightweight browser dashboard - completed
- Dashboard auto-refresh/status UI polish - completed
- Camera health status - next
- Search and filter
- Future face recognition view
- Future plate recognition view

Important dashboard URLs:

- /dashboard-ui
- /dashboard/summary
- /dashboard/cameras
- /dashboard/events/latest
- /dashboard/evidence
- /dashboard/cameras/{camera_id}/latest-event
- /dashboard/cameras/{camera_id}/stats

## Phase 7 - Production Deployment

Status: Planned

Goal:

Deploy the system to a dedicated Windows Server or always-on local machine.

Planned features:

- Windows Server setup
- Production .env
- Scheduled monitoring
- Backup strategy
- Access control
- Documentation

## Roadmap Update - Dashboard API Foundation

Status: In progress

A dashboard-ready monitor summary endpoint has been added:

- GET /monitor/person/summary

This is the first backend endpoint designed specifically for future dashboard use.

Planned next dashboard APIs:

- Latest events summary
- Evidence summary
- Per-camera latest event
- Per-camera statistics
- Camera health overview

Future dashboard pages:

- Camera status page
- Latest detection events
- Evidence viewer
- Person detection summary
- Future face recognition summary
- Future number plate recognition summary

## Roadmap Update - Dashboard Summary

Status: In progress

The first dashboard-level endpoint has been completed:

- GET /dashboard/summary

This endpoint provides a lightweight overview for a future web dashboard without triggering new AI detection.

Dashboard foundation currently includes:

- Camera count summary
- Disabled camera list
- Event statistics
- Latest event
- Latest 10 events
- Useful backend links

Next dashboard work:

- Per-camera detail endpoint
- Camera health dashboard endpoint
- Frontend dashboard UI

## Roadmap Update - Lightweight Dashboard Data APIs

Status: Completed

The dashboard API foundation now includes lightweight read-only endpoints:

- GET /dashboard/evidence
- GET /dashboard/cameras
- GET /dashboard/events/latest

These endpoints support the future dashboard evidence viewer, camera list, and latest events page without triggering YOLO detection or opening CCTV streams.

Dashboard data now available:

- Evidence image metadata with /events/evidence/{filename} links
- Credential-safe camera list from backend/config/cameras.json
- Latest event log entries from backend/data/events.jsonl
- Per-camera latest event and event stats
- Lightweight browser dashboard at /dashboard-ui

Next dashboard work:

- GET /dashboard/health
- Camera health/offline summary
- Latest successful check per camera
- Dashboard health card
- Investigate block_f_cam_8

## Roadmap Update - Per-Camera Dashboard APIs

Status: Completed

Per-camera dashboard API endpoints have been added:

- GET /dashboard/cameras/{camera_id}/latest-event
- GET /dashboard/cameras/{camera_id}/stats

These endpoints make the dashboard camera detail view possible without triggering YOLO detection. Unknown camera IDs return 404 after validation against backend/config/cameras.json.

Dashboard camera detail data now available:

- Latest event for a configured camera
- Per-camera total event count
- Per-camera person event count
- Latest event timestamp
- Latest evidence link when available

## Roadmap Update - Lightweight Dashboard UI

Status: Completed

A simple mobile-friendly browser dashboard has been added:

- GET /dashboard-ui

The page consumes existing dashboard API endpoints only and does not run YOLO detection.

Dashboard UI currently includes:

- camera totals
- disabled camera list
- latest event summary
- latest 10 events
- clickable evidence thumbnails and links
- camera enabled or disabled badges
- per-camera total and person event counts
- last updated time and next refresh countdown
- 30-second auto-refresh
- quick links to refresh, summary, cameras, latest events, and evidence

Next dashboard work:

- GET /dashboard/health
- Camera health/offline summary
- Latest successful check per camera
- Dashboard health card
- Investigate block_f_cam_8
- Later: face detection planning
- Later: number plate recognition planning

## Roadmap Update - Dashboard Summary

Status: In progress

The first dashboard-level endpoint has been completed:

- GET /dashboard/summary

This endpoint provides a lightweight overview for a future web dashboard without triggering new AI detection.

Dashboard foundation currently includes:

- Camera count summary
- Disabled camera list
- Event statistics
- Latest event
- Latest 10 events
- Useful backend links

Next dashboard work:

- GET /dashboard/health
- Camera health/offline summary
- Latest successful check per camera
- Dashboard health card
- Investigate block_f_cam_8
- Later: face detection planning
- Later: number plate recognition planning
