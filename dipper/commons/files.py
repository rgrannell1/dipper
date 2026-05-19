"""File reading and FileTarget: shared utilities for batch file processing."""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dipper.commons.git import changed_files, changed_lines
from dipper.commons.help import print_help
from dipper.commons.loader import is_stale
from dipper.commons.paths import annotation_path, find_all_files, find_unannotated_files, resolve_output_path


@dataclass
class FileTarget:
    """Bundles everything needed to open one file in a dipper session."""

    source: str
    filename: str
    output_path: str | None
    load_path: str | None
    diff_lines: set[int] = field(default_factory=set)


def read_text_file(fpath: Path) -> str | None:
    """Return file contents as text, or None if the file cannot be decoded."""
    try:
        return fpath.read_text()
    except UnicodeDecodeError:
        print(f"dipper: skipping binary file: {fpath}", file=sys.stderr)
        return None


def read_source(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> tuple[str, str | None]:
    if args.file:
        return Path(args.file).read_text(), args.file
    if sys.stdin.isatty():
        print_help()
        sys.exit(1)
    return sys.stdin.read(), None


def resolve_load_path(source: str, sidecar: Path, assume_yes: bool) -> str | None:
    """Return sidecar path to load, or None if it is stale and the user confirmed dropping it."""
    if not sidecar.exists():
        return None
    annotations_text = sidecar.read_text()
    if not is_stale(source, annotations_text):
        return str(sidecar)
    if assume_yes:
        sidecar.unlink()
        print(f"dipper: dropped stale annotations: {sidecar}", file=sys.stderr)
        return None
    answer = input(f"dipper: annotations for {sidecar.stem!r} are stale (source changed). Drop them? [y/N] ")
    if answer.strip().lower() == "y":
        sidecar.unlink()
        return None
    return str(sidecar)


def iter_diff_targets(args: argparse.Namespace):
    """Yield a FileTarget for each file changed in the current git diff."""
    for fpath in changed_files(cached=args.cached):
        if not fpath.exists():
            continue
        source = read_text_file(fpath)
        if source is None:
            continue
        sidecar = annotation_path(fpath)
        lines = changed_lines(fpath, cached=args.cached)
        load_path = resolve_load_path(source, sidecar, getattr(args, "assume_yes", False))
        yield FileTarget(source=source, filename=str(fpath), output_path=str(sidecar), load_path=load_path, diff_lines=lines)


def iter_files_targets(args: argparse.Namespace):
    """Yield a FileTarget for each file in the --files glob batch."""
    candidates = find_all_files(args.files) if args.edit else find_unannotated_files(args.files)
    for fpath in candidates:
        source = read_text_file(fpath)
        if source is None:
            continue
        sidecar = annotation_path(fpath)
        load_path = resolve_load_path(source, sidecar, args.assume_yes) if args.edit else None
        yield FileTarget(source=source, filename=str(fpath), output_path=str(sidecar), load_path=load_path)


def iter_run_targets(args: argparse.Namespace, parser: argparse.ArgumentParser):
    """Yield a FileTarget for each file to process."""
    if args.diff:
        yield from iter_diff_targets(args)
    elif args.files:
        yield from iter_files_targets(args)
    else:
        source, filename = read_source(args, parser)
        output_path = resolve_output_path(args.output, filename)
        load_path = args.load
        if load_path:
            load_path = resolve_load_path(source, Path(load_path), args.assume_yes)
        yield FileTarget(source=source, filename=filename or "", output_path=output_path, load_path=load_path)
