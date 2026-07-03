from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.cameras import router as cameras_router
from app.routes.detections import router as detections_router
from app.routes.events import router as events_router

app = FastAPI(
    title="ITU AI CCTV Backend",
    description="Backend API for ITU AI CCTV detection system.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(cameras_router)
app.include_router(detections_router)
app.include_router(events_router)

@app.get("/")
def root():
    return {
        "name": "ITU AI CCTV Backend",
        "status": "running"
    }
