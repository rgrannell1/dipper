import pytest

from dipper.model.state import (
    DocumentModel,
    GroupState,
    LineState,
    RangeFillState,
    SearchState,
    nearest_annotated_group,
    nearest_group,
    selected_groups,
)


def make_model(*texts: str, active_group: int = 1) -> DocumentModel:
    return DocumentModel(
        lines=[LineState(text=text) for text in texts],
        active_group=active_group,
    )


class TestToggleLine:
    def test_unselected_line_joins_active_group(self):
        model = make_model("a", "b")
        model.toggle_line(0)
        assert model.lines[0].group == 1

    def test_toggle_same_group_clears_line(self):
        model = make_model("a")
        model.toggle_line(0)
        model.toggle_line(0)
        assert model.lines[0].group == 0

    def test_toggle_different_group_moves_line(self):
        model = make_model("a", active_group=1)
        model.toggle_line(0)
        model.active_group = 2
        model.toggle_line(0)
        assert model.lines[0].group == 2

    def test_other_lines_unaffected(self):
        model = make_model("a", "b", "c")
        model.toggle_line(1)
        assert model.lines[0].group == 0
        assert model.lines[2].group == 0


class TestSelectedGroups:
    def test_empty_model_has_no_groups(self):
        model = make_model("a", "b")
        assert selected_groups(model.lines) == set()

    def test_reports_groups_in_use(self):
        model = make_model("a", "b", "c")
        model.toggle_line(0)
        model.active_group = 2
        model.toggle_line(2)
        assert selected_groups(model.lines) == {1, 2}

    def test_cleared_line_removed_from_groups(self):
        model = make_model("a")
        model.toggle_line(0)
        model.toggle_line(0)
        assert selected_groups(model.lines) == set()


class TestGroupLabel:
    def test_default_label(self):
        model = make_model("a")
        assert model.groups.label(3) == "group 3"

    def test_named_group_label(self):
        model = make_model("a")
        model.groups.names[1] = "bugs"
        assert model.groups.label(1) == "bugs"


class TestNearestAnnotatedGroup:
    def test_none_when_no_annotations(self):
        model = make_model("a", "b")
        model.toggle_line(0)
        assert nearest_annotated_group(model.lines, model.groups.annotations, 0) is None

    def test_returns_group_of_nearest_annotated_line(self):
        model = make_model("a", "b", "c", "d")
        model.toggle_line(0)
        model.groups.set_annotation(1, "note")
        model.active_group = 2
        model.toggle_line(3)
        model.groups.set_annotation(2, "other")
        # cursor at line 1: closer to line 0 (group 1) than line 3 (group 2)
        assert nearest_annotated_group(model.lines, model.groups.annotations, 1) == 1
        # cursor at line 3: closer to line 3 (group 2)
        assert nearest_annotated_group(model.lines, model.groups.annotations, 3) == 2

    def test_ignores_selected_lines_without_annotation(self):
        model = make_model("a", "b")
        model.toggle_line(0)
        # group 1 selected but not annotated
        assert nearest_annotated_group(model.lines, model.groups.annotations, 0) is None


class TestNearestGroup:
    def test_none_when_no_groups(self):
        model = make_model("a", "b")
        assert nearest_group(model.lines, 0) is None

    def test_returns_nearest_group(self):
        model = make_model("a", "b", "c", "d")
        model.toggle_line(0)          # group 1 at line 0
        model.active_group = 2
        model.toggle_line(3)          # group 2 at line 3
        assert nearest_group(model.lines, 1) == 1   # closer to line 0
        assert nearest_group(model.lines, 3) == 2   # closer to line 3

    def test_equidistant_returns_some_group(self):
        model = make_model("a", "b", "c")
        model.toggle_line(0)
        model.active_group = 2
        model.toggle_line(2)
        assert nearest_group(model.lines, 1) in {1, 2}


