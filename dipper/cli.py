"""CLI argument helpers: source reading, config merging, group resolution"""

import argparse
import sys
from pathlib import Path

from dipper.commons.config import config_path, parse_config
from dipper.commons.constants import BUILTIN_PRESETS
from dipper.commons.help import print_help
from dipper.commons.paths import (
    AUTO_OUTPUT_SENTINEL,
    annotation_path,
    find_annotated_files,
    find_unannotated_files,
    resolve_output_path,
)
from dipper.view.app import run
from dipper.view.app_types import RunArgs


def resolve_groups(args: argparse.Namespace, presets: dict[str, str]) -> str | None:
    if args.groups:
        return args.groups
    if args.preset:
        merged = {**BUILTIN_PRESETS, **presets}
        if args.preset not in merged:
            print(f"dipper: unknown preset '{args.preset}'", file=sys.stderr)
            sys.exit(1)
        return merged[args.preset]
    return None


def merge_config(cli_ns: argparse.Namespace, config_ns: argparse.Namespace) -> None:
    for key, value in vars(config_ns).items():
        if key == "file":
            continue
        if getattr(cli_ns, key, None) is None and value is not None:
            setattr(cli_ns, key, value)


def read_source(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> tuple[str, str | None]:
    if args.file:
        return Path(args.file).read_text(), args.file
    if sys.stdin.isatty():
        print_help()
        sys.exit(1)
    return sys.stdin.read(), None


def parse_group_names(groups_csv: str | None) -> dict[int, str]:
    if not groups_csv:
        return {}
    return {
        idx: name.strip()
        for idx, name in enumerate(groups_csv.split(","), start=1)
        if name.strip()
    }


def validate_files_flags(args: argparse.Namespace) -> None:
    if args.files and args.file:
        print("dipper: --files and a positional file argument are mutually exclusive", file=sys.stderr)
        sys.exit(1)
    if args.files and args.load:
        print("dipper: --files and --load are mutually exclusive", file=sys.stderr)
        sys.exit(1)
    if args.files and args.output is not None:
        print("dipper: --files and --output are mutually exclusive", file=sys.stderr)
        sys.exit(1)
    if args.edit and not args.files:
        print("dipper: --edit requires --files", file=sys.stderr)
        sys.exit(1)


def validate_full_flags(args: argparse.Namespace) -> None:
    if not args.full:
        return
    if args.lines or args.summary:
        print("dipper: --full is mutually exclusive with --lines and --summary", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print("dipper: --full is mutually exclusive with --json", file=sys.stderr)
        sys.exit(1)


def validate_output_flags(args: argparse.Namespace) -> None:
    text_mode = args.lines or args.summary
    if args.json and text_mode:
        print("dipper: --json is mutually exclusive with --lines and --summary", file=sys.stderr)
        sys.exit(1)
    if args.load and not args.file:
        print("dipper: --load requires a file argument", file=sys.stderr)
        sys.exit(1)
    validate_full_flags(args)
    validate_files_flags(args)


def add_output_flags(parser: argparse.ArgumentParser) -> None:
    """Register output-mode flags on parser."""
    parser.add_argument("--full", action="store_true", default=False,
                        help="Output full annotated file (default is compact: lines + summary)")
    parser.add_argument("--lines", action="store_true", default=False,
                        help="Output selected lines with marks only")
    parser.add_argument("--summary", action="store_true", default=False,
                        help="Output group summary block only")
    parser.add_argument("--json", action="store_true", default=False,
                        help="Output annotations as JSON (mutually exclusive with --lines/--summary)")
    parser.add_argument("--output", metavar="FILE", nargs="?", const=AUTO_OUTPUT_SENTINEL, default=None,
                        help="Write output to FILE; bare --output writes to <fpath>.annotations")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argparse parser for the dipper CLI."""
    parser = argparse.ArgumentParser(prog="dipper", description="Annotate text interactively")
    parser.add_argument("file", nargs="?", help="File to annotate (omit to read stdin)")
    parser.add_argument("--prompt", metavar="STR", default=None,
                        help="Subtitle shown in the header bar")
    parser.add_argument("--header", metavar="STR", default=None,
                        help="Label shown above the line list")
    parser.add_argument("--groups", metavar="CSV", default=None,
                        help="Comma-separated group names")
    parser.add_argument("--preset", metavar="NAME", default=None,
                        help="Named group preset from config file")
    add_output_flags(parser)
    parser.add_argument("--load", metavar="FILE", default=None,
                        help="Restore session from a previously written annotations file")
    parser.add_argument("--files", metavar="GLOB", default=None,
                        help="Annotate all files matching GLOB that lack a .annotations file")
    parser.add_argument("--edit", action="store_true", default=False,
                        help="With --files: open already-annotated files by loading their .annotations sidecar")
    return parser


def iter_run_targets(
    args: argparse.Namespace, parser: argparse.ArgumentParser
):
    """Yield (source, filename, output_path, load_path) for each file to process."""
    if args.files:
        candidates = find_annotated_files(args.files) if args.edit else find_unannotated_files(args.files)
        for fpath in candidates:
            try:
                source = fpath.read_text()
            except UnicodeDecodeError:
                print(f"dipper: skipping binary file: {fpath}", file=sys.stderr)
                continue
            sidecar = str(annotation_path(fpath))
            load_path = sidecar if args.edit else None
            yield source, str(fpath), sidecar, load_path
    else:
        source, filename = read_source(args, parser)
        yield source, filename, resolve_output_path(args.output, filename), args.load


def run_batch(args: argparse.Namespace, targets: list, group_names: dict[int, str]) -> None:
    """Launch a TUI session for each (source, filename, output_path, load_path) target."""
    for source, filename, output_path, load_path in targets:
        run(source, RunArgs(
            filename=filename, prompt=args.prompt, header=args.header, group_names=group_names,
            output_lines=args.lines, output_summary=args.summary, output_json=args.json, output_full=args.full,
            output_path=output_path, load_path=load_path,
        ))


def main() -> None:
    """Orchestrate config loading, argument parsing, source reading, and launch the TUI."""
    parser = build_parser()
    config_flag_tokens, presets = parse_config(config_path())
    config_ns = (
        parser.parse_args([*config_flag_tokens, "--"])
        if config_flag_tokens
        else argparse.Namespace()
    )
    cli_ns = parser.parse_args()
    merge_config(cli_ns, config_ns)
    args = cli_ns
    validate_output_flags(args)
    group_names = parse_group_names(resolve_groups(args, presets))
    targets = list(iter_run_targets(args, parser))
    if args.files and not targets:
        label = "annotated" if args.edit else "unannotated"
        print(f"dipper: no {label} files found", file=sys.stderr)
        return
    run_batch(args, targets, group_names)
