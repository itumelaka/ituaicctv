# ITU AI CCTV - Security Notes

## Current Production Security Posture

- Production backend path: C:\ituaicctv
- Production dashboard: http://192.168.1.254:8000/dashboard-ui
- TV command center dashboard: http://192.168.1.254:8000/dashboard-tv
- Backend service ITUAICCTVBackend is Running and Automatic.
- Task Scheduler task ITU AI CCTV Person Monitor is Ready.
- Backend listens on port 8000.
- Windows Firewall allows inbound TCP 8000 for dashboard/API.
- UDM Pro allows server 192.168.1.254 to CCTV subnet 192.168.40.0/24 on TCP 554.
- Current camera inventory has 13 known cameras, 12 enabled cameras, and 1 disabled/offline camera. The mistaken 192.168.40.26 entry is not part of the current inventory.
- Evidence share: \\192.168.1.254\ituaicctv-evidence
- Normal evidence share access: Read for Everyone.
- Temporary Change access is allowed only during controlled copy operations and must be reverted to Read.
- NTFS Everyone Modify was removed after copy cleanup.
- Browser may show a directory index if opening the UNC/share path; use File Explorer for folder browsing.
- `/dashboard-tv` includes a selectable backend-proxied MJPEG live camera view.
- Browser access is internal HTTP, so browsers may show "Not secure" unless HTTPS, a reverse proxy, and a certificate are configured.

Verify production access:

```powershell
Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType
Get-ScheduledTask -TaskName "ITU AI CCTV Person Monitor" | Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName "ITU AI CCTV Person Monitor"
Invoke-RestMethod http://127.0.0.1:8000/dashboard/health | ConvertTo-Json -Depth 8
Get-SmbShareAccess -Name "ituaicctv-evidence"
```

## Credentials

Never commit real CCTV usernames or passwords.

backend/.env is local only. It must stay on the deployment machine and must not be committed, copied into documentation, pasted into chat, or included in screenshots.

Do not commit:

- backend/.env
- .env
- Virtualenv folders such as .venv, .venv312, or backend/.venv
- Runtime logs under backend/data/task-logs/
- Runtime service logs under backend/data/service-logs/
- Evidence images under backend/data/evidence/
- Local handoff notes
- Any screenshot showing CCTV credentials
- RTSP URLs that contain a username or password
- Telegram bot tokens or chat IDs
- CCTV passwords or credential-bearing connection strings
- Face images, face crops, face embeddings, or personal identity data

Use backend/.env.example for placeholders only.

## Local Handoff Notes

Private local handoff notes, including sambung.txt, are for local continuity only and should not be committed.

## Dashboard Security

Dashboard endpoints and the browser dashboard must remain credential-safe.

Rules:

- Do not expose RTSP usernames, passwords, or credential-bearing RTSP URLs in dashboard responses.
- Do not show backend/.env values in the dashboard.
- Keep dashboard endpoints lightweight and read-only unless a future change explicitly adds protected controls.
- Evidence links should use the local evidence-serving endpoint, such as /events/evidence/{filename}, not direct camera URLs.
- Scheduler log health summaries must stay credential-safe. If log lines ever contain credential-like fields or RTSP URLs, dashboard health output should mask them before display.
- The TV MJPEG endpoint `/dashboard/live/{camera_id}/stream.mjpg` must remain a backend proxy. The browser must never receive RTSP URLs, CCTV usernames, or CCTV passwords.
- The MJPEG stream is intended for one selected camera/viewer on the TV dashboard. Avoid opening many browser tabs or streaming many cameras at once.
- The snapshot fallback `/dashboard/live/{camera_id}/snapshot.jpg` returns one JPEG frame and should also remain credential-safe.
- Future public or wider LAN exposure should use HTTPS through a reverse proxy or certificate-backed deployment.

## CCTV User Account

Recommended:

Create a dedicated CCTV user for AI backend.

Example:

- Username: ai_backend
- Permission: Live view / RTSP only
- Avoid admin permission if possible

## Runtime Data

Runtime event logs and evidence images are ignored from Git.

Ignored paths:

- backend/data/events.jsonl
- backend/data/task-logs/
- backend/data/evidence/

