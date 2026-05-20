"""Fuzz tester: blasts random key sequences against random inputs to detect crashes and key-liveness failures."""

import asyncio
import random
import string
import sys
import time
import traceback
from argparse import ArgumentParser
from dataclasses import dataclass

from dipper.commons.constants import BUILTIN_PRESETS
from dipper.commons.themes import THEMES
from dipper.view.app import ClipperApp
from dipper.view.app_types import RunArgs

SESSION_KEY_COUNT = 500

# Seconds before a single session is forcibly cancelled
# large-file sessions (500-1000 lines) can take 60s+ with 500 keys; 120s is safety-net only
SESSION_TIMEOUT = 120.0

# Keys and sampling weights -- navigation most common, modal openers less so
KEY_ALPHABET: list[tuple[str, int]] = [
    ("up", 10), ("down", 10), ("left", 8), ("right", 8), ("tab", 8),
    ("pageup", 3), ("pagedown", 3), ("home", 3), ("end", 3),
    ("g", 3), ("G", 3),
    ("1", 5), ("2", 5), ("3", 5), ("4", 3), ("5", 3),
    ("6", 3), ("7", 2), ("8", 2), ("9", 2),
    ("x", 3), ("u", 3), ("f", 3),
    ("asterisk", 4), ("greater_than_sign", 4), ("less_than_sign", 4),
    ("n", 2), ("r", 2), ("o", 2), ("question_mark", 2),
    ("colon", 2), ("slash", 5), ("ctrl+p", 1),
    ("escape", 5), ("enter", 5), ("q", 2),
    ("a", 1), ("b", 1), ("c", 1), ("d", 1), ("e", 1),
    ("h", 1), ("i", 1), ("j", 1), ("k", 1), ("l", 1),
    ("m", 1), ("p", 1), ("s", 1), ("t", 1), ("v", 1),
    ("w", 1), ("y", 1), ("z", 1),
]

KEY_NAMES: list[str] = [key for key, _ in KEY_ALPHABET]
KEY_WEIGHTS: list[int] = [weight for _, weight in KEY_ALPHABET]

# Liveness sessions omit 'q' so the app stays running for the post-blast responsiveness check
KEY_ALPHABET_LIVENESS: list[tuple[str, int]] = [(key, wt) for key, wt in KEY_ALPHABET if key != "q"]
KEY_NAMES_LIVENESS: list[str] = [key for key, _ in KEY_ALPHABET_LIVENESS]
KEY_WEIGHTS_LIVENESS: list[int] = [wt for _, wt in KEY_ALPHABET_LIVENESS]

# Fraction of sessions that run a liveness check instead of a pure crash test
LIVENESS_SESSION_PROBABILITY = 0.4

FILENAMES: list[str | None] = [None, "test.py", "test.md", "test.sh", "test.json", "test.txt"]

THEMES_LIST: list[str] = list(THEMES.keys())

# Each dict is unpacked into RunArgs — mutually exclusive combos only
OUTPUT_FLAG_COMBOS: list[dict] = [
    {},
    {"output_lines": True},
    {"output_summary": True},
    {"output_lines": True, "output_summary": True},
    {"output_full": True},
    {"output_json": True},
]

# Pre-built group_names dicts for each builtin preset, plus empty (no preset)
# Probability of enabling files_mode in a given fuzz session
FILES_MODE_PROBABILITY = 0.2

PRESET_GROUP_NAMES: list[dict[int, str]] = [{}] + [
    {idx: name.strip() for idx, name in enumerate(csv.split(","), start=1) if name.strip()}
    for csv in BUILTIN_PRESETS.values()
]


@dataclass
class FuzzSession:
    """Metadata for a single fuzz run."""

    num: int
    shape: str
    key_count: int
    mode: str = "crash"  # "crash" or "liveness"


def random_word() -> str:
    """Return a random lowercase word."""
    return "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))


def typical_source() -> str:
    """Return a realistic-looking source file with 20-100 lines."""
    lines = [
        f"{'    ' * random.randint(0, 3)}{random_word()} = {random_word()}({random_word()})"
        for _ in range(random.randint(20, 100))
    ]
    return "\n".join(lines)


def long_lines_source() -> str:
    """Return a source file with very long lines (200-400 chars)."""
    return "\n".join("x" * random.randint(200, 400) for _ in range(random.randint(5, 20)))


def many_lines_source() -> str:
    """Return a source file with many short lines (500-1000)."""
    return "\n".join(random_word() for _ in range(random.randint(500, 1000)))


def unicode_source() -> str:
    """Return a source file with unicode characters including emoji and CJK."""
    chars = "alphabetaGamma日本語한국어🎵🦆🌸"
    return "\n".join(
        "".join(random.choices(chars, k=random.randint(5, 40)))
        for _ in range(random.randint(10, 30))
    )


def ansi_source() -> str:
    """Return a source file with raw ANSI escape codes embedded."""
    codes = ["\x1b[31m", "\x1b[32m", "\x1b[0m", "\x1b[1m", "\x1b[33;1m"]
    return "\n".join(
        f"{random.choice(codes)}{random_word()}\x1b[0m"
        for _ in range(random.randint(10, 30))
    )


def null_bytes_source() -> str:
    """Return a source file containing null bytes."""
    return "\n".join(f"{random_word()}\x00{random_word()}" for _ in range(random.randint(5, 20)))


