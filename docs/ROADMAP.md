# ITU AI CCTV - Roadmap

## Current Production Roadmap Context

Production is now running from `C:\ituaicctv` on the Windows Server with backend dashboard at `http://192.168.1.254:8000/dashboard-ui`. GitHub Pages is no longer the primary dashboard. Latest deployed work includes:

- e2e7f8f feat: add ignore zones and event review workflow
- bd556ec fix: correct and rename additional CCTV cameras
- aa62e5b feat: add additional CCTV cameras to inventory
- 7b8271e fix: add tv dashboard link to normal dashboard
- 6da444a docs: document tv dashboard mjpeg live stream
- 073424a fix: improve dashboard tv live camera selection
- b89afba feat: add mjpeg live camera stream to tv dashboard

Operational foundation:

- Backend service `ITUAICCTVBackend` is Running and Automatic.
- Primary alerting task `ITU AI CCTV Live Monitor` is Running as a startup-triggered long-running Windows Task Scheduler task.
- Old 5-minute scheduler task `ITU AI CCTV Person Monitor` is Disabled and retained only as backup.
- Camera registry has 13 known cameras, 12 enabled cameras, and 1 disabled/offline camera.
- One camera remains disabled/offline: `block_f_cam_8 / ITU BLOCK F CAM8`.
- Newly confirmed enabled cameras: `kuarantin_cam_11` / `192.168.40.23`, `biosekuriti_cam_12` / `192.168.40.24`, and `makmal_cam_13` / `192.168.40.25`.
- Evidence is saved only for `person_detected=True`.
- New evidence is a composite full-frame-plus-zoom-crop image.
- The person crop is review evidence only. Low-resolution sub-stream crops are not suitable proof for face identity recognition.
- Face readiness metadata is now advisory groundwork only: local face detection availability, face count, best face box, quality, readiness, and reasons. It does not identify people.
- Optional internal staff/student recognition foundation is config-controlled and disabled by default. It supports local backend selection with `auto`, `face_recognition`, and OpenCV LBPH when `opencv-contrib-python` provides `cv2.face`.
- Production currently has OpenCV LBPH available and a test internal label `BURN` enrolled. This remains approved internal-use only and is not high-security identity proof.
- Fullscreen TV Command Center mode is available at `/dashboard-tv`.
- TV mode now separates a selectable backend-proxied MJPEG live camera view from historical evidence snapshots.
- Direct selected-camera stream endpoint is available at `/dashboard/live/{camera_id}/stream.mjpg` with a 4 FPS limit; `/dashboard/live/{camera_id}/snapshot.jpg` remains as fallback.
- Live view quality selection supports `quality=standard` for the configured camera channel, usually 102, and `quality=hd` for Hikvision main-stream channel 101. Invalid quality values return HTTP 400. HD MJPEG allows a larger 1920px max width, but actual resolution depends on camera main-stream settings and may still be 720p. This is viewing only and does not change detection, alerts, evidence, event review, ignore zones, or live monitor behavior.
- MJPEG live view has no audio. Audio depends on camera audio availability and a future HLS/WebRTC/FFmpeg proxy.
- Near-live monitoring runs repeated sequential scan cycles. Configured interval is 10 seconds, but real full-cycle time is about 30 seconds because 12 enabled cameras are scanned sequentially.
- Telegram group alerts are verified for the internal monitoring group. Bot token and numeric chat ID remain private configuration.
- Event review / acknowledgement is deployed and verified through API endpoints and `/dashboard-ui` buttons, but it remains an internal local workflow with no user login/authentication yet.
- Ignore-zone polygon support is deployed. Current kuarantin_cam_11 and makmal_cam_13 placeholders remain disabled until accurate coordinates are calibrated.

## Forward Backlog

