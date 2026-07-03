from fastapi import APIRouter, HTTPException, Query
from app.events import evaluate_person_event, get_latest_events

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.get("/person")
def person_event():
    try:
        return evaluate_person_event()

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Person event evaluation failed: {error}"
        )


@router.get("/logs")
def event_logs(limit: int = Query(default=20, ge=1, le=100)):
    try:
        return get_latest_events(limit=limit)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Reading event logs failed: {error}"
        )
