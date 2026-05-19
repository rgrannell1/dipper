"""Flag validation: mutual-exclusion and dependency checks for CLI arguments."""

import argparse
import sys


def validate_clear_flags(args: argparse.Namespace) -> None:
    if args.clear and not args.files and not args.diff:
        print("dipper: --clear requires --files or --diff", file=sys.stderr)
        sys.exit(1)
    if args.clear and args.edit:
        print("dipper: --clear and --edit are mutually exclusive", file=sys.stderr)
        sys.exit(1)


def validate_diff_flags(args: argparse.Namespace) -> None:
    if args.cached and not args.diff:
        print("dipper: --cached requires --diff", file=sys.stderr)
        sys.exit(1)
    if args.diff and args.files:
        print("dipper: --diff and --files are mutually exclusive", file=sys.stderr)
        sys.exit(1)
    if args.diff and args.file:
        print("dipper: --diff and a positional file argument are mutually exclusive", file=sys.stderr)
        sys.exit(1)


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
    validate_clear_flags(args)


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
    validate_diff_flags(args)
    validate_files_flags(args)
