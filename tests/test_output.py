import re
import pytest
from clipper.constants import CLIPPER_PREFIX, SEPARATOR_LINE, UNDERLINE_MIN
from clipper.model import DocumentModel, LineState
from clipper.output import render_output


def make_model(*texts: str) -> DocumentModel:
    return DocumentModel(lines=[LineState(text=t) for t in texts])


def select(model: DocumentModel, idx: int, group: int = 1) -> None:
    model.active_group = group
    model.toggle_line(idx)


class TestNoSelections:
    def test_original_lines_reproduced(self):
        m = make_model("foo", "bar")
        assert render_output(m) == "foo\nbar"

    def test_no_separator_or_markers(self):
        m = make_model("foo", "bar")
        out = render_output(m)
        assert CLIPPER_PREFIX not in out


class TestMarkLine:
    def test_mark_line_follows_selected_line(self):
        m = make_model("hello")
        select(m, 0)
        lines = render_output(m).splitlines()
        assert lines[0] == "hello"
        assert lines[1].startswith("%%clipper:mark:1%%")

    def test_mark_line_contains_group_number(self):
        m = make_model("x")
        select(m, 0, group=3)
        out = render_output(m)
        assert "%%clipper:mark:3%%" in out

    def test_underline_minimum_length(self):
        m = make_model("hi")  # len 2 < UNDERLINE_MIN
        select(m, 0)
        mark = render_output(m).splitlines()[1]
        underline = mark.split("%%", 2)[-1].strip()
        assert len(underline) >= UNDERLINE_MIN

    def test_underline_matches_source_line_length(self):
        text = "x" * (UNDERLINE_MIN + 10)
        m = make_model(text)
        select(m, 0)
        mark = render_output(m).splitlines()[1]
        underline = mark.split("%%", 2)[-1].strip()
        assert len(underline) == len(text)

    def test_unselected_line_has_no_mark(self):
        m = make_model("a", "b")
        select(m, 0)
        lines = render_output(m).splitlines()
        # line index 2 is "b"; it should not be followed by a mark
        b_idx = lines.index("b")
        assert b_idx == len(lines) - 1 or not lines[b_idx + 1].startswith("%%clipper:mark")


class TestSeparator:
    def test_separator_present_when_groups_used(self):
        m = make_model("a")
        select(m, 0)
        assert SEPARATOR_LINE in render_output(m)

    def test_separator_absent_when_no_groups(self):
        m = make_model("a")
        assert SEPARATOR_LINE not in render_output(m)

    def test_body_before_separator(self):
        m = make_model("line1")
        select(m, 0)
        out = render_output(m)
        sep_pos = out.index(SEPARATOR_LINE)
        assert out.index("line1") < sep_pos


class TestAnnotations:
    def test_annotation_text_in_summary(self):
        m = make_model("code")
        select(m, 0)
        m.set_annotation(1, "this is important")
        assert "this is important" in render_output(m)

    def test_annotation_after_group_header(self):
        m = make_model("code")
        select(m, 0)
        m.set_annotation(1, "my note")
        lines = render_output(m).splitlines()
        header_idx = next(i for i, l in enumerate(lines) if "%%clipper:group:1%%" in l)
        assert lines[header_idx + 1] == "my note"

    def test_empty_annotation_produces_empty_line(self):
        m = make_model("code")
        select(m, 0)
        lines = render_output(m).splitlines()
        header_idx = next(i for i, l in enumerate(lines) if "%%clipper:group:1%%" in l)
        assert lines[header_idx + 1] == ""


class TestGroupNames:
    def test_named_group_in_header(self):
        m = make_model("code")
        select(m, 0)
        m.group_names[1] = "bugs"
        out = render_output(m)
        assert "%%clipper:group:1%% bugs" in out

    def test_unnamed_group_header_has_no_trailing_name(self):
        m = make_model("code")
        select(m, 0)
        out = render_output(m)
        assert "%%clipper:group:1%%" in out
        line = next(l for l in out.splitlines() if "%%clipper:group:1%%" in l)
        assert line.strip() == "%%clipper:group:1%%"


class TestMultipleGroups:
    def test_each_group_gets_header(self):
        m = make_model("a", "b")
        select(m, 0, group=1)
        select(m, 1, group=2)
        out = render_output(m)
        assert "%%clipper:group:1%%" in out
        assert "%%clipper:group:2%%" in out

    def test_groups_in_sorted_order(self):
        m = make_model("a", "b", "c")
        select(m, 2, group=3)
        select(m, 0, group=1)
        out = render_output(m)
        g1 = out.index("%%clipper:group:1%%")
        g3 = out.index("%%clipper:group:3%%")
        assert g1 < g3

    def test_each_group_annotation_present(self):
        m = make_model("a", "b")
        select(m, 0, group=1)
        select(m, 1, group=2)
        m.set_annotation(1, "note one")
        m.set_annotation(2, "note two")
        out = render_output(m)
        assert "note one" in out
        assert "note two" in out


class TestMarkerPattern:
    def test_all_clipper_lines_match_pattern(self):
        pattern = re.compile(r"^%%clipper:[^%]+%%")
        m = make_model("alpha", "beta")
        select(m, 0, group=1)
        select(m, 1, group=2)
        m.set_annotation(1, "ann")
        for line in render_output(m).splitlines():
            if line.startswith("%%"):
                assert pattern.match(line), f"Bad marker line: {line!r}"
