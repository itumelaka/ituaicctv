# ITU AI CCTV - TODO List

## Immediate TODO

- [ ] Add GET /dashboard/health
- [ ] Add camera health/offline summary
- [ ] Track latest successful check per camera
- [ ] Add dashboard health card
- [ ] Investigate block_f_cam_8 network/RTSP issue
- [ ] Prepare face detection planning notes later
- [ ] Prepare number plate recognition planning notes later

## Camera Configuration TODO

Camera registry current summary:

- [x] Total cameras configured: 10
- [x] Enabled cameras: 9
- [x] Disabled cameras: 1
- [x] block_f_cam_8 / 192.168.40.20 is disabled because ping and RTSP port 554 are not reachable

Camera list:

- [x] block_e_cam_1 - 192.168.40.13
- [x] block_e_cam_2 - 192.168.40.14
- [x] block_e_cam_3 - 192.168.40.15
- [x] block_e_cam_4 - 192.168.40.16
- [x] block_e_cam_5 - 192.168.40.17
- [x] block_f_cam_6 - 192.168.40.18
- [x] block_f_cam_7 - 192.168.40.19
- [x] block_f_cam_8 - 192.168.40.20 disabled
- [x] block_f_cam_9 - 192.168.40.21
- [x] block_f_cam_10 - 192.168.40.22

## Backend TODO

- [x] Add camera audit summary endpoint
- [ ] Add camera readiness status
- [ ] Add ready_for_ai field in cameras.json
- [x] Add monitor all enabled cameras endpoint
- [x] Add per-camera event stats
- [x] Add per-camera latest event endpoint
- [ ] Add duplicate detection filtering
- [ ] Add configurable detection classes
- [ ] Add configurable monitoring interval
- [ ] Add structured log rotation

## Face Detection TODO

- [ ] Add face detection only endpoint
- [ ] Detect face presence without identifying identity
- [ ] Add face crop evidence storage
- [ ] Add privacy and consent notes
- [ ] Design face enrolment flow
- [ ] Add face recognition pilot only for authorised users
- [ ] Add known persons database
- [ ] Add confidence threshold for identity matching

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
- [ ] GET /dashboard/health
- [ ] Camera health/offline summary
- [ ] Latest successful check per camera
- [ ] Dashboard health card
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

- [ ] Add GET /dashboard/health
- [ ] Add camera health/offline summary
- [ ] Track latest successful check per camera
- [ ] Add dashboard health card
- [ ] Investigate block_f_cam_8 network/RTSP issue
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
- [ ] Add GET /dashboard/health
- [ ] Add camera health/offline summary
- [ ] Track latest successful check per camera
- [ ] Add dashboard health card
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
