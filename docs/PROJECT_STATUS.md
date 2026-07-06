# ITU AI CCTV - Project Status

Last updated: 2026-07-05

## Current Production Status

Repository:

- GitHub repo: https://github.com/itumelaka/ituaicctv
- Production server path: C:\ituaicctv
- Local laptop dev path: C:\Users\burnk\OneDrive\Documents-assets\ai-cctv-detection
- Production dashboard: http://192.168.1.254:8000/dashboard-ui
- TV command center: http://192.168.1.254:8000/dashboard-tv
- Normal dashboard includes a TV Mode link to /dashboard-tv.
- TV command center includes a Normal dashboard link back to /dashboard-ui.
- GitHub Pages is no longer the primary dashboard. Production dashboard is served by backend /dashboard-ui.

Current production feature summary:

- Backend is served by FastAPI through the `ITUAICCTVBackend` Windows service.
- Primary production monitor is `ITU AI CCTV Live Monitor`.
- Old batch monitor `ITU AI CCTV Person Monitor` is intentionally disabled and retained as backup.
- Live monitor writes `backend/data/task-logs/live_monitor_status.json`.
- `/dashboard/health` prefers the live monitor status JSON and falls back to the old `monitor_person_all.log`.
- Evidence composites show the full frame with all detected person boxes plus up to three top-confidence person crops.
- New event metadata is synced to rendered evidence crops through `person_detections` with `crop_rank`, `confidence`, and `bbox`.
- Evidence metadata includes `evidence_source`: `hd_redetect`, `hd_scaled_bbox`, or `detection_frame`.
- Dashboard Assign Identity is available for unknown/unrecognized evidence events and supports person-specific targets for multi-person events.
- Identity assignments persist locally under `backend/data/face-enrollment/identity-assignments/identity_assignments.json`.
- Face Enrollment Manager is local-only and uses private CSV/OpenCV LBPH workflows. It does not use paid APIs, cloud recognition, or external image upload.
- Assignment records are human review records only. They do not auto-train the face model.

Documentation map:

- Operations: docs/OPERATIONS.md
- Live view: docs/LIVE_VIEW.md
- Event review: docs/EVENT_REVIEW.md
- Ignore zones: docs/IGNORE_ZONES.md
- Face recognition: docs/FACE_RECOGNITION.md

Latest important deployed commits:

- e2e7f8f feat: add ignore zones and event review workflow
- bd556ec fix: correct and rename additional CCTV cameras
- aa62e5b feat: add additional CCTV cameras to inventory
- 7b8271e fix: add tv dashboard link to normal dashboard
- 6da444a docs: document tv dashboard mjpeg live stream
- 073424a fix: improve dashboard tv live camera selection
- b89afba feat: add mjpeg live camera stream to tv dashboard

Production service and scheduler:

- Windows Server backend service name: ITUAICCTVBackend
- Service status: Running
- Service StartType: Automatic
- Backend listens on port 8000 and should auto-start after Windows Server reboot.
- Primary monitor task: ITU AI CCTV Live Monitor
- Live monitor state: Running
- Live monitor command: C:\ituaicctv\.venv312\Scripts\python.exe C:\ituaicctv\scripts\monitor_person_live.py
- Live monitor runs through Windows Task Scheduler as a long-running task triggered at startup.
- Configured scan interval is 10 seconds between full scan cycles; real observed cycle time is about 30 seconds because scanning 12 cameras takes time.
- Latest verification showed `enabled=12 attention=0 failed=0 next_scan=10s`.
- Old 5-minute scheduled monitor task `ITU AI CCTV Person Monitor` is Disabled, not deleted, and can be re-enabled as backup.
- Camera registry now has 12 enabled cameras.
- Near-live monitor default alert cooldown is 300 seconds.
- Exit code 0 means no person detected / no action.
- Exit code 2 means attention required / person detected, not a crash.

Camera and health:

