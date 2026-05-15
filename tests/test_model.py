import pytest
from clipper.model import DocumentModel, GroupAnnotation, LineState


def make_model(*texts: str, active_group: int = 1) -> DocumentModel:
    return DocumentModel(
        lines=[LineState(text=t) for t in texts],
        active_group=active_group,
    )


class TestToggleLine:
    def test_unselected_line_joins_active_group(self):
        m = make_model("a", "b")
        m.toggle_line(0)
        assert m.lines[0].group == 1

    def test_toggle_same_group_clears_line(self):
        m = make_model("a")
        m.toggle_line(0)
        m.toggle_line(0)
        assert m.lines[0].group == 0

    def test_toggle_different_group_moves_line(self):
        m = make_model("a", active_group=1)
        m.toggle_line(0)
        m.active_group = 2
        m.toggle_line(0)
        assert m.lines[0].group == 2

    def test_other_lines_unaffected(self):
        m = make_model("a", "b", "c")
        m.toggle_line(1)
        assert m.lines[0].group == 0
        assert m.lines[2].group == 0


class TestSelectedGroups:
    def test_empty_model_has_no_groups(self):
        m = make_model("a", "b")
        assert m.selected_groups() == set()

    def test_reports_groups_in_use(self):
        m = make_model("a", "b", "c")
        m.toggle_line(0)
        m.active_group = 2
        m.toggle_line(2)
        assert m.selected_groups() == {1, 2}

    def test_cleared_line_removed_from_groups(self):
        m = make_model("a")
        m.toggle_line(0)
        m.toggle_line(0)
        assert m.selected_groups() == set()


class TestGroupLabel:
    def test_default_label(self):
        m = make_model("a")
        assert m.group_label(3) == "group 3"

    def test_named_group_label(self):
        m = make_model("a")
        m.group_names[1] = "bugs"
        assert m.group_label(1) == "bugs"


class TestNearestAnnotatedGroup:
    def test_none_when_no_annotations(self):
        m = make_model("a", "b")
        m.toggle_line(0)
        assert m.nearest_annotated_group(0) is None

    def test_returns_group_of_nearest_annotated_line(self):
        m = make_model("a", "b", "c", "d")
        m.toggle_line(0)
        m.set_annotation(1, "note")
        m.active_group = 2
        m.toggle_line(3)
        m.set_annotation(2, "other")
        # cursor at line 1: closer to line 0 (group 1) than line 3 (group 2)
        assert m.nearest_annotated_group(1) == 1
        # cursor at line 3: closer to line 3 (group 2)
        assert m.nearest_annotated_group(3) == 2

    def test_ignores_selected_lines_without_annotation(self):
        m = make_model("a", "b")
        m.toggle_line(0)
        # group 1 selected but not annotated
        assert m.nearest_annotated_group(0) is None
