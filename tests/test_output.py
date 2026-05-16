import json
import re

from dipper.commons.constants import DIPPER_PREFIX, SEPARATOR_LINE, UNDERLINE_MIN
from dipper.controller.output import encode_ranges, render_json, render_output
from dipper.model.state import DocumentModel, LineState


def make_model(*texts: str) -> DocumentModel:
    return DocumentModel(lines=[LineState(text=text) for text in texts])


def select(model: DocumentModel, idx: int, group: int = 1) -> None:
    model.active_group = group
    model.toggle_line(idx)


class TestNoSelections:
    def test_original_lines_reproduced(self):
        """Proves full mode with no selections reproduces the source verbatim."""
        model = make_model("foo", "bar")
        assert render_output(model, full=True) == "foo\nbar"

    def test_default_compact_with_no_selections_is_empty(self):
        """Proves compact default with no selections produces empty output."""
        model = make_model("foo", "bar")
        assert render_output(model) == ""

    def test_no_separator_or_markers(self):
        model = make_model("foo", "bar")
        out = render_output(model)
        assert DIPPER_PREFIX not in out


class TestMarkLine:
    def test_mark_line_follows_selected_line(self):
        model = make_model("hello")
        select(model, 0)
        lines = render_output(model).splitlines()
        assert lines[0] == "hello"
        assert lines[1].startswith("%%dipper:mark:1:")

    def test_mark_line_contains_group_number(self):
        model = make_model("x")
        select(model, 0, group=3)
        out = render_output(model)
        assert "%%dipper:mark:3:" in out

    def test_mark_line_contains_1based_line_number(self):
        model = make_model("a", "b", "c")
        select(model, 2)  # third line → line number 3
        lines = render_output(model).splitlines()
        c_idx = lines.index("c")
        assert lines[c_idx + 1].startswith("%%dipper:mark:1:3%%")

    def test_mark_line_first_line_number_is_1(self):
        model = make_model("first")
        select(model, 0)
        mark = render_output(model).splitlines()[1]
        assert mark.startswith("%%dipper:mark:1:1%%")

    def test_underline_minimum_length(self):
        model = make_model("hi")  # len 2 < UNDERLINE_MIN
        select(model, 0)
        mark = render_output(model).splitlines()[1]
        parts = mark.split("%%", 2)
        underline = parts[-1].strip()
        assert len(underline) >= UNDERLINE_MIN

    def test_underline_matches_source_line_length(self):
        text = "x" * (UNDERLINE_MIN + 10)
        model = make_model(text)
        select(model, 0)
        mark = render_output(model).splitlines()[1]
        parts = mark.split("%%", 2)
        underline = parts[-1].strip()
        assert len(underline) == len(text)

    def test_unselected_line_has_no_mark(self):
        """Proves unselected lines appear without a mark in full mode."""
        model = make_model("a", "b")
        select(model, 0)
        lines = render_output(model, full=True).splitlines()
        b_idx = lines.index("b")
        is_last_line = b_idx == len(lines) - 1
        if not is_last_line:
            assert not lines[b_idx + 1].startswith("%%dipper:mark")


class TestSeparator:
    def test_separator_present_in_full_mode_when_groups_used(self):
        """Proves separator appears in --full mode when lines are selected."""
        model = make_model("a")
        select(model, 0)
        assert SEPARATOR_LINE in render_output(model, full=True)

    def test_separator_absent_in_compact_mode(self):
        """Proves compact default never emits the separator line."""
        model = make_model("a")
        select(model, 0)
        assert SEPARATOR_LINE not in render_output(model)

    def test_separator_absent_when_no_groups(self):
        model = make_model("a")
        assert SEPARATOR_LINE not in render_output(model)

    def test_body_before_separator(self):
        """Proves full-file body appears before the separator in --full mode."""
        model = make_model("line1")
        select(model, 0)
        out = render_output(model, full=True)
        sep_pos = out.index(SEPARATOR_LINE)
        assert out.index("line1") < sep_pos


class TestAnnotations:
    def test_annotation_text_in_summary(self):
        model = make_model("code")
        select(model, 0)
        model.groups.set_annotation(1, 0, "this is important")
        assert "this is important" in render_output(model)

    def test_annotation_after_group_header(self):
        model = make_model("code")
        select(model, 0)
        model.groups.set_annotation(1, 0, "my note")
        lines = render_output(model).splitlines()
        header_idx = next(idx for idx, ln in enumerate(lines) if "%%dipper:group:1:" in ln)
        assert lines[header_idx + 1] == "my note"

    def test_empty_annotation_produces_empty_line(self):
        model = make_model("code")
        select(model, 0)
        lines = render_output(model).splitlines()
        header_idx = next(idx for idx, ln in enumerate(lines) if "%%dipper:group:1:" in ln)
        assert lines[header_idx + 1] == ""


