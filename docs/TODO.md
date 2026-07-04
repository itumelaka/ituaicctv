# ITU AI CCTV - TODO List

## Current Production TODO Context

- Production backend path: C:\ituaicctv
- Production dashboard: http://192.168.1.254:8000/dashboard-ui
- Backend service ITUAICCTVBackend is Running and Automatic.
- Task Scheduler task ITU AI CCTV Person Monitor is Ready.
- Scheduler uses C:\ituaicctv\.venv312\Scripts\python.exe.
- Scheduler scans 9 enabled cameras; latest logs show status ok and failed 0.
- Exit code 0 = ok/no attention. Exit code 2 = attention/person detected, not a crash.
- Evidence is saved only when person_detected=True.
- New evidence image behavior: full-frame boxes plus zoom crop of highest-confidence person.
- Evidence crop labels avoid implying face identity quality; low-resolution crops can be marked FACE ID NOT SUITABLE.
- Dashboard is now the dark AI Command Center served by backend /dashboard-ui.
- Fullscreen TV Command Center mode is available at /dashboard-tv.
- TV mode includes a selectable backend-proxied MJPEG live camera panel; latest evidence is shown separately as historical proof.

## Current Production Backlog

- [ ] Tune person threshold per camera.
- [ ] Add minimum bounding box size filtering for person detections.
- [ ] Add false-positive review labels in dashboard.
- [ ] Improve dashboard confidence display and review workflow.
- [ ] Add polygon zone intrusion detection per camera.
- [ ] Add restricted zone alerts.
- [ ] Add line crossing detection with direction.
- [ ] Add loitering duration alerts.
- [ ] Add vehicle detection / parking monitoring.
- [ ] Add number plate recognition as future module.
- [ ] Add camera health AI for blur/dark/blocked/angle changed/stale frame.
- [ ] Add human review actions: true positive / false positive / ignore / download.
- [ ] Add AI risk score using confidence, zone, after-hours, and camera importance.
- [ ] Add after-hours detection.
- [x] Add fullscreen command center / TV mode.
- [ ] Continue face detection and safe opt-in face recognition roadmap.
- [ ] Add high-resolution main-stream/snapshot evidence capture after person_detected=True for future face detection.
- [ ] Add explicit face evidence quality/readiness metadata before any recognition pilot.

## Production Verification Commands

```powershell
Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType
Get-ScheduledTask -TaskName "ITU AI CCTV Person Monitor" | Select-Object TaskName, State
Invoke-RestMethod http://127.0.0.1:8000/dashboard/health | ConvertTo-Json -Depth 6
```

## Current Checkpoint

Latest confirmed commit:

8352f37

Checkpoint notes:

- Production backend runs on Windows Server at C:\ituaicctv.
- Production dashboard: http://192.168.1.254:8000/dashboard-ui.
- Use 127.0.0.1 dashboard URLs only on the machine running the backend.
- GitHub Pages is no longer the primary production dashboard.
- Backend service listens on 0.0.0.0:8000 and is reachable from LAN / Teleport.
- Scheduler task ITU AI CCTV Person Monitor is Ready.
- Latest successful check-all run: enabled=9, person=0, no_person=9, failed=0, exit code 0.
- Evidence share: \\192.168.1.254\ituaicctv-evidence.
- Evidence images are saved only for person_detected=True; no_person events usually have no evidence image.

- GET /dashboard-ui is usable.
- GET /dashboard/health is usable.
- Scheduler task BAT resolves project root dynamically.
- Scheduler task supports .venv312 before falling back to .venv or python from PATH.
- Scheduler summary in GET /dashboard/health is usable.
- Stale camera health logic in GET /dashboard/health is usable.
- Dashboard UI has auto-refresh, status timing, quick links, improved badges, clickable evidence thumbnails, Health card, and per-camera health badges.
- Unit tests pass with: python -m unittest discover -s tests -p "test_*.py" -v
- Compile passes with: python -m compileall backend/app
- block_f_cam_8 / 192.168.40.20 remains disabled because ping and RTSP port 554 are not reachable.
- sambung.txt is a private local handoff note and should not be committed.

