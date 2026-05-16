"""CLI argument helpers: source reading, config merging, group resolution"""

import argparse
import glob
import sys
from pathlib import Path

from dipper.commons.config import config_path, parse_config
from dipper.commons.constants import BUILTIN_PRESETS
from dipper.commons.help import print_help
from dipper.view.app import run

# Sentinel value for bare --output (no path given), meaning auto-derive from filename
AUTO_OUTPUT_SENTINEL = "__auto__"


def annotation_path(fpath: Path) -> Path:
    return Path(str(fpath) + ".annotations")


def resolve_output_path(output_arg: str | None, filename: str | None) -> str | None:
    """Resolve --output: None means stdout, sentinel means auto <fpath>.annotations, else literal path."""
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


def run_files_mode(args: argparse.Namespace, group_names: dict[int, str]) -> None:
    """Cycle through unannotated files matching the glob, opening each in turn."""
    files = find_unannotated_files(args.files)
    if not files:
        print("dipper: no unannotated files found", file=sys.stderr)
        return
    for fpath in files:
        source = fpath.read_text()
        out_path = str(annotation_path(fpath))
        run(
            source, str(fpath),
            prompt=args.prompt, header=args.header, group_names=group_names,
            output_lines=args.lines, output_summary=args.summary, output_json=args.json,
            output_path=out_path, load_path=None,
        )


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


def validate_output_flags(args: argparse.Namespace) -> None:
    text_mode = args.lines or args.summary
    if args.json and text_mode:
        print("dipper: --json is mutually exclusive with --lines and --summary", file=sys.stderr)
        sys.exit(1)
    if args.load and not args.file:
        print("dipper: --load requires a file argument", file=sys.stderr)
        sys.exit(1)
    validate_files_flags(args)


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
    parser.add_argument("--lines", action="store_true", default=False,
                        help="Output selected lines with marks only")
    parser.add_argument("--summary", action="store_true", default=False,
                        help="Output group summary block only")
    parser.add_argument("--json", action="store_true", default=False,
                        help="Output annotations as JSON (mutually exclusive with --lines/--summary)")
    parser.add_argument("--output", metavar="FILE", nargs="?", const=AUTO_OUTPUT_SENTINEL, default=None,
                        help="Write output to FILE; bare --output writes to <fpath>.annotations")
    parser.add_argument("--load", metavar="FILE", default=None,
                        help="Restore session from a previously written annotations file")
    parser.add_argument("--files", metavar="GLOB", default=None,
                        help="Annotate all files matching GLOB that lack a .annotations file")
    return parser


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
    if args.files:
        run_files_mode(args, group_names)
        return
    source, filename = read_source(args, parser)
    output_path = resolve_output_path(args.output, filename)
    run(
        source, filename,
        prompt=args.prompt, header=args.header, group_names=group_names,
        output_lines=args.lines, output_summary=args.summary, output_json=args.json,
        output_path=output_path, load_path=args.load,
    )
