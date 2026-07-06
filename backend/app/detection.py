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
from app.face_recognition import recognize_face

logger = logging.getLogger(__name__)

MODEL_NAME = "yolov8n.pt"
PERSON_CLASS_NAME = "person"
PERSON_CROP_PADDING_PX = 32
PERSON_CROP_PANEL_MIN_WIDTH = 320
PERSON_CROP_PANEL_MAX_CROPS = 3
FACE_READY_MIN_FRAME_HEIGHT_PX = 720
FACE_READY_MIN_PERSON_BOX_WIDTH_PX = 120
FACE_READY_MIN_PERSON_BOX_HEIGHT_PX = 220
DEFAULT_EVIDENCE_CHANNEL = "101"
FACE_MIN_SIZE_PX = 48
FACE_GOOD_SIZE_PX = 96
FACE_BLUR_POOR_THRESHOLD = 70.0
FACE_BLUR_GOOD_THRESHOLD = 150.0


def _bbox_center(detection: dict) -> tuple[float, float]:
    box = detection["box"]
    return (
        (float(box["x1"]) + float(box["x2"])) / 2,
        (float(box["y1"]) + float(box["y2"])) / 2,
    )


def normalized_polygon_to_pixels(
    points: list[list[float]] | list[tuple[float, float]],
    frame_width: int,
    frame_height: int,
) -> list[tuple[float, float]]:
    return [
        (
            max(0.0, min(1.0, float(point[0]))) * frame_width,
            max(0.0, min(1.0, float(point[1]))) * frame_height,
        )
        for point in points
    ]


def point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    if len(polygon) < 3:
        return False

    x, y = point
    inside = False
    previous_x, previous_y = polygon[-1]

    for current_x, current_y in polygon:
        crosses = (current_y > y) != (previous_y > y)
        if crosses:
            slope_x = (
                (previous_x - current_x) * (y - current_y)
                / ((previous_y - current_y) or 1e-12)
                + current_x
            )
            if x < slope_x:
                inside = not inside

        previous_x, previous_y = current_x, current_y

    return inside


def _active_ignore_zones(camera: dict | None) -> list[dict]:
    if not camera:
        return []

    return [
        zone for zone in camera.get("ignore_zones", [])
        if zone.get("enabled") and zone.get("type") == "polygon"
    ]


def filter_detections_by_ignore_zones(
    camera: dict | None,
    detections: list[dict],
    frame_width: int,
    frame_height: int,
) -> tuple[list[dict], list[dict]]:
    filtered_detections = []
    ignored_detections = []
    active_zones = _active_ignore_zones(camera)

    if not active_zones:
        return detections, ignored_detections

    for detection in detections:
        center = _bbox_center(detection)
        ignored_detection = None

        for zone in active_zones:
            pixel_polygon = normalized_polygon_to_pixels(
                zone.get("points", []),
                frame_width,
                frame_height,
            )

            if point_in_polygon(center, pixel_polygon):
                ignored_detection = {
                    **detection,
                    "ignored_by_zone": True,
                    "ignore_zone_id": zone.get("id"),
                    "ignore_zone_label": zone.get("label"),
                }
                break

        if ignored_detection:
            ignored_detections.append(ignored_detection)
        else:
            filtered_detections.append(detection)

    return filtered_detections, ignored_detections


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
    frame_height, frame_width = frame.shape[:2]
    detections, ignored_detections = filter_detections_by_ignore_zones(
        camera,
        detections,
        frame_width,
        frame_height,
    )
    detection_response = _build_detection_response(
        frame,
        detections,
        camera_info=camera,
        filter_name=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )
    active_ignore_zones = _active_ignore_zones(camera)
    configured_ignore_zones = camera.get("ignore_zones", [])
    detection_response["ignore_zones"] = {
        "configured_count": len(configured_ignore_zones),
        "enabled_count": len(active_ignore_zones),
    }

    if ignored_detections:
        detection_response["ignored_detections_count"] = len(ignored_detections)
        detection_response["ignored_detections"] = ignored_detections

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


def _top_confidence_detections(detections, limit: int = PERSON_CROP_PANEL_MAX_CROPS):
    return sorted(
        detections,
        key=lambda detection: detection.get("confidence", 0),
        reverse=True,
    )[:limit]


def evidence_person_targets(
    detections,
    limit: int = PERSON_CROP_PANEL_MAX_CROPS,
) -> list[dict]:
    return [
        {
            "detection": detection,
            "metadata": {
                "bbox": detection.get("box"),
                "confidence": detection.get("confidence"),
                "crop_rank": index,
            },
        }
        for index, detection in enumerate(
            _top_confidence_detections(detections, limit=limit),
            start=1,
        )
    ]


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


