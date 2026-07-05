# ITU AI CCTV - Ignore Zones

Ignore-zone polygon support is deployed as groundwork for camera-specific static false positives.

## Purpose

Ignore zones suppress person detections whose bounding-box center falls inside an enabled polygon. They are intended for fixed objects that repeatedly trigger false positives, such as a tree/topiary or fixed pipe.

## Configuration

Polygon points use normalized coordinates from `0.0` to `1.0`, relative to the frame width and height.

Zones are disabled by default. Current placeholders:

- `makmal_cam_13`: 1 placeholder zone, enabled 0
- `kuarantin_cam_11`: 1 placeholder zone, enabled 0

## Safety

Enabling a bad polygon can suppress real person alerts. Test against screenshots and evidence images before enabling.

Recommended workflow:

1. Review repeated false-positive evidence.
2. Estimate a polygon around only the static object area.
3. Test with recent frames.
4. Enable only after confirming real people are not masked.

Future work: visual polygon editor on dashboard snapshots.
