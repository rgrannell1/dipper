"""Shared dataclasses for the view layer."""

from dataclasses import dataclass, field

from dipper.commons.themes import DEFAULT_THEME


@dataclass
class RunArgs:
    """Bundles all CLI-derived configuration for a single dipper session."""

    filename: str | None = None
    prompt: str | None = None
    header: str | None = None
    group_names: dict[int, str] = field(default_factory=dict)
    output_lines: bool = False
    output_summary: bool = False
    output_json: bool = False
    output_full: bool = False
    output_path: str | None = None
    load_path: str | None = None
    theme: str = DEFAULT_THEME
    files_mode: bool = False
    presets: dict[str, str] = field(default_factory=dict)
