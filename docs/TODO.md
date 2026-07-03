# ITU AI CCTV - TODO List

## Immediate TODO

- [ ] Audit all 10 CCTV cameras
- [ ] Confirm each camera RTSP stream works
- [ ] Confirm each camera sub-stream is H.264
- [ ] Confirm each camera uses channel 102
- [ ] Mark unstable cameras as enabled: false
- [ ] Add GET /cameras/audit
- [ ] Add GET /monitor/person/check-all
- [ ] Create script to monitor all enabled cameras
- [ ] Update Windows Task Scheduler to use multi-camera script
- [ ] Keep scheduler disabled until multi-camera check is stable

## Camera Configuration TODO

Camera list currently added:

- [ ] block_e_cam_1 - 192.168.40.13
- [x] block_e_cam_2 - 192.168.40.14
- [ ] block_e_cam_3 - 192.168.40.15
- [ ] block_e_cam_4 - 192.168.40.16
- [ ] block_e_cam_5 - 192.168.40.17
- [ ] block_f_cam_6 - 192.168.40.18
- [ ] block_f_cam_7 - 192.168.40.19
- [ ] block_f_cam_8 - 192.168.40.20
- [x] block_f_cam_9 - 192.168.40.21
- [ ] block_f_cam_10 - 192.168.40.22

## Backend TODO

- [ ] Add camera audit summary endpoint
- [ ] Add camera readiness status
- [ ] Add ready_for_ai field in cameras.json
- [ ] Add monitor all enabled cameras endpoint
- [ ] Add per-camera event stats
- [ ] Add per-camera latest evidence endpoint
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

- [ ] Camera status page
- [ ] Latest events page
- [ ] Evidence image viewer
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

- [ ] Update Windows Task Scheduler documentation
- [ ] Add summary-friendly monitor output
- [ ] Add event cooldown to avoid repeated evidence spam
- [ ] Add per-camera confidence threshold
- [ ] Investigate block_f_cam_8 network issue
- [ ] Lower block_e_cam_1 sub-stream from 1280x720 to 640x360 if CPU usage is high
- [ ] Add dashboard-ready API endpoint
- [ ] Prepare face detection planning notes
- [ ] Prepare number plate recognition planning notes

## Completed on 2026-07-03 - Dashboard Summary

- [x] Add dashboard-ready API endpoint
- [x] Add GET /monitor/person/summary
- [x] Return compact per-camera monitor status
- [x] Return attention_cameras list
- [x] Return failed_cameras list

## Next TODO After Dashboard Summary

- [ ] Create dashboard API for latest events summary
- [ ] Create dashboard API for evidence summary
- [ ] Add per-camera latest event endpoint
- [ ] Add per-camera stats endpoint
- [ ] Add event cooldown test with real person detection
- [ ] Add face detection planning notes
- [ ] Add number plate recognition planning notes

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
- [ ] Add per-camera latest event endpoint
- [ ] Add per-camera stats endpoint
- [ ] Add simple frontend dashboard page later

## Completed on 2026-07-03 - Lightweight Dashboard Endpoints

- [x] Add GET /dashboard/evidence
- [x] Return evidence filename, URL, modified time, and size
- [x] Add GET /dashboard/cameras
- [x] Return camera totals and credential-safe camera list
- [x] Add GET /dashboard/events/latest
- [x] Include evidence_url for events with evidence images
- [x] Keep dashboard endpoints lightweight with no YOLO execution

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
- [ ] Add per-camera latest event endpoint
- [ ] Add per-camera stats endpoint
- [ ] Add simple frontend dashboard page later
