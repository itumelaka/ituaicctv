from fastapi import APIRouter, HTTPException
from app.events import evaluate_person_event

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
