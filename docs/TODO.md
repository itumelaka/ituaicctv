# ITU AI CCTV - TODO List

## Current Production TODO Context

- Production backend path: C:\ituaicctv
- Production dashboard: http://192.168.1.254:8000/dashboard-ui
- Backend service ITUAICCTVBackend is Running and Automatic.
- Primary task ITU AI CCTV Live Monitor is Running as a long-running startup-triggered Task Scheduler task.
- Old 5-minute task ITU AI CCTV Person Monitor is Disabled and retained as backup.
- Live monitor uses C:\ituaicctv\.venv312\Scripts\python.exe C:\ituaicctv\scripts\monitor_person_live.py.
- Camera registry has 13 known cameras, 12 enabled cameras, and 1 disabled/offline camera.
- Exit code 0 = ok/no attention. Exit code 2 = attention/person detected, not a crash.
- Evidence is saved only when person_detected=True.
- New evidence image behavior: full-frame boxes plus up to three top-confidence person crops.
- Evidence crop labels avoid implying face identity quality; low-resolution crops can be marked FACE ID NOT SUITABLE.
- Face readiness metadata is advisory only and does not perform identity recognition or store face embeddings.
- Internal staff/student recognition foundation is disabled by default in code and supports `face_recognition` or OpenCV LBPH backends after approved local enrollment.
- Dashboard is now the dark AI Command Center served by backend /dashboard-ui.
- Fullscreen TV Command Center mode is available at /dashboard-tv.
- MediaMTX runs as the production WebRTC gateway service `MediaMTX` / `MediaMTX WebRTC Gateway`.
- TV mode includes a selectable single-camera live panel; latest evidence is shown separately as historical proof.
- TV mode uses an iVMS-style single-camera live monitor layout with camera dropdown, WebRTC Smooth/MJPEG Fallback toggle, MJPEG Smooth Live/HD Live toggle, restart stream, HD snapshot, and fullscreen controls.
- WebRTC Smooth uses the MediaMTX gateway on port 8889. MediaMTX path names should match dashboard `camera_id` values, and RTSP credentials are not exposed to the browser.
- MediaMTX WebRTC uses TCP 8889 for the player and UDP 8189 for ICE; HLS TCP 8888 and RTSP TCP 8554 are available at the gateway but are not the current dashboard path.
- Direct stream endpoint /dashboard/live/{camera_id}/stream.mjpg is available for one selected camera/viewer at 4 FPS; /dashboard/live/{camera_id}/snapshot.jpg remains as fallback.
- Live view supports `quality=standard` for the configured camera channel, usually 102, and `quality=hd` for Hikvision main-stream channel 101. Invalid quality values return HTTP 400. HD MJPEG allows a larger 1920px max width, but actual resolution depends on camera main-stream settings and may still be 720p. This is viewing only and does not change AI detection.
- /dashboard-tv defaults the selected camera stream to WebRTC Smooth for better TV performance. MJPEG Fallback remains available, with Smooth Live/Standard as its default and HD Live available if detail is needed.
- Snapshot prefers HD even when live display is WebRTC Smooth or MJPEG Smooth. Evidence crops use the separate HD evidence pipeline when available.
- Dashboard live view has no audio. Audio would require camera audio support plus future WebRTC/MediaMTX handling.
- There is intentionally no 13-camera simultaneous live grid.
- Near-live monitor script scripts/monitor_person_live.py is the primary alerting path on production.
- Configured live monitor scan interval is 10 seconds; observed full-cycle time is about 30 seconds across 12 enabled cameras.
- Live monitor writes lightweight health status to backend/data/task-logs/live_monitor_status.json for /dashboard/health.
- Existing 5-minute Task Scheduler scan is Disabled and remains as backup.
- /dashboard/health now prefers live monitor status JSON and falls back to the old batch monitor log.
- Dashboard Assign Identity is available for unknown/unrecognized evidence events.
- Multi-person events require selecting the matching `PERSON 1`, `PERSON 2`, or `PERSON 3` metadata target before saving identity assignment.
- Identity assignments persist under backend/data/face-enrollment/identity-assignments/identity_assignments.json.
- Assignments are human review records only and do not auto-train the face model.
- New multi-person evidence metadata is synced to the rendered evidence crops.
- HD evidence metadata uses `evidence_source`: `hd_redetect`, `hd_scaled_bbox`, or `detection_frame`.
- HD scaled-bbox fallback can improve face readiness when HD re-detection fails but the HD frame is available.

