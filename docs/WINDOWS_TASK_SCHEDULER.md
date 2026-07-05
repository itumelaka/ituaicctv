# ITU AI CCTV - Windows Task Scheduler

Last updated: 2026-07-05

## Current Scheduler Status

Primary task:

ITU AI CCTV Live Monitor

Current state:

- Confirmed Running on production.
- Runs as a long-running Windows Task Scheduler task triggered at startup.
- Command: C:\ituaicctv\.venv312\Scripts\python.exe C:\ituaicctv\scripts\monitor_person_live.py
- Scans enabled cameras sequentially.
- Configured interval is 10 seconds between full scan cycles.
- Real observed cycle time is about 30 seconds because scanning 12 cameras takes time.
- Latest production verification showed `enabled=12 attention=0 failed=0 next_scan=10s`.
- Replaces the old 5-minute batch monitor as the primary alerting path.
- Reuses existing person detection, evidence save, event, cooldown, and Telegram alert flow.
- Suppresses routine no_person event writes to avoid excessive event-log noise.

Backup task:

- ITU AI CCTV Person Monitor is Disabled.
- It is not deleted and can be re-enabled as backup if needed.
- It uses the older check-all batch monitor path.

Production server path:

C:\ituaicctv

Production scheduler Python:

C:\ituaicctv\.venv312\Scripts\python.exe

Current camera registry:

- Total known cameras: 13
- Enabled cameras: 12
- Disabled/offline cameras: 1
- Disabled/offline camera: block_f_cam_8 / ITU BLOCK F CAM8 / 192.168.40.20
- 192.168.40.26 is not part of current inventory.
- Exit code 0 means no person detected / no action.
- Exit code 2 means attention required / person detected, not a crash.
- LastTaskResult 267009 / 0x41301 means a long-running task is currently running.
- A one-time HEVC/RTSP warning such as `Could not find ref with POC 34` can be harmless if the live monitor continues scanning. Investigate only if a camera freezes, repeated read failures appear, or the failed count increases.

## Reboot Behavior

- Backend service `ITUAICCTVBackend` is confirmed `Running`.
- Service `StartType` is confirmed `Automatic`.
- Backend/API/dashboard should auto-start after Windows Server reboot.
- Task `ITU AI CCTV Live Monitor` should be `Running`.
- Task `ITU AI CCTV Person Monitor` should be `Disabled`.
- Live monitor should continue using `C:\ituaicctv\.venv312\Scripts\python.exe`.

Verify after restart:

```powershell
Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType
Get-ScheduledTask |
  Where-Object { $_.TaskName -like "ITU AI CCTV*" } |
  Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName "ITU AI CCTV Live Monitor" |
  Select-Object LastRunTime, LastTaskResult
Invoke-RestMethod http://127.0.0.1:8000/dashboard/health | ConvertTo-Json -Depth 8
```

## Scheduler Scripts

Main monitor script:

backend/scripts/monitor_person_all_once.py

BAT launcher:

backend/scripts/run_monitor_person_all_once.bat

Hidden VBS launcher:

backend/scripts/run_monitor_person_all_once_hidden.vbs

Runtime log:

backend/data/task-logs/monitor_person_all.log

Production runtime log:

C:\ituaicctv\backend\data\task-logs\monitor_person_all.log

## Launcher Flow

Windows Task Scheduler
-> backend/scripts/run_monitor_person_all_once_hidden.vbs
-> backend/scripts/run_monitor_person_all_once.bat
-> backend/scripts/monitor_person_all_once.py
-> backend/data/task-logs/monitor_person_all.log

## Monitor Scope

The multi-camera script checks all enabled cameras from the camera registry.

Current camera summary:

- Total cameras: 13
- Enabled cameras: 12
- Disabled cameras: 1
- Disabled camera: block_f_cam_8 / 192.168.40.20
- Reason: ping and RTSP port 554 are not reachable

## Primary Near-Live Monitor

Near-live alerting now uses the long-running monitor:

```text
scripts/monitor_person_live.py
```

Manual production run command for troubleshooting:

```powershell
C:\ituaicctv\.venv312\Scripts\python.exe C:\ituaicctv\scripts\monitor_person_live.py
```

Default behavior:

