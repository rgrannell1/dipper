"""dipper.state — re-exports for the state package."""

from dipper.state.group import GroupState
from dipper.state.line import GroupAnnotation, LineState
from dipper.state.queries import nearest_annotated_group, nearest_group, selected_groups
from dipper.state.range_fill import RangeFillState
from dipper.state.search import SearchState
from dipper.state.state import AppState, DocumentModel

__all__ = [
    "AppState",
    "DocumentModel",
    "GroupAnnotation",
    "GroupState",
    "LineState",
    "RangeFillState",
    "SearchState",
    "nearest_annotated_group",
    "nearest_group",
    "selected_groups",
]