def _scale_detection_box(detection: dict, scale_x: float, scale_y: float) -> dict:
    box = detection["box"]
    scaled_detection = {
        **detection,
        "box": {
            "x1": round(float(box["x1"]) * scale_x, 2),
            "y1": round(float(box["y1"]) * scale_y, 2),
            "x2": round(float(box["x2"]) * scale_x, 2),
            "y2": round(float(box["y2"]) * scale_y, 2),
        },
    }
    scaled_detection["evidence_bbox_source"] = "scaled_from_detection_frame"
    return scaled_detection


def _scaled_detections_for_frame(
    detections: list[dict],
    source_frame,
    target_frame,
) -> list[dict]:
    source_height, source_width = source_frame.shape[:2]
    target_height, target_width = target_frame.shape[:2]

    if source_width <= 0 or source_height <= 0:
        return []

    scale_x = target_width / source_width
    scale_y = target_height / source_height
    scaled_detections = [
        _scale_detection_box(detection, scale_x, scale_y)
        for detection in detections
    ]

    return [
        detection for detection in scaled_detections
        if _crop_detection(target_frame, detection) is not None
    ]


def _default_face_readiness(
    available: bool,
    quality: str = "unknown",
    readiness: str = "not_available",
    reasons: list[str] | None = None,
) -> dict:
    return {
        "face_detection_available": available,
        "face_detected": False,
        "face_count": 0,
        "best_face_box": None,
        "face_quality": quality,
        "face_readiness": readiness,
        "reasons": reasons or [],
    }


def _face_cascade_path() -> str | None:
    haarcascades = getattr(getattr(cv2, "data", None), "haarcascades", None)

    if not haarcascades:
        return None

    cascade_path = f"{haarcascades}haarcascade_frontalface_default.xml"

    try:
        if cv2.CascadeClassifier(cascade_path).empty():
            return None
    except Exception:
        return None

    return cascade_path


def assess_face_readiness(image) -> dict:
    try:
        if image is None:
            return _default_face_readiness(
                available=False,
                reasons=["face_detection_unavailable"],
            )

        cascade_path = _face_cascade_path()

        if not cascade_path:
            return _default_face_readiness(
                available=False,
                reasons=["face_detection_unavailable"],
            )

        cascade = cv2.CascadeClassifier(cascade_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        crop_height, crop_width = gray.shape[:2]
        crop_area = max(1, crop_width * crop_height)
        low_resolution_crop = min(crop_width, crop_height) < 160
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(24, 24),
        )

        if len(faces) == 0:
            return _default_face_readiness(
                available=True,
                quality="poor",
                readiness="not_suitable",
                reasons=["no_face_detected"],
            )

        best_face = max(faces, key=lambda face: int(face[2]) * int(face[3]))
        x, y, width, height = [int(value) for value in best_face]
        face_crop = gray[y:y + height, x:x + width]
        blur_score = float(cv2.Laplacian(face_crop, cv2.CV_64F).var())
        min_face_size = min(width, height)
        face_area_ratio = (width * height) / crop_area
        reasons = []

        if low_resolution_crop:
            reasons.append("low_resolution_crop")

        if min_face_size < FACE_MIN_SIZE_PX:
            reasons.append("face_too_small")

        if face_area_ratio < 0.015:
            reasons.append("face_too_small")

        if blur_score < FACE_BLUR_POOR_THRESHOLD:
            reasons.append("image_blurry")

        reasons = list(dict.fromkeys(reasons))

        if reasons:
            quality = "poor"
            readiness = "not_suitable"
            reasons.append("face_detected_but_quality_low")
        elif min_face_size >= FACE_GOOD_SIZE_PX and blur_score >= FACE_BLUR_GOOD_THRESHOLD:
            quality = "good"
            readiness = "suitable"
            reasons.append("face_quality_suitable")
        else:
            quality = "fair"
            readiness = "possible"
            reasons.append("face_quality_possible")

        return {
            "face_detection_available": True,
            "face_detected": True,
            "face_count": len(faces),
            "best_face_box": {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            },
            "face_quality": quality,
            "face_readiness": readiness,
            "reasons": reasons,
            "blur_score": round(blur_score, 2),
            "face_area_ratio": round(face_area_ratio, 4),
        }
    except Exception as error:
        logger.warning("Face readiness assessment failed: %s", error)
        return _default_face_readiness(
            available=False,
            reasons=["face_detection_unavailable"],
        )