## Recently Completed Production Work

- [x] Local Face Enrollment Manager groundwork
- [x] CSV enrollment workflow: template, draft, batch enrollment, and reject report
- [x] Dashboard identity assignment UI
- [x] Person-specific identity assignment
- [x] Persistent identity assignment storage path fix
- [x] Multi-person evidence composite
- [x] Metadata sync for multi-person evidence
- [x] HD evidence scaled-bbox fallback after failed HD re-detection
- [x] Live monitor health status support
- [x] MediaMTX WebRTC Smooth mode integration for /dashboard-tv
- [x] MediaMTX Windows service setup through NSSM

## Current Production Backlog

- [x] Add per-camera person threshold support; makmal_cam_13 uses 0.75 for known topiary/tree false positive, and kuarantin_cam_11 uses 0.75 for known blue-pipe false positive.
- [x] Add backend ignore-zone polygon mask support for camera-specific static false positives.
- [x] Add disabled placeholder ignore-zone polygons for makmal_cam_13 and kuarantin_cam_11.
- [x] Add local event review API/storage for valid, false positive, ignored, and follow-up decisions.
- [x] Verify production event review / acknowledgement endpoints and dashboard buttons.
- [x] Verify Telegram group alert delivery to the internal monitoring group.
- [ ] Add minimum bounding box size filtering for person detections.
- [ ] Calibrate makmal_cam_13 and kuarantin_cam_11 ignore-zone polygon points from reviewed production frames before enabling them.
- [ ] Add a visual dashboard editor for drawing/testing ignore zones on camera snapshots.
- [ ] Improve dashboard review workflow with filters for unreviewed only, false positive only, and follow-up only.
- [ ] Add review audit log and authenticated users before treating review actions as controlled approvals.
- [ ] Add daily Telegram summary report to the internal group.
- [ ] Design optional critical-only Telegram health alert cooldowns for live monitor stopped, failed cameras, and stale cameras. Do not spam normal health status.
- [ ] Add camera health alert if live monitor failed count increases or a camera freezes.
- [ ] Verify all enabled camera paths in MediaMTX for WebRTC Smooth and keep disabled/offline `block_f_cam_8` excluded.
- [ ] Fix `makmal_cam_13` sub-stream channel 102 to H.264 for browser WebRTC compatibility.
- [ ] Optionally force MediaMTX WebRTC ICE/announce address if some LAN clients see unusable 169.254.x.x candidates.
- [ ] Add dashboard UI health/status indicator for MediaMTX availability.
- [ ] Add documentation for adding a new camera path to MediaMTX.
- [ ] Review HD MJPEG fallback CPU/network impact before encouraging routine HD monitoring.
- [ ] Add future audio-capable live view only if cameras provide audio streams.
- [ ] Add visual ignore-zone polygon editor for reviewed dashboard snapshots.
- [x] Add CSV-based private face enrollment workflow.
- [ ] Add review audit logs and retention/deletion policy.
- [ ] Keep evaluating internal LBPH recognition with approved private samples; do not treat matches as high-security identity proof.
- [ ] Add approved assignment-to-training-sample workflow with manual review.
- [ ] Add cleanup/manage identity assignment records UI.
- [ ] Add per-camera crowd/wide-view tuning.
- [ ] Evaluate stronger local model for selected cameras.
- [ ] Add tracking/counting line/zone with ByteTrack or BoT-SORT.
- [ ] Evaluate local deep face embedding backend.
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
- [x] Add optional near-live continuous person monitor script.
- [x] Activate near-live monitor on production as primary long-running startup-triggered Task Scheduler task.
- [ ] Watch CPU/network/camera load before reducing live monitor interval below 10 seconds.
- [ ] Continue face detection and safe opt-in face recognition roadmap.
- [x] Try high-resolution main-stream evidence capture after person_detected=True, with fallback to detection frame.
- [ ] Add explicit per-camera evidence_channel/high_resolution_channel config after confirming H.264 main-stream support.
- [ ] Add optional Telegram send-as-document mode to reduce Telegram photo compression for evidence review.
- [x] Add explicit face evidence quality/readiness metadata before any recognition pilot.
- [x] Add disabled-by-default internal face recognition foundation and enrollment script scaffold.
- [x] Add OpenCV LBPH backend option for local internal recognition when opencv-contrib-python is installed.
- [x] Confirm kuarantin_cam_11, biosekuriti_cam_12, and makmal_cam_13 in inventory with VLC labels.

