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

## Storage

Review data is local JSON under:

```text
backend/data/event-reviews/
```

This directory is ignored by Git. Do not commit runtime review JSON.

## Limitations

There is no user login/authentication yet. Treat event review as an internal LAN operator workflow, not a controlled approval system.

Future work:

- review filters for unreviewed, false positive, and follow-up events
- reviewer audit log
- authenticated users
- review export/reporting
