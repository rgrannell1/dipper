"""Line state data class."""

from dataclasses import dataclass


@dataclass
class LineState:
    text: str
    group: int = 0