- Total known cameras: 13
- Enabled cameras: 12
- Disabled/offline cameras: 1
- Disabled/offline: block_f_cam_8 / ITU BLOCK F CAM8 / 192.168.40.20
- Disabled reason: ping and RTSP port 554 are not reachable.
- Confirmed additional cameras: kuarantin_cam_11 / ITU KUARANTIN CAM11 / 192.168.40.23, biosekuriti_cam_12 / ITU BIOSEKURITI CAM12 / 192.168.40.24, and makmal_cam_13 / ITU MAKMAL CAM13 / 192.168.40.25.
- 192.168.40.26 is not part of the current inventory and was only a mistaken/stale entry.
- Current stale threshold: 120 minutes.

Network:

- Production server LAN IP: 192.168.1.254
- Server source interface to CCTV subnet: Ethernet 2 / 192.168.1.254
- GOVNET NIC: 10.65.28.254
- CCTV subnet: 192.168.40.0/24
- UDM Pro firewall rule allows server 192.168.1.254 to CCTV subnet 192.168.40.0/24 on TCP 554.
- Windows Firewall allows inbound TCP 8000 for dashboard/API.
- Teleport/laptop can access http://192.168.1.254:8000/dashboard-ui.

Evidence:

- Server evidence folder: C:\ituaicctv\backend\data\evidence
- SMB share: \\192.168.1.254\ituaicctv-evidence
- Share is read-only for Everyone under normal operation.
- Temporary Change access can be granted only when manually copying evidence from laptop to server, then should be reverted to Read.
- NTFS Everyone Modify was removed after copy cleanup.
- Backend/server can still save evidence locally.
- Laptop evidence was successfully copied to server using robocopy.

Current AI and dashboard features:

- YOLO person detection from Hikvision RTSP streams.
- PERSON_CONFIDENCE_THRESHOLD default is 0.60.
- makmal_cam_13 uses `person_confidence_threshold: 0.75` due to a fixed tree/topiary false positive around 0.62-0.63.
- kuarantin_cam_11 uses `person_confidence_threshold: 0.75` due to a fixed blue pipe false positive around 0.65.
- Ignore-zone / polygon mask support is implemented for fixed objects instead of relying only on threshold increases.
- Placeholder zones for makmal_cam_13 and kuarantin_cam_11 are disabled by default and must be calibrated from reviewed frames before enabling.
- Enabled ignore zones suppress detections whose bounding-box center falls inside the polygon before alert/evidence creation.
- Event review metadata is available through `/events/reviews/{event_id}` and is stored as ignored local runtime data under `backend/data/event-reviews/`.
- Production verification confirmed `/events/reviews`, `/events/latest-with-reviews`, and `/dashboard/cameras`.
- Dashboard UI shows event review status and Valid / False positive / Follow up buttons. Evidence gallery remained working after verification.
- Test review succeeded with status `valid`, reviewer `Burn`, and a PowerShell test note.
- Current ignore-zone placeholders: kuarantin_cam_11 has 1 configured / 0 enabled; makmal_cam_13 has 1 configured / 0 enabled.
- Telegram person alerts include confidence and threshold when available.
- Telegram group alert delivery was verified for the internal `itunetmonitor` group. Bot token and numeric group chat ID remain private configuration.
- One HEVC/RTSP decoder warning, `Could not find ref with POC 34`, was observed once. Treat this as harmless if monitoring continues and failed counts stay at 0; investigate only if a camera freezes or failed counts increase.
- Evidence image now uses clearer composite output: full CCTV frame with all detected person boxes plus up to three top-confidence person crops.
- HD evidence first tries channel 101 re-detection. If HD re-detection fails but the HD frame was captured, the system can scale original sub-stream boxes onto the HD frame for clearer crops before falling back to the original detection frame.
- High-resolution evidence is attempted after person detection. If a high-resolution frame is captured, person detection runs again on that frame and high-resolution boxes are used. If capture or re-detection fails, the system falls back to the original detection frame and boxes.
- Person evidence now includes advisory face readiness metadata when local OpenCV face detection is available: detection availability, face count, best face box, quality, readiness, and reasons. This is not identity recognition.
- Internal staff/student face recognition foundation is privacy-gated and disabled by default in code. Production can enable OpenCV LBPH recognition for approved local labels; it only runs when face readiness is possible/suitable and local model/backend files are available.
- Approved local enrollment remains internal testing only and is not high-security identity proof. Some candidate samples may be rejected because face detection/quality is not suitable.
- Local recognition backends now support `FACE_RECOGNITION_BACKEND=auto`, `face_recognition`, or `opencv_lbph`; OpenCV LBPH requires `opencv-contrib-python` so `cv2.face` is available.
- /dashboard-ui is now a dark AI Command Center with LIVE AI MONITORING indicator, scan line, summary cards, AI Status / Health, latest AI event, event timeline, evidence gallery, camera cards, section scroll navigation, refresh loading state, hover/glow effects, person-detected pulse/glow, and prefers-reduced-motion support.

