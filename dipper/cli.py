"""CLI argument helpers: source reading, config merging, group resolution"""

import argparse
import sys
from pathlib import Path

from dipper.constants import BUILTIN_PRESETS


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
        parser.print_usage(sys.stderr)
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