## Immediate TODO

- [ ] Improve block_f_cam_8 metadata if not already committed
- [x] Add camera health from scheduler log
- [x] Enhance dashboard health card
- [x] Add stale camera health logic
- [x] Dashboard stale/offline visual polish
- [x] Scheduler task server readiness confirmed
- [x] Document production dashboard and evidence share
- [ ] Investigate block_f_cam_8 network/IP issue
- [ ] Avoid overlapping scheduler runs if check-all takes too long
- [ ] Prepare face detection planning notes later
- [ ] Prepare number plate recognition planning notes later

## Camera Configuration TODO

Camera registry current summary:

- [x] Total cameras configured: 10
- [x] Enabled cameras: 9
- [x] Disabled cameras: 1
- [x] block_f_cam_8 / 192.168.40.20 is disabled/offline because ping and RTSP port 554 are not reachable

Camera list:

- [x] block_e_cam_1 - 192.168.40.13
- [x] block_e_cam_2 - 192.168.40.14
- [x] block_e_cam_3 - 192.168.40.15
- [x] block_e_cam_4 - 192.168.40.16
- [x] block_e_cam_5 - 192.168.40.17
- [x] block_f_cam_6 - 192.168.40.18
- [x] block_f_cam_7 - 192.168.40.19
- [x] block_f_cam_8 - 192.168.40.20 disabled/offline
- [x] block_f_cam_9 - 192.168.40.21
- [x] block_f_cam_10 - 192.168.40.22

## Backend TODO

- [x] Add camera audit summary endpoint
- [ ] Add camera readiness status
- [ ] Add ready_for_ai field in cameras.json
- [x] Add monitor all enabled cameras endpoint
- [x] Add per-camera event stats
- [x] Add per-camera latest event endpoint
- [x] Add configurable PERSON_CONFIDENCE_THRESHOLD for person-only detection
- [x] Include person detection confidence in Telegram alerts when available
- [ ] Add duplicate detection filtering
- [ ] Add configurable detection classes
- [ ] Add configurable monitoring interval
- [ ] Add structured log rotation

## Face Detection TODO

- [x] Document phased face feature roadmap
- [x] Document private future face folders without creating sensitive data
- [x] Ignore future private face data folders in Git
- [ ] Add face detection only endpoint
- [ ] Detect face presence without identifying identity
- [ ] Keep face_recognition_ready false until suitable high-resolution face evidence exists
- [ ] Capture high-resolution main-stream/snapshot evidence before any reliable face recognition attempt
- [ ] Add face crop evidence storage
- [ ] Add privacy and consent notes
- [ ] Design face enrolment flow
- [ ] Add face recognition pilot only for authorised users
- [ ] Add known persons database
- [ ] Add confidence threshold for identity matching
- [ ] Add dashboard human review and confirmation flow before identity actions

## Number Plate Recognition TODO

- [ ] Identify suitable vehicle camera angle
- [ ] Test vehicle detection
- [ ] Add plate detection model
- [ ] Add OCR for plate text
- [ ] Store plate event log
- [ ] Add plate evidence snapshot
- [ ] Add search by plate number

## Dashboard TODO

