"""Action functions for ClipperApp — plain functions taking app as first argument."""

from dipper.actions.groups import (
    annotate_done,
    open_annotate,
    open_rename_group,
    rename_done,
    set_group,
)
from dipper.actions.misc import open_groups_overview, reset
from dipper.actions.nav import cursor_group, jump_to_line, open_goto_line
from dipper.actions.range_fill import fill_range
from dipper.actions.search import (
    apply_clear_search,
    apply_search,
    next_match,
    open_search,
    prev_match,
    search_result,
    select_all_matches,
)
from dipper.actions.theme import change_theme

__all__ = [
    "annotate_done",
    "apply_clear_search",
    "apply_search",
    "change_theme",
    "cursor_group",
    "fill_range",
    "jump_to_line",
    "next_match",
    "open_annotate",
    "open_goto_line",
    "open_groups_overview",
    "open_rename_group",
    "open_search",
    "prev_match",
    "rename_done",
    "reset",
    "search_result",
    "select_all_matches",
    "set_group",
]
