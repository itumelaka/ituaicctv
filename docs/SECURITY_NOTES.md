# ITU AI CCTV - Security Notes

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

## Face Recognition

Face recognition involves biometric data.

Before enabling identity recognition:

- Define clear purpose
- Get proper approval
- Notify affected users
- Limit who can access recognition results
- Set retention period
- Avoid storing unnecessary face data
- Keep audit logs

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
