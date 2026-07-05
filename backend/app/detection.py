from functools import lru_cache
import logging
import cv2
from ultralytics import YOLO
from app.camera import (
    capture_frame,
    capture_frame_for_camera,
    capture_frame_for_camera_channel,
)
from app.config import settings

logger = logging.getLogger(__name__)

MODEL_NAME = "yolov8n.pt"
PERSON_CLASS_NAME = "person"
PERSON_CROP_PADDING_PX = 32
PERSON_CROP_PANEL_MIN_WIDTH = 320
FACE_READY_MIN_FRAME_HEIGHT_PX = 720
FACE_READY_MIN_PERSON_BOX_WIDTH_PX = 120
FACE_READY_MIN_PERSON_BOX_HEIGHT_PX = 220
DEFAULT_EVIDENCE_CHANNEL = "101"


def _person_confidence_threshold(camera: dict | None = None) -> float:
    if camera and camera.get("person_confidence_threshold") is not None:
        return float(camera.get("person_confidence_threshold"))

    return settings.person_confidence_threshold


def _evidence_channel(camera: dict | None = None) -> str | None:
    if not camera:
        return None

    configured_channel = (
        camera.get("evidence_channel")
        or camera.get("high_resolution_channel")
        or camera.get("main_stream_channel")
    )

    if configured_channel:
        return str(configured_channel)

    detection_channel = str(camera.get("channel", "102"))

    if detection_channel != DEFAULT_EVIDENCE_CHANNEL:
        return DEFAULT_EVIDENCE_CHANNEL

    return None


@lru_cache(maxsize=1)
def get_model():
    return YOLO(MODEL_NAME)


def detect_objects(
    frame,
    class_name_filter: str | None = None,
    confidence_threshold: float | None = None
):
    model = get_model()
    confidence = settings.yolo_confidence if confidence_threshold is None else confidence_threshold

    results = model.predict(
        source=frame,
        conf=confidence,
        verbose=False,
        device="cpu"
    )

    detections = []

    if results and len(results) > 0:
        result = results[0]
        names = result.names

        for box in result.boxes:
            class_id = int(box.cls[0].item())
            class_name = names.get(class_id, str(class_id))

            if class_name_filter and class_name != class_name_filter:
                continue

            confidence = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": round(confidence, 4),
                "box": {
                    "x1": round(float(x1), 2),
                    "y1": round(float(y1), 2),
                    "x2": round(float(x2), 2),
                    "y2": round(float(y2), 2)
                }
            })

    return detections


def _build_detection_response(
    frame,
    detections,
    camera_info: dict | None = None,
    filter_name: str | None = None,
    confidence_threshold: float | None = None
):
    height, width = frame.shape[:2]
    confidence = settings.yolo_confidence if confidence_threshold is None else confidence_threshold

    response = {
        "status": "ok",
        "model": MODEL_NAME,
        "confidence_threshold": confidence,
        "camera": {
            "frame_width": width,
            "frame_height": height
        },
        "detections_count": len(detections),
        "detections": detections
    }

    if filter_name:
        response["filter"] = filter_name

    if filter_name == PERSON_CLASS_NAME:
        response["person_detected"] = len(detections) > 0

    if camera_info:
        response["camera"].update({
            "id": camera_info.get("id"),
            "name": camera_info.get("name"),
            "host": camera_info.get("host"),
            "channel": camera_info.get("channel")
        })

    return response


def run_yolo_detection() -> dict:
    frame = capture_frame()
    detections = detect_objects(frame)
    return _build_detection_response(frame, detections)


def run_person_detection() -> dict:
    detection_response, _ = run_person_detection_with_frame()
    return detection_response


def run_person_detection_with_frame() -> tuple[dict, object]:
    frame = capture_frame()
    confidence = _person_confidence_threshold()
    detections = detect_objects(
        frame,
        class_name_filter=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )
    detection_response = _build_detection_response(
        frame,
        detections,
        filter_name=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )

    return detection_response, frame