def _face_label(face_readiness: dict | None) -> str:
    if not face_readiness or not face_readiness.get("face_detection_available"):
        return "FACE DETECTION: UNAVAILABLE"

    readiness = face_readiness.get("face_readiness")

    if readiness == "suitable":
        return "FACE: SUITABLE"

    if readiness == "possible":
        return "FACE: POSSIBLE"

    return "FACE: NOT SUITABLE"


def _recognition_label(face_recognition: dict | None) -> str | None:
    if not face_recognition:
        return None

    if not face_recognition.get("recognition_attempted"):
        return None

    label = face_recognition.get("recognized_label")
    if not label:
        return None

    confidence = face_recognition.get("recognition_confidence")
    if isinstance(confidence, (int, float)) and label != "UNKNOWN":
        return f"{label} {float(confidence):.2f}"

    if label == "UNKNOWN":
        return None

    return str(label)


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


def _draw_person_crop_label(
    panel,
    *,
    rank: int,
    detection: dict,
    y_offset: int,
    confidence_threshold: float | None = None,
) -> None:
    confidence = detection.get("confidence")
    confidence_text = (
        f"CONF {float(confidence):.2f}"
        if isinstance(confidence, (int, float))
        else "CONF N/A"
    )

    if confidence_threshold is not None:
        confidence_text += f" / THR {float(confidence_threshold):.2f}"

    cv2.putText(
        panel,
        f"PERSON {rank}",
        (12, y_offset + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        panel,
        confidence_text,
        (12, y_offset + 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (210, 230, 255),
        1,
    )


def _build_person_crops_panel(
    frame,
    detections,
    face_readiness: dict | None = None,
    confidence_threshold: float | None = None,
):
    height, width = frame.shape[:2]
    label_height = 48
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

    person_targets = evidence_person_targets(detections)
    top_detections = [target["detection"] for target in person_targets]

    if not top_detections:
        return panel

    single_person = len(top_detections) == 1
    slot_count = len(top_detections)
    slot_height = max(1, height // slot_count)

    for index, detection in enumerate(top_detections):
        slot_y = index * slot_height
        slot_bottom = height if index == slot_count - 1 else min(height, slot_y + slot_height)
        slot_available_height = max(1, slot_bottom - slot_y)
        footer_height = warning_height if single_person else 8
        crop_area_height = max(1, slot_available_height - label_height - footer_height)
        crop = _crop_detection(frame, detection)

        _draw_person_crop_label(
            panel,
            rank=index + 1,
            detection=detection,
            y_offset=slot_y,
            confidence_threshold=confidence_threshold,
        )

        if crop is None:
            continue

        resized_crop = _resize_into_panel(crop, panel_width, crop_area_height)

        if resized_crop is None:
            continue

        crop_height, crop_width = resized_crop.shape[:2]
        x_offset = max(0, (panel_width - crop_width) // 2)
        crop_y = slot_y + label_height + max(0, (crop_area_height - crop_height) // 2)
        panel[crop_y:crop_y + crop_height, x_offset:x_offset + crop_width] = resized_crop

        if not single_person and index < slot_count - 1:
            cv2.line(
                panel,
                (0, slot_bottom - 1),
                (panel_width, slot_bottom - 1),
                (45, 58, 74),
                1,
            )

    if not single_person:
        return panel

    main_detection = top_detections[0]
    readiness = _face_recognition_readiness(frame, main_detection)
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

    face_label = _face_label(face_readiness)
    cv2.putText(
        panel,
        face_label,
        (12, max(44, height - 56)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )

    return panel


def _build_person_crop_panel(frame, detection, face_readiness: dict | None = None):
    return _build_person_crops_panel(
        frame,
        [detection],
        face_readiness=face_readiness,
    )


def _build_person_evidence_frame(
    frame,
    detections,
    face_readiness: dict | None = None,
    face_recognition: dict | None = None,
    confidence_threshold: float | None = None,
):
    boxed_frame = _draw_detections(frame.copy(), detections)
    main_detection = _highest_confidence_detection(detections)

    if main_detection is None:
        return boxed_frame

    recognition_label = _recognition_label(face_recognition)
    if recognition_label:
        box = main_detection["box"]
        x1 = max(0, int(box["x1"]))
        y1 = max(24, int(box["y1"]))
        cv2.putText(
            boxed_frame,
            recognition_label,
            (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 255, 255),
            2,
        )

    try:
        crop_panel = _build_person_crops_panel(
            frame,
            detections,
            face_readiness=face_readiness,
            confidence_threshold=confidence_threshold,
        )
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
    confidence = _person_confidence_threshold()
    detections = detect_objects(
        frame,
        class_name_filter=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )
    frame = _build_person_evidence_frame(
        frame,
        detections,
        confidence_threshold=confidence,
    )
    return _encode_jpeg(frame)


def run_person_snapshot_jpeg_for_camera(camera: dict) -> bytes:
    frame = capture_frame_for_camera(camera)
    confidence = _person_confidence_threshold(camera)
    detections = detect_objects(
        frame,
        class_name_filter=PERSON_CLASS_NAME,
        confidence_threshold=confidence
    )
    frame = _build_person_evidence_frame(
        frame,
        detections,
        confidence_threshold=confidence,
    )
    return _encode_jpeg(frame)


def build_person_evidence_from_detection(
    frame,
    detection_result: dict,
    camera: dict | None = None,
) -> tuple[bytes, dict, dict, dict]:
    evidence_frame = frame
    detections = detection_result.get("detections", [])
    evidence_detections = detections
    evidence_source = "detection_frame"
    channel = _evidence_channel(camera)

    if channel:
        try:
            high_res_frame = capture_frame_for_camera_channel(camera, channel)
            high_res_detections = detect_objects(
                high_res_frame,
                class_name_filter=PERSON_CLASS_NAME,
                confidence_threshold=_person_confidence_threshold(camera),
            )
            high_res_height, high_res_width = high_res_frame.shape[:2]
            high_res_detections, ignored_high_res_detections = (
                filter_detections_by_ignore_zones(
                    camera,
                    high_res_detections,
                    high_res_width,
                    high_res_height,
                )
            )

            if high_res_detections:
                evidence_detections = high_res_detections
                evidence_frame = high_res_frame
                evidence_source = "hd_redetect"
            else:
                scaled_detections = _scaled_detections_for_frame(
                    detections,
                    frame,
                    high_res_frame,
                )
                camera_id = camera.get("id") if camera else "default_camera"
                ignored_note = (
                    f" {len(ignored_high_res_detections)} high-resolution "
                    "detection(s) were inside enabled ignore zones."
                    if ignored_high_res_detections else ""
                )
                if scaled_detections:
                    evidence_detections = scaled_detections
                    evidence_frame = high_res_frame
                    evidence_source = "hd_scaled_bbox"
                    logger.warning(
                        "High-resolution evidence re-detection found no person "
                        "for %s channel %s; using scaled detection boxes on the "
                        "high-resolution frame.%s",
                        camera_id,
                        channel,
                        ignored_note,
                    )
                    print(
                        "WARNING: High-resolution evidence re-detection found "
                        f"no person for {camera_id} channel {channel}; using "
                        "scaled detection boxes on the high-resolution frame."
                        f"{ignored_note}"
                    )
                else:
                    logger.warning(
                        "High-resolution evidence re-detection found no person "
                        "for %s channel %s and scaled crops were invalid; "
                        "falling back to detection frame.%s",
                        camera_id,
                        channel,
                        ignored_note,
                    )
                    print(
                        "WARNING: High-resolution evidence re-detection found "
                        f"no person for {camera_id} channel {channel} and "
                        "scaled crops were invalid; falling back to detection "
                        f"frame.{ignored_note}"
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

    main_detection = _highest_confidence_detection(evidence_detections)
    person_crop = _crop_detection(evidence_frame, main_detection) if main_detection else None
    face_readiness = assess_face_readiness(person_crop)
    face_recognition = recognize_face(person_crop, face_readiness)

    evidence_frame = _build_person_evidence_frame(
        evidence_frame,
        evidence_detections,
        face_readiness=face_readiness,
        face_recognition=face_recognition,
        confidence_threshold=detection_result.get("confidence_threshold"),
    )
    person_targets = evidence_person_targets(evidence_detections)
    evidence_metadata = {
        "detections": [target["detection"] for target in person_targets],
        "person_detections": [target["metadata"] for target in person_targets],
        "detections_count": len(person_targets),
        "evidence_source": evidence_source,
    }
    return _encode_jpeg(evidence_frame), face_readiness, face_recognition, evidence_metadata


def build_person_evidence_jpeg_from_detection(
    frame,
    detection_result: dict,
    camera: dict | None = None,
) -> bytes:
    result = build_person_evidence_from_detection(
        frame,
        detection_result,
        camera=camera,
    )
    image_bytes = result[0]
    return image_bytes
