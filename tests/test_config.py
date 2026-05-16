# Tests for YAML config file parsing and --preset resolution

import tempfile
from pathlib import Path

import pytest

from dipper.cli import resolve_groups
from dipper.commons.config import parse_config


def write_config(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    tmp.write(content)
    tmp.flush()
    return Path(tmp.name)


class TestParseConfig:
    def test_missing_file_returns_empty(self):
        "Proves missing config file returns empty tokens and presets."
        tokens, presets = parse_config(Path("/nonexistent/path/config.yaml"))
        assert tokens == []
        assert presets == {}

    def test_empty_file_returns_empty(self):
        "Proves empty YAML file returns empty tokens and presets."
        path = write_config("")
        tokens, presets = parse_config(path)
        assert tokens == []
        assert presets == {}

    def test_value_flag_produces_tokens(self):
        "Proves a value flag key produces a --flag value token pair."
        path = write_config("prompt: code review\n")
        tokens, _ = parse_config(path)
        assert tokens == ["--prompt", "code review"]

    def test_bool_flag_true_produces_flag_token(self):
        "Proves a true boolean flag produces a bare --flag token."
        path = write_config("full: true\n")
        tokens, _ = parse_config(path)
        assert tokens == ["--full"]

    def test_bool_flag_false_produces_no_token(self):
        "Proves a false boolean flag produces no tokens."
        path = write_config("full: false\n")
        tokens, _ = parse_config(path)
        assert tokens == []

    def test_output_bare_true_produces_bare_flag(self):
        "Proves output: true produces bare --output token (auto-derive path)."
        path = write_config("output: true\n")
        tokens, _ = parse_config(path)
        assert tokens == ["--output"]

    def test_output_path_produces_value_token(self):
        "Proves output: /path produces --output /path token pair."
        path = write_config("output: /tmp/out.annotations\n")
        tokens, _ = parse_config(path)
        assert tokens == ["--output", "/tmp/out.annotations"]

    def test_presets_section_parsed(self):
        "Proves presets section is returned as a dict, not as flag tokens."
        path = write_config("presets:\n  testing: bug,critical,security\n")
        tokens, presets = parse_config(path)
        assert presets == {"testing": "bug,critical,security"}
        assert tokens == []

    def test_multiple_presets(self):
        "Proves multiple presets are all captured."
        path = write_config("presets:\n  testing: bug,critical\n  reading: quote\n")
        _, presets = parse_config(path)
        assert presets["testing"] == "bug,critical"
        assert presets["reading"] == "quote"

    def test_flags_and_presets_coexist(self):
        "Proves flag defaults and presets can appear together."
        path = write_config("prompt: review\npresets:\n  cr: bug,critical\n")
        tokens, presets = parse_config(path)
        assert tokens == ["--prompt", "review"]
        assert presets == {"cr": "bug,critical"}

    def test_unknown_key_warns(self, capsys):
        "Proves unknown keys emit a warning and are ignored."
        path = write_config("boguskey: value\n")
        tokens, _ = parse_config(path)
        assert tokens == []
        assert "boguskey" in capsys.readouterr().err

    def test_known_keys_do_not_warn(self, capsys):
        "Proves well-formed config emits no warnings."
        path = write_config("prompt: foo\nfull: false\npresets:\n  cr: bug\n")
        parse_config(path)
        assert capsys.readouterr().err == ""


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
