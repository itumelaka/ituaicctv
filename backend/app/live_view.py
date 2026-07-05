LIVE_VIEW_STANDARD_QUALITY = "standard"
LIVE_VIEW_HD_QUALITY = "hd"
LIVE_VIEW_HD_CHANNEL = "101"
LIVE_VIEW_QUALITIES = {LIVE_VIEW_STANDARD_QUALITY, LIVE_VIEW_HD_QUALITY}
LIVE_VIEW_STANDARD_MAX_WIDTH = 960
LIVE_VIEW_HD_MAX_WIDTH = 1920


class InvalidLiveViewQuality(ValueError):
    pass


def live_view_channel_for_quality(quality: str) -> str | None:
    normalized_quality = normalize_live_view_quality(quality)

    if normalized_quality == LIVE_VIEW_HD_QUALITY:
        return LIVE_VIEW_HD_CHANNEL

    return None


def live_view_max_width_for_quality(quality: str) -> int:
    normalized_quality = normalize_live_view_quality(quality)

    if normalized_quality == LIVE_VIEW_HD_QUALITY:
        return LIVE_VIEW_HD_MAX_WIDTH

    return LIVE_VIEW_STANDARD_MAX_WIDTH


def normalize_live_view_quality(quality: str) -> str:
    normalized_quality = (quality or LIVE_VIEW_STANDARD_QUALITY).strip().lower()

    if normalized_quality not in LIVE_VIEW_QUALITIES:
        raise InvalidLiveViewQuality(
            "Invalid live view quality. Expected "
            f"{LIVE_VIEW_STANDARD_QUALITY} or {LIVE_VIEW_HD_QUALITY}."
        )

    return normalized_quality