class TestGroupHeader:
    def test_group_header_contains_line_range(self):
        model = make_model("a", "b", "c")
        select(model, 0)
        select(model, 2)
        out = render_output(model)
        # lines 1 and 3 are each a separate block; each gets its own header
        assert "%%dipper:group:1:1%%" in out
        assert "%%dipper:group:1:3%%" in out

    def test_contiguous_lines_encoded_as_range(self):
        model = make_model("a", "b", "c")
        select(model, 0)
        select(model, 1)
        select(model, 2)
        out = render_output(model)
        assert "%%dipper:group:1:1-3%%" in out

    def test_named_group_in_header(self):
        model = make_model("code")
        select(model, 0)
        model.groups.names[1] = "bugs"
        out = render_output(model)
        assert "%%dipper:group:1:1%% bugs" in out

    def test_unnamed_group_header_ends_at_closing_delimiter(self):
        model = make_model("code")
        select(model, 0)
        out = render_output(model)
        line = next(ln for ln in out.splitlines() if "%%dipper:group:1:" in ln)
        assert line.strip() == "%%dipper:group:1:1%%"


class TestMultipleGroups:
    def test_each_group_gets_header(self):
        model = make_model("a", "b")
        select(model, 0, group=1)
        select(model, 1, group=2)
        out = render_output(model)
        assert "%%dipper:group:1:" in out
        assert "%%dipper:group:2:" in out

    def test_groups_sorted_by_start_line(self):
        "Proves blocks are emitted in ascending line-number order."
        model = make_model("a", "b", "c")
        select(model, 2, group=3)
        select(model, 0, group=1)
        out = render_output(model)
        g1 = out.index("%%dipper:group:1:")
        g3 = out.index("%%dipper:group:3:")
        assert g1 < g3

    def test_each_group_annotation_present(self):
        model = make_model("a", "b")
        select(model, 0, group=1)
        select(model, 1, group=2)
        model.groups.set_annotation(1, 0, "note one")
        model.groups.set_annotation(2, 1, "note two")
        out = render_output(model)
        assert "note one" in out
        assert "note two" in out

    def test_each_group_has_correct_line_numbers(self):
        model = make_model("a", "b", "c")
        select(model, 0, group=1)
        select(model, 2, group=2)
        out = render_output(model)
        assert "%%dipper:group:1:1%%" in out
        assert "%%dipper:group:2:3%%" in out


class TestPerBlockSummary:
    def test_two_disjoint_blocks_get_separate_headers(self):
        "Proves that two separate blocks in the same group each get their own header."
        model = make_model("a", "b", "c", "d", "e")
        select(model, 0)
        select(model, 2)
        select(model, 4)
        out = render_output(model)
        assert "%%dipper:group:1:1%%" in out
        assert "%%dipper:group:1:3%%" in out
        assert "%%dipper:group:1:5%%" in out

    def test_block_annotations_emitted_per_block(self):
        "Proves each block's annotation is emitted under its own header."
        model = make_model("a", "b", "c")
        select(model, 0)
        select(model, 2)
        model.groups.set_annotation(1, 0, "first block note")
        model.groups.set_annotation(1, 2, "second block note")
        out = render_output(model)
        assert "first block note" in out
        assert "second block note" in out

    def test_blocks_ordered_by_line_number_ascending(self):
        "Proves blocks from different groups are interleaved by line number."
        model = make_model("a", "b", "c", "d")
        select(model, 0, group=2)
        select(model, 1, group=1)
        select(model, 2, group=2)
        select(model, 3, group=1)
        out = render_output(model)
        g2_first = out.index("%%dipper:group:2:1%%")
        g1_second = out.index("%%dipper:group:1:2%%")
        g2_third = out.index("%%dipper:group:2:3%%")
        g1_fourth = out.index("%%dipper:group:1:4%%")
        assert g2_first < g1_second < g2_third < g1_fourth


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
        model = make_model("first", "middle", "last")
        select(model, 1)
        out = render_output(model, lines=True)
        assert "middle" in out
        assert "first" not in out
        assert "last" not in out

    def test_mark_follows_each_selected_line(self):
        model = make_model("a", "b")
        select(model, 0)
        lines = render_output(model, lines=True).splitlines()
        assert lines[0] == "a"
        assert lines[1].startswith("%%dipper:mark:1:1%%")

    def test_no_separator_in_lines_mode(self):
        model = make_model("a", "b")
        select(model, 0)
        assert SEPARATOR_LINE not in render_output(model, lines=True)

    def test_no_group_header_in_lines_mode(self):
        model = make_model("a")
        select(model, 0)
        assert "%%dipper:group:" not in render_output(model, lines=True)

    def test_empty_when_nothing_selected(self):
        model = make_model("a", "b")
        assert render_output(model, lines=True) == ""


