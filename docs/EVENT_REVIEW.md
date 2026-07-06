# ITU AI CCTV - Event Review

Event review / acknowledgement is deployed and verified as an internal local workflow.

## API Endpoints

```text
GET /events/reviews
GET /events/reviews/{event_id}
PUT /events/reviews/{event_id}
POST /events/reviews/{event_id}
GET /events/latest-with-reviews
```

## Review Statuses

- `unreviewed`: no operator decision has been recorded yet.
- `valid`: the event appears to be a real person alert.
- `false_positive`: the event appears to be a mistaken person detection.
- `ignored`: the event is intentionally ignored for operations.
- `needs_follow_up`: the event needs another check or action.
- `reviewed`: generic reviewed state when no more specific status is chosen.

## Dashboard Workflow

The normal dashboard shows review status in latest event cards and provides quick buttons:

- Valid
- False positive
- Follow up

Evidence gallery remains separate and continues to show historical evidence images.

Evidence event cards can also show `Assign Identity` when an event has evidence and the face/person is unknown or recognition was not attempted. This is a human review record only. It does not auto-train, update the face model, or change Telegram behavior.

For single-person events, `PERSON 1` is selected automatically. For multi-person events, operators must choose the matching metadata target, such as `PERSON 1`, `PERSON 2`, or `PERSON 3`, before saving. The dashboard uses event metadata, not image pixel analysis.

New multi-person evidence events include synced `person_detections` metadata:

- `crop_rank`
- `confidence`
- `bbox`

Evidence can also include `evidence_source`:

- `hd_redetect`
- `hd_scaled_bbox`
- `detection_frame`

Existing old events are not migrated and may not have multi-person target metadata.

## Storage

Review data is local JSON under:

```text
backend/data/event-reviews/
```

This directory is ignored by Git. Do not commit runtime review JSON.

Identity assignment records are stored separately under:

```text
backend/data/face-enrollment/identity-assignments/identity_assignments.json
```

This file is also private runtime data and must not be committed.

## Limitations

There is no user login/authentication yet. Treat event review as an internal LAN operator workflow, not a controlled approval system.

If YOLO detects only one person even though humans can see multiple overlapping people, the assignment modal can only offer the detected `PERSON 1`. Crowded scenes may require future per-camera tuning, a stronger local detector, or tracking/counting support.

Future work:

- review filters for unreviewed, false positive, and follow-up events
- reviewer audit log
- authenticated users
- review export/reporting
