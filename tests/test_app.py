import pytest
from textual.widgets import Input, Label

from clipper.app import ClipperApp, LineListView
from clipper.constants import CLIPPER_PREFIX, SEPARATOR_LINE


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
            texts = [l.text for l in pilot.app._model.lines]
            assert texts == ["alpha", "beta", "gamma"]

    async def test_default_active_group_is_1(self):
        async with make_app().run_test() as pilot:
            assert pilot.app._model.active_group == 1


class TestTabToggle:
    async def test_tab_selects_line_into_active_group(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            assert pilot.app._model.lines[0].group == 1

    async def test_tab_again_deselects_line(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("tab")
            assert pilot.app._model.lines[0].group == 0

    async def test_tab_on_different_active_group_moves_line(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")       # group 1
            await pilot.press("2")         # switch to group 2
            await pilot.press("tab")       # moves line 0 to group 2
            assert pilot.app._model.lines[0].group == 2


class TestNumberKeys:
    async def test_number_key_changes_active_group(self):
        async with make_app().run_test() as pilot:
            await pilot.press("3")
            assert pilot.app._model.active_group == 3

    async def test_all_digit_keys_accepted(self):
        async with make_app().run_test() as pilot:
            for n in range(1, 10):
                await pilot.press(str(n))
                assert pilot.app._model.active_group == n


class TestWriteAndQuit:
    async def test_w_exits_with_output_string(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("w")
            await pilot.pause()
        assert isinstance(app._return_value, str)

    async def test_w_output_contains_clipper_marker(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("w")
            await pilot.pause()
        assert CLIPPER_PREFIX in app._return_value

    async def test_w_output_contains_separator(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("w")
            await pilot.pause()
        assert SEPARATOR_LINE in app._return_value

    async def test_q_exits_with_no_output(self):
        app = make_app()
        async with app.run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("q")
            await pilot.pause()
        assert app._return_value is None


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
            ann = pilot.app._model.annotations.get(1)
            assert ann is not None
            assert ann.text == "important fix"

    async def test_escape_dismisses_without_setting_annotation(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("n")
            await pilot.pause(delay=0.1)
            await pilot.press("escape")
            await pilot.pause(delay=0.1)
            assert pilot.app._model.annotations.get(1) is None
            assert len(pilot.app.screen_stack) == 1


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
            assert pilot.app._model.group_names.get(1) == "bugs"

    async def test_rename_escape_leaves_name_unchanged(self):
        async with make_app().run_test() as pilot:
            await pilot.press("tab")
            await pilot.press("r")
            await pilot.pause(delay=0.1)
            await pilot.press("escape")
            await pilot.pause(delay=0.1)
            assert pilot.app._model.group_names.get(1) is None


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
            assert pilot.app._model.group_names[1] == "bugs"
            assert pilot.app._model.group_names[2] == "features"

    async def test_group_label_uses_prepopulated_name(self):
        async with make_app(group_names={1: "todo"}).run_test() as pilot:
            assert pilot.app._model.group_label(1) == "todo"