- [x] Camera status page
- [x] Latest events page
- [x] Evidence image viewer
- [x] Dashboard summary API
- [x] Per-camera dashboard event endpoints
- [x] Lightweight browser dashboard
- [x] Dashboard auto-refresh/status UI polish
- [x] GET /dashboard/health
- [x] Camera health/offline summary
- [x] Dashboard health card
- [x] Per-camera health badges
- [x] Scheduler log summary in dashboard health
- [x] Scheduler latest run and summary in dashboard UI Health card
- [x] Improve latest successful check tracking per camera
- [x] Add stale health badge support
- [x] Document active/stale/no_recent_event/disabled/offline health logic
- [x] Dashboard stale/offline visual polish
- [x] Redesign /dashboard-ui as dark AI Command Center
- [x] Add live dashboard visual effects
- [x] Add zoomed person evidence composite
- [x] Add face-identity caution labels to person crop evidence
- [x] Add /dashboard-tv fullscreen monitor mode
- [x] Add selectable live camera snapshot panel to /dashboard-tv
- [x] Add selectable MJPEG live camera stream to /dashboard-tv
- [ ] Consider WebRTC or HLS upgrade for better TV stream scaling and lower CPU/network usage
- [ ] Search by camera
- [ ] Search by date
- [ ] Search by event type
- [ ] Person detection summary
- [ ] Future face recognition summary
- [ ] Future plate recognition summary

## Deployment TODO

- [ ] Prepare Windows Server deployment guide
- [ ] Install Python on Windows Server
- [ ] Clone repo on Windows Server
- [ ] Create production .env
- [ ] Install requirements
- [ ] Test RTSP from server
- [ ] Setup Windows Task Scheduler on server
- [ ] Configure runtime data folder
- [ ] Configure backup for evidence/logs
- [ ] Add service monitoring

## Completed on 2026-07-03

- [x] Add GET /cameras/audit
- [x] Add GET /monitor/person/check-all
- [x] Create script to monitor all enabled cameras
- [x] Create BAT launcher for multi-camera monitor
- [x] Create hidden VBS launcher for Task Scheduler
- [x] Update Task Scheduler action to use multi-camera launcher
- [x] Keep scheduler disabled after manual test

## Next TODO

- [ ] Improve block_f_cam_8 metadata if not already committed
- [x] Add camera health from scheduler log
- [x] Enhance dashboard health card
- [x] Add stale camera health logic
- [x] Dashboard stale/offline visual polish
- [x] Scheduler task server readiness confirmed
- [ ] Investigate block_f_cam_8 network/IP issue
- [ ] Add event cooldown to avoid repeated evidence spam
- [ ] Add per-camera confidence threshold
- [ ] Lower block_e_cam_1 sub-stream from 1280x720 to 640x360 if CPU usage is high
- [ ] Later: prepare face detection planning notes
- [ ] Later: prepare number plate recognition planning notes

## Completed on 2026-07-03 - Dashboard Summary

- [x] Add dashboard-ready API endpoint
- [x] Add GET /monitor/person/summary
- [x] Return compact per-camera monitor status
- [x] Return attention_cameras list
- [x] Return failed_cameras list

## Remaining TODO After Dashboard Foundation

- [x] Create dashboard API for latest events summary
- [x] Create dashboard API for evidence summary
- [x] Add per-camera latest event endpoint
- [x] Add per-camera stats endpoint
- [x] Add GET /dashboard/health
- [x] Add camera health/offline summary
- [x] Add dashboard health card
- [x] Add scheduler log summary to dashboard health
- [x] Show scheduler latest run and summary in dashboard Health card
- [x] Improve latest successful check tracking per camera
- [ ] Investigate block_f_cam_8 network/RTSP issue
- [ ] Add event cooldown test with real person detection
- [ ] Later: add face detection planning notes
- [ ] Later: add number plate recognition planning notes

## Completed on 2026-07-03 - Dashboard Summary Endpoint

- [x] Add GET /dashboard/summary
- [x] Register dashboard router in FastAPI main app
- [x] Include camera total/enabled/disabled summary
- [x] Include disabled camera list
- [x] Include event statistics
- [x] Include latest event summary
- [x] Include latest 10 events
- [x] Include dashboard API links

## Next Dashboard TODO

