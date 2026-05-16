# Dipper — Expectations

Dipper is a terminal TUI for annotating a text file line by line. You tag lines into named colour groups, optionally leave a note per group, then write structured output. The output is consumed by downstream tools (LLMs, scripts) that need to know which lines were flagged and why.

---

## Data model

**Lines** — each source line carries a group number. 0 = unselected. 1–9 = assigned to that group.

**Groups** — each group has:
- a number (1–9), fixed
- an optional name string (e.g. `bug`, `p1`). Falls back to `"group N"` if not set.
- an optional annotation string (free-text note, one per group)

**Active group** — the group that selection operations (`tab`, `f`-fill) write into. Shown prominently in the status bar. Changed by pressing digit keys 1–9.

---

## Invocation

```
dipper [FILE] [--prompt STR] [--header STR] [--groups CSV] [--preset NAME]
              [--lines] [--summary] [--output FILE]
```

- `FILE` — file to annotate. Reads stdin if omitted (and stdin is not a TTY).
- `--prompt STR` — subtitle shown in the Textual header bar.
- `--header STR` — label rendered above the line list inside the TUI.
- `--groups CSV` — comma-separated group names assigned to groups 1, 2, 3, … in order.
- `--preset NAME` — expands to `--groups <csv>` from a named preset. Mutually exclusive with `--groups`; `--groups` wins if both are passed.
- `--lines` — output mode: emit only selected lines with their mark lines.
- `--summary` — output mode: emit only the group summary block.
- `--output FILE` — write output to FILE instead of stdout.

### Built-in presets

| Preset | Groups |
|---|---|
| `priorities` | `p1,p2,p3,p4,p5` |
| `cr` | `bug,critical,minor,praise,question,note` |

User-defined presets in `$XDG_CONFIG_HOME/dipper/config` (falling back to `~/.config/dipper/config`) take precedence over built-ins with the same name. The config file format: one CLI flag per line, or `name: group1,group2,...` for preset lines.

---

## TUI — key bindings

| Key | Action |
|---|---|
| `tab` | Toggle cursor line into/out of active group. If the line is already in a different group, move it to the active group. |
| `1`–`9` | Set active group. Clears any pending range anchor. |
| `f` | First press: place range anchor on cursor line (shown as `◆` in the active group's colour). Second press: fill all lines between anchor and cursor (inclusive) into the active group, then clear the anchor. |
| `n` | Open annotation modal for the active group (or the first used group if active has no lines). Pre-fills with any existing annotation. Submitting empty text deletes the annotation. |
| `r` | Open rename modal for the group nearest the cursor (or the active group if cursor is on an unselected line). |
| `g` / `G` | Jump to first / last line. |
| `/` | Open search bar. Accepts a regex. Highlights all matching lines in the gutter. |
| `>` / `<` | Jump to next / previous search match. |
| `*` | Assign all current search matches to the active group. |
| `:` | Open goto-line bar. Accepts a 1-based line number. |
| `q` | Write output and quit. |
| `escape` | Cancel current modal without saving. |

### Range anchor invariants
- Pressing `f` twice on the same line fills just that one line (degenerate range, not a crash).
- Switching active group (digit key) clears any pending anchor.
- The `◆` indicator uses the colour of the group that was active when the anchor was placed.

---

## TUI — status bar

Bottom bar shows (left to right):

1. `◉ <active-group-name>` — active group dot + name, in that group's colour.
2. `  |  ` separator (only if any lines are assigned).
3. One `●` per group that has at least one line assigned, in each group's colour. These dots are stable — they only reflect assignments, never the active group selection.
4. `  |  /pattern [N/M]` — search indicator if a search is active.
5. `  |  <filename>` — the file being annotated.

---

## TUI — line display

Each line is rendered as:

```
<line-num> <indicator> <syntax-highlighted source text>
```

- **Line number** — right-justified, dim. Bold yellow if the line is a search match.
- **Indicator** — `● ` in the group's colour if assigned; `◆ ` in the anchor group's colour if this is the pending range anchor; `  ` (two spaces) otherwise.
- **Source text** — syntax-highlighted via tree-sitter/Pygments where possible, bold in the group's colour if the line is assigned.

---

## TUI — command palette

Opened with `ctrl+p` (Textual default). Shows all groups that have at least one line assigned, searchable by group number, name, and annotation text. Selecting a group jumps to its first line.

---

## Output format

All dipper-generated lines share the prefix `%%dipper:` and match `^%%dipper:[^%]+%%`.

### Default output (no flags)

Full annotated file: every source line, with a mark line inserted after each selected line, followed by a separator and a summary block.

```
source line here
%%dipper:mark:1:3%% ^^^^^^^^^^^^^^^^^^^
next source line

%%dipper:separator%%

%%dipper:group:1:3,7-9%% bug
Annotation text for group 1

%%dipper:group:2:15%% critical
Annotation text for group 2
```

### `--lines` output

Only selected source lines, each followed by its mark line. Unselected lines, the separator, and the summary are omitted.

### `--summary` output

Only the summary block (group headers + annotations). Source lines and separator are omitted.

### `--lines --summary`

Selected lines with marks, then the summary block. No unselected source lines, no separator.

### Mark line format

```
%%dipper:mark:<group>:<1-based-line-number>%% <underline>
```

The underline is `^` repeated for the width of the source line (minimum 6).

### Group header format

```
%%dipper:group:<group>:<ranges>%% <name-or-empty>
```

`<ranges>` is a comma-separated run-length-encoded list of 1-based line numbers, e.g. `3,7-9,15`. The group name follows the closing `%%` after a space; omitted if the group has no name. The annotation text follows on the next non-empty line.

---

## Syntax highlighting

Dipper attempts to syntax-highlight the source file using Pygments, inferred from the filename extension. Falls back to plain text if the language is unknown or the file has no extension.

---

## Open design questions (snags)

- **#27** — Annotation modal label shows `COMMENT_GROUP_N` placeholder (should show group name). Already partially fixed in modals/annotation.py but not confirmed working.
- **#31** — Two blocks of the same group separated only by blank lines should optionally be treated as one contiguous range in the output.
- **#32** — Pressing `f` twice on the same line crashes the TUI (should be a no-op or single-line fill).