def run_person_detection_for_camera(camera: dict) -> dict:
    detection_response, _ = run_person_detection_with_frame_for_camera(camera)
    return detection_response


def run_person_detection_with_frame_for_camera(camera: dict) -> tuple[dict, object]:
    frame = capture_frame_for_camera(camera)
    confidence = _person_confidence_threshold(camera)
    detections = detect_objects(
        frame,
        class_name_filter=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )
    detection_response = _build_detection_response(
        frame,
        detections,
        camera_info=camera,
        filter_name=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )

    return detection_response, frame


def _draw_detections(frame, detections):
    for detection in detections:
        box = detection["box"]
        class_name = detection["class_name"]
        confidence = detection["confidence"]

        x1 = int(box["x1"])
        y1 = int(box["y1"])
        x2 = int(box["x2"])
        y2 = int(box["y2"])

        label = f"{class_name} {confidence:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    return frame


def _highest_confidence_detection(detections):
    if not detections:
        return None

    return max(
        detections,
        key=lambda detection: detection.get("confidence", 0)
    )


def _crop_detection(frame, detection, padding: int = PERSON_CROP_PADDING_PX):
    height, width = frame.shape[:2]
    box = detection["box"]

    x1 = max(0, int(box["x1"]) - padding)
    y1 = max(0, int(box["y1"]) - padding)
    x2 = min(width, int(box["x2"]) + padding)
    y2 = min(height, int(box["y2"]) + padding)

    if x2 <= x1 or y2 <= y1:
        return None

    return frame[y1:y2, x1:x2].copy()


def _person_box_size(detection):
    box = detection["box"]
    width = max(0, float(box["x2"]) - float(box["x1"]))
    height = max(0, float(box["y2"]) - float(box["y1"]))
    return width, height


def _face_recognition_readiness(frame, detection):
    frame_height, _ = frame.shape[:2]
    box_width, box_height = _person_box_size(detection)
    reasons = ["face not detected yet"]

    if frame_height < FACE_READY_MIN_FRAME_HEIGHT_PX:
        reasons.append("low source resolution")

    if (
        box_width < FACE_READY_MIN_PERSON_BOX_WIDTH_PX
        or box_height < FACE_READY_MIN_PERSON_BOX_HEIGHT_PX
    ):
        reasons.append("person crop too small")

    return {
        "face_recognition_ready": False,
        "reasons": reasons
    }


def _face_readiness_warnings(readiness):
    reasons = readiness.get("reasons", [])

    if "low source resolution" in reasons or "person crop too small" in reasons:
        return ["LOW-RES CROP", "FACE ID NOT SUITABLE"]

    return ["FACE ID NOT SUITABLE"]


def _resize_into_panel(image, panel_width: int, panel_height: int):
    image_height, image_width = image.shape[:2]

    if image_height <= 0 or image_width <= 0:
        return None

    scale = min(panel_width / image_width, panel_height / image_height)
    resized_width = max(1, int(image_width * scale))
    resized_height = max(1, int(image_height * scale))

    return cv2.resize(
        image,
        (resized_width, resized_height),
        interpolation=cv2.INTER_CUBIC
    )