1. Person detection reliability: per-camera thresholds, minimum bounding box size, calibrated ignore-zone/polygon masks for known static false positives such as trees, topiary, or fixed pipes, and better dashboard review metrics.
2. Zone intrusion detection: polygon zones per camera and restricted zone alerts.
3. Line crossing detection: virtual line and direction.
4. Loitering detection: duration-based alert.
5. Vehicle detection and parking monitoring.
6. Number plate recognition as a future module.
7. Camera health AI: blur, dark, blocked, angle changed, stale frame.
8. Human review workflow: event review metadata now supports valid, false positive, ignored, and follow-up statuses; future work should add unreviewed/false-positive/follow-up filters, notes, exports, review audit log, and authenticated users.
9. AI risk score: confidence, zone, after-hours, camera importance.
10. After-hours detection.
11. Improve fullscreen command center / TV mode after real TV review.
12. WebRTC/HLS/media-server upgrade for better live-view scaling if multiple viewers or cameras need streaming.
13. Harden the live monitor operation with clearer status reporting, overlap protection, CPU/network observation before lowering scan intervals, and camera-health alerts if failed counts increase.
14. Face detection and safe opt-in face recognition roadmap, including high-resolution evidence capture before any identity pilot.
15. Optional Telegram send-as-document evidence delivery to reduce Telegram photo compression.
16. CSV-based private face enrollment mapping for staff/student sources, without hardcoding source folders in application code.
17. Calibrate and enable ignore-zone polygons only after screenshot/evidence review confirms coordinates.
18. Add daily Telegram summary report to the internal monitoring group.
19. Add audio-capable live view only if camera microphone/audio streams are available, likely through HLS/WebRTC/FFmpeg rather than MJPEG.
20. Add visual ignore-zone editor for calibrated polygon setup.
21. Add private CSV enrollment mapping, face-recognition audit logs, and retention/deletion policy.

## Current Checkpoint

Latest confirmed commit:

e2e7f8f

Checkpoint summary:

- Production backend is live on the Windows Server at C:\ituaicctv.
- Production dashboard is http://192.168.1.254:8000/dashboard-ui for LAN / Teleport access.
- GitHub Pages is no longer the primary production dashboard; daily operation uses the Windows Server backend dashboard.
- Backend service listens on 0.0.0.0:8000 with Windows Firewall inbound rule ITU AI CCTV Backend Port 8000.
- Primary `ITU AI CCTV Live Monitor` task is Running. The old 5-minute `ITU AI CCTV Person Monitor` task is Disabled and retained as backup.
- Event review / acknowledgement workflow is deployed and verified.
- Ignore-zone polygon support is deployed, with kuarantin_cam_11 and makmal_cam_13 placeholders still disabled.
- Telegram group alert delivery is verified for the internal monitoring group.
- Evidence share is available at \\192.168.1.254\ituaicctv-evidence, mapped to C:\ituaicctv\backend\data\evidence.
- Evidence images are saved only when person_detected=True; no_person events usually do not have evidence images.

- Backend FastAPI works.
- Hikvision RTSP works.
- Multi-camera config has 13 cameras: 12 enabled and 1 disabled/offline.
- Disabled camera: block_f_cam_8 / 192.168.40.20.
- Disabled camera reason: ping and RTSP port 554 are not reachable.
- GET /dashboard-ui is usable.
- GET /dashboard/health is usable.
- Dashboard UI includes auto-refresh, status timing, quick links, improved badges, clickable evidence thumbnails, Health card, and per-camera health badges.
- Dashboard health includes scheduler log summary when backend/data/task-logs/monitor_person_all.log is available.
- Scheduler summary in GET /dashboard/health is usable.
- Stale camera health logic in GET /dashboard/health is usable.
- Dashboard stale/offline visual polish is usable.
- Scheduler BAT now resolves project root dynamically and supports .venv312 before falling back to .venv or python from PATH.
- Unit tests and compile checks passed at this checkpoint.
- sambung.txt is a private local handoff note and should not be committed.

Next recommended work:

1. Dashboard production polish and evidence review workflow
2. Investigate block_f_cam_8 network/IP
3. Avoid overlapping scheduler runs if check-all takes too long
4. Later: face detection planning
5. Later: number plate recognition planning

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

- Total cameras: 13
- Enabled cameras: 12
- Disabled cameras: 1
- block_f_cam_8 / 192.168.40.20 is disabled because ping and RTSP port 554 are not reachable

## Phase 3 - Stable Local Monitoring

Status: Planned

Goal:

Run AI CCTV monitoring automatically on an always-on machine.

Planned features:

- Multi-camera monitor script
- Windows Task Scheduler configuration - operational checkpoint completed
- Optional near-live continuous monitor script - completed
- Runtime cleanup script
- Log rotation
- Evidence retention policy
- Windows Server deployment guide

## Phase 4 - Face Detection and Recognition

Status: Foundation started; operational recognition remains opt-in and policy-gated

Goal:

Build a controlled face module in phases. Do not implement automatic identity recognition until person detection reliability, privacy controls, and review workflow are ready.

Important note:

Face recognition involves biometric data. It must be used only with clear authorization, consent or policy, access control, and retention rules.

Phased approach:

1. Face detection/readiness only, no identity recognition.
2. Face crop saving linked to existing person detection evidence.
3. Opt-in internal staff/student recognition using approved reference images only.
4. Dashboard review and human confirmation before any operational identity action.

Operational constraints:

- Do not store random unknown face identities by default.
- Do not expose a face database through public routes, public shares, screenshots, or Git.
- Never commit face images, face embeddings, or personal identity data.
- Keep face reference data local and private on the production server.
- Telegram alerts should avoid unnecessary personal data. Prefer "face present" or "review required" over names unless policy explicitly allows it.
- Person detection can stay on a lightweight sub-stream, but reliable face review or recognition requires a higher-resolution evidence frame or snapshot after person_detected=True.
- Camera placement, distance, lens angle, lighting, and source resolution can make face identity recognition unsuitable even when person detection is correct.
- Current face readiness fields are advisory quality metadata only. They must not be interpreted as identity matches.
- Current recognition plumbing is disabled by default through `FACE_RECOGNITION_ENABLED=false`. Recognition should only be enabled for approved internal staff/student enrollment.
- `FACE_RECOGNITION_BACKEND=auto` prefers the optional `face_recognition` library, then OpenCV LBPH, then safely reports unavailable. LBPH is a lightweight local baseline, not high-security identity proof.
- `UNKNOWN` means no reliable enrolled internal match, not suspicious behavior.
- Recognition accuracy depends on camera distance, angle, lighting, motion blur, face size, and CCTV stream quality.

Proposed future private folders, documented only:

- backend/data/faces/reference/ - private approved reference images, ignored
- backend/data/faces/embeddings/ - private embeddings, ignored
- backend/data/faces/crops/ - private detected face crops, ignored

Before Phase 4 implementation:

- Finish person detection tuning and review false-positive examples.
- Keep person evidence snapshots with bounding boxes enabled for review.
- Keep fast person detection on CCTV sub-streams where useful, but capture a high-resolution main-stream or snapshot frame after person_detected=True before attempting face detection or recognition.
- Treat face_recognition_ready as false until a suitable face is detected in high-resolution evidence. Low-resolution person crops may support human review but should not be used for identity decisions.
- Define retention, approval, access, and audit rules for any face data.
- Add a formal face enrolment workflow only after policy approval. It should cover reference-image consent, private storage, access control, audit trail, deletion, and human confirmation.
- Keep Hikvision/NVR recording separate from AI evidence, face references, and embedding storage.

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

Status: In progress / production command center live

Goal:

Provide a clean web dashboard for monitoring and review.

Planned features:

- Camera list - completed
- Latest events - completed
- Event statistics - completed
- Evidence viewer - completed
- Dashboard summary API - completed
- Dashboard health API - completed
- Per-camera dashboard event endpoints - completed
- Lightweight browser dashboard - completed
- Dashboard auto-refresh/status UI polish - completed
- Camera health status - completed
- Dashboard health card - completed
- Scheduler log health summary - completed
- Stale camera health logic - completed
- Dashboard stale/offline visual polish - completed
- AI Command Center dark UI - completed
- LIVE AI MONITORING indicator and live visual effects - completed
- Section scroll navigation - completed
- Evidence gallery with clearer composite evidence - completed
- Fullscreen TV Command Center mode at /dashboard-tv - completed
- Selectable live camera snapshot panel in TV mode - completed
- Selectable backend-proxied MJPEG live camera stream in TV mode - completed
- MJPEG endpoint is one selected-camera/viewer feature at 4 FPS; browser never receives RTSP credentials
- Search and filter
- Human review actions
- TV mode visual tuning after wall-monitor review
- Future WebRTC/HLS live stream scaling or high-resolution event snapshot path
- Future face recognition view
- Future plate recognition view

