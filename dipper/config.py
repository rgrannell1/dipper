# Config file discovery and parsing

import os
import shlex
from pathlib import Path


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