## Production Verification Commands

```powershell
Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType
Get-ScheduledTask |
  Where-Object { $_.TaskName -like "ITU AI CCTV*" } |
  Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName "ITU AI CCTV Live Monitor" |
  Select-Object LastRunTime, LastTaskResult
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
- ITU AI CCTV Live Monitor is Running; LastTaskResult 267009 / 0x41301 means the long-running task is currently running.
- ITU AI CCTV Person Monitor is Disabled and retained as a backup task.
- Current camera registry after confirmed VLC labels: total=13, enabled=12, disabled/offline=1.
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
- [ ] Confirm RTSP and health status for kuarantin_cam_11 / 192.168.40.23, biosekuriti_cam_12 / 192.168.40.24, and makmal_cam_13 / 192.168.40.25 after deployment
- [ ] Avoid overlapping scheduler runs if check-all takes too long
- [ ] Prepare face detection planning notes later
- [ ] Prepare number plate recognition planning notes later

## Camera Configuration TODO

Camera registry current summary:

- [x] Total cameras configured: 13
- [x] Enabled cameras: 12
- [x] Disabled/offline cameras: 1
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
- [x] kuarantin_cam_11 - 192.168.40.23 enabled, confirmed VLC RTSP stream label KUARANTIN
- [x] biosekuriti_cam_12 - 192.168.40.24 enabled, confirmed VLC RTSP stream label BIOSEKURITI
- [x] makmal_cam_13 - 192.168.40.25 enabled, confirmed VLC RTSP stream label MAKMAL

## Backend TODO

- [x] Add camera audit summary endpoint
- [ ] Add camera readiness status
- [ ] Add ready_for_ai field in cameras.json
- [x] Add monitor all enabled cameras endpoint
- [x] Add optional near-live continuous monitor script
- [x] Add per-camera event stats
- [x] Add per-camera latest event endpoint
- [x] Add configurable PERSON_CONFIDENCE_THRESHOLD for person-only detection
- [x] Add optional per-camera person_confidence_threshold
- [x] Include person detection confidence in Telegram alerts when available
- [ ] Add duplicate detection filtering
- [ ] Add configurable detection classes
- [ ] Add configurable monitoring interval
- [ ] Add structured log rotation

## Face Detection TODO

- [x] Document phased face feature roadmap
- [x] Document private future face folders without creating sensitive data
- [x] Ignore future private face data folders in Git
- [x] Add advisory face readiness metadata to person evidence without identifying identity
- [x] Detect face presence/readiness from evidence crops when local OpenCV face detection is available
- [x] Keep face_recognition_ready false until suitable high-resolution face evidence exists
- [ ] Add face detection only endpoint
- [ ] Capture high-resolution main-stream/snapshot evidence before any reliable face recognition attempt
- [ ] Add face crop evidence storage
- [ ] Add privacy and consent notes
- [ ] Design face enrolment flow
- [x] Add local enrollment script scaffold for approved internal labels
- [x] Install/approve local face embedding dependency for LBPH: opencv-contrib-python 5.0.0.93 on production
- [x] Verify production LBPH support with `C:\ituaicctv\.venv312\Scripts\python.exe -c "import cv2; print(hasattr(cv2, 'face'))"`
- [x] Support approved internal labels with OpenCV LBPH using private local photos
- [ ] Add face recognition pilot only for authorised internal staff/student
- [ ] Add known persons database only as private local biometric data, never in Git
- [ ] Add confidence threshold for identity matching
- [ ] Add dashboard human review and confirmation flow before identity actions
- [ ] Add formal face data retention/deletion and audit controls before any identity recognition pilot
- [ ] Document operating procedure for `UNKNOWN` labels so they are not treated as suspicious by default

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
- [x] Improve /dashboard-tv as iVMS-style single-camera live monitor with HD/Standard toggle
- [x] Document MJPEG live stream endpoint, snapshot fallback, security, and performance limits
- [ ] Consider WebRTC or HLS upgrade for better TV stream scaling and lower CPU/network usage
- [ ] Consider multi-camera grid only after performance testing; avoid 13 simultaneous MJPEG streams for now
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