Important dashboard URLs:

- /dashboard-ui
- /dashboard/summary
- /dashboard/health
- /dashboard/cameras
- /dashboard/events/latest
- /dashboard/evidence
- /dashboard/live/{camera_id}/stream.mjpg
- /dashboard/live/{camera_id}/snapshot.jpg
- /dashboard/cameras/{camera_id}/latest-event
- /dashboard/cameras/{camera_id}/stats

GET /dashboard/health currently includes:

- camera totals
- disabled/offline camera list
- event health
- scheduler summary
- per-camera active/stale/no_recent_event/disabled/offline status
- stale threshold minutes
- stale_minutes
- last_seen_source

Current dashboard health status logic:

- offline for disabled cameras with status offline
- disabled for disabled cameras
- active for enabled cameras with recent event/check
- stale for enabled cameras with old event/check
- no_recent_event for enabled cameras with no event/check yet

## Phase 7 - Production Deployment

Status: Planned

Goal:

Deploy the system to a dedicated Windows Server or always-on local machine.

Planned features:

- Windows Server setup
- Production .env
- Scheduled monitoring
- Optional near-live continuous monitoring
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

- Dashboard production polish and evidence review workflow
- Investigate block_f_cam_8 network/IP

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

- Dashboard production polish and evidence review workflow
- Investigate block_f_cam_8 network/IP

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
- scheduler latest run and summary in the Health card
- stale camera badges based on latest event/check age

Next dashboard work:

- Dashboard production polish and evidence review workflow
- Investigate block_f_cam_8 network/IP
- Later: face detection planning
- Later: number plate recognition planning

## Roadmap Update - Scheduler Log Health Summary

Status: Completed

GET /dashboard/health now includes a scheduler block based on:

- backend/data/task-logs/monitor_person_all.log

The scheduler summary reads existing log files only and returns unknown or null when values are not available.

Dashboard health now includes:

- scheduler status
- latest scheduler run time
- latest scheduler summary
- failed count
- person detected count
- no-person count
- recent safe scheduler log lines

The /dashboard-ui Health card now shows the latest scheduler run and summary without running YOLO detection or opening RTSP streams.

## Roadmap Update - Stale Camera Health

Status: Completed

GET /dashboard/health now classifies enabled cameras using the latest event/check time from backend/data/events.jsonl.

Default stale threshold:

- 120 minutes

Per-camera health now includes:

- health_status
- last_event_time
- stale_minutes
- stale_threshold_minutes
- last_seen_source

Supported camera health statuses now include:

- active
- stale
- no_recent_event
- disabled
- offline

The /dashboard-ui camera cards now show stale cameras with the warning badge style.

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

- Dashboard production polish and evidence review workflow
- Investigate block_f_cam_8 network/IP
- Later: face detection planning
- Later: number plate recognition planning

## Roadmap Update - Dashboard Stale/Offline Visual Polish

Status: Completed

The browser dashboard now shows clearer stale and offline health information from /dashboard/health.

Health card visual summary now includes:

- active count
- stale count
- no_recent_event count
- offline count
- disabled count

Camera cards now show health_status, stale_minutes, stale_threshold_minutes, last_seen_source, and health_note when available.

Badge behavior now maps active to success, stale and no_recent_event to warning, offline to danger, and disabled to muted.

## Roadmap Update - Scheduler Laptop Environment Fix

Status: Completed

The scheduler BAT launcher now resolves the project root dynamically from the script location.

Python selection order:

1. .venv312\Scripts\python.exe
2. .venv\Scripts\python.exe
3. python from PATH

This supports laptop environments where the old .venv is missing or broken but .venv312 exists.

Current expected healthy dashboard state:

- total cameras: 13
- enabled: 12
- disabled/offline: 1
- active/stale counts depend on latest live monitor events and the configured stale threshold
- live monitor task: ITU AI CCTV Live Monitor Running
- old batch task: ITU AI CCTV Person Monitor Disabled

Next operational decisions:

- Decide when to enable the scheduler task
- Investigate block_f_cam_8 / 192.168.40.20 only if it should be re-enabled later