- [x] Add GET /dashboard/evidence
- [x] Add GET /dashboard/cameras
- [x] Add GET /dashboard/events/latest
- [x] Add per-camera latest event endpoint
- [x] Add per-camera stats endpoint
- [x] Add simple frontend dashboard page later

## Completed on 2026-07-03 - Lightweight Dashboard UI

- [x] Add GET /dashboard-ui
- [x] Show camera totals, enabled count, and disabled count
- [x] Show disabled camera list
- [x] Show latest event summary
- [x] Show latest 10 events
- [x] Show clickable evidence thumbnails and links
- [x] Show camera list with enabled or disabled badge
- [x] Show per-camera total and person event counts
- [x] Add 30-second auto-refresh
- [x] Show last updated time and next refresh countdown
- [x] Add quick links for refresh, summary, cameras, latest events, and evidence
- [x] Use danger badge style for person events and success badge style for no-person events
- [x] Use existing dashboard API endpoints only
- [x] Keep UI lightweight with no external build tools

## Completed on 2026-07-03 - Scheduler Log Health Summary

- [x] Parse backend/data/task-logs/monitor_person_all.log safely
- [x] Add scheduler status to GET /dashboard/health
- [x] Add scheduler latest run time to GET /dashboard/health
- [x] Add scheduler summary and counts to GET /dashboard/health
- [x] Add recent safe scheduler log lines to GET /dashboard/health
- [x] Show scheduler latest run and summary in /dashboard-ui Health card
- [x] Keep scheduler health lightweight with no YOLO or RTSP access

## Completed on 2026-07-03 - Stale Camera Health

- [x] Add stale camera health logic to GET /dashboard/health
- [x] Use backend/data/events.jsonl latest event/check time where available
- [x] Add 120-minute default stale threshold
- [x] Return stale_minutes, stale_threshold_minutes, and last_seen_source per camera
- [x] Return offline for disabled cameras marked offline
- [x] Show stale health badge style in /dashboard-ui

## Completed on 2026-07-03 - Dashboard Stale/Offline Visual Polish

- [x] Show active, stale, no_recent_event, offline, and disabled counts in Health card
- [x] Use success badge for active cameras
- [x] Use warning badge for stale and no_recent_event cameras
- [x] Use danger badge for offline cameras
- [x] Use muted badge for disabled cameras
- [x] Show health_status, stale_minutes, stale_threshold_minutes, last_seen_source, and health_note in camera cards

## Completed on 2026-07-03 - Lightweight Dashboard Endpoints

- [x] Add GET /dashboard/evidence
- [x] Return evidence filename, URL, modified time, and size
- [x] Add GET /dashboard/cameras
- [x] Return camera totals and credential-safe camera list
- [x] Add GET /dashboard/events/latest
- [x] Include evidence_url for events with evidence images
- [x] Keep dashboard endpoints lightweight with no YOLO execution

## Completed on 2026-07-03 - Per-Camera Dashboard Endpoints

- [x] Add GET /dashboard/cameras/{camera_id}/latest-event
- [x] Add GET /dashboard/cameras/{camera_id}/stats
- [x] Validate camera_id against configured cameras
- [x] Return 404 for unknown camera_id
- [x] Include evidence_url when evidence is available
- [x] Keep per-camera dashboard endpoints lightweight with no YOLO execution

## Completed on 2026-07-03 - Dashboard Summary Endpoint

- [x] Add GET /dashboard/summary
- [x] Register dashboard router in FastAPI main app
- [x] Include camera total/enabled/disabled summary
- [x] Include disabled camera list
- [x] Include event statistics
- [x] Include latest event summary
- [x] Include latest 10 events
- [x] Include dashboard API links

## Next Dashboard TODO

- [x] Add GET /dashboard/evidence
- [x] Add GET /dashboard/cameras
- [x] Add GET /dashboard/events/latest
- [x] Add per-camera latest event endpoint
- [x] Add per-camera stats endpoint
- [x] Add simple frontend dashboard page later
