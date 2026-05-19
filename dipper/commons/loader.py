"""Session loader: restores line assignments, group names, and block annotations from a dipper annotations file."""

import contextlib
import hashlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dipper.commons.constants import GROUP_COUNT

MARK_RE = re.compile(r"^%%dipper:mark:(\d+):(\d+)%%")
GROUP_RE = re.compile(r"^%%dipper:group:(\d+):([^%]+)%%\s*(.*)")
META_RE = re.compile(r"^%%dipper:meta:filepath:(.+)%%")
META_HASH_RE = re.compile(r"^%%dipper:meta:hash:([0-9a-f]{64})%%")
DIPPER_LINE_RE = re.compile(r"^%%dipper:[^%]+%%")
SEPARATOR = "%%dipper:separator%%"


@dataclass
class LoadedSession:
    line_groups: dict[int, int] = field(default_factory=dict)
    group_names: dict[int, str] = field(default_factory=dict)
    block_annotations: dict[tuple[int, int], str] = field(default_factory=dict)


def decode_ranges(ranges_str: str) -> list[int]:
    """Decode a range string like '1-3,7' into a sorted list of 1-based line numbers."""
    line_nums: list[int] = []
    for part in ranges_str.split(","):
        part = part.strip()
        if "-" in part:
            start_str, _, end_str = part.partition("-")
            with contextlib.suppress(ValueError):
                line_nums.extend(range(int(start_str), int(end_str) + 1))
        else:
            with contextlib.suppress(ValueError):
                line_nums.append(int(part))
    return sorted(line_nums)


def warn(message: str) -> None:
    print(f"dipper: load warning: {message}", file=sys.stderr)


def apply_mark_line(raw_line: str, session: LoadedSession, source_line_count: int) -> None:
    """Parse a %%dipper:mark:%% line and record the line assignment."""
    mark_match = MARK_RE.match(raw_line)
    if not mark_match:
        return
    try:
        group = int(mark_match.group(1))
        line_num = int(mark_match.group(2))
    except ValueError:
        warn(f"malformed mark line: {raw_line!r}")
        return
    if not (1 <= group <= GROUP_COUNT):
        warn(f"group {group} out of range in mark line, skipping")
        return
    if 1 <= line_num <= source_line_count:
        session.line_groups[line_num] = group


def extract_group_key(group_match: re.Match, session: LoadedSession) -> tuple[int, int] | None:
    """Extract block key and update group name from a parsed group match."""
    try:
        group = int(group_match.group(1))
    except ValueError:
        warn(f"malformed group header: {group_match.group(0)!r}")
        return None
    range_nums = decode_ranges(group_match.group(2))
    if not range_nums:
        warn(f"empty ranges in group header: {group_match.group(0)!r}")
        return None
    name = group_match.group(3).strip()
    if name:
        session.group_names[group] = name
    return (group, min(range_nums) - 1)


def apply_group_header(raw_line: str, session: LoadedSession) -> tuple[int, int] | None:
    group_match = GROUP_RE.match(raw_line)
    if not group_match:
        return None
    return extract_group_key(group_match, session)


def split_at_separator(lines: list[str]) -> tuple[list[str], list[str]]:
    """Split annotation file lines into pre-separator and post-separator."""
    for idx, line in enumerate(lines):
        if line.strip() == SEPARATOR:
            return lines[:idx], lines[idx + 1:]
    return lines, []


def parse_body_lines(body: list[str], session: LoadedSession, source_line_count: int) -> None:
    for raw_line in body:
        if not META_RE.match(raw_line):
            apply_mark_line(raw_line, session, source_line_count)


def parse_summary_lines(summary: list[str], session: LoadedSession) -> None:
    pending_key: tuple[int, int] | None = None
    for raw_line in summary:
        if GROUP_RE.match(raw_line):
            pending_key = apply_group_header(raw_line, session)
            continue
        if pending_key is not None:
            annotation = raw_line.strip()
            if annotation and not DIPPER_LINE_RE.match(raw_line):
                session.block_annotations[pending_key] = annotation
            pending_key = None


def parse_annotations_file(text: str, source_line_count: int) -> LoadedSession:
    """Parse a dipper annotations file and return the restored session state."""
    session = LoadedSession()
    body, summary = split_at_separator(text.splitlines())
    parse_body_lines(body, session, source_line_count)
    parse_summary_lines(summary, session)
    return session


def verify_filepath(annotations_text: str, source_abs: str) -> None:
    """Exit with an error if the stored filepath does not match source_abs."""
    for raw_line in annotations_text.splitlines():
        meta_match = META_RE.match(raw_line)
        if meta_match:
            stored_raw = meta_match.group(1)
            stored_path = str(Path(stored_raw).resolve())
            if stored_path != source_abs:
                print(
                    f"dipper: --load: filepath mismatch — annotations are for {stored_path!r}, "
                    f"but opening {source_abs!r}",
                    file=sys.stderr,
                )
                sys.exit(1)
            break


def stored_hash(annotations_text: str) -> str | None:
    """Extract the stored source hash from an annotations file, or None if absent."""
    for raw_line in annotations_text.splitlines():
        match = META_HASH_RE.match(raw_line)
        if match:
            return match.group(1)
    return None


def is_stale(source: str, annotations_text: str) -> bool:
    """Return True if the stored hash exists and does not match the current source hash."""
    expected = stored_hash(annotations_text)
    if expected is None:
        return False
    actual = hashlib.sha256(source.encode()).hexdigest()
    return actual != expected


def load_session(source: str, filepath: str | None, load_path: str) -> LoadedSession:
    """Read a dipper annotations file and verify it matches filepath before parsing."""
    annotations_path = Path(load_path)
    if not annotations_path.exists():
        print(f"dipper: --load: file not found: {load_path}", file=sys.stderr)
        sys.exit(1)
    annotations_text = annotations_path.read_text()
    if filepath is not None:
        source_abs = str(Path(filepath).resolve())
        verify_filepath(annotations_text, source_abs)
    return parse_annotations_file(annotations_text, len(source.splitlines()))
