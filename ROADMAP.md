# Project Roadmap

Roadmap ini disusun untuk membangunkan projek **Hikvision AI CCTV Detection Project** secara berperingkat.

## Phase 0: Documentation and Planning

Status: **Complete**

Tasks:

- [x] Sediakan README.md.
- [x] Sediakan SECURITY.md.
- [x] Sediakan REQUIREMENTS.md.
- [x] Sediakan ARCHITECTURE.md.
- [x] Senaraikan kamera/NVR yang terlibat (camera-inventory.md).
- [x] Tetapkan use case pilot.

Deliverable:

- Dokumentasi asas projek lengkap.

## Phase 1: RTSP Pilot Test

Status: **Complete**

Tasks:

- [x] Dapatkan IP NVR/kamera (192.168.40.21).
- [x] Cipta user read-only untuk stream.
- [x] Test RTSP dalam VLC.
- [x] Test main stream dan sub stream (channel 101/102).
- [x] Rekod format RTSP yang berjaya (H.264, sub-stream 640x360).

Acceptance Criteria:

- Satu kamera berjaya live view melalui RTSP.
- Stream stabil sekurang-kurangnya 30 minit.

## Phase 2: Basic AI Detection Prototype

Status: **Complete**

Tasks:

- [x] Setup Python environment (.venv312).
- [x] Install OpenCV dan YOLO/Ultralytics.
- [x] Baca RTSP stream (camera.py).
- [x] Detect person (detection.py — YOLO person-only mode).
- [x] Return bounding box, confidence, detection result.

Acceptance Criteria:

- Sistem boleh detect person daripada live CCTV.
- FPS dan CPU/GPU usage direkod.

## Phase 3: Event Logging and Snapshot

Status: **Complete**

Tasks:

- [x] Simpan snapshot apabila person detection berlaku (evidence/).
- [x] Simpan event log dalam JSONL (events.jsonl).
- [x] Tambah cooldown untuk elak spam event (PERSON_EVENT_COOLDOWN_SECONDS).
- [x] Tambah camera name, timestamp, severity, evidence_path.

Acceptance Criteria:

- Event detection menghasilkan snapshot dan log.
- Duplicate alert terkawal.

## Phase 4: Alert System

Status: **Complete**

Tasks:

- [x] Setup Telegram Bot alert (alert.py).
- [x] Hantar alert apabila person_detected=True dan cooldown tidak aktif.
- [x] Sertakan snapshot sebagai foto Telegram jika evidence ada.
- [x] Alert skip secara senyap jika token tidak dikonfigurasi.
- [x] `alert_sent` dikembalikan dalam response monitor endpoint.
- [ ] Enable/disable alert per kamera (future enhancement).

Acceptance Criteria:

- PIC menerima alert dengan maklumat event.
- Alert tidak spam berulang tanpa kawalan.

## Phase 5: Dashboard Basic

Status: **Complete**

Tasks:

- [x] Papar status kamera (dashboard/cameras, per-camera health).
- [x] Papar senarai event terkini (dashboard/events/latest).
- [x] Papar snapshot event (dashboard/evidence, evidence thumbnails).
- [x] Dashboard UI boleh dibuka dalam LAN (GET /dashboard-ui).
- [x] Auto-refresh setiap 30 saat.
- [x] Health monitoring per kamera (active/stale/offline/disabled).
- [x] Scheduler log summary dalam health endpoint.

Acceptance Criteria:

- Dashboard boleh dibuka dalam LAN.
- Event terkini boleh disemak oleh PIC.

## Phase 6: Advanced Detection

Status: **Not started**

Possible features:

- Intrusion zone.
- Line crossing.
- PPE detection.
- Animal detection.
- After-hours detection.
- Crowd counting.
- Loitering detection.

Acceptance Criteria:

- Use case lanjutan diuji satu per satu.
- False positive direkod dan dikurangkan.

## Phase 7: Production Hardening

Status: **In Progress**

Tasks:

- [x] GitHub Pages dashboard live di https://itumelaka.github.io/ituaicctv/
- [x] Dashboard installable sebagai PWA (Add to Home Screen).
- [x] CORS enabled pada backend supaya browser LAN boleh connect dari GitHub Pages.
- [x] Backend URL configurable dalam dashboard (simpan dalam localStorage).
- [x] Windows Server deployment guide dalam README.
- [ ] Deploy backend ke Windows Server (bilik server).
- [ ] Setup NSSM untuk auto-start backend sebagai Windows Service.
- [ ] Allow port 8000 dalam Windows Firewall (LAN only).
- [ ] Log rotation.
- [ ] Config backup.
- [ ] Retention policy snapshot/log.

Acceptance Criteria:

- Sistem boleh berjalan stabil untuk tempoh panjang.
- Ada SOP restart, backup dan troubleshooting.

## Suggested First Pilot

Cadangan paling selamat:

```text
Kamera: Pintu masuk / laluan umum
Detection: Person detected after office hours
Alert: Telegram
Storage: Snapshot + JSONL log
```

Sebab:

- Use case jelas.
- Risiko privacy lebih rendah berbanding kawasan sensitif.
- Mudah validate sama ada detection tepat atau tidak.
