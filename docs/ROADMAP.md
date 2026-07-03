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

Status: In progress

Goal:

Support all Block E and Block F CCTV cameras using a camera registry.

Planned features:

- Camera registry using backend/config/cameras.json
- Camera audit endpoint
- Camera-specific detection
- Camera-specific monitor check
- Monitor all enabled cameras
- Per-camera event log and evidence path

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

Status: Planned

Goal:

Provide a clean web dashboard for monitoring and review.

Planned features:

- Camera list
- Camera health status
- Latest events
- Event statistics
- Evidence viewer
- Search and filter
- Future face recognition view
- Future plate recognition view

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

Next dashboard work:

- Per-camera detail endpoint
- Frontend dashboard UI

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

- Evidence summary endpoint
- Camera health dashboard endpoint
- Latest events endpoint
- Per-camera detail endpoint
- Frontend dashboard UI
