# ITU AI CCTV - Windows Task Scheduler

Last updated: 2026-07-03

## Current Scheduler Status

Task name:

ITU AI CCTV Person Monitor

Current state:

- Intentionally Disabled
- Enable only when operational testing is ready
- Uses the multi-camera hidden VBS launcher
- Checks enabled cameras from backend/config/cameras.json
- BAT launcher returns 0 to Task Scheduler so person detection or camera check results do not appear as Task Scheduler failures

## Scheduler Scripts

Main monitor script:

backend/scripts/monitor_person_all_once.py

BAT launcher:

backend/scripts/run_monitor_person_all_once.bat

Hidden VBS launcher:

backend/scripts/run_monitor_person_all_once_hidden.vbs

Runtime log:

backend/data/task-logs/monitor_person_all.log

## Launcher Flow

Windows Task Scheduler
-> backend/scripts/run_monitor_person_all_once_hidden.vbs
-> backend/scripts/run_monitor_person_all_once.bat
-> backend/scripts/monitor_person_all_once.py
-> backend/data/task-logs/monitor_person_all.log

## Monitor Scope

The multi-camera script checks all enabled cameras from the camera registry.

Current camera summary:

- Total cameras: 10
- Enabled cameras: 9
- Disabled cameras: 1
- Disabled camera: block_f_cam_8 / 192.168.40.20
- Reason: ping and RTSP port 554 are not reachable

## Script Exit Meaning

The Python monitor script can report:

- 0 = no person detected
- 1 = one or more camera checks failed
- 2 = person detected

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

## PowerShell Commands

Enable the task:

Enable-ScheduledTask -TaskName "ITU AI CCTV Person Monitor"

Disable the task:

Disable-ScheduledTask -TaskName "ITU AI CCTV Person Monitor"

Check task state:

Get-ScheduledTask -TaskName "ITU AI CCTV Person Monitor" | Select-Object TaskName, State
