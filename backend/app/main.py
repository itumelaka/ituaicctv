from fastapi import FastAPI
from app.routes.health import router as health_router

app = FastAPI(
    title="ITU AI CCTV Backend",
    description="Backend API for ITU AI CCTV detection system.",
    version="0.1.0",
)

app.include_router(health_router)

@app.get("/")
def root():
    return {
        "name": "ITU AI CCTV Backend",
        "status": "running"
    }