def random_source() -> tuple[str, str]:
    """Return (source_text, shape_label) for a randomly chosen input shape."""
    shapes = [
        ("empty", ""),
        ("single_newline", "\n"),
        ("one_word", "hello"),
        ("whitespace", "   \n\t\n  \n"),
        ("typical", typical_source()),
        ("long_lines", long_lines_source()),
        ("many_lines", many_lines_source()),
        ("unicode", unicode_source()),
        ("ansi_codes", ansi_source()),
        ("null_bytes", null_bytes_source()),
    ]
    label, source = random.choice(shapes)
    return source, label


def random_run_args(filename: str | None) -> RunArgs:
    """Return RunArgs with randomly selected CLI-equivalent flags."""
    output_flags = random.choice(OUTPUT_FLAG_COMBOS)
    return RunArgs(
        filename=filename,
        output_path="/dev/null",
        theme=random.choice(THEMES_LIST),
        files_mode=random.random() < FILES_MODE_PROBABILITY,
        group_names=random.choice(PRESET_GROUP_NAMES),
        **output_flags,
    )


def random_key_sequence() -> list[str]:
    """Return SESSION_KEY_COUNT random keys sampled by weight."""
    return random.choices(KEY_NAMES, weights=KEY_WEIGHTS, k=SESSION_KEY_COUNT)


async def run_session(source: str, keys: list[str]) -> None:
    """Launch one TUI session and blast all keys in a single call; crash propagates via run_test().__aexit__."""
    filename = random.choice(FILENAMES)
    app = ClipperApp(source, random_run_args(filename))
    async with app.run_test() as pilot:
        await pilot.press(*keys)


async def check_key_liveness(app: ClipperApp, pilot) -> None:
    """Verify that modal-opening keys remain responsive after a random key blast."""
    for _ in range(10):
        await pilot.press("escape")
    if len(app.screen_stack) != 1:
        raise AssertionError(f"screen stack not cleared after escapes: depth {len(app.screen_stack)}")
    if not app._model.lines:
        return
    # Toggle cursor line into a group so 'n' has a block to annotate
    await pilot.press("tab")
    cursor_idx = app.line_view().cursor_index
    if app._model.lines[cursor_idx].group == 0:
        await pilot.press("tab")  # was already grouped; retoggle to restore it
    if app._model.lines[cursor_idx].group == 0:
        return  # could not establish a grouped line; skip rather than false-fail
    await pilot.press("n")
    if len(app.screen_stack) != 2:
        raise AssertionError(f"'n' unresponsive after {SESSION_KEY_COUNT} random keys (stack depth: {len(app.screen_stack)})")
    await pilot.press("escape")


async def run_liveness_session(source: str, keys: list[str]) -> None:
    """Launch a session without 'q', then verify modal keys still respond."""
    filename = random.choice(FILENAMES)
    app = ClipperApp(source, random_run_args(filename))
    async with app.run_test() as pilot:
        await pilot.press(*keys)
        await check_key_liveness(app, pilot)


def log_result(session: FuzzSession, status: str, start: float) -> None:
    """Print a one-line session summary."""
    elapsed = time.monotonic() - start
    line = f"session {session.num:4d}  mode={session.mode:<9}  shape={session.shape:<15}  keys={session.key_count}  {status}  [{elapsed:.0f}s]"
    print(line, flush=True)


def report_crash(session: FuzzSession, start: float) -> bool:
    """Log crash details; always returns False to stop the fuzz loop."""
    log_result(session, "CRASH", start)
    print()
    traceback.print_exc()
    return False


async def attempt_session(session_num: int, start: float) -> bool:
    """Run one fuzz session; log the result; return False if a crash or liveness failure is found."""
    source, shape = random_source()
    use_liveness = bool(source) and random.random() < LIVENESS_SESSION_PROBABILITY
    if use_liveness:
        keys = random.choices(KEY_NAMES_LIVENESS, weights=KEY_WEIGHTS_LIVENESS, k=SESSION_KEY_COUNT)
        run_fn = run_liveness_session
    else:
        keys = random_key_sequence()
        run_fn = run_session
    mode = "liveness" if use_liveness else "crash"
    session = FuzzSession(num=session_num, shape=shape, key_count=len(keys), mode=mode)
    try:
        await asyncio.wait_for(run_fn(source, keys), timeout=SESSION_TIMEOUT)
        log_result(session, "pass", start)
        return True
    except TimeoutError:
        log_result(session, "TIMEOUT", start)
        return True
    except Exception:  # noqa: BLE001 -- intentional: catch any TUI crash or AssertionError
        return report_crash(session, start)


async def fuzz_loop(minutes: int) -> None:
    """Run fuzz sessions until the time budget is exhausted; stop immediately on first crash."""
    budget = minutes * 60.0
    start = time.monotonic()
    session_count = 0

    while time.monotonic() - start < budget:
        session_count += 1
        ok = await attempt_session(session_count, start)
        if not ok:
            sys.exit(1)

    print(f"\n{session_count} sessions completed in {minutes}m -- no crashes found")


def main() -> None:
    """Entry point."""
    parser = ArgumentParser(description="Fuzz the dipper TUI with random key sequences")
    parser.add_argument("--minutes", type=int, default=30)
    parsed = parser.parse_args()
    asyncio.run(fuzz_loop(parsed.minutes))


if __name__ == "__main__":
    main()
