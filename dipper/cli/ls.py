"""ls subcommand: list, display, or export annotation sidecars."""

import argparse
import sys
from pathlib import Path

from dipper.commons.git import changed_files
from dipper.commons.loader import META_RE, parse_annotations_file
from dipper.commons.paths import annotation_path, find_annotated_files
from dipper.controller.output import render_json
from dipper.model.state import AppState, LineState


def find_sidecars_default() -> list[Path]:
    """Find all .annotations files recursively under cwd, excluding .git."""
    return sorted(path for path in Path(".").glob("**/*.annotations") if ".git" not in path.parts)


def find_sidecars_files(glob_pattern: str) -> list[Path]:
    """Find .annotations sidecars for source files matching glob_pattern."""
    return [annotation_path(fpath) for fpath in find_annotated_files(glob_pattern)]


def find_sidecars_diff(cached: bool) -> list[Path]:
    """Find .annotations sidecars for files in the current git diff."""
    return [annotation_path(fpath) for fpath in changed_files(cached=cached) if annotation_path(fpath).exists()]


def sidecar_filepath(sidecar_text: str) -> str | None:
    """Extract the source filepath from the sidecar meta line, or None if absent."""
    for raw_line in sidecar_text.splitlines():
        meta_match = META_RE.match(raw_line)
        if meta_match:
            return meta_match.group(1)
    return None


def build_model_from_sidecar(source: str, sidecar_text: str) -> AppState:
    """Reconstruct AppState from source text and a sidecar annotations file."""
    session = parse_annotations_file(sidecar_text, len(source.splitlines()))
    lines = [LineState(text=line) for line in source.splitlines()]
    model = AppState(lines, group_names=dict(session.group_names))
    for line_num, grp in session.line_groups.items():
        idx = line_num - 1
        if 0 <= idx < len(model.lines):
            model.set_line_group(idx, grp)
    for (grp, block_start), text in session.block_annotations.items():
        if 0 <= block_start < len(model.lines):
            model.groups.set_annotation(grp, block_start, text)
    return model


def ls_paths(sidecars: list[Path]) -> None:
    """Print sidecar paths, one per line."""
    for sidecar in sidecars:
        print(sidecar)


def ls_cat(sidecars: list[Path]) -> None:
    """Print raw sidecar content to stdout."""
    for sidecar in sidecars:
        print(sidecar.read_text(), end="")


def ls_json_sidecar(sidecar: Path) -> None:
    """Parse one sidecar and emit JSON output; prints a warning and skips on error."""
    sidecar_text = sidecar.read_text()
    filepath = sidecar_filepath(sidecar_text)
    if filepath is None:
        print(f"dipper ls: no filepath meta in {sidecar}", file=sys.stderr)
        return
    source_path = Path(filepath)
    if not source_path.exists():
        print(f"dipper ls: source not found: {filepath}", file=sys.stderr)
        return
    source = source_path.read_text()
    model = build_model_from_sidecar(source, sidecar_text)
    print(render_json(model, filepath))


def ls_json(sidecars: list[Path]) -> None:
    """Parse each sidecar and emit JSON output."""
    for sidecar in sidecars:
        ls_json_sidecar(sidecar)


def resolve_sidecars(args: argparse.Namespace) -> list[Path]:
    """Resolve the sidecar list based on --files/--diff scope flags."""
    if args.diff:
        return find_sidecars_diff(args.cached)
    if args.files:
        return find_sidecars_files(args.files)
    return find_sidecars_default()


def run_ls(args: argparse.Namespace) -> None:
    """Execute the ls subcommand."""
    sidecars = resolve_sidecars(args)
    if args.cat:
        ls_cat(sidecars)
    elif args.json:
        ls_json(sidecars)
    else:
        ls_paths(sidecars)
