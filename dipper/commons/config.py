"""Config file discovery and parsing."""

import os
import shlex
import sys
from pathlib import Path


def config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "dipper" / "config"


def classify_line(line: str) -> tuple[str, str]:
    """Classify one config line as 'flag', 'preset', 'skip', or 'malformed'."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return "skip", stripped
    if stripped.startswith("--"):
        return "flag", stripped
    if ":" in stripped:
        return "preset", stripped
    return "malformed", stripped


def parse_config(path: Path) -> tuple[list[str], dict[str, str]]:
    """Return (flag_tokens, presets) from the config file."""
    if not path.exists():
        return [], {}
    flag_tokens: list[str] = []
    presets: dict[str, str] = {}
    for line in path.read_text().splitlines():
        kind, value = classify_line(line)
        if kind == "flag":
            flag_tokens.extend(shlex.split(value))
        elif kind == "preset":
            name, _, csv = value.partition(":")
            presets[name.strip()] = csv.strip()
        elif kind == "malformed":
            print(f"dipper: config warning: malformed line ignored: {value!r}", file=sys.stderr)
    return flag_tokens, presets
