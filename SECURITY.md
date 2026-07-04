# Security Policy

Dokumen ini menerangkan garis panduan keselamatan untuk projek **Hikvision AI CCTV Detection Project**.

## Current Production Security Status

- Production backend path: `C:\ituaicctv`
- Production dashboard: `http://192.168.1.254:8000/dashboard-ui`
- GitHub Pages is no longer the primary production dashboard.
- Backend service `ITUAICCTVBackend` is confirmed `Running` and `Automatic`.
- Task Scheduler task `ITU AI CCTV Person Monitor` is confirmed `Ready`.
- Windows Firewall allows inbound TCP `8000` for dashboard/API access.
- UDM Pro allows server `192.168.1.254` to CCTV subnet `192.168.40.0/24` on TCP `554`.
- Evidence share: `\\192.168.1.254\ituaicctv-evidence`
- Evidence share should normally be read-only for Everyone.
- Temporary Change access for evidence copying must be reverted to Read after copying.
- NTFS Everyone Modify was removed after copy cleanup; backend/server can still save evidence locally.

Verify service, scheduler, and health:

```powershell
Get-Service ITUAICCTVBackend | Select-Object Name, Status, StartType
Get-ScheduledTask -TaskName "ITU AI CCTV Person Monitor" | Select-Object TaskName, State
Invoke-RestMethod http://127.0.0.1:8000/dashboard/health | ConvertTo-Json -Depth 6
```

## Prinsip Keselamatan

Sistem CCTV mengandungi data sensitif. Semua pembangunan dan penggunaan sistem ini mesti mengutamakan keselamatan rangkaian, privasi pengguna, dan kawalan akses.

## Credential dan Password

Jangan simpan maklumat berikut dalam GitHub atau mana-mana repository awam:

- Username CCTV/NVR sebenar.
- Password CCTV/NVR sebenar.
- RTSP URL lengkap yang mengandungi username/password.
- Token Telegram Bot.
- Telegram chat ID.
- SMTP password.
- IP dalaman sensitif jika repo dijadikan public.
- Log runtime, gambar evidence CCTV, folder virtualenv, atau nota handoff local.
- Face images, face embeddings, or personal identity data.

Gunakan fail `.env` atau config local yang dimasukkan dalam `.gitignore`.

Contoh `.env`:

```env
CCTV_USERNAME=readonly_user
CCTV_PASSWORD=change_this_password
TELEGRAM_BOT_TOKEN=change_this_token
TELEGRAM_CHAT_ID=change_this_chat_id
```

## Akses CCTV

- Gunakan akaun **read-only** untuk AI system.
- Elakkan guna akaun admin utama NVR.
- Tukar password default kamera/NVR.
- Hadkan akses kepada IP server AI sahaja jika boleh.
- Jangan expose port RTSP/NVR ke internet.
- Jika akses luar diperlukan, gunakan VPN.

## Network Security

Cadangan asas:

```text
CCTV VLAN / LAN dalaman
        ↓
AI Server dengan akses terkawal
        ↓
Dashboard dalaman / Alert service
```

Elakkan:

```text
Internet public → RTSP/NVR port terbuka
```

## Data dan Privasi

- Simpan snapshot hanya apabila perlu.
- Tetapkan retention policy untuk memadam log/snapshot lama.
- Elakkan rakaman atau snapshot kawasan privasi tinggi.
- Letakkan notis CCTV jika diperlukan oleh polisi organisasi.
- Hadkan akses kepada dashboard/event log kepada pegawai berkaitan sahaja.

## Git Ignore Cadangan

Pastikan fail ini tidak di-commit:

```gitignore
.env
config/cameras.json
events/*
!events/.gitkeep
*.log
__pycache__/
.venv/
.venv312/
backend/data/task-logs/
backend/data/service-logs/
backend/data/evidence/
```

Evidence production disimpan di Windows Server pada `C:\ituaicctv\backend\data\evidence` dan boleh dibuka secara dalaman melalui `\\192.168.1.254\ituaicctv-evidence`. Jangan commit evidence image, log, token, password, atau RTSP URL yang mengandungi credential.

## Evidence Share Operations

Normal operation:

- Share path: `\\192.168.1.254\ituaicctv-evidence`
- Server folder: `C:\ituaicctv\backend\data\evidence`
- Share access: Read for Everyone
- Backend writes locally; users review evidence through dashboard or File Explorer.

Temporary copy workflow:

```powershell
Grant-SmbShareAccess -Name "ituaicctv-evidence" -AccountName "Everyone" -AccessRight Change -Force
icacls "C:\ituaicctv\backend\data\evidence" /grant "*S-1-1-0:(OI)(CI)M"

$source = "C:\Users\burnk\OneDrive\Documents-assets\ai-cctv-detection\backend\data\evidence"
$dest = "\\192.168.1.254\ituaicctv-evidence"
robocopy $source $dest *.jpg /E /XO /R:2 /W:2

Revoke-SmbShareAccess -Name "ituaicctv-evidence" -AccountName "Everyone" -Force
Grant-SmbShareAccess -Name "ituaicctv-evidence" -AccountName "Everyone" -AccessRight Read -Force
icacls "C:\ituaicctv\backend\data\evidence" /remove:g "*S-1-1-0"
Get-SmbShareAccess -Name "ituaicctv-evidence"
```

Do not leave Change/Modify access open after copying.

## Responsible Use

Sistem ini bertujuan membantu keselamatan dan operasi institut. Ia tidak patut digunakan untuk pemantauan individu secara berlebihan, pengecaman identiti tanpa kebenaran, atau penggunaan yang melanggar polisi organisasi.
