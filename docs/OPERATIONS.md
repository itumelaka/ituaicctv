# ITU AI CCTV - Operations

## Production State

- Production backend path: `C:\ituaicctv`
- Backend dashboard: `http://192.168.1.254:8000/dashboard-ui`
- TV dashboard: `http://192.168.1.254:8000/dashboard-tv`
- Backend service: `ITUAICCTVBackend`, running
- Primary monitor task: `ITU AI CCTV Live Monitor`, running
- Old monitor task: `ITU AI CCTV Person Monitor`, disabled and retained as backup
- Live monitor status file: `backend/data/task-logs/live_monitor_status.json`
- `/dashboard/health` prefers live monitor status and falls back to `backend/data/task-logs/monitor_person_all.log`
- Camera inventory: 13 total, 12 enabled, 1 disabled/offline
- Disabled/offline camera: `block_f_cam_8 / 192.168.40.20`

GitHub Pages is not the primary production dashboard. Daily operation uses the backend-served dashboard.

## Live Monitor

The live monitor runs as a long-running startup-triggered Scheduled Task and scans enabled cameras sequentially.

Healthy recent summary example:

```text
enabled=12 attention=0 failed=0 next_scan=10s
```

The configured interval is 10 seconds between scan cycles, but the real full-cycle time can be longer because cameras are scanned one by one.

HEVC/RTSP decoder warnings such as `Could not find ref with POC 34` can be harmless if monitoring continues and failed counts stay at 0. Investigate only if a camera freezes, repeated read failures appear, or failed counts increase.

Dashboard health reads the lightweight live monitor status JSON first. The old batch monitor log is retained only as fallback because `ITU AI CCTV Person Monitor` is intentionally disabled backup.

Optional future health alerts should be critical-only and cooldown protected, for example live monitor stopped, failed camera count above zero, or camera stale beyond threshold. Do not send normal health status repeatedly to Telegram.

## Evidence And Identity Review

New person evidence composites show the full frame with all detected person boxes plus up to three top-confidence person crops. New event metadata includes matching `person_detections` entries with `crop_rank`, `confidence`, and `bbox`; existing old events are not migrated.

Dashboard Assign Identity is available for unknown/unrecognized evidence events. Single-person events use `PERSON 1`; multi-person events require the operator to choose `PERSON 1`, `PERSON 2`, or `PERSON 3` based on metadata. Assignments are stored locally as human review records and do not train the face model.

HD evidence behavior:

- `hd_redetect`: channel 101/main-stream capture succeeded and YOLO found valid persons on the HD frame.
- `hd_scaled_bbox`: HD capture succeeded, HD re-detection found no person, and scaled sub-stream boxes produced valid HD crops.
- `detection_frame`: HD capture failed or scaled crops were invalid, so the original detection frame was used.

The HD scaled-bbox fallback can improve face readiness when the sub-stream crop was too small. It does not guarantee identity recognition and may still return `UNKNOWN`.

## Telegram Group Alerts

Production Telegram group alerting has been verified for the internal `itunetmonitor` group.

- Set `TELEGRAM_CHAT_ID` in private `.env` to send to a Telegram group.
- Use Telegram `getUpdates` after posting in the group to discover the group chat ID.
- Do not publish the bot token or numeric chat ID.

Future work: daily Telegram summary report to the internal group.

## Runtime Data

The following are private runtime data and must not be committed:

- evidence images
- event logs
- event review JSON
- face enrollment images
- face enrollment CSVs and identity assignments
- face embeddings
- generated recognition models
- service/task logs

If an accidental `backend/backend/` runtime folder appears from the old identity-assignment path bug, do not commit it. Stop the backend first, verify current writes go to `backend/data/`, move any needed private runtime data to the correct folder, and delete the stray folder locally.

## Operator Links

- Event review: [EVENT_REVIEW.md](EVENT_REVIEW.md)
- Live view: [LIVE_VIEW.md](LIVE_VIEW.md)
- Ignore zones: [IGNORE_ZONES.md](IGNORE_ZONES.md)
- Face recognition: [FACE_RECOGNITION.md](FACE_RECOGNITION.md)
- Scheduler: [WINDOWS_TASK_SCHEDULER.md](WINDOWS_TASK_SCHEDULER.md)
