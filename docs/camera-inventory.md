# Camera Inventory

Dokumen ini digunakan untuk merekod maklumat asas CCTV/NVR Hikvision yang akan diuji untuk projek AI CCTV Detection.

> Jangan letak password sebenar dalam fail ini.

## NVR / DVR Info

| Item | Maklumat |
|---|---|
| Brand | Hikvision |
| Model | TBD |
| IP Address | TBD |
| RTSP Port | 554 |
| HTTP Port | TBD |
| Location | Institut |
| Network Segment | LAN sahaja |
| Admin Access | Ya / Tidak |
| ONVIF Enabled | Ya / Tidak |

## Camera List

| Channel | Nama Kamera | Lokasi | Stream Test | AI Use Case | Catatan |
|---|---|---|---|---|---|
| 1 | CAM-01 | TBD | Belum test | Person detection | Pilot camera |
| 2 | CAM-02 | TBD | Belum test | TBD | TBD |

## Priority Pilot

Untuk fasa awal, pilih 1 kamera sahaja.

Cadangan pilihan:
- Kamera yang menghadap pintu masuk
- Kamera yang stabil siang/malam
- Kamera yang tidak terlalu ramai objek bergerak
- Kamera yang jelas dan tidak terlalu kabur

## Notes

- Gunakan akaun read-only jika boleh.
- Jangan expose RTSP ke internet.
- Simpan credential dalam `.env`, bukan dalam fail Markdown.