class TestSearchState:
    def test_initial_state_is_empty(self):
        "Proves SearchState starts with no pattern, no indices, and cursor at zero."
        state = SearchState()
        assert state.pattern == "" and state.indices == [] and state.cursor == 0

    def test_set_stores_pattern_and_indices(self):
        "Proves set() stores the new pattern and match positions."
        state = SearchState()
        state.set("foo", [1, 3, 5])
        assert state.pattern == "foo" and state.indices == [1, 3, 5]

    def test_set_resets_cursor_to_zero(self):
        "Proves set() resets the cursor even if advance() was called previously."
        state = SearchState()
        state.set("foo", [1, 3, 5])
        state.advance()
        state.set("bar", [2, 4])
        assert state.cursor == 0

    def test_clear_empties_all_fields(self):
        "Proves clear() wipes pattern, indices, and cursor."
        state = SearchState()
        state.set("foo", [1, 2])
        state.clear()
        assert state.pattern == "" and state.indices == [] and state.cursor == 0

    def test_advance_moves_to_next_index(self):
        "Proves advance() steps the cursor forward and returns the new match position."
        state = SearchState()
        state.set("foo", [10, 20, 30])
        assert state.advance() == 20   # cursor 0 → 1, returns indices[1]

    def test_advance_wraps_around(self):
        "Proves advance() wraps from the last match back to the first."
        state = SearchState()
        state.set("foo", [10, 20])
        state.advance()               # cursor → 1
        assert state.advance() == 10  # wraps to cursor 0, returns indices[0]

    def test_retreat_moves_to_previous_index(self):
        "Proves retreat() steps the cursor backward and returns the new match position."
        state = SearchState()
        state.set("foo", [10, 20, 30])
        state.advance()               # cursor → 1
        assert state.retreat() == 10  # cursor 1 → 0, returns indices[0]

    def test_retreat_wraps_around(self):
        "Proves retreat() wraps from the first match back to the last."
        state = SearchState()
        state.set("foo", [10, 20, 30])
        assert state.retreat() == 30  # cursor 0 → 2 (wraps), returns indices[2]

    def test_advance_on_empty_returns_none(self):
        "Proves advance() returns None when there are no matches."
        assert SearchState().advance() is None

    def test_retreat_on_empty_returns_none(self):
        "Proves retreat() returns None when there are no matches."
        assert SearchState().retreat() is None

    def test_select_all_assigns_lines_to_group(self):
        "Proves select_all() sets the group on every matched line."
        lines = [LineState(text="a"), LineState(text="b"), LineState(text="c")]
        state = SearchState()
        state.set("a", [0, 2])
        state.select_all(lines, active_group=3)
        assert lines[0].group == 3 and lines[1].group == 0 and lines[2].group == 3

    def test_select_all_returns_changed_indices(self):
        "Proves select_all() returns the list of indices it assigned."
        lines = [LineState(text="a"), LineState(text="b")]
        state = SearchState()
        state.set("a", [0])
        assert state.select_all(lines, active_group=2) == [0]


class TestRangeFillState:
    def test_initial_anchor_is_none(self):
        "Proves RangeFillState starts with no anchor."
        assert RangeFillState().anchor is None

    def test_set_anchor_stores_index_and_group(self):
        "Proves set_anchor() records the line index and group."
        state = RangeFillState()
        state.set_anchor(5, 3)
        assert state.anchor == 5 and state.anchor_group == 3

    def test_clear_anchor_resets_to_none(self):
        "Proves clear_anchor() removes the anchor."
        state = RangeFillState()
        state.set_anchor(5, 3)
        state.clear_anchor()
        assert state.anchor is None

    def test_fill_forward_assigns_group(self):
        "Proves fill() assigns the active group to lines between anchor and end (inclusive)."
        lines = [LineState(text=str(idx)) for idx in range(5)]
        state = RangeFillState()
        state.set_anchor(1, 1)
        state.fill(lines, 3, active_group=2)
        assert [line.group for line in lines] == [0, 2, 2, 2, 0]

    def test_fill_reversed_range_assigns_group(self):
        "Proves fill() works when end_idx is before the anchor."
        lines = [LineState(text=str(idx)) for idx in range(5)]
        state = RangeFillState()
        state.set_anchor(3, 1)
        state.fill(lines, 1, active_group=2)
        assert [line.group for line in lines] == [0, 2, 2, 2, 0]

    def test_fill_clears_anchor(self):
        "Proves fill() clears the anchor after use."
        lines = [LineState(text=str(idx)) for idx in range(3)]
        state = RangeFillState()
        state.set_anchor(0, 1)
        state.fill(lines, 2, active_group=1)
        assert state.anchor is None

    def test_fill_returns_affected_range(self):
        "Proves fill() returns the range of line indices it modified."
        lines = [LineState(text=str(idx)) for idx in range(5)]
        state = RangeFillState()
        state.set_anchor(1, 1)
        affected = state.fill(lines, 3, active_group=1)
        assert list(affected) == [1, 2, 3]

    def test_fill_without_anchor_raises(self):
        "Proves fill() raises RuntimeError when no anchor has been set."
        with pytest.raises(RuntimeError):
            RangeFillState().fill([LineState(text="a")], 0, active_group=1)

    def test_fill_out_of_bounds_raises(self):
        "Proves fill() raises IndexError when end_idx exceeds the line list."
        lines = [LineState(text="a"), LineState(text="b")]
        state = RangeFillState()
        state.set_anchor(0, 1)
        with pytest.raises(IndexError):
            state.fill(lines, 5, active_group=1)