class TestSummaryFlag:
    def test_only_group_headers_and_annotations(self):
        model = make_model("a", "b")
        select(model, 0)
        model.groups.set_annotation(1, 0, "found it")
        out = render_output(model, summary=True)
        assert "%%dipper:group:1:" in out
        assert "found it" in out

    def test_no_source_lines_in_summary_mode(self):
        model = make_model("alpha", "beta")
        select(model, 0)
        out = render_output(model, summary=True)
        assert "alpha" not in out
        assert "beta" not in out

    def test_no_separator_in_summary_mode(self):
        model = make_model("a")
        select(model, 0)
        assert SEPARATOR_LINE not in render_output(model, summary=True)

    def test_empty_when_nothing_selected(self):
        model = make_model("a")
        assert render_output(model, summary=True) == ""


class TestLinesPlusSummary:
    def test_selected_lines_and_summary_both_present(self):
        model = make_model("a", "b", "c")
        select(model, 1)
        model.groups.set_annotation(1, 1, "note")
        out = render_output(model, lines=True, summary=True)
        assert "b" in out
        assert "%%dipper:mark:1:2%%" in out
        assert "%%dipper:group:1:" in out
        assert "note" in out

    def test_unselected_lines_absent(self):
        model = make_model("first", "middle", "last")
        select(model, 1)
        out = render_output(model, lines=True, summary=True)
        assert "first" not in out
        assert "last" not in out

    def test_no_separator_between_sections(self):
        model = make_model("a")
        select(model, 0)
        out = render_output(model, lines=True, summary=True)
        assert SEPARATOR_LINE not in out


class TestMarkerPattern:
    def test_all_dipper_lines_match_pattern(self):
        pattern = re.compile(r"^%%dipper:[^%]+%%")
        model = make_model("alpha", "beta")
        select(model, 0, group=1)
        select(model, 1, group=2)
        model.groups.set_annotation(1, 0, "ann")
        for line in render_output(model).splitlines():
            if line.startswith("%%"):
                assert pattern.match(line), f"Bad marker line: {line!r}"


class TestRenderJson:
    def test_json_contains_filepath(self):
        "Proves render_json() includes the filepath field."
        model = make_model("code")
        select(model, 0)
        data = json.loads(render_json(model, "myfile.py"))
        assert data["filepath"] == "myfile.py"

    def test_json_filepath_null_for_stdin(self):
        "Proves render_json() emits null filepath when no file was given."
        model = make_model("code")
        select(model, 0)
        data = json.loads(render_json(model, None))
        assert data["filepath"] is None

    def test_json_groups_keyed_by_string_number(self):
        "Proves render_json() keys groups by their string number."
        model = make_model("a", "b")
        select(model, 0, group=1)
        select(model, 1, group=2)
        data = json.loads(render_json(model, None))
        assert "1" in data["groups"]
        assert "2" in data["groups"]

    def test_json_group_name(self):
        "Proves render_json() includes the group name."
        model = make_model("a")
        select(model, 0)
        model.groups.set_name(1, "bugs")
        data = json.loads(render_json(model, None))
        assert data["groups"]["1"]["name"] == "bugs"

    def test_json_default_group_name(self):
        "Proves render_json() uses 'group N' when no name is set."
        model = make_model("a")
        select(model, 0)
        data = json.loads(render_json(model, None))
        assert data["groups"]["1"]["name"] == "group 1"

    def test_json_lines_are_1based(self):
        "Proves render_json() emits 1-based line numbers."
        model = make_model("a", "b", "c")
        select(model, 2)
        data = json.loads(render_json(model, None))
        assert data["groups"]["1"]["lines"] == [3]

    def test_json_empty_groups_omitted(self):
        "Proves render_json() omits groups with no selected lines."
        model = make_model("a")
        data = json.loads(render_json(model, None))
        assert data["groups"] == {}

    def test_json_annotation_present(self):
        "Proves render_json() includes the annotation for a group with one block."
        model = make_model("a")
        select(model, 0)
        model.groups.set_annotation(1, 0, "important finding")
        data = json.loads(render_json(model, None))
        assert data["groups"]["1"]["annotation"] == "important finding"

    def test_json_annotation_null_when_absent(self):
        "Proves render_json() emits null annotation when no annotation exists."
        model = make_model("a")
        select(model, 0)
        data = json.loads(render_json(model, None))
        assert data["groups"]["1"]["annotation"] is None
