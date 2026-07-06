# ITU AI CCTV - Internal Face Recognition Notes

Face recognition is optional, internal, privacy-gated, and not high-security identity proof.

## Current State

- OpenCV LBPH backend is deployed for approved internal testing.
- Production can enable the backend through private `.env`.
- Approved internal test labels can be enrolled with private local samples.
- Some private candidate samples may be rejected because face detection or quality is not suitable.

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

The face enrollment manager is local-only and uses OpenCV/LBPH. It does not use paid APIs, cloud face recognition, or external upload of staff/student images.

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
- `POST /faces/enrollment/identity-assignment` validates, normalizes, and persists a local identity assignment payload.
- `GET /faces/enrollment/identity-assignments` reads saved local assignment records.

These endpoints do not upload face images, copy private image paths, or call any cloud recognition service.

Private runtime storage:

```text
backend/data/face-enrollment/
backend/data/face-enrollment/identity-assignments/identity_assignments.json
backend/data/face-embeddings/
```

Do not commit CSVs, reject reports containing private paths, crops, assignments, face images, embeddings, model files, evidence, logs, `.env`, `.venv`, or `.venv312`.

## Dashboard Identity Assignment

The backend dashboard can show a compact `Assign Identity` action for evidence events that are unknown or not yet recognized. Operators can enter an approved local label, display name, reviewer name, note, and whether the event may be considered for future training.

For single-person evidence, `PERSON 1` is selected automatically. For multi-person evidence, the dashboard requires the operator to choose the person target, such as `PERSON 1`, `PERSON 2`, or `PERSON 3`, before saving. The assignment payload includes person rank, confidence, and bounding box metadata so later review can distinguish which detected person was assigned.

This dashboard action records a human review assignment only. It does not train OpenCV LBPH, update the face model, change Telegram alerts, or add new reference images.

Identity assignments are persisted locally in the private runtime file `backend/data/face-enrollment/identity-assignments/identity_assignments.json`. The file stores operator-approved assignment metadata only, including the event/evidence identifiers and person target metadata for multi-person events. Saved assignments can be read back through `GET /faces/enrollment/identity-assignments`.

Assignment payload fields:

- `event_id`
- `review_id`
- `evidence_filename`
- `assigned_label`
- `assigned_display_name`
- `assigned_by`
- `note`
- `approved_for_training`
- `person_rank`
- `person_confidence`
- `person_bbox`
- `person_target_label`

Recommended label examples are neutral local IDs such as `STAFF_001`, `STUDENT_001`, or `VISITOR_001`. `assigned_display_name` can be human-readable in private runtime data if local policy allows it. `approved_for_training` should normally remain false until a proper approval, consent, and manual review process exists.

## Multi-Person Evidence Metadata

New evidence composites show up to the top three detected person crops, ordered by confidence, while the main frame keeps all detected person boxes. New event metadata includes `person_detections` with `crop_rank`, `confidence`, and `bbox`, synced to the rendered evidence crops.

Evidence metadata also includes `evidence_source`:

- `hd_redetect`: HD/main-stream capture succeeded and YOLO found valid persons on the HD frame.
- `hd_scaled_bbox`: HD/main-stream capture succeeded, HD re-detection found no person, and scaled sub-stream boxes produced valid HD crops.
- `detection_frame`: the system used the original detection frame because HD capture failed or scaled HD crops were invalid.

The HD scaled-bbox fallback can improve face readiness from `not_suitable` to `possible` or `suitable` when the original sub-stream crop was too small. It does not guarantee identity recognition; a clear face can still return `UNKNOWN` when the local model does not match.

Assign Identity uses event metadata, not image pixel analysis. Existing old events are not migrated, so older evidence may not have multi-person target metadata.

If YOLO detects only one person even though a human sees multiple overlapping people, the dashboard can only assign detected `PERSON 1`. Crowded or wide scenes may need per-camera tuning or a future local detector/tracker.

## Limitations

- `UNKNOWN` means no reliable enrolled internal match. It does not mean suspicious.
- `face_not_suitable` / face not suitable means the face is not clear enough for recognition.
- LBPH is a proof-of-concept local backend, not high-security identity proof.
- Assignments are human review records only until a future approved-training workflow exists.
- Future local options include InsightFace/ArcFace ONNX, DeepFace local backend, OpenVINO person detection, selected-camera stronger YOLO models, and ByteTrack/BoT-SORT for counting/tracking.
- Keep the local-only, no paid API, and no cloud upload principle.

## Future Work

- reviewer audit logs
- retention/deletion policy
- clearer operator wording for unknown/low-quality recognition results
- higher-resolution face evidence path before any broader identity pilot
- approved assignment-to-training-sample workflow with manual review
- cleanup/manage identity assignment records UI
