"""CLI orchestration: config merging, batch execution, and the main entry point."""

import argparse
import sys
from pathlib import Path

from dipper.cli.flags import build_ls_parser, build_parser
from dipper.cli.ls import run_ls
from dipper.cli.validations import validate_output_flags
from dipper.commons.config import config_path, parse_config
from dipper.commons.constants import ABORT_BATCH, BUILTIN_PRESETS, PREV_FILE
from dipper.commons.files import FileTarget, iter_run_targets, prompt_drop_stale
from dipper.commons.git import changed_files
from dipper.commons.paths import annotation_path, clear_annotation_sidecars
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


def parse_group_names(groups_csv: str | None) -> dict[int, str]:
    if not groups_csv:
        return {}
    return {
        idx: name.strip()
        for idx, name in enumerate(groups_csv.split(","), start=1)
        if name.strip()
    }


def make_run_args(args: argparse.Namespace, target: FileTarget, group_names: dict[int, str], presets: dict[str, str]) -> RunArgs:
    """Construct a RunArgs from CLI args and a resolved FileTarget."""
    return RunArgs(
        filename=target.filename or None,
        prompt=args.prompt,
        header=args.header,
        group_names=group_names,
        output_lines=args.lines,
        output_summary=args.summary,
        output_json=args.json,
        output_full=args.full,
        output_path=target.output_path,
        load_path=target.load_path,
        files_mode=bool(args.files) or bool(args.diff),
        presets=presets,
        diff_lines=target.diff_lines,
    )


def refresh_load_path(target: FileTarget) -> None:
    """Update target.load_path from disk before each session, so navigation reloads written sidecars."""
    if target.output_path:
        sidecar = Path(target.output_path)
        target.load_path = str(sidecar) if sidecar.exists() else None


def run_batch(args: argparse.Namespace, targets: list, group_names: dict[int, str], presets: dict[str, str]) -> None:
    """Launch a TUI session for each FileTarget, supporting forward (]) and backward ([) navigation."""
    idx = 0
    while 0 <= idx < len(targets):
        refresh_load_path(targets[idx])
        run_args = make_run_args(args, targets[idx], group_names, presets)
        result, group_names = run(targets[idx].source, run_args)
        if result == ABORT_BATCH:
            break
        if result == PREV_FILE:
            idx = max(0, idx - 1)
        else:
            idx += 1


def resolve_config(parser: argparse.ArgumentParser) -> tuple[argparse.Namespace, dict[str, str]]:
    """Parse CLI args merged with config-file defaults; return (args, presets)."""
    config_flag_tokens, presets = parse_config(config_path())
    config_ns = (
        parser.parse_args([*config_flag_tokens, "--"])
        if config_flag_tokens
        else argparse.Namespace()
    )
    cli_ns = parser.parse_args()
    merge_config(cli_ns, config_ns)
    return cli_ns, presets


def clear_diff_sidecars(args: argparse.Namespace) -> None:
    """Delete .annotations sidecars for all files in the current git diff."""
    for fpath in changed_files(cached=args.cached):
        sidecar = annotation_path(fpath)
        if sidecar.exists():
            sidecar.unlink()
            print(f"cleared {sidecar}")


def run_clear(args: argparse.Namespace) -> bool:
    """Execute --clear: delete sidecars and return True if --clear was active."""
    if not args.clear:
        return False
    if args.diff:
        clear_diff_sidecars(args)
    else:
        for sidecar in clear_annotation_sidecars(args.files):
            print(f"cleared {sidecar}")
    return True


def run_tui(args: argparse.Namespace, parser: argparse.ArgumentParser, presets: dict[str, str]) -> None:
    """Resolve targets, handle stale sidecars, and launch the annotation batch."""
    group_names = parse_group_names(resolve_groups(args, presets))
    targets = list(iter_run_targets(args, parser))
    if args.files or args.diff:
        prompt_drop_stale(targets, args.assume_yes)
    if args.files and not targets:
        label = "annotated" if args.edit else "unannotated"
        print(f"dipper: no {label} files found", file=sys.stderr)
        return
    merged_presets = {**BUILTIN_PRESETS, **presets}
    run_batch(args, targets, group_names, merged_presets)


def main() -> None:
    """Orchestrate config loading, argument parsing, source reading, and launch the TUI."""
    if len(sys.argv) > 1 and sys.argv[1] == "ls":
        run_ls(build_ls_parser().parse_args(sys.argv[2:]))
        return
    parser = build_parser()
    args, presets = resolve_config(parser)
    validate_output_flags(args)
    if run_clear(args):
        return
    run_tui(args, parser, presets)
