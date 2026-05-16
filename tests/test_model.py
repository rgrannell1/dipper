import pytest
from dipper.model import DocumentModel
from dipper.state import GroupAnnotation, LineState


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
        assert model.selected_groups() == set()

    def test_reports_groups_in_use(self):
        model = make_model("a", "b", "c")
        model.toggle_line(0)
        model.active_group = 2
        model.toggle_line(2)
        assert model.selected_groups() == {1, 2}

    def test_cleared_line_removed_from_groups(self):
        model = make_model("a")
        model.toggle_line(0)
        model.toggle_line(0)
        assert model.selected_groups() == set()


class TestGroupLabel:
    def test_default_label(self):
        model = make_model("a")
        assert model.group_label(3) == "group 3"

    def test_named_group_label(self):
        model = make_model("a")
        model.group_names[1] = "bugs"
        assert model.group_label(1) == "bugs"


class TestNearestAnnotatedGroup:
    def test_none_when_no_annotations(self):
        model = make_model("a", "b")
        model.toggle_line(0)
        assert model.nearest_annotated_group(0) is None

    def test_returns_group_of_nearest_annotated_line(self):
        model = make_model("a", "b", "c", "d")
        model.toggle_line(0)
        model.set_annotation(1, "note")
        model.active_group = 2
        model.toggle_line(3)
        model.set_annotation(2, "other")
        # cursor at line 1: closer to line 0 (group 1) than line 3 (group 2)
        assert model.nearest_annotated_group(1) == 1
        # cursor at line 3: closer to line 3 (group 2)
        assert model.nearest_annotated_group(3) == 2

    def test_ignores_selected_lines_without_annotation(self):
        model = make_model("a", "b")
        model.toggle_line(0)
        # group 1 selected but not annotated
        assert model.nearest_annotated_group(0) is None
