"""Render a piRadar-style sea-level pressure panel into a 1-bit framebuffer."""

import framebuf

from config import GRAPH_MAX_INHG, GRAPH_MIN_INHG

HPA_PER_INHG = 33.8638866667
_ATMOSPHERE_HEIGHT_M = 44330.77
_ATMOSPHERE_EXPONENT = 5.25588

CELL_LEFT = 2
CELL_RIGHT = 76
CELL_HEIGHT = 37
CELL_STEP = 38
TOP_MARGIN = 6


def station_to_sea_level_hpa(pressure_hpa, elevation_m):
    fraction = 1.0 - elevation_m / _ATMOSPHERE_HEIGHT_M
    return pressure_hpa / fraction**_ATMOSPHERE_EXPONENT


def _span_text(seconds):
    if seconds < 3600:
        return "{}m".format(max(1, round(seconds / 60)))
    if seconds < 86400:
        return "{}h".format(round(seconds / 3600))
    return "{}d".format(round(seconds / 86400))


def _title_bar(image, x1, y1, x2, y2, text):
    image.fill_rect(x1, y1, x2 - x1 + 1, y2 - y1 + 1, 0)
    image.text(text, x1 + 4, y1 + 1, 1)


def _big_text(image, text, x, y, x_scale, y_scale):
    """Draw text with the 8x8 font enlarged; '.' is drawn narrow to save width."""
    glyph = framebuf.FrameBuffer(bytearray(8), 8, 8, framebuf.MONO_HLSB)
    for char in text:
        if char == ".":
            image.fill_rect(x + 1, y + 7 * y_scale - x_scale, x_scale + 1, x_scale + 1, 0)
            x += x_scale * 3
            continue
        glyph.fill(1)
        glyph.text(char, 0, 0, 0)
        for gy in range(8):
            for gx in range(8):
                if not glyph.pixel(gx, gy):
                    image.fill_rect(x + gx * x_scale, y + gy * y_scale, x_scale, y_scale, 0)
        x += 8 * x_scale


def _big_text_width(text, x_scale):
    return sum(x_scale * 3 if char == "." else 8 * x_scale for char in text)


def render(samples_hpa, interval_seconds, history_samples, width, height, elevation_m):
    """Return a 1-bit framebuffer from station-pressure samples in hPa."""
    stride = (width + 7) // 8
    pixels = bytearray(stride * height)
    image = framebuf.FrameBuffer(pixels, width, height, framebuf.MONO_HLSB)
    image.fill(1)

    sea_level = [station_to_sea_level_hpa(p, elevation_m) for p in samples_hpa]
    count = len(sea_level)

    stats = [("HIGH", None), ("NOW", None), ("LOW", None)]
    if count:
        stats = [
            ("HIGH", max(sea_level)),
            ("NOW", sea_level[-1]),
            ("LOW", min(sea_level)),
        ]

    for row, (label, value) in enumerate(stats):
        top = TOP_MARGIN + row * CELL_STEP
        image.rect(CELL_LEFT, top, CELL_RIGHT - CELL_LEFT + 1, CELL_HEIGHT, 0)
        _title_bar(image, CELL_LEFT, top, CELL_RIGHT, top + 10, label)
        text = "---" if value is None else "{:.2f}".format(value / HPA_PER_INHG)
        text_x = CELL_LEFT + (CELL_RIGHT - CELL_LEFT + 1 - _big_text_width(text, 2)) // 2
        _big_text(image, text, text_x, top + 12, 2, 3)

    graph_left = CELL_RIGHT + 6
    graph_right = width - 3
    plot_top = TOP_MARGIN + 12
    plot_bottom = height - 15
    _title_bar(image, graph_left, TOP_MARGIN, graph_right, plot_top, "SEA-LEVEL PRESSURE")
    image.rect(graph_left, plot_top, graph_right - graph_left + 1, plot_bottom - plot_top + 1, 0)

    full_window = history_samples * interval_seconds
    elapsed = (count - 1) * interval_seconds
    window_seconds = min(full_window, max(3600, elapsed))
    image.text(_span_text(window_seconds), graph_left, height - 11, 0)
    image.text("now", graph_right - 23, height - 11, 0)

    if count < 2:
        image.text("Collecting", graph_left + 8, plot_top + 20, 0)
        image.text("readings", graph_left + 8, plot_top + 32, 0)
        return pixels

    low = GRAPH_MIN_INHG * HPA_PER_INHG
    high = GRAPH_MAX_INHG * HPA_PER_INHG
    span = high - low
    plot_width = graph_right - graph_left - 2
    plot_height = plot_bottom - plot_top - 4

    tick = 29.6
    while tick < GRAPH_MAX_INHG - 0.01:
        tick_y = plot_top + 2 + int((GRAPH_MAX_INHG - tick) * plot_height / (GRAPH_MAX_INHG - GRAPH_MIN_INHG))
        for x in range(graph_left + 2, graph_right - 1, 4):
            image.pixel(x, tick_y, 0)
        tick += 0.2

    previous = None
    for index, value in enumerate(sea_level):
        age = (count - 1 - index) * interval_seconds
        x = graph_right - 1 - int(age * plot_width / window_seconds)
        clamped = max(low, min(high, value))
        y = plot_top + 2 + int((high - clamped) * plot_height / span)
        if previous is not None:
            image.line(previous[0], previous[1], x, y, 0)
            image.line(previous[0], previous[1] + 1, x, y + 1, 0)
        previous = (x, y)

    return pixels
