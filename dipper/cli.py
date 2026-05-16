"""CLI argument helpers: source reading, config merging, group resolution"""

import argparse
import sys
from pathlib import Path

from dipper.commons.config import config_path, parse_config
from dipper.commons.constants import BUILTIN_PRESETS
from dipper.commons.help import print_help
from dipper.view.app import run


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


def validate_output_flags(args: argparse.Namespace) -> None:
    text_mode = args.lines or args.summary
    if args.json and text_mode:
        print("dipper: --json is mutually exclusive with --lines and --summary", file=sys.stderr)
        sys.exit(1)
    if args.load and not args.file:
        print("dipper: --load requires a file argument", file=sys.stderr)
        sys.exit(1)


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
    parser.add_argument("--output", metavar="FILE", default=None,
                        help="Write output to FILE instead of stdout")
    parser.add_argument("--load", metavar="FILE", default=None,
                        help="Restore session from a previously written annotations file")
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
    source, filename = read_source(args, parser)
    group_names = parse_group_names(resolve_groups(args, presets))
    run(
        source, filename,
        prompt=args.prompt, header=args.header, group_names=group_names,
        output_lines=args.lines, output_summary=args.summary, output_json=args.json,
        output_path=args.output, load_path=args.load,
    )
