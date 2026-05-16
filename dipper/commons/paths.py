"""File path utilities: annotation path derivation, output resolution, glob filtering."""

import glob
import sys
from pathlib import Path

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


def find_unannotated_files(glob_pattern: str) -> list[Path]:
    """Return files matching glob_pattern that have no corresponding .annotations file."""
    matched = sorted(Path(path_str) for path_str in glob.glob(glob_pattern, recursive=True))
    return [fpath for fpath in matched if fpath.is_file() and not annotation_path(fpath).exists()]
