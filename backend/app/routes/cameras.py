from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.camera import test_rtsp_connection, capture_snapshot_jpeg, test_camera_connection
from app.camera_registry import load_cameras, list_enabled_cameras, get_camera_by_id

router = APIRouter(
    prefix="/cameras",
    tags=["Cameras"]
)

@router.get("/test")
def test_camera():
    return test_rtsp_connection()


@router.get("/snapshot")
def camera_snapshot():
    try:
        image_bytes = capture_snapshot_jpeg()
        return Response(
            content=image_bytes,
            media_type="image/jpeg"
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )


@router.get("/list")
def list_cameras():
    cameras = load_cameras()

    return {
        "status": "ok",
        "cameras_count": len(cameras),
        "enabled_count": len([camera for camera in cameras if camera.get("enabled", True)]),
        "cameras": cameras
    }


@router.get("/enabled")
def enabled_cameras():
    cameras = list_enabled_cameras()

    return {
        "status": "ok",
        "enabled_count": len(cameras),
        "cameras": cameras
    }


@router.get("/{camera_id}/test")
def test_camera_by_id(camera_id: str):
    try:
        camera = get_camera_by_id(camera_id)
        return test_camera_connection(camera)

    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )
