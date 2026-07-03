# Security Policy

Dokumen ini menerangkan garis panduan keselamatan untuk projek **Hikvision AI CCTV Detection Project**.

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

## Responsible Use

Sistem ini bertujuan membantu keselamatan dan operasi institut. Ia tidak patut digunakan untuk pemantauan individu secara berlebihan, pengecaman identiti tanpa kebenaran, atau penggunaan yang melanggar polisi organisasi.
