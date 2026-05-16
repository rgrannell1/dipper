import re
import pytest
from dipper.constants import DIPPER_PREFIX, SEPARATOR_LINE, UNDERLINE_MIN
from dipper.model import DocumentModel
from dipper.state import LineState
from dipper.output import render_output, encode_ranges


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
        assert DIPPER_PREFIX not in out


class TestMarkLine:
    def test_mark_line_follows_selected_line(self):
        m = make_model("hello")
        select(m, 0)
        lines = render_output(m).splitlines()
        assert lines[0] == "hello"
        assert lines[1].startswith("%%dipper:mark:1:")

    def test_mark_line_contains_group_number(self):
        m = make_model("x")
        select(m, 0, group=3)
        out = render_output(m)
        assert "%%dipper:mark:3:" in out

    def test_mark_line_contains_1based_line_number(self):
        m = make_model("a", "b", "c")
        select(m, 2)  # third line → line number 3
        lines = render_output(m).splitlines()
        c_idx = lines.index("c")
        assert lines[c_idx + 1].startswith("%%dipper:mark:1:3%%")

    def test_mark_line_first_line_number_is_1(self):
        m = make_model("first")
        select(m, 0)
        mark = render_output(m).splitlines()[1]
        assert mark.startswith("%%dipper:mark:1:1%%")

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
        b_idx = lines.index("b")
        assert b_idx == len(lines) - 1 or not lines[b_idx + 1].startswith("%%dipper:mark")


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
        header_idx = next(i for i, l in enumerate(lines) if "%%dipper:group:1:" in l)
        assert lines[header_idx + 1] == "my note"

    def test_empty_annotation_produces_empty_line(self):
        m = make_model("code")
        select(m, 0)
        lines = render_output(m).splitlines()
        header_idx = next(i for i, l in enumerate(lines) if "%%dipper:group:1:" in l)
        assert lines[header_idx + 1] == ""


class TestGroupHeader:
    def test_group_header_contains_line_range(self):
        m = make_model("a", "b", "c")
        select(m, 0)
        select(m, 2)
        out = render_output(m)
        # lines 1 and 3 selected — should appear as "1,3" in group header
        assert "%%dipper:group:1:1,3%%" in out

    def test_contiguous_lines_encoded_as_range(self):
        m = make_model("a", "b", "c")
        select(m, 0)
        select(m, 1)
        select(m, 2)
        out = render_output(m)
        assert "%%dipper:group:1:1-3%%" in out

    def test_named_group_in_header(self):
        m = make_model("code")
        select(m, 0)
        m.group_names[1] = "bugs"
        out = render_output(m)
        assert "%%dipper:group:1:1%% bugs" in out

    def test_unnamed_group_header_ends_at_closing_delimiter(self):
        m = make_model("code")
        select(m, 0)
        out = render_output(m)
        line = next(l for l in out.splitlines() if "%%dipper:group:1:" in l)
        assert line.strip() == "%%dipper:group:1:1%%"


class TestMultipleGroups:
    def test_each_group_gets_header(self):
        m = make_model("a", "b")
        select(m, 0, group=1)
        select(m, 1, group=2)
        out = render_output(m)
        assert "%%dipper:group:1:" in out
        assert "%%dipper:group:2:" in out

    def test_groups_in_sorted_order(self):
        m = make_model("a", "b", "c")
        select(m, 2, group=3)
        select(m, 0, group=1)
        out = render_output(m)
        g1 = out.index("%%dipper:group:1:")
        g3 = out.index("%%dipper:group:3:")
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

    def test_each_group_has_correct_line_numbers(self):
        m = make_model("a", "b", "c")
        select(m, 0, group=1)
        select(m, 2, group=2)
        out = render_output(m)
        assert "%%dipper:group:1:1%%" in out
        assert "%%dipper:group:2:3%%" in out


class TestEncodeRanges:
    def test_single_line(self):
        assert encode_ranges([5]) == "5"

    def test_contiguous_run(self):
        assert encode_ranges([3, 4, 5]) == "3-5"

    def test_isolated_lines(self):
        assert encode_ranges([1, 3, 5, 7]) == "1,3,5,7"

    def test_mixed_ranges(self):
        assert encode_ranges([3, 4, 5, 10, 11, 20]) == "3-5,10-11,20"

    def test_unsorted_input_sorted_in_output(self):
        assert encode_ranges([10, 1, 5]) == "1,5,10"

    def test_empty_list(self):
        assert encode_ranges([]) == ""


class TestLinesFlag:
    def test_only_selected_lines_emitted(self):
        m = make_model("first", "middle", "last")
        select(m, 1)
        out = render_output(m, lines=True)
        assert "middle" in out
        assert "first" not in out
        assert "last" not in out

    def test_mark_follows_each_selected_line(self):
        m = make_model("a", "b")
        select(m, 0)
        lines = render_output(m, lines=True).splitlines()
        assert lines[0] == "a"
        assert lines[1].startswith("%%dipper:mark:1:1%%")

    def test_no_separator_in_lines_mode(self):
        m = make_model("a", "b")
        select(m, 0)
        assert SEPARATOR_LINE not in render_output(m, lines=True)

    def test_no_group_header_in_lines_mode(self):
        m = make_model("a")
        select(m, 0)
        assert "%%dipper:group:" not in render_output(m, lines=True)

    def test_empty_when_nothing_selected(self):
        m = make_model("a", "b")
        assert render_output(m, lines=True) == ""


class TestSummaryFlag:
    def test_only_group_headers_and_annotations(self):
        m = make_model("a", "b")
        select(m, 0)
        m.set_annotation(1, "found it")
        out = render_output(m, summary=True)
        assert "%%dipper:group:1:" in out
        assert "found it" in out

    def test_no_source_lines_in_summary_mode(self):
        m = make_model("alpha", "beta")
        select(m, 0)
        out = render_output(m, summary=True)
        assert "alpha" not in out
        assert "beta" not in out

    def test_no_separator_in_summary_mode(self):
        m = make_model("a")
        select(m, 0)
        assert SEPARATOR_LINE not in render_output(m, summary=True)

    def test_empty_when_nothing_selected(self):
        m = make_model("a")
        assert render_output(m, summary=True) == ""


class TestLinesPlusSummary:
    def test_selected_lines_and_summary_both_present(self):
        m = make_model("a", "b", "c")
        select(m, 1)
        m.set_annotation(1, "note")
        out = render_output(m, lines=True, summary=True)
        assert "b" in out
        assert "%%dipper:mark:1:2%%" in out
        assert "%%dipper:group:1:" in out
        assert "note" in out

    def test_unselected_lines_absent(self):
        m = make_model("first", "middle", "last")
        select(m, 1)
        out = render_output(m, lines=True, summary=True)
        assert "first" not in out
        assert "last" not in out

    def test_no_separator_between_sections(self):
        m = make_model("a")
        select(m, 0)
        out = render_output(m, lines=True, summary=True)
        assert SEPARATOR_LINE not in out


class TestMarkerPattern:
    def test_all_dipper_lines_match_pattern(self):
        pattern = re.compile(r"^%%dipper:[^%]+%%")
        m = make_model("alpha", "beta")
        select(m, 0, group=1)
        select(m, 1, group=2)
        m.set_annotation(1, "ann")
        for line in render_output(m).splitlines():
            if line.startswith("%%"):
                assert pattern.match(line), f"Bad marker line: {line!r}"