## How to Verify After Server Restart

```powershell
Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType
Get-ScheduledTask |
  Where-Object { $_.TaskName -like "ITU AI CCTV*" } |
  Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName "ITU AI CCTV Live Monitor" |
  Select-Object LastRunTime, LastTaskResult
Invoke-RestMethod http://127.0.0.1:8000/dashboard/health | ConvertTo-Json -Depth 8
```

Optional operational checks:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/detections/block_f_cam_6/person |
  ConvertTo-Json -Depth 10
Get-Content C:\ituaicctv\backend\.env |
  Select-String "FACE_RECOGNITION"
C:\ituaicctv\.venv312\Scripts\python.exe -c "import cv2; print('cv2', cv2.__version__); print('cv2.face exists:', hasattr(cv2, 'face')); print('LBPH:', hasattr(cv2.face, 'LBPHFaceRecognizer_create') if hasattr(cv2, 'face') else False)"
Get-ChildItem C:\ituaicctv\backend\data\face-embeddings |
  Select-Object Name, Length, LastWriteTime
Get-ChildItem C:\ituaicctv\backend\data\evidence |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 10 Name, LastWriteTime, Length
explorer "\\192.168.1.254\ituaicctv-evidence"
```

Near-live monitor manual run for troubleshooting:

```powershell
C:\ituaicctv\.venv312\Scripts\python.exe C:\ituaicctv\scripts\monitor_person_live.py
```

## Deployment Status

First production deployment on 2026-07-03:

- Deployed on the Windows Server at C:\ituaicctv.
- Server LAN IP: 192.168.1.254.
- Server NICs: GOVNET/NIC 10.65.28.254 and LAN/NIC 192.168.1.254.
- Backend runs as a Windows Service (ITUAICCTVBackend) via NSSM, auto-start enabled, confirmed Running.
- Health confirmed: GET /health returns {"status":"ok","service":"ituaicctv-backend"} locally and across the LAN.
- Backend service listens on 0.0.0.0:8000.
- Windows Firewall inbound rule: ITU AI CCTV Backend Port 8000, TCP local port 8000, Profile Any.
- Dashboard reachable from LAN / Teleport at http://192.168.1.254:8000/dashboard-ui.
- Use http://127.0.0.1:8000/dashboard-ui only when browsing on the backend server itself.
- GitHub Pages is no longer the primary production dashboard. It may remain static/PWA/demo/client, but daily operation uses the Windows Server backend dashboard.
- Current primary monitor is `ITU AI CCTV Live Monitor`, confirmed Running. The older `ITU AI CCTV Person Monitor` batch task is Disabled and retained as backup.
- Setup scripts fixed for Windows PowerShell 5.1 and SETUP_GUIDE.txt rewritten (commit 60d241c).
- Latest production documentation checkpoint after commit 8352f37.

Production network notes:

- CCTV cameras are on 192.168.40.0/24.
- Initial server RTSP failed because server-to-CCTV VLAN traffic was not allowed.
- Teleport laptop access worked because VPN client traffic was a different flow from server-to-CCTV traffic.
- UDM Pro rule required: Firewall, Allow, Source Zone Internal, Source IP 192.168.1.254, Source Port Any, Destination Zone Internal, Destination IP/Subnet 192.168.40.0/24, Destination Port TCP 554, Auto Allow Return Traffic On.
- Place the UDM Pro rule above inter-VLAN block/drop rules.
- After the rule, Test-NetConnection to 192.168.40.21 and 192.168.40.22 on port 554 succeeded from SourceAddress 192.168.1.254.
- Laptop via Teleport uses a source IP around 192.168.2.x.
- After the Windows Firewall backend rule, Test-NetConnection 192.168.1.254 -Port 8000 succeeded from laptop SourceAddress 192.168.2.7.

Production evidence and logs:

- Evidence images are saved only when person_detected=True.
- no_person events usually have evidence_path=null and no evidence image.
- Person-only detection uses PERSON_CONFIDENCE_THRESHOLD with a safer default of 0.60.
- Telegram person alerts include the highest available person confidence and active threshold when detection data is available.
- Person evidence snapshots are generated through the person snapshot path, which draws bounding boxes and confidence labels.
- Face readiness is stored with person evidence events when available, but the system does not store face identities, embeddings, reference images, or identity labels.
- When enabled and matched, internal recognition metadata can include `recognized_label` and `recognition_confidence`; otherwise disabled/unavailable/unknown states are recorded without exposing biometric data.
- OpenCV LBPH model files are private runtime biometric artifacts under `backend/data/face-embeddings/` and must not be committed.
- Production face recognition dependency status: `opencv-contrib-python 5.0.0.93`, `numpy 2.4.6`, `cv2.face exists: True`, and `LBPHFaceRecognizer_create exists: True`.
- OpenCV Haar cascade file was manually added to the production venv under `cv2\data\haarcascade_frontalface_default.xml`; confirmed length was 930127 bytes.
- Production tests passed after installing OpenCV contrib: `python -m compileall backend\app scripts` and `python -m unittest discover -s tests -p "test_*.py" -v`, result 17 tests OK.
- Test internal label `BURN` has been enrolled with OpenCV LBPH using three private local samples. Generated private files `opencv_lbph_model.yml` and `opencv_lbph_labels.json` live under the ignored `backend/data/face-embeddings/` directory and must not be committed.
- Production `.env` currently includes `FACE_RECOGNITION_ENABLED=true` and `FACE_RECOGNITION_BACKEND=opencv_lbph`; keep `.env` private.
- Production evidence folder: C:\ituaicctv\backend\data\evidence.
- Production task log folder: C:\ituaicctv\backend\data\task-logs.
- Production service log folder: C:\ituaicctv\backend\data\service-logs.
- Laptop evidence folders are not production evidence storage.
- Laptop should not run the production scheduler when the server is production backend.
- SMB share: \\192.168.1.254\ituaicctv-evidence -> C:\ituaicctv\backend\data\evidence.
- Share created with: New-SmbShare -Name "ituaicctv-evidence" -Path "C:\ituaicctv\backend\data\evidence" -ReadAccess "Everyone".
- Dashboard has Refresh Evidence and Copy Evidence Folder Path actions. Paste the UNC path into File Explorer if the browser blocks direct folder links.

Current expected healthy dashboard state:

- total known cameras: 13
- enabled: 12
- disabled/offline: 1
- active/stale counts depend on latest live monitor events and the configured stale threshold
- live monitor task: ITU AI CCTV Live Monitor Running
- old batch task: ITU AI CCTV Person Monitor Disabled

## Current Checkpoint

Latest confirmed commit:

8352f37

Confirmed at this checkpoint:

- Backend FastAPI works.
- Hikvision RTSP works.
- Multi-camera config has 13 known cameras.
- 12 cameras are enabled.
- 1 camera is disabled/offline: block_f_cam_8 / 192.168.40.20.
- Disabled camera reason: ping and RTSP port 554 are not reachable.
- GET /dashboard-ui is usable.
- GET /dashboard/health is usable.
- Scheduler summary in GET /dashboard/health is usable.
- Stale camera health logic in GET /dashboard/health is usable.
- Scheduler BAT resolves the project root dynamically from its script location.
- Scheduler BAT uses .venv312 first, then .venv, then python from PATH.
- Dashboard UI includes auto-refresh every 30 seconds, last updated time, next refresh countdown, quick links/buttons, improved badges, clickable evidence thumbnails, Health card, and per-camera health badges.
- Dashboard UI includes stale/offline health counts and camera freshness details.
- /dashboard-tv includes a selectable backend-proxied MJPEG live camera view, camera dropdown, clickable camera cards, Restart stream button, and a separate latest evidence snapshot panel.
- Direct MJPEG stream endpoint is available at /dashboard/live/{camera_id}/stream.mjpg and is limited to 4 FPS for one selected camera/viewer.
- Snapshot fallback endpoint remains available at /dashboard/live/{camera_id}/snapshot.jpg.
- Live view quality supports `quality=standard` for the configured camera channel, usually 102, and `quality=hd` for Hikvision main-stream channel 101. Invalid quality values return HTTP 400. HD MJPEG allows a larger 1920px max width, but actual resolution depends on camera main-stream settings and may still be 720p. This is viewing only and does not change AI detection, evidence, Telegram, event review, ignore zones, or live monitor behavior.
- HD snapshot was confirmed at 3200x1800 on block_f_cam_7 where the camera main stream provided that resolution.
- MJPEG live view has no audio; audio would require camera audio support and a future HLS/WebRTC/FFmpeg proxy.
- Browser clients connect to the backend only; RTSP URLs, usernames, and passwords are not exposed to the frontend.
- backend/app/dashboard_health.py exists.
- tests/test_dashboard_health.py exists.
- Unit test passed with: python -m unittest discover -s tests -p "test_*.py" -v
- Compile passed with: python -m compileall backend/app
- sambung.txt is a private local handoff note and should not be committed.

Next recommended work:

1. Review recent person alerts at PERSON_CONFIDENCE_THRESHOLD=0.60 before lowering the threshold.
2. Dashboard production polish and evidence review workflow
3. Investigate block_f_cam_8 network/IP
4. Avoid overlapping scheduler runs if check-all takes too long
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
- Scheduler-log health summary
- Stale camera health logic
- Per-camera dashboard event endpoints
- Lightweight browser dashboard
- Dashboard auto-refresh and status UI polish
- Dashboard health card with per-camera health badges
- Dashboard stale/offline visual polish

Current camera status:

- Total known cameras: 13
- Enabled cameras: 12
- Disabled/offline cameras: 1
- Disabled/offline camera: block_f_cam_8 / 192.168.40.20
- Status: offline
- Reason: ping and RTSP port 554 are not reachable

New confirmed Hikvision cameras:

- kuarantin_cam_11 / ITU KUARANTIN CAM11 / 192.168.40.23 / channel 102 / enabled, confirmed VLC RTSP stream label KUARANTIN.
- biosekuriti_cam_12 / ITU BIOSEKURITI CAM12 / 192.168.40.24 / channel 102 / enabled, confirmed VLC RTSP stream label BIOSEKURITI.
- makmal_cam_13 / ITU MAKMAL CAM13 / 192.168.40.25 / channel 102 / enabled, confirmed VLC RTSP stream label MAKMAL.

Important dashboard URLs:

- http://127.0.0.1:8000/dashboard-ui
- http://127.0.0.1:8000/dashboard/health
- /dashboard-ui
- /dashboard/summary
- /dashboard/health
- /dashboard/cameras
- /dashboard/events/latest
- /dashboard/evidence
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

Current scheduler status:

- Task name: ITU AI CCTV Person Monitor
- State: intentionally Disabled
- BAT launcher returns 0 to Task Scheduler
- Main script: backend/scripts/monitor_person_all_once.py
- BAT launcher: backend/scripts/run_monitor_person_all_once.bat
- Hidden VBS launcher: backend/scripts/run_monitor_person_all_once_hidden.vbs
- Runtime log: backend/data/task-logs/monitor_person_all.log
- BAT launcher resolves project root dynamically from script location
- Python selection order:
  1. .venv312\Scripts\python.exe
  2. .venv\Scripts\python.exe
  3. python from PATH
- This fixes laptop environments where old .venv is missing or broken but .venv312 exists

Current expected healthy dashboard state:

- total known cameras: 13
- enabled: 12
- disabled/offline: 1
- active/stale counts depend on latest live monitor events and the configured stale threshold
- live monitor task: ITU AI CCTV Live Monitor Running
- old batch task: ITU AI CCTV Person Monitor Disabled

Known disabled/offline camera:

- block_f_cam_8 / ITU BLOCK F CAM8
- IP: 192.168.40.20
- Reason: ping and RTSP port 554 are not reachable
- Do not treat this as a system failure unless the camera is intentionally re-enabled later

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

1. Review person detection false positives with PERSON_CONFIDENCE_THRESHOLD=0.60.
2. Dashboard production polish and evidence review workflow.
3. Investigate block_f_cam_8 network/IP.
4. Avoid overlapping scheduler runs if check-all takes too long.
5. Later: phased face detection planning, starting with face detection only and no identity recognition.
6. Later: number plate recognition planning.

## Latest Milestone - Multi-Camera Scheduler

Updated: 2026-07-03

Multi-camera monitoring is now working.

Confirmed:

- GET /cameras/audit works
- GET /monitor/person/check-all works
- Current registry has 12 enabled cameras; 9 were confirmed in the earlier multi-camera monitor test before the newly labelled cameras were added.
- 1 camera is disabled/offline:
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
- kuarantin_cam_11
- biosekuriti_cam_12
- makmal_cam_13

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

- cameras_total: 13
- cameras_enabled: 12
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

## Latest Milestone - Scheduler Log Health Summary

Updated: 2026-07-03

GET /dashboard/health now includes a lightweight scheduler summary from:

- backend/data/task-logs/monitor_person_all.log

The scheduler block includes:

- status
- latest_run_time
- latest_summary
- failed_count
- person_detected_count
- no_person_count
- log_path
- recent_lines

The parser reads existing log text only. If the log format is unclear or a value is missing, the dashboard returns null or unknown instead of inventing data.

The /dashboard-ui Health card now shows:

- scheduler latest run
- scheduler summary

This keeps scheduler visibility in the dashboard without running YOLO detection or opening RTSP streams.

## Latest Milestone - Stale Camera Health

Updated: 2026-07-03

GET /dashboard/health now includes stale camera health logic for enabled cameras.

The health check reads existing event data from:

- backend/data/events.jsonl

Per-camera health now includes:

- health_status
- last_event_time
- stale_minutes
- stale_threshold_minutes
- last_seen_source

Default stale threshold:

- 120 minutes

Current status behavior:

- offline for disabled cameras marked offline
- disabled for disabled cameras without offline status
- active for enabled cameras with a recent event/check
- stale for enabled cameras with an old event/check
- no_recent_event for enabled cameras with no event yet

The /dashboard-ui camera cards show stale health using the warning badge style.

## Latest Milestone - Dashboard Stale/Offline Visual Polish

Updated: 2026-07-03

The /dashboard-ui Health card now shows derived health counts from /dashboard/health:

- active
- stale
- no_recent_event
- offline
- disabled

Camera cards now show:

- health_status
- stale_minutes
- stale_threshold_minutes
- last_seen_source
- health_note when available

Badge behavior:

- active uses success style
- stale uses warning style
- offline uses danger style
- disabled uses muted style
- no_recent_event uses warning style

## Latest Milestone - Dashboard Summary Endpoint

Updated: 2026-07-03

A new dashboard summary endpoint has been added:

- GET /dashboard/summary

This endpoint is lightweight because it reads existing camera configuration and event logs only. It does not run YOLO detection.

Current confirmed output:

- cameras_total: 13
- cameras_enabled: 12
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
