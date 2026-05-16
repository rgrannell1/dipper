import re
import tempfile
from pathlib import Path

import pytest
from textual.widgets import Input, Label

from dipper.app import ClipperApp, LineListView, run
from dipper.constants import DIPPER_PREFIX, SEPARATOR_LINE


SOURCE = "alpha\nbeta\ngamma"


def make_app(**kwargs) -> ClipperApp:
    return ClipperApp(SOURCE, None, **kwargs)


class TestInitialState:
    async def test_list_has_correct_item_count(self):
        async with make_app().run_test() as pilot:
            lv = pilot.app.query_one(LineListView)
            assert len(lv._nodes) == 3

    async def test_model_lines_match_source(self):
        async with make_app().run_test() as pilot:
            texts = [line.text for line in pilot.app._model.lines]
            assert texts == ["alpha", "beta", "gamma"]

    async def test_default_active_group_is_1(self):
        async with make_app().run_test() as pilot:
            assert pilot.app._model.active_group == 1


class TestTabToggle:
    async def test_tab_selects_line_into_active_group(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            model = pilot.app._model
            assert model.lines[0].group == 1

    async def test_tab_again_deselects_line(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("tab")
            model = pilot.app._model
            assert model.lines[0].group == 0

    async def test_tab_on_different_active_group_moves_line(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")       # group 1
            await pilot.press("2")         # switch to group 2
            await pilot.press("tab")       # moves line 0 to group 2
            model = pilot.app._model
            assert model.lines[0].group == 2


class TestNumberKeys:
    async def test_number_key_changes_active_group(self):
        async with make_app().run_test() as pilot:
            await pilot.press("3")
            assert pilot.app._model.active_group == 3

    async def test_all_digit_keys_accepted(self):
        async with make_app().run_test() as pilot:
            for num in range(1, 10):
                await pilot.press(str(num))
                assert pilot.app._model.active_group == num


class TestReset:
    async def test_x_clears_all_line_selections(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("down")
            await pilot.press("tab")
            await pilot.press("x")
            groups = [line.group for line in pilot.app._model.lines]
            assert groups == [0, 0, 0]

    async def test_x_resets_active_group_to_1(self):
        async with make_app().run_test() as pilot:
            await pilot.press("3")
            await pilot.press("x")
            assert pilot.app._model.active_group == 1

    async def test_x_clears_annotations_and_group_names(self):
        async with make_app().run_test() as pilot:
            model = pilot.app._model
            model.set_annotation(1, "note")
            model.set_group_name(1, "bugs")
            await pilot.press("x")
            assert model.groups.annotations == {}
            assert model.groups.names == {}

    async def test_x_clears_range_anchor(self):
        async with make_app().run_test() as pilot:
            model = pilot.app._model
            model.set_range_anchor(0)
            await pilot.press("x")
            assert model.range_fill.anchor is None

    async def test_x_clears_search_state(self):
        async with make_app().run_test() as pilot:
            model = pilot.app._model
            model.set_search("alpha", [0])
            await pilot.press("x")
            assert model.search.pattern == ""
            assert model.search.indices == []


class TestGroupsOverview:
    async def test_o_opens_groups_modal(self):
        from dipper.modals.groups import GroupsModal
        async with make_app().run_test() as pilot:
            await pilot.press("o")
            await pilot.pause()
            assert isinstance(pilot.app.screen, GroupsModal)

    async def test_modal_shows_all_nine_groups(self):
        from dipper.modals.groups import GroupsModal
        from textual.widgets import ListView
        async with make_app().run_test() as pilot:
            await pilot.press("o")
            await pilot.pause()
            modal = pilot.app.screen
            lv = modal.query_one(ListView)
            assert len(lv._nodes) == 9

    async def test_x_in_modal_clears_focused_group_name(self):
        async with make_app().run_test() as pilot:
            model = pilot.app._model
            model.set_group_name(1, "bugs")
            await pilot.press("o")
            await pilot.pause()
            await pilot.press("x")
            assert model.groups.names.get(1, "") == ""

    async def test_x_in_modal_does_not_clear_other_groups(self):
        async with make_app().run_test() as pilot:
            model = pilot.app._model
            model.set_group_name(1, "bugs")
            model.set_group_name(2, "notes")
            await pilot.press("o")
            await pilot.pause()
            await pilot.press("x")
            assert model.groups.names.get(2, "") == "notes"

    async def test_escape_closes_modal(self):
        from dipper.modals.groups import GroupsModal
        async with make_app().run_test() as pilot:
            await pilot.press("o")
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(pilot.app.screen, GroupsModal)


class TestWriteAndQuit:
    async def test_q_exits_with_output_string(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        assert isinstance(app._return_value, str)

    async def test_q_output_contains_clipper_marker(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        assert DIPPER_PREFIX in app._return_value

    async def test_q_output_contains_separator(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        assert SEPARATOR_LINE in app._return_value


class TestAnnotationModal:
    async def test_n_opens_modal_when_line_selected(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            assert len(pilot.app.screen_stack) == 2

    async def test_n_does_nothing_with_no_selection(self):
        async with make_app().run_test() as pilot:
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            assert len(pilot.app.screen_stack) == 1

    async def test_typing_and_enter_sets_annotation(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            for ch in "important fix":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(delay=0.1)
            model = pilot.app._model
            ann = model.groups.annotations.get(1)
            assert ann is not None
            assert ann.text == "important fix"

    async def test_escape_dismisses_without_setting_annotation(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            await pilot.press("escape")
            await pilot.pause(delay=0.1)
            model = pilot.app._model
            assert model.groups.annotations.get(1) is None
            assert len(pilot.app.screen_stack) == 1

    async def test_modal_label_shows_group_name(self):
        async with make_app(group_names={1: "bugs"}).run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            label = pilot.app.screen.query_one("#modal-label", Label)
            assert "bugs" in label.render_line(0).text

    async def test_modal_label_falls_back_to_group_number(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            label = pilot.app.screen.query_one("#modal-label", Label)
            assert "group 1" in label.render_line(0).text


class TestRenameModal:
    async def test_r_opens_rename_modal(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("r")
            await pilot.pause(delay=0.1)
            assert len(pilot.app.screen_stack) == 2

    async def test_rename_sets_group_name(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("r")
            await pilot.pause(delay=0.1)
            for ch in "bugs":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(delay=0.1)
            group_names = pilot.app._model.groups.names
            assert group_names.get(1) == "bugs"

    async def test_rename_escape_leaves_name_unchanged(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("r")
            await pilot.pause(delay=0.1)
            await pilot.press("escape")
            await pilot.pause(delay=0.1)
            group_names = pilot.app._model.groups.names
            assert group_names.get(1) is None


class TestPromptFlag:
    async def test_prompt_sets_subtitle(self):
        async with make_app(prompt="review pass").run_test() as pilot:
            assert pilot.app.sub_title == "review pass"

    async def test_no_prompt_leaves_subtitle_empty(self):
        async with make_app().run_test() as pilot:
            assert pilot.app.sub_title == ""


class TestHeaderFlag:
    async def test_header_label_rendered(self):
        async with make_app(header="Select lines to clip").run_test() as pilot:
            label = pilot.app.query_one("#header-label", Label)
            assert "Select lines to clip" in label.content

    async def test_no_header_label_absent(self):
        async with make_app().run_test() as pilot:
            assert not pilot.app.query("#header-label")


class TestGroupsFlag:
    async def test_groups_prepopulate_names(self):
        async with make_app(group_names={1: "bugs", 2: "features"}).run_test() as pilot:
            group_names = pilot.app._model.groups.names
            assert group_names[1] == "bugs"
            assert group_names[2] == "features"

    async def test_group_label_uses_prepopulated_name(self):
        async with make_app(group_names={1: "todo"}).run_test() as pilot:
            model = pilot.app._model
            assert model.group_label(1) == "todo"


class TestWorkflow:
    async def test_single_group_write_contains_mark_with_line_number(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")  # select line 1
            await pilot.press("q")
            await pilot.pause()
        assert "%%dipper:mark:1:1%%" in app._return_value

    async def test_mark_line_number_reflects_position_in_source(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("down")
            await pilot.press("down")
            await pilot.press("tab")  # select line 3
            await pilot.press("q")
            await pilot.pause()
        assert "%%dipper:mark:1:3%%" in app._return_value

    async def test_group_summary_contains_line_range(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        assert "%%dipper:group:1:1%%" in app._return_value

    async def test_two_groups_both_appear_in_summary(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")       # line 1 → group 1
            await pilot.press("2")
            await pilot.press("down")
            await pilot.press("tab")       # line 2 → group 2
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        assert "%%dipper:group:1:" in output
        assert "%%dipper:group:2:" in output
        assert output.index("%%dipper:group:1:") < output.index("%%dipper:group:2:")

    async def test_rename_group_name_appears_in_output(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("r")
            await pilot.pause(delay=0.1)
            for ch in "bugs":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(delay=0.1)
            await pilot.press("q")
            await pilot.pause()
        assert "bugs" in app._return_value

    async def test_annotation_appears_after_group_header(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            for ch in "important note":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(delay=0.1)
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        header_pos = output.index("%%dipper:group:1:")
        note_pos = output.index("important note")
        assert note_pos > header_pos

    async def test_full_workflow_output_matches_spec(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")           # select line 1 into group 1
            await pilot.press("r")
            await pilot.pause(delay=0.1)
            for ch in "findings":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(delay=0.1)
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            for ch in "check this":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(delay=0.1)
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        assert "%%dipper:mark:1:1%%" in output
        assert SEPARATOR_LINE in output
        assert "%%dipper:group:1:1%% findings" in output
        assert "check this" in output

    async def test_output_lines_mode_omits_summary(self):
        app = make_app(output_lines=True)
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        assert "%%dipper:mark:1:1%%" in output
        assert SEPARATOR_LINE not in output
        assert "%%dipper:group:" not in output

    async def test_output_lines_mode_omits_unselected_source_lines(self):
        app = make_app(output_lines=True)
        async with app.run_test() as pilot:
            await pilot.press("down")
            await pilot.press("tab")   # select line 2 only
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        assert "alpha" not in output   # line 1 not selected
        assert "beta" in output        # line 2 selected

    async def test_output_summary_mode_omits_source_lines(self):
        app = make_app(output_summary=True)
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            for ch in "my note":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(delay=0.1)
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        assert "%%dipper:group:1:" in output
        assert "my note" in output
        assert "alpha" not in output
        assert SEPARATOR_LINE not in output


class TestOutputPath:
    """--output FILE must write clean annotation data, not terminal screen buffer."""

    async def test_output_file_contains_dipper_markers(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            path = tmp.name
        try:
            app = ClipperApp(SOURCE, None)
            async with app.run_test() as pilot:
                await pilot.press("tab")
                await pilot.press("q")
                await pilot.pause()
            result = app._return_value
            Path(path).write_text(result)
            content = Path(path).read_text()
            assert DIPPER_PREFIX in content
        finally:
            Path(path).unlink(missing_ok=True)

    async def test_output_file_contains_no_ansi_escapes(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            path = tmp.name
        try:
            app = ClipperApp(SOURCE, None)
            async with app.run_test() as pilot:
                await pilot.press("tab")
                await pilot.press("q")
                await pilot.pause()
            result = app._return_value
            Path(path).write_text(result)
            content = Path(path).read_text()
            assert not re.search(r"\x1b\[", content), "output file contains ANSI escape sequences from terminal buffer"
        finally:
            Path(path).unlink(missing_ok=True)

    async def test_output_file_contains_source_text(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            path = tmp.name
        try:
            app = ClipperApp(SOURCE, None)
            async with app.run_test() as pilot:
                await pilot.press("tab")
                await pilot.press("q")
                await pilot.pause()
            result = app._return_value
            Path(path).write_text(result)
            content = Path(path).read_text()
            assert "alpha" in content
        finally:
            Path(path).unlink(missing_ok=True)


class TestRangeFill:
    async def test_f_sets_anchor_on_current_line(self):
        async with make_app().run_test() as pilot:
            await pilot.press("f")
            assert pilot.app._model.range_fill.anchor == 0

    async def test_f_twice_fills_range_into_active_group(self):
        async with make_app().run_test() as pilot:
            await pilot.press("f")
            await pilot.press("down")
            await pilot.press("down")
            await pilot.press("f")
            model = pilot.app._model
            assert model.lines[0].group == 1
            assert model.lines[1].group == 1
            assert model.lines[2].group == 1

    async def test_f_twice_clears_anchor(self):
        async with make_app().run_test() as pilot:
            await pilot.press("f")
            await pilot.press("down")
            await pilot.press("f")
            assert pilot.app._model.range_fill.anchor is None

    async def test_f_fill_respects_active_group(self):
        async with make_app().run_test() as pilot:
            await pilot.press("2")
            await pilot.press("f")
            await pilot.press("down")
            await pilot.press("f")
            model = pilot.app._model
            assert model.lines[0].group == 2
            assert model.lines[1].group == 2

    async def test_f_fill_reversed_range(self):
        async with make_app().run_test() as pilot:
            await pilot.press("down")
            await pilot.press("down")
            await pilot.press("f")
            await pilot.press("up")
            await pilot.press("up")
            await pilot.press("f")
            model = pilot.app._model
            assert model.lines[0].group == 1
            assert model.lines[1].group == 1
            assert model.lines[2].group == 1

    async def test_switching_group_clears_anchor(self):
        async with make_app().run_test() as pilot:
            await pilot.press("f")
            await pilot.press("2")
            assert pilot.app._model.range_fill.anchor is None


class TestRenderedUI:
    async def test_status_bar_shows_dot_after_selection(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.pause(delay=0.1)
            status = pilot.app.query_one("#status", Label)
            text = status.render_line(0).text
            assert "●" in text or "◉" in text

    async def test_status_bar_shows_group_name_after_rename(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("r")
            await pilot.pause(delay=0.1)
            for ch in "findings":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(delay=0.1)
            status = pilot.app.query_one("#status", Label)
            text = status.render_line(0).text
            assert "findings" in text

    async def test_status_bar_shows_filename(self):
        async with make_app().run_test() as pilot:
            status = pilot.app.query_one("#status", Label)
            text = status.render_line(0).text
            assert "<stdin>" in text


class TestMetadataFilepath:
    async def test_filepath_metadata_line_present_when_filename_given(self):
        app = ClipperApp(SOURCE, "some/file.py")
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        assert output.startswith("%%dipper:meta:filepath:some/file.py%%")

    async def test_filepath_metadata_line_absent_when_no_filename(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        assert "%%dipper:meta:filepath:" not in output

    async def test_filepath_metadata_first_line_in_lines_mode(self):
        app = ClipperApp(SOURCE, "src/main.py", output_lines=True)
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        assert output.startswith("%%dipper:meta:filepath:src/main.py%%")

    async def test_filepath_metadata_first_line_in_summary_mode(self):
        app = ClipperApp(SOURCE, "src/main.py", output_summary=True)
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        output = app._return_value
        assert output.startswith("%%dipper:meta:filepath:src/main.py%%")
