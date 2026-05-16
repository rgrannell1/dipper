## Snag List

- [x] #1 `fixed` — Blank lines in the source file are not rendered in the TUI; whitespace-only lines are missing from the view.
- [x] #2 `fixed` — Scrolling the cursor past the bottom of the viewport does not scroll the view; the page stays still while the cursor moves off-screen.
- [x] #3 `fixed` — Line numbers are not displayed.
- [x] #4 `fixed` — Mouse clicks do not move the cursor or select lines; Textual supports mouse input but it is not wired up.
- [x] #5 `fixed` — The cursor highlight smears across the full terminal width on every line; short and blank lines show a padded reverse block rather than a line highlight.
- [x] #6 `fixed` — The custom ScrollView double-renders content after scrolling; the right half of the viewport shows a ghost copy of the content.
- [x] #7 `fixed` — Two help bars appear at the bottom: the custom status label repeats key hints already shown in the Textual Footer.
- [x] #8 `fixed` — The enter/annotate hint appears in the status bar but not the footer alongside the other key bindings.
- [x] #9 `fixed` — Pressing enter does nothing; binding changed to n (note).
- [x] #10 `fixed` — There is no way to see an existing note in the editor; notes are invisible once added.
- [x] #11 `fixed` — There is no way to delete a note; submitting an empty annotation is a no-op rather than a deletion.
- [x] #12 `fixed` — There is no visual cue that pressing n on a group with an existing note will open it for editing.
- [x] #13 `fixed` — The app crashes immediately on launch with NoMatches; _status_text queries LineListView before it is mounted during compose.
- [x] #14 `fixed` — Comment groups cannot be renamed; they are always displayed as "group N" with no way to assign a meaningful label.
- [x] #15 `fixed` — The status bar "Group 1 | Active: 1" section is not useful; needs redesign.
- [x] #16 `fixed` — Group colours do not render in the status bar; dots appear but are unstyled.
- [x] #17 `fixed` — The rename action targets the active group rather than the group nearest the cursor.
- [x] #18 `fixed` — The rename modal label redundantly shows "Rename group 1".
- [x] #19 `fixed` — Group names in the status bar are unstable; they change as the cursor moves because nearest_annotated_group only tracks groups with notes, so renamed groups without notes are ignored, and the rename action targets the wrong group.
- [x] #20 `fixed` — Pressing 1–9 to change the active group does nothing; ListView consumed digit keys before the handler could fire.
- [x] #21 `fixed` — Command palette shows no results on an empty query; groups only appear after typing.
- [x] #22 `fixed` — Group commands have no discoverable prefix; typing "group" does not surface them.
- [x] #23 `fixed` — `:` goto-line command is not discoverable; it does not appear in the command palette.
- [x] #24 `fixed` — `>` (next match) and `<` (prev match) do not work after a `/` search.
- [ ] #27 `open` — The annotation modal shows `COMMENT_GROUP_N` instead of the group's name (e.g. `p1`, `bug`). No test covers the modal label text.
- [x] #26 `fixed` — There is no way to quickly assign a range of lines to a group; lines must be selected one at a time with tab.
  - **Design:** press `f` to place a range anchor on the current line (shown with a distinct symbol); navigate to another line; press `f` again to fill all lines between the two anchors into the active group.
- [x] #28 `fixed` — Pressing digit keys (1–9) to switch the active group is flaky; the active group does not reliably change.
- [x] #29 `fixed` — Pressing digit n to set the active group does not show group n's colour indicator in the status bar unless lines are already assigned to that group; the active group is invisible until used.
- [x] #30 `fixed` — Switching to a different group while a range anchor is set does not clear the anchor; the stale anchor marker (◆) remains visible and the fill will use the wrong group.
- [ ] #25 `wontfix` — `--preset priorities` only shows group 1 labelled `p1`; groups p2–p5 are missing. Could not reproduce.
- [ ] #31 `open` — Two blocks of the same group separated only by blank lines are not treated as contiguous in the output; they produce separate line ranges instead of one spanning range.
- [ ] #32 `open` — Pressing `f` twice on the same line crashes the TUI.

## Passing

- `--preset cr` — built-in code review preset loads groups bug, critical, minor, praise, question correctly.
- `--preset priorities` — built-in priorities preset exists alongside cr.

- `g` / `G` — jump to first/last line works correctly.
- `/` search — highlights matches correctly.
- `--preset` — named group presets load from config file and appear correctly in the TUI and output.
- `--lines` — output contains only selected lines with marks; no separator or summary.
- `--summary` — output contains only group headers and annotations; no source lines.
