"""File path utilities: annotation path derivation, output resolution, glob filtering."""

import glob
import sys
from pathlib import Path

from dipper.commons.constants import MARK_LINE_PREFIX

# Sentinel for bare --output (no path given): auto-derive <fpath>.annotations
AUTO_OUTPUT_SENTINEL = "__auto__"


def annotation_path(fpath: Path) -> Path:
    return Path(str(fpath) + ".annotations")


def resolve_output_path(output_arg: str | None, filename: str | None) -> str | None:
    """Resolve --output: None means stdout, sentinel means auto <fpath>.annotations, else literal."""
    if output_arg is None:
        return None
    if output_arg == AUTO_OUTPUT_SENTINEL:
        if filename is None:
            print("dipper: bare --output requires a file argument", file=sys.stderr)
            sys.exit(1)
        return str(annotation_path(Path(filename)))
    return output_arg


def sidecar_has_marks(sidecar: Path) -> bool:
    """Return True if the sidecar contains at least one mark line, meaning lines were actually selected."""
    try:
        return any(line.startswith(MARK_LINE_PREFIX) for line in sidecar.read_text().splitlines())
    except (OSError, UnicodeDecodeError):
        return False


def find_unannotated_files(glob_pattern: str) -> list[Path]:
    """Return files matching glob_pattern with no meaningful .annotations sidecar (missing or no mark lines)."""
    matched = sorted(Path(path_str) for path_str in glob.glob(glob_pattern, recursive=True))
    return [
        fpath for fpath in matched
        if fpath.is_file() and not (annotation_path(fpath).exists() and sidecar_has_marks(annotation_path(fpath)))
    ]


def find_all_files(glob_pattern: str) -> list[Path]:
    """Return all files matching glob_pattern, regardless of annotation state."""
    matched = sorted(Path(path_str) for path_str in glob.glob(glob_pattern, recursive=True))
    return [fpath for fpath in matched if fpath.is_file()]


def find_annotated_files(glob_pattern: str) -> list[Path]:
    """Return files matching glob_pattern that have a corresponding .annotations file."""
    matched = sorted(Path(path_str) for path_str in glob.glob(glob_pattern, recursive=True))
    return [fpath for fpath in matched if fpath.is_file() and annotation_path(fpath).exists()]


def clear_annotation_sidecars(glob_pattern: str) -> list[Path]:
    """Delete .annotations sidecars for all files matching glob_pattern. Returns list of deleted paths."""
    deleted = []
    for fpath in find_annotated_files(glob_pattern):
        sidecar = annotation_path(fpath)
        sidecar.unlink()
        deleted.append(sidecar)
    return deleted
