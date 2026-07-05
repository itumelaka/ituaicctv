# ITU AI CCTV - Operations

## Production State

- Production backend path: `C:\ituaicctv`
- Backend dashboard: `http://192.168.1.254:8000/dashboard-ui`
- TV dashboard: `http://192.168.1.254:8000/dashboard-tv`
- Backend service: `ITUAICCTVBackend`, running
- Primary monitor task: `ITU AI CCTV Live Monitor`, running
- Old monitor task: `ITU AI CCTV Person Monitor`, disabled and retained as backup
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
- face embeddings
- generated recognition models
- service/task logs

## Operator Links

- Event review: [EVENT_REVIEW.md](EVENT_REVIEW.md)
- Live view: [LIVE_VIEW.md](LIVE_VIEW.md)
- Ignore zones: [IGNORE_ZONES.md](IGNORE_ZONES.md)
- Face recognition: [FACE_RECOGNITION.md](FACE_RECOGNITION.md)
- Scheduler: [WINDOWS_TASK_SCHEDULER.md](WINDOWS_TASK_SCHEDULER.md)
