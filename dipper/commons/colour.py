"""Colour utilities: HSL conversion, theme-aware diff colour selection, and diff line markers."""

import colorsys
import re

from pygments.style import Style

from dipper.commons.constants import (
    COLOUR_PREFIX_PARTS,
    DEFAULT_SEARCH_COLOUR,
    DIFF_ADDED,
    DIFF_ADDED_FALLBACK,
    DIFF_MARKS,
    DIFF_MODIFIED,
    DIFF_MODIFIED_FALLBACK,
)

HEX_RE = re.compile(r"^#([0-9a-fA-F]{6})$")

# Target hues for diff semantic labels (degrees, 0-360)
DIFF_TARGET_HUES: dict[str, float] = {
    DIFF_ADDED: 120.0,
    DIFF_MODIFIED: 180.0,
}

DIFF_FALLBACKS: dict[str, str] = {
    DIFF_ADDED: DIFF_ADDED_FALLBACK,
    DIFF_MODIFIED: DIFF_MODIFIED_FALLBACK,
}

# Minimum saturation and lightness thresholds for candidate colours
MIN_SATURATION = 0.25
MIN_LIGHTNESS = 0.20
MAX_LIGHTNESS = 0.88

# Maximum hue distance (degrees) before falling back to hardcoded defaults
MAX_HUE_DISTANCE = 45.0


def hex_to_hsl(hex_colour: str) -> tuple[float, float, float] | None:
    """Convert a '#RRGGBB' hex string to (hue_degrees, saturation, lightness), or None if invalid."""
    match = HEX_RE.match(hex_colour)
    if not match:
        return None
    raw = match.group(1)
    red = int(raw[0:2], 16) / 255.0
    green = int(raw[2:4], 16) / 255.0
    blue = int(raw[4:6], 16) / 255.0
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    return hue * 360.0, saturation, lightness


def hue_distance(hue_a: float, hue_b: float) -> float:
    """Circular distance between two hues in degrees."""
    delta = abs(hue_a - hue_b) % 360.0
    return min(delta, 360.0 - delta)


def theme_colours(style: type[Style]) -> list[str]:
    """Extract all unique valid hex colours from a Pygments style's token map."""
    seen: set[str] = set()
    result: list[str] = []
    for value in style.styles.values():
        for token in value.split():
            if token.startswith("#") and token not in seen:
                seen.add(token)
                result.append(token)
    return result


def best_hue_match(colours: list[str], target_hue: float) -> str | None:
    """Return the hex colour closest in hue to target_hue within MAX_HUE_DISTANCE, or None."""
    best_colour: str | None = None
    best_distance = MAX_HUE_DISTANCE
    for hex_colour in colours:
        hsl = hex_to_hsl(hex_colour)
        if hsl is None:
            continue
        hue, saturation, lightness = hsl
        if saturation < MIN_SATURATION or lightness < MIN_LIGHTNESS or lightness > MAX_LIGHTNESS:
            continue
        distance = hue_distance(hue, target_hue)
        if distance < best_distance:
            best_distance = distance
            best_colour = hex_colour
    return best_colour


def diff_colour_for_style(style: type[Style], label: str) -> str:
    """Return the theme colour best matching the diff semantic label, or a hardcoded fallback."""
    target_hue = DIFF_TARGET_HUES.get(label)
    if target_hue is None:
        return DIFF_FALLBACKS.get(label, DIFF_ADDED_FALLBACK)
    colours = theme_colours(style)
    match = best_hue_match(colours, target_hue)
    return match or DIFF_FALLBACKS.get(label, DIFF_ADDED_FALLBACK)


def resolve_diff_colours(style: type[Style], diff_lines: dict[int, str]) -> dict[int, str]:
    """Convert {1-based line num: semantic label} to {0-based idx: hex colour} using the theme."""
    return {line_num - 1: diff_colour_for_style(style, label) for line_num, label in diff_lines.items()}


def resolve_diff_marks(diff_lines: dict[int, str]) -> dict[int, str]:
    """Convert {1-based line num: semantic label} to {0-based idx: gutter glyph (+ / ~)}."""
    return {line_num - 1: DIFF_MARKS[label] for line_num, label in diff_lines.items() if label in DIFF_MARKS}


def parse_colour_prefix(value: str) -> tuple[str, str]:
    """Split '!<colour> <pattern>' into (colour, pattern); return (default, value) if no prefix."""
    if value.startswith("!"):
        parts = value[1:].split(" ", 1)
        if len(parts) == COLOUR_PREFIX_PARTS and parts[0]:
            return parts[0], parts[1]
    return DEFAULT_SEARCH_COLOUR, value
