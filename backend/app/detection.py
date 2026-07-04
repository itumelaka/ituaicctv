from functools import lru_cache
import cv2
from ultralytics import YOLO
from app.camera import capture_frame, capture_frame_for_camera
from app.config import settings

MODEL_NAME = "yolov8n.pt"
PERSON_CLASS_NAME = "person"
PERSON_CROP_PADDING_PX = 32
PERSON_CROP_PANEL_MIN_WIDTH = 320


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
    frame = capture_frame()
    confidence = settings.person_confidence_threshold
    detections = detect_objects(
        frame,
        class_name_filter=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )
    return _build_detection_response(
        frame,
        detections,
        filter_name=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )


def run_person_detection_for_camera(camera: dict) -> dict:
    frame = capture_frame_for_camera(camera)
    confidence = settings.person_confidence_threshold
    detections = detect_objects(
        frame,
        class_name_filter=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )
    return _build_detection_response(
        frame,
        detections,
        camera_info=camera,
        filter_name=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )


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

    available_height = height - label_height
    resized_crop = _resize_into_panel(crop, panel_width, available_height)

    if resized_crop is None:
        return panel

    crop_height, crop_width = resized_crop.shape[:2]
    x_offset = max(0, (panel_width - crop_width) // 2)
    y_offset = label_height + max(0, (available_height - crop_height) // 2)
    panel[y_offset:y_offset + crop_height, x_offset:x_offset + crop_width] = resized_crop

    label = f"{detection['class_name']} {detection['confidence']:.2f}"
    cv2.putText(
        panel,
        f"ZOOM CROP  {label}",
        (12, 23),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
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
    except Exception:
        return boxed_frame


def _encode_jpeg(frame) -> bytes:
    success, buffer = cv2.imencode(".jpg", frame)

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
        confidence_threshold=settings.person_confidence_threshold
    )
    frame = _build_person_evidence_frame(frame, detections)
    return _encode_jpeg(frame)


def run_person_snapshot_jpeg_for_camera(camera: dict) -> bytes:
    frame = capture_frame_for_camera(camera)
    detections = detect_objects(
        frame,
        class_name_filter=PERSON_CLASS_NAME,
        confidence_threshold=settings.person_confidence_threshold
    )
    frame = _build_person_evidence_frame(frame, detections)
    return _encode_jpeg(frame)
