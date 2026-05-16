"""Line and group annotation data classes."""

from dataclasses import dataclass


@dataclass
class LineState:
    text: str
    group: int = 0


@dataclass
class GroupAnnotation:
    group: int
    text: str = ""
