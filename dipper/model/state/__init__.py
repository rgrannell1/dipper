"""dipper.state — re-exports for the state package."""

from dipper.model.state.group import GroupState
from dipper.model.state.line import GroupAnnotation, LineState
from dipper.model.state.queries import nearest_annotated_group, nearest_group, selected_groups
from dipper.model.state.range_fill import RangeFillState
from dipper.model.state.search import SearchState
from dipper.model.state.state import AppState, DocumentModel

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
