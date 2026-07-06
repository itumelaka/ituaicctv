# ITU AI CCTV - Internal Face Recognition Notes

Face recognition is optional, internal, privacy-gated, and not high-security identity proof.

## Current State

- OpenCV LBPH backend is deployed for approved internal testing.
- Production can enable the backend through private `.env`.
- The approved internal test label `BURN` has been enrolled with private local samples.
- The test enrollment was improved from 3 samples to 6 samples using private CCTV-derived crops.
- Some CCTV-derived samples were rejected because face detection or quality was not suitable.

Do not include private sample filenames, generated crop filenames, enrollment images, embeddings, or model contents in public docs or Git.

## Recognition Limits

Recognition depends on:

- face readiness
- face angle
- lighting
- blur
- distance from camera
- camera resolution
- how closely live evidence matches enrolled samples

`UNKNOWN` means no reliable internal match. It does not mean suspicious.

## Privacy Rules

- Use only approved internal reference images.
- Keep reference images, embeddings, and models local/private.
- Never commit face enrollment images, embeddings, or model files.
- Do not expose face data through public dashboards or docs.
- Do not commit real enrollment CSV files with staff/student names, IDs, or private image paths.

## Face Enrollment Manager

The face enrollment manager is local-only and uses OpenCV/LBPH. It does not use paid APIs or cloud face recognition.

Write a placeholder CSV template:

```powershell
python scripts\manage_face_enrollment.py template --output private-face-enrollment-template.csv
```

Generate a draft CSV from a private local folder:

```powershell
python scripts\manage_face_enrollment.py draft `
  --source-dir "C:\private\approved-face-reference" `
  --output "C:\private\face-enrollment-draft.csv"
```

Draft rows are not approved by default. A human reviewer must verify each row and set `approved_for_face_recognition` to `yes` before enrollment.

Batch enroll approved rows into the local LBPH model:

```powershell
python scripts\manage_face_enrollment.py batch-enroll `
  --csv "C:\private\face-enrollment-reviewed.csv" `
  --reject-report "C:\private\face-enrollment-reject-report.json"
```

CSV columns:

- `label`
- `identity_id`
- `display_name`
- `image_path`
- `approved_for_face_recognition`
- `approved_by`
- `consent_reference`
- `notes`

Rejected rows are written to the reject report with row number, image path, label, and reason. Common reject reasons include unapproved rows, missing image paths, unreadable images, no suitable detected face, and low-quality face readiness.

Optional backend helpers:

- `GET /faces/enrollment/template` returns the placeholder CSV headers and example row.
- `POST /faces/enrollment/identity-assignment` validates and normalizes a local identity assignment payload.

These endpoints do not upload face images, copy private image paths, or call any cloud recognition service.

## Dashboard Identity Assignment

The backend dashboard can show a compact `Assign Identity` action for evidence events that are unknown or not yet recognized. Operators can enter an approved local label, display name, reviewer name, note, and whether the event may be considered for future training.

This dashboard action only records/validates the operator assignment payload through `/faces/enrollment/identity-assignment`. It does not train OpenCV LBPH, update the face model, change Telegram alerts, or add new reference images.

## Future Work

- reviewer audit logs
- retention/deletion policy
- clearer operator wording for unknown/low-quality recognition results
- higher-resolution face evidence path before any broader identity pilot