- Scans all enabled cameras sequentially.
- Uses `LIVE_MONITOR_INTERVAL_SECONDS` when set; default is 10.
- Observed full-cycle time is about 30 seconds because scanning 12 enabled cameras takes time.
- Uses `LIVE_MONITOR_ALERT_COOLDOWN_SECONDS` when set; default is 300.
- Reuses the existing person detection, evidence save, event, cooldown, and Telegram alert flow.
- Suppresses routine no_person event writes to avoid excessive event-log noise.
- Continues running when a single camera fails and prints compact cycle summaries.
- Stops cleanly with Ctrl+C and exit code 0.

Current production task plan:

- Current Task Scheduler task name: ITU AI CCTV Live Monitor
- Keep the existing disabled `ITU AI CCTV Person Monitor` task as a backup path.
- Watch CPU, network, and camera load before reducing the interval to 5 seconds.
- MJPEG TV live stream is for viewing only and does not trigger AI detection.

## Script Exit Meaning

The Python monitor script can report:

- 0 = ok / no attention required / no person detected
- 1 = one or more camera checks failed
- 2 = attention required / person detected, not a crash

The BAT launcher returns 0 to Windows Task Scheduler. This is intentional because person detection is an operational event, not a failed scheduled task.

Review backend/data/task-logs/monitor_person_all.log for actual monitor results.

## Dashboard Scheduler Health

GET /dashboard/health reads backend/data/task-logs/monitor_person_all.log and returns a lightweight scheduler summary when the log is available.

Scheduler health fields:

- status
- latest_run_time
- latest_summary
- failed_count
- person_detected_count
- no_person_count
- log_path
- recent_lines

The dashboard parser reads existing log text only. It does not run YOLO detection, open RTSP streams, or expose credentials. If a value cannot be found in the log, the API returns null or unknown.

The /dashboard-ui Health card shows the latest scheduler run and summary.

GET /dashboard/health also combines scheduler status with event-log based camera freshness. Per-camera health can report:

- active
- stale
- no_recent_event
- disabled
- offline

The default stale threshold is 120 minutes. Stale health is based on existing event/check timestamps from backend/data/events.jsonl.

Current expected healthy dashboard state:

- Dashboard UI: http://192.168.1.254:8000/dashboard-ui
- Health endpoint: http://192.168.1.254:8000/dashboard/health
- total cameras: 13
- enabled: 12
- disabled/offline: 1
- active/stale counts depend on latest live monitor events and the configured stale threshold
- live monitor task: ITU AI CCTV Live Monitor Running
- old batch task: ITU AI CCTV Person Monitor Disabled

Use 127.0.0.1 only when browsing on the server itself.

Known camera note:

- block_f_cam_8 / ITU BLOCK F CAM8 remains disabled/offline.
- IP: 192.168.40.20.
- Ping and RTSP port 554 are not reachable.
- Do not treat it as a system failure unless intentionally re-enabled later.

Operational notes:

- RTSP timeouts may happen temporarily if the CCTV network is unstable.
- Avoid overlapping scheduler runs if check-all takes too long.
- When working inside OneDrive, pause sync during coding or Git work if Git, virtualenv, or project files are being modified.
- Never commit backend/.env, virtualenv folders, logs, evidence images, or local handoff notes.

## PowerShell Commands

Check backend service:

Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType

Check backend listening port:

netstat -ano | findstr ":8000"

Check backend Python process:

Get-CimInstance Win32_Process -Filter "name='python.exe'" |
  Select-Object ProcessId, CreationDate, CommandLine |
  Format-List

Check task state:

Get-ScheduledTask -TaskName "ITU AI CCTV Person Monitor" | Select-Object TaskName, State

Show task info:

Get-ScheduledTaskInfo -TaskName "ITU AI CCTV Person Monitor"

Enable the task:

Enable-ScheduledTask -TaskName "ITU AI CCTV Person Monitor"

Disable the task:

Disable-ScheduledTask -TaskName "ITU AI CCTV Person Monitor"

Start the task manually:

Start-ScheduledTask -TaskName "ITU AI CCTV Person Monitor"
Start-Sleep -Seconds 60

Read scheduler log:

Get-Content C:\ituaicctv\backend\data\task-logs\monitor_person_all.log -Tail 160

Check latest evidence:

Get-ChildItem C:\ituaicctv\backend\data\evidence |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 10 Name, LastWriteTime, Length

Open evidence share:

explorer "\\192.168.1.254\ituaicctv-evidence"

Check RTSP reachability from server:

Test-NetConnection 192.168.40.21 -Port 554
Test-NetConnection 192.168.40.22 -Port 554

Check dashboard port from laptop / Teleport:

Test-NetConnection 192.168.1.254 -Port 8000
