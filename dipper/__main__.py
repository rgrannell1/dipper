"""CLI entry point — reads from file path argument or stdin"""

import argparse

from dipper.app import run
from dipper.cli import merge_config, parse_group_names, read_source, resolve_groups
from dipper.config import config_path, parse_config


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


def main() -> None:
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
    source, filename = read_source(args, parser)
    group_names = parse_group_names(resolve_groups(args, presets))
    run(
        source, filename,
        prompt=args.prompt, header=args.header, group_names=group_names,
        output_lines=args.lines, output_summary=args.summary, output_path=args.output,
    )


if __name__ == "__main__":
    main()
