# CLI entry point — reads from file path argument or stdin

import argparse
import os
import shlex
import sys
from pathlib import Path
from dipper.app import run


def config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "dipper" / "config"


def parse_config(path: Path) -> tuple[list[str], dict[str, str]]:
    """Return (flag_tokens, presets) from the config file."""
    if not path.exists():
        return [], {}
    flag_tokens: list[str] = []
    presets: dict[str, str] = {}
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped and not stripped.startswith("--"):
            name, _, csv = stripped.partition(":")
            presets[name.strip()] = csv.strip()
        else:
            flag_tokens.extend(shlex.split(stripped))
    return flag_tokens, presets


def build_parser() -> argparse.ArgumentParser:
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
    parser.add_argument("--output", metavar="FILE", default=None,
                        help="Write output to FILE instead of stdout")
    return parser


BUILTIN_PRESETS: dict[str, str] = {
    "priorities": "p1,p2,p3,p4,p5",
    "cr": "bug,critical,minor,praise,question,note",
}


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
        return open(args.file).read(), args.file
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


def main() -> None:
    parser = build_parser()
    config_flag_tokens, presets = parse_config(config_path())
    config_ns = (
        parser.parse_args(config_flag_tokens + ["--"])
        if config_flag_tokens
        else argparse.Namespace()
    )
    cli_ns = parser.parse_args()
    merge_config(cli_ns, config_ns)
    args = cli_ns
    source, filename = read_source(args, parser)
    group_names = parse_group_names(resolve_groups(args, presets))
    run(
        source, filename,
        prompt=args.prompt, header=args.header, group_names=group_names,
        output_lines=args.lines, output_summary=args.summary, output_path=args.output,
    )


if __name__ == "__main__":
    main()
