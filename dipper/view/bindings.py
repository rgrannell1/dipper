"""Key binding definitions: single source of truth for Textual BINDINGS and the help modal."""

from dataclasses import dataclass
from typing import ClassVar

from textual.binding import Binding


@dataclass
class BindingDef:
    """Single binding definition — drives both the Textual BINDINGS list and the help modal."""

    key: str           # display key shown in help modal (e.g. "tab", "> / <")
    description: str   # label used in both the footer bar and help modal
    textual_key: str = ""      # Textual key name; empty = informational only
    action: str = ""           # Textual action name
    show_footer: bool = False  # include in the Textual footer bar
    show_help: bool = True     # include in the help modal
    priority: bool = False     # Textual binding priority flag


tab_key = BindingDef("tab", "select / deselect line")

group_digits_key = BindingDef("1-9", "set active group")

jump_key = BindingDef("g / G", "jump to top / bottom")

search_key = BindingDef("/", "search", textual_key="slash", action="search")

next_block_key = BindingDef("> / <", "next / previous block", textual_key="greater_than_sign", action="next_block", priority=True)

prev_block_key = BindingDef("<", "prev block", textual_key="less_than_sign", action="prev_block", priority=True, show_help=False)

select_all_key = BindingDef("*", "select all matches")

fill_range_key = BindingDef("f", "fill range", textual_key="f", action="fill_range")

annotate_key = BindingDef("n", "annotate block", textual_key="n", action="annotate", show_footer=True)

paste_last_key = BindingDef("p", "paste last annotation", textual_key="p", action="paste_last")

rename_group_key = BindingDef("r", "rename group", textual_key="r", action="rename_group", show_footer=True)

groups_overview_key = BindingDef("o", "groups overview", textual_key="o", action="groups_overview", show_footer=True)

undo_key = BindingDef("u", "undo", textual_key="u", action="undo", show_footer=True)

reset_key = BindingDef("x", "reset all", textual_key="x", action="reset", show_footer=True)

write_quit_key = BindingDef("q", "write & quit", textual_key="q", action="write_output", show_footer=True)

batch_nav_key = BindingDef("[ / ]", "prev / next file  (batch mode)")

help_key = BindingDef("?", "help", textual_key="question_mark", action="help", show_footer=True)

command_palette_key = BindingDef("ctrl+p", "command palette")

goto_line_key = BindingDef(":", "go to line", textual_key="colon", action="goto_line", show_help=False)

BINDING_DEFS: list[BindingDef] = [
    # Navigation / selection
    tab_key,
    group_digits_key,
    jump_key,
    BindingDef("", ""),  # separator
    # Search
    search_key,
    next_block_key,
    prev_block_key,
    select_all_key,
    BindingDef("", ""),  # separator
    # Annotation / editing
    fill_range_key,
    annotate_key,
    paste_last_key,
    rename_group_key,
    groups_overview_key,
    BindingDef("", ""),  # separator
    # App control
    undo_key,
    reset_key,
    write_quit_key,
    batch_nav_key,
    help_key,
    command_palette_key,
    # Hidden: active binding, not shown in footer or help
    goto_line_key,
]


def app_bindings() -> list[Binding]:
    """Derive Textual Binding list from BINDING_DEFS."""
    result = []
    for bd in BINDING_DEFS:
        if not bd.textual_key:
            continue
        result.append(Binding(bd.textual_key, bd.action, bd.description, show=bd.show_footer, priority=bd.priority))
    return result


APP_BINDINGS: ClassVar[list[Binding]] = app_bindings()