Evidence images may contain real CCTV footage. Handle them carefully:

- Do not commit evidence images.
- Share evidence only with authorised staff.
- Production evidence is stored on the Windows Server at C:\ituaicctv\backend\data\evidence.
- The operational SMB share is \\192.168.1.254\ituaicctv-evidence.
- Laptop evidence folders are not production evidence storage.
- Avoid posting evidence images in public chats, issue trackers, or documentation.
- Apply a retention policy before production use.

Evidence images are saved only for person_detected=True events. no_person events usually have no evidence image.

## Evidence Share Maintenance

Copy laptop evidence to the server only when needed:

```powershell
$source = "C:\Users\burnk\OneDrive\Documents-assets\ai-cctv-detection\backend\data\evidence"
$dest = "\\192.168.1.254\ituaicctv-evidence"
robocopy $source $dest *.jpg /E /XO /R:2 /W:2
```

If write access is needed temporarily, grant it on the server and revert immediately after copying:

```powershell
Grant-SmbShareAccess -Name "ituaicctv-evidence" -AccountName "Everyone" -AccessRight Change -Force
icacls "C:\ituaicctv\backend\data\evidence" /grant "*S-1-1-0:(OI)(CI)M"

Revoke-SmbShareAccess -Name "ituaicctv-evidence" -AccountName "Everyone" -Force
Grant-SmbShareAccess -Name "ituaicctv-evidence" -AccountName "Everyone" -AccessRight Read -Force
icacls "C:\ituaicctv\backend\data\evidence" /remove:g "*S-1-1-0"
Get-SmbShareAccess -Name "ituaicctv-evidence"
```

Do not leave temporary share Change access or NTFS Everyone Modify in place.

## Face Recognition

Face recognition involves biometric data.

Face work must be phased and privacy-first:

1. Face detection only, no identity recognition.
2. Face crop saving linked to existing person detection evidence.
3. Opt-in known-person recognition using approved reference images only.
4. Dashboard review and human confirmation before operational identity action.

Rules:

- Current face readiness metadata is advisory only. It may report face detection availability, face count, a best face box, quality, readiness, and quality reasons, but it must not identify anyone.
- Optional face recognition is internal staff/student only, config-controlled, and disabled by default. Do not enable it unless authorization, consent/policy, access control, audit logs, and retention/deletion rules are ready.
- Use face recognition only with clear authorization, consent, or written policy.
- Do not store random unknown face identities by default.
- Do not expose any face database, crop folder, embedding store, or identity mapping publicly.
- Never commit face images, face embeddings, or personal identity data to Git.
- Keep face reference data local and private on the production server.
- Telegram alerts should avoid unnecessary personal data. Prefer a generic review alert unless policy explicitly allows names.
- `UNKNOWN` means no reliable enrolled internal match. It must not be treated as suspicious by itself.
- Keep Hikvision/NVR recording separate from AI evidence, face references, and face embeddings.

Proposed future private folders:

- backend/data/faces/reference/ - approved reference images only
- backend/data/faces/embeddings/ - private generated embeddings
- backend/data/faces/crops/ - detected face crops linked to evidence review
- backend/data/face-embeddings/ - legacy/private embeddings path, ignored
- backend/data/face-reference/ - legacy/private reference path, ignored

Before enabling identity recognition:

- Define clear purpose
- Get proper approval
- Notify affected users
- Limit who can access recognition results
- Set retention period
- Avoid storing unnecessary face data
- Keep audit logs
- Verify high-resolution face evidence quality and camera placement first

For early development, start with face detection only.

## Number Plate Recognition

Vehicle number plates may become personal data if linked to individuals or ownership records.

Recommended controls:

- Store only necessary events
- Limit access
- Define retention period
- Use for security purpose only
- Avoid public exposure

## Deployment

For production:

- Use an always-on Windows Server or dedicated monitoring PC
- Secure .env file
- Restrict folder permissions
- Keep GitHub repo free from secrets
- Backup only required evidence and logs

## OneDrive Development Note

When working inside OneDrive, pause sync during coding or Git work if Git, virtualenv, or project files are being modified. This helps avoid file-locking or partial-sync issues.
