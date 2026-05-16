# Tests for XDG config file parsing and --preset resolution

import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

from dipper.cli import resolve_groups
from dipper.config import parse_config


def write_config(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix="config", delete=False)
    tmp.write(textwrap.dedent(content))
    tmp.flush()
    return Path(tmp.name)


class TestParseConfig:
    def test_missing_file_returns_empty(self):
        tokens, presets = parse_config(Path("/nonexistent/path/config"))
        assert tokens == []
        assert presets == {}

    def test_blank_lines_ignored(self):
        path = write_config("\n\n--prompt foo\n\n")
        tokens, presets = parse_config(path)
        assert tokens == ["--prompt", "foo"]

    def test_comment_lines_ignored(self):
        path = write_config("# this is a comment\n--prompt bar\n")
        tokens, presets = parse_config(path)
        assert tokens == ["--prompt", "bar"]

    def test_flag_line_tokenised(self):
        path = write_config('--prompt "code review"\n')
        tokens, presets = parse_config(path)
        assert tokens == ["--prompt", "code review"]

    def test_preset_line_parsed(self):
        path = write_config("testing: bug,critical,security\n")
        tokens, presets = parse_config(path)
        assert presets == {"testing": "bug,critical,security"}
        assert tokens == []

    def test_multiple_presets(self):
        path = write_config("testing: bug,critical\nreading: quote\n")
        _, presets = parse_config(path)
        assert presets["testing"] == "bug,critical"
        assert presets["reading"] == "quote"

    def test_preset_with_spaces_around_colon(self):
        path = write_config("testing : bug , critical\n")
        _, presets = parse_config(path)
        assert "testing" in presets

    def test_flag_and_preset_coexist(self):
        path = write_config("--prompt review\ntesting: bug,critical\n")
        tokens, presets = parse_config(path)
        assert tokens == ["--prompt", "review"]
        assert presets == {"testing": "bug,critical"}


class TestResolveGroups:
    def ns(self, groups=None, preset=None):
        import argparse
        namespace = argparse.Namespace()
        namespace.groups = groups
        namespace.preset = preset
        return namespace

    def test_no_groups_no_preset_returns_none(self):
        assert resolve_groups(self.ns(), {}) is None

    def test_groups_returned_directly(self):
        assert resolve_groups(self.ns(groups="bug,critical"), {}) == "bug,critical"

    def test_preset_expands_to_csv(self):
        presets = {"testing": "bug,critical,security"}
        result = resolve_groups(self.ns(preset="testing"), presets)
        assert result == "bug,critical,security"

    def test_groups_wins_over_preset(self):
        presets = {"testing": "bug,critical"}
        result = resolve_groups(self.ns(groups="custom", preset="testing"), presets)
        assert result == "custom"

    def test_unknown_preset_exits(self):
        with pytest.raises(SystemExit):
            resolve_groups(self.ns(preset="nonexistent"), {})
