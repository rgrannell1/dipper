# CLI entry point — reads from file path argument or stdin

import argparse
import sys
from clipper.app import run


def main() -> None:
    parser = argparse.ArgumentParser(prog="clipper", description="Annotate text interactively")
    parser.add_argument("file", nargs="?", help="File to annotate (omit to read stdin)")
    parser.add_argument("--prompt", metavar="STR", default=None, help="Subtitle shown in the header bar")
    parser.add_argument("--header", metavar="STR", default=None, help="Label shown above the line list")
    parser.add_argument("--groups", metavar="CSV", default=None, help="Comma-separated group names (group 1, 2, …)")
    args = parser.parse_args()

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
        for i, name in enumerate(args.groups.split(","), start=1):
            name = name.strip()
            if name:
                group_names[i] = name

    run(source, filename, prompt=args.prompt, header=args.header, group_names=group_names)


if __name__ == "__main__":
    main()
