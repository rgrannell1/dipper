"""Git integration: resolve changed files and changed line numbers from diff hunks."""

from pathlib import Path

import git

from dipper.commons.constants import DIFF_ADDED, DIFF_MODIFIED


def repo_for(path: Path) -> git.Repo:
    """Find the git repo containing path, searching upward."""
    return git.Repo(path, search_parent_directories=True)


def changed_files(cached: bool) -> list[Path]:
    """Return absolute paths of files changed in the working tree (or index when cached=True)."""
    repo = repo_for(Path.cwd())
    diff = repo.index.diff("HEAD" if cached else None, cached=cached)
    root = Path(repo.working_tree_dir)
    return [root / item.a_path for item in diff if item.a_path]


def parse_hunk_counts(hunk_header: str) -> tuple[int, int, int]:
    """Parse '@@ -old_start,old_count +new_start,new_count @@' into (old_count, new_start, new_count)."""
    parts = hunk_header.split()
    old_part = next((part.lstrip("-") for part in parts if part.startswith("-")), "0,0")
    new_part = next((part.lstrip("+") for part in parts if part.startswith("+")), "0,0")
    old_count = int(old_part.split(",")[1]) if "," in old_part else 1
    new_str = new_part.split(",", 1)
    new_start = int(new_str[0])
    new_count = int(new_str[1]) if len(new_str) > 1 else 1
    return old_count, new_start, new_count


def hunk_line_types(hunk_header: str) -> dict[int, str]:
    """Return {1-based_line_num: colour} for lines introduced by this hunk."""
    old_count, new_start, new_count = parse_hunk_counts(hunk_header)
    if new_count == 0:
        return {}
    label = DIFF_ADDED if old_count == 0 else DIFF_MODIFIED
    return dict.fromkeys(range(new_start, new_start + new_count), label)


def changed_lines(path: Path, cached: bool) -> dict[int, str]:
    """Return {1-based_line_num: colour} for added/modified lines in path from the current diff."""
    repo = repo_for(path)
    diff_args = ["HEAD", "--"] if cached else ["--"]
    raw = repo.git.diff("--unified=0", *(["--cached"] if cached else []), *diff_args, str(path))
    result: dict[int, str] = {}
    for line in raw.splitlines():
        if line.startswith("@@"):
            result |= hunk_line_types(line)
    return result
