"""Command palette providers: GroupProvider and ThemeProvider"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from rich.style import Style
from rich.text import Text
from textual.command import Hit, Hits, Provider

from dipper.constants import GROUP_COLOURS
from dipper.themes import THEMES
from dipper.view import group_dot

if TYPE_CHECKING:
    from dipper.app import ClipperApp


def group_display(group: int, label: str, note: str) -> Text:
    colour = GROUP_COLOURS[group]
    display = Text()
    display.append_text(group_dot(colour))
    display.append(f"group {group}: ", style="dim")
    display.append(label, style=Style(color=colour, bold=True))
    if note:
        display.append(f"  —  {note}", style="dim")
    return display


def group_score(matcher, query: str, searchable: str) -> float:
    return matcher.match(searchable) if query else 1.0


def group_hit(app: ClipperApp, matcher, query: str, group: int) -> Hit | None:
    model = app._model
    label = model.group_label(group)
    annotation = model.groups.annotations.get(group)
    note = annotation.text if annotation else ""
    searchable = f"group {group}: {label}  {note}"
    score = group_score(matcher, query, searchable)
    if score == 0:
        return None
    first_line = next(
        (idx for idx, line in enumerate(model.lines) if line.group == group), None
    )
    command = functools.partial(app.jump_to_line, first_line) if first_line is not None else (lambda: None)
    return Hit(score=score, match_display=group_display(group, label, note), command=command)


def theme_display(name: str, primary: str) -> Text:
    result = Text()
    result.append("◉ ", style=f"bold {primary}")
    result.append(name, style=Style(color=primary, bold=True))
    return result


class GroupProvider(Provider):
    """Command palette provider listing all annotated groups with jump-to support."""

    async def search(self, query: str) -> Hits:
        app: ClipperApp = self.app  # type: ignore
        model = app._model
        matcher = self.matcher(query)
        for group in sorted(model.selected_groups()):
            hit = group_hit(app, matcher, query, group)
            if hit is not None:
                yield hit


class ThemeProvider(Provider):
    """Command palette provider listing all available colour themes."""

    async def search(self, query: str) -> Hits:
        app: ClipperApp = self.app  # type: ignore
        matcher = self.matcher(query)

        for name, entry in THEMES.items():
            searchable = f"Theme - {name}"
            score = matcher.match(searchable) if query else 1.0
            if score == 0:
                continue
            primary = entry["textual"].primary
            yield Hit(
                score=score,
                match_display=theme_display(searchable, primary),
                command=functools.partial(app.change_theme, name),
            )
