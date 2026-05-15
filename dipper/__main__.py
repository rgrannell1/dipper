# CLI entry point — reads from file path argument or stdin

import argparse
import os
import shlex
import sys
from pathlib import Path
from dipper.app import run


def _config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "dipper" / "config"


def _load_config_args(parser: argparse.ArgumentParser) -> list[str]:
    path = _config_path()
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    tokens: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        tokens.extend(shlex.split(stripped))
    return tokens


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dipper", description="Annotate text interactively")
    parser.add_argument("file", nargs="?", help="File to annotate (omit to read stdin)")
    parser.add_argument("--prompt", metavar="STR", default=None, help="Subtitle shown in the header bar")
    parser.add_argument("--header", metavar="STR", default=None, help="Label shown above the line list")
    parser.add_argument("--groups", metavar="CSV", default=None, help="Comma-separated group names (group 1, 2, …)")
    parser.add_argument("--header-group", metavar="NAME", default=None, dest="header_group", help="Group name to use as section headers")
    return parser


def main() -> None:
    parser = _build_parser()

    config_args = _load_config_args(parser)
    config_ns = parser.parse_args(config_args + ["--"]) if config_args else argparse.Namespace()

    cli_ns = parser.parse_args()

    # CLI wins over config; merge by only applying config values for unset CLI args
    for key, value in vars(config_ns).items():
        if key == "file":
            continue
        if getattr(cli_ns, key, None) is None and value is not None:
            setattr(cli_ns, key, value)

    args = cli_ns

    if args.file:
        source = open(args.file).read()
        filename = args.file
    else:
        if sys.stdin.isatty():
            parser.print_usage(sys.stderr)
            sys.exit(1)
        source = sys.stdin.read()
        filename = None

    group_names = {}
    if args.groups:
        for idx, name in enumerate(args.groups.split(","), start=1):
            name = name.strip()
            if name:
                group_names[idx] = name

    run(
        source,
        filename,
        prompt=args.prompt,
        header=args.header,
        group_names=group_names,
        header_group=args.header_group,
    )


if __name__ == "__main__":
    main()