def _build_person_crop_panel(frame, detection):
    height, width = frame.shape[:2]
    label_height = 34
    warning_height = 46
    panel_width = max(PERSON_CROP_PANEL_MIN_WIDTH, min(width, height))
    panel = cv2.copyMakeBorder(
        frame[:height, :1],
        0,
        0,
        0,
        panel_width - 1,
        cv2.BORDER_CONSTANT,
        value=(12, 18, 26)
    )
    panel[:, :] = (12, 18, 26)

    crop = _crop_detection(frame, detection)

    if crop is None:
        return panel

    available_height = max(1, height - label_height - warning_height)
    resized_crop = _resize_into_panel(crop, panel_width, available_height)

    if resized_crop is None:
        return panel

    crop_height, crop_width = resized_crop.shape[:2]
    x_offset = max(0, (panel_width - crop_width) // 2)
    y_offset = label_height + max(0, (available_height - crop_height) // 2)
    panel[y_offset:y_offset + crop_height, x_offset:x_offset + crop_width] = resized_crop

    label = f"PERSON CROP  {detection['confidence']:.2f}"
    cv2.putText(
        panel,
        label,
        (12, 23),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    readiness = _face_recognition_readiness(frame, detection)
    warning_lines = _face_readiness_warnings(readiness)
    for index, warning in enumerate(reversed(warning_lines)):
        cv2.putText(
            panel,
            warning,
            (12, height - 12 - (index * 18)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 220, 255),
            1
        )

    return panel


def _build_person_evidence_frame(frame, detections):
    boxed_frame = _draw_detections(frame.copy(), detections)
    main_detection = _highest_confidence_detection(detections)

    if main_detection is None:
        return boxed_frame

    try:
        crop_panel = _build_person_crop_panel(frame, main_detection)
        return cv2.hconcat([boxed_frame, crop_panel])
    except Exception as error:
        logger.warning(
            "Composite person evidence failed; falling back to boxed full frame: %s",
            error,
        )
        return boxed_frame


def _encode_jpeg(frame) -> bytes:
    success, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    if not success:
        raise RuntimeError("Failed to encode frame as JPEG.")

    return buffer.tobytes()


def run_yolo_snapshot_jpeg() -> bytes:
    frame = capture_frame()
    detections = detect_objects(frame)
    frame = _draw_detections(frame, detections)
    return _encode_jpeg(frame)


def run_person_snapshot_jpeg() -> bytes:
    frame = capture_frame()
    detections = detect_objects(
        frame,
        class_name_filter=PERSON_CLASS_NAME,
        confidence_threshold=_person_confidence_threshold()
    )
    frame = _build_person_evidence_frame(frame, detections)
    return _encode_jpeg(frame)


def run_person_snapshot_jpeg_for_camera(camera: dict) -> bytes:
    frame = capture_frame_for_camera(camera)
    detections = detect_objects(
        frame,
        class_name_filter=PERSON_CLASS_NAME,
        confidence_threshold=_person_confidence_threshold(camera)
    )
    frame = _build_person_evidence_frame(frame, detections)
    return _encode_jpeg(frame)


def build_person_evidence_jpeg_from_detection(
    frame,
    detection_result: dict,
    camera: dict | None = None,
) -> bytes:
    evidence_frame = frame
    detections = detection_result.get("detections", [])
    evidence_detections = detections
    channel = _evidence_channel(camera)

    if channel:
        try:
            high_res_frame = capture_frame_for_camera_channel(camera, channel)
            high_res_detections = detect_objects(
                high_res_frame,
                class_name_filter=PERSON_CLASS_NAME,
                confidence_threshold=_person_confidence_threshold(camera),
            )

            if high_res_detections:
                evidence_detections = high_res_detections
                evidence_frame = high_res_frame
            else:
                camera_id = camera.get("id") if camera else "default_camera"
                logger.warning(
                    "High-resolution evidence re-detection found no person for "
                    "%s channel %s; falling back to detection frame.",
                    camera_id,
                    channel,
                )
                print(
                    "WARNING: High-resolution evidence re-detection found no "
                    f"person for {camera_id} channel {channel}; falling back "
                    "to detection frame."
                )
        except Exception as error:
            camera_id = camera.get("id") if camera else "default_camera"
            logger.warning(
                "High-resolution evidence capture failed for %s channel %s; "
                "falling back to detection frame: %s",
                camera_id,
                channel,
                error,
            )
            print(
                "WARNING: High-resolution evidence capture failed for "
                f"{camera_id} channel {channel}; falling back to detection frame. "
                f"Reason: {error}"
            )

    evidence_frame = _build_person_evidence_frame(
        evidence_frame,
        evidence_detections,
    )
    return _encode_jpeg(evidence_frame)
