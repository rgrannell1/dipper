"""Argument registration: adds flag groups to an argparse parser."""

import argparse

from dipper.commons.paths import AUTO_OUTPUT_SENTINEL


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


def add_batch_flags(parser: argparse.ArgumentParser) -> None:
    """Register --files, --edit, --clear, --diff, --cached, --assume-yes flags."""
    parser.add_argument("--files", metavar="GLOB", default=None,
                        help="Annotate all files matching GLOB that lack a .annotations file")
    parser.add_argument("--edit", action="store_true", default=False,
                        help="With --files: open already-annotated files by loading their .annotations sidecar")
    parser.add_argument("--clear", action="store_true", default=False,
                        help="With --files or --diff: delete .annotations sidecars, then exit")
    parser.add_argument("--diff", action="store_true", default=False,
                        help="Annotate files changed in the working tree (or index with --cached)")
    parser.add_argument("--cached", action="store_true", default=False,
                        help="With --diff: use staged changes instead of working tree")
    parser.add_argument("--assume-yes", action="store_true", default=False,
                        help="Drop stale annotation sidecars without prompting")


def build_ls_subparser(subparsers) -> None:
    """Register the ls subcommand."""
    ls_parser = subparsers.add_parser("ls", help="List annotation sidecars")
    scope = ls_parser.add_mutually_exclusive_group()
    scope.add_argument("--files", metavar="GLOB", default=None,
                       help="Limit to files matching GLOB")
    scope.add_argument("--diff", action="store_true", default=False,
                       help="Limit to files in the git working tree diff")
    ls_parser.add_argument("--cached", action="store_true", default=False,
                           help="With --diff: use staged changes instead of working tree")
    output = ls_parser.add_mutually_exclusive_group()
    output.add_argument("--cat", action="store_true", default=False,
                        help="Print raw sidecar contents to stdout")
    output.add_argument("--json", action="store_true", default=False,
                        help="Parse and emit JSON output for each sidecar")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argparse parser for the dipper CLI."""
    parser = argparse.ArgumentParser(prog="dipper", description="Annotate text interactively")
    subparsers = parser.add_subparsers(dest="subcommand")
    build_ls_subparser(subparsers)
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
    add_batch_flags(parser)
    return parser