class TestGroupState:
    def test_default_label_uses_group_number(self):
        "Proves label() returns a fallback string when no name is set."
        assert GroupState({}).label(3) == "group 3"

    def test_named_label_returned(self):
        "Proves label() returns the stored name when one exists."
        assert GroupState({2: "bugs"}).label(2) == "bugs"

    def test_set_annotation_stores_text(self):
        "Proves set_annotation() creates an annotation entry."
        state = GroupState({})
        state.set_annotation(1, "important")
        assert state.annotations[1].text == "important"

    def test_set_annotation_empty_removes_annotation(self):
        "Proves set_annotation('') removes an existing annotation."
        state = GroupState({})
        state.set_annotation(1, "note")
        state.set_annotation(1, "")
        assert 1 not in state.annotations

    def test_set_name_stores_name(self):
        "Proves set_name() records the group name."
        state = GroupState({})
        state.set_name(2, "critical")
        assert state.names[2] == "critical"

    def test_set_name_empty_removes_name(self):
        "Proves set_name('') removes an existing name."
        state = GroupState({2: "critical"})
        state.set_name(2, "")
        assert 2 not in state.names

    def test_reset_clears_names_annotations_and_active_group(self):
        "Proves reset() wipes names, annotations, and resets active to 1."
        state = GroupState({1: "bugs"})
        state.set_annotation(1, "note")
        state.active = 3
        state.reset()
        assert state.names == {} and state.annotations == {} and state.active == 1

    def test_active_setter_rejects_zero(self):
        "Proves setting active_group to 0 raises ValueError."
        with pytest.raises(ValueError):
            GroupState({}).active = 0

    def test_active_setter_rejects_out_of_range(self):
        "Proves setting active_group beyond GROUP_COUNT raises ValueError."
        with pytest.raises(ValueError):
            GroupState({}).active = 10


class TestAppStateValidation:
    def test_invalid_active_group_at_init_raises(self):
        "Proves DocumentModel rejects active_group=0 at construction time."
        with pytest.raises(ValueError):
            DocumentModel(lines=[LineState(text="a")], active_group=0)

    def test_toggle_out_of_bounds_raises(self):
        "Proves toggle_line raises IndexError for an index past the end of lines."
        with pytest.raises(IndexError):
            make_model("a").toggle_line(5)

    def test_set_line_group_out_of_bounds_raises(self):
        "Proves set_line_group raises IndexError for an out-of-range index."
        with pytest.raises(IndexError):
            make_model("a").set_line_group(5, 1)

    def test_set_line_group_invalid_group_raises(self):
        "Proves set_line_group raises ValueError for a group number outside 0-GROUP_COUNT."
        with pytest.raises(ValueError):
            make_model("a").set_line_group(0, 10)


class TestSetLineGroup:
    def test_assigns_group_to_line(self):
        "Proves set_line_group() changes a line's group."
        model = make_model("a", "b")
        model.set_line_group(0, 3)
        assert model.lines[0].group == 3

    def test_clears_group_with_zero(self):
        "Proves set_line_group(idx, 0) removes a line from any group."
        model = make_model("a")
        model.set_line_group(0, 2)
        model.set_line_group(0, 0)
        assert model.lines[0].group == 0


class TestAppStateReset:
    def test_reset_clears_all_line_groups(self):
        "Proves reset() sets every line's group back to 0."
        model = make_model("a", "b", "c")
        model.toggle_line(0)
        model.active_group = 2
        model.toggle_line(2)
        model.reset()
        assert all(line.group == 0 for line in model.lines)

    def test_reset_clears_search_state(self):
        "Proves reset() clears active search indices."
        model = make_model("a")
        model.search.set("foo", [0])
        model.reset()
        assert model.search.indices == []

    def test_reset_clears_range_fill_anchor(self):
        "Proves reset() removes any pending range-fill anchor."
        model = make_model("a")
        model.range_fill.set_anchor(0, 1)
        model.reset()
        assert model.range_fill.anchor is None

    def test_reset_resets_active_group_to_1(self):
        "Proves reset() returns active_group to 1 regardless of prior value."
        model = make_model("a", active_group=3)
        model.reset()
        assert model.active_group == 1
