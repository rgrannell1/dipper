"""Config file discovery and parsing from YAML."""

import os
import sys
from pathlib import Path

import yaml

# Boolean flags — presence alone is sufficient, no value needed
BOOL_FLAGS = {"full", "lines", "summary", "json"}

# Value flags — require a string argument
VALUE_FLAGS = {"prompt", "header", "groups", "preset", "load", "files", "theme"}

# Optional-value flags — bare (True) or with a string path
OPTIONAL_VALUE_FLAGS = {"output"}


def config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "dipper" / "config.yaml"


def key_to_tokens(key: str, value: object) -> list[str]:
    """Convert one YAML key/value pair to argparse flag tokens."""
    if key in BOOL_FLAGS:
        return [f"--{key}"] if value else []
    if key in VALUE_FLAGS:
        return [f"--{key}", str(value)]
    if key in OPTIONAL_VALUE_FLAGS:
        if isinstance(value, bool):
            return [f"--{key}"] if value else []
        return [f"--{key}", str(value)] if value else []
    print(f"dipper: config warning: unknown key ignored: {key!r}", file=sys.stderr)
    return []


def flag_tokens_from_yaml(data: dict) -> list[str]:
    tokens: list[str] = []
    for key, value in data.items():
        tokens.extend(key_to_tokens(key, value))
    return tokens


def parse_config(path: Path) -> tuple[list[str], dict[str, str]]:
    """Return (flag_tokens, presets) from the YAML config file."""
    if not path.exists():
        return [], {}
    data = yaml.safe_load(path.read_text()) or {}
    raw_presets = data.pop("presets", {})
    presets = {str(name): str(csv) for name, csv in raw_presets.items()}
    return flag_tokens_from_yaml(data), presets
