# ITU AI CCTV - Windows Task Scheduler

Last updated: 2026-07-04

## Current Scheduler Status

Task name:

ITU AI CCTV Person Monitor

Current state:

- Registered on the Windows Server on 2026-07-03 via scripts/server/setup_task_scheduler.ps1
- Confirmed Ready on the production Windows Server
- Current production state confirmed Ready
- Uses the multi-camera hidden VBS launcher
- Checks enabled cameras from backend/config/cameras.json
- BAT launcher returns 0 to Task Scheduler so person detection or camera check results do not appear as Task Scheduler failures
- BAT launcher resolves the project root dynamically from the script location
- Python selection order:
  1. .venv312\Scripts\python.exe
  2. .venv\Scripts\python.exe
  3. python from PATH
- This fixes laptop environments where old .venv is missing or broken but .venv312 exists

Production server path:

C:\ituaicctv

Production scheduler Python:

C:\ituaicctv\.venv312\Scripts\python.exe

Latest confirmed successful server check-all run:

- Enabled cameras: 9
- Failed: 0
- Latest logs show status ok
- Current camera registry now has 12 enabled cameras after the newly labelled cameras were added.
- Exit code 0 means no person detected / no action
- Exit code 2 means attention required / person detected, not a crash
- YOLOv8n downloaded successfully on the server during the first successful run

## Reboot Behavior

- Backend service `ITUAICCTVBackend` is confirmed `Running`.
- Service `StartType` is confirmed `Automatic`.
- Backend/API/dashboard should auto-start after Windows Server reboot.
- Task `ITU AI CCTV Person Monitor` is confirmed `Ready`.
- Scheduler should continue using `C:\ituaicctv\.venv312\Scripts\python.exe`.

Verify after restart:

```powershell
Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType
Get-ScheduledTask -TaskName "ITU AI CCTV Person Monitor" | Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName "ITU AI CCTV Person Monitor"
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

## Optional Near-Live Monitor

The 5-minute Windows Task Scheduler job remains in place and can stay as a backup. For near-live alerting, the project also includes an optional long-running monitor:

```text
scripts/monitor_person_live.py
```

Manual production run command:

```powershell
C:\ituaicctv\.venv312\Scripts\python.exe C:\ituaicctv\scripts\monitor_person_live.py
```

Default behavior:

- Scans all enabled cameras sequentially every 10 seconds.
- Uses `LIVE_MONITOR_INTERVAL_SECONDS` when set; default is 10.
- Uses `LIVE_MONITOR_ALERT_COOLDOWN_SECONDS` when set; default is 300.
- Reuses the existing person detection, evidence save, event, cooldown, and Telegram alert flow.
- Suppresses routine no_person event writes to avoid excessive event-log noise.
- Continues running when a single camera fails and prints compact cycle summaries.
- Stops cleanly with Ctrl+C and exit code 0.

Production service plan:

- Optional future NSSM service name: ITUAICCTVLiveMonitor
- Keep the existing Task Scheduler job until the live monitor is proven stable.
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

Current expected healthy dashboard state after a successful scheduler run:

- Dashboard UI: http://192.168.1.254:8000/dashboard-ui
- Health endpoint: http://192.168.1.254:8000/dashboard/health
- total cameras: 13
- enabled: 12
- disabled/offline: 1
- active: 12 after the newly labelled cameras are confirmed by health checks
- stale: 0
- latest scheduler summary: status=ok, mode=check_all, enabled=9, person=0, no_person=9, failed=0

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
