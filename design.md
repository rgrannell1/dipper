# Output Format Design

## In-band delimiter

Clipper embeds annotation markers directly into the original source text. The markers must be distinguishable from source content — a collision would make the output unparseable and corrupt the original text on round-trip.

### Constraints

- The source file can be any text: code, prose, data. No assumptions about content.
- Markers must be identifiable by a simple regex; no probabilistic or context-dependent parsing.
- The format should be human-readable as well as machine-readable.
- The delimiter must not require scanning source content before writing (unlike MIME boundaries).

### Rejected options

| Candidate | Problem |
|-----------|---------|
| `^` underline + `COMMENT_GROUP_N` | `^` appears in Python format strings, shell `${var^}`, math; `COMMENT_GROUP_` is plain English |
| `~~~...~~~` separator | appears in markdown strikethrough and shell heredocs |
| `#`, `//`, `--` prefixes | comment syntax in dozens of languages |
| `>` prefix | email quoting convention; common in markdown blockquotes |
| Random MIME-style boundary | non-deterministic; makes output format unstable across runs |

### Chosen delimiter: `%%clipper:`

All clipper-generated lines are prefixed with `%%clipper:`. The full line format is:

```
%%clipper:<type>[:<data>]%%
```

`%%` at line-start is not valid syntax in any common language and does not appear in ordinary prose. The `clipper:` namespace makes provenance clear and the output grep-friendly.

### Output format

```
original line of code here
%%clipper:mark:1:1%% ^^^^^^^^^^^^^^^^^^^
next line

%%clipper:separator%%

%%clipper:group:1%%
Annotation text for group 1

%%clipper:group:2%%
Annotation text for group 2
```

**Line types:**

| Line | Meaning |
|------|---------|
| `%%clipper:mark:N:L%%` | Follows a selected line; `N` is the group number, `L` is the 1-based line number of the selected source line. The `^` characters after the prefix are a visual underline and are not parsed. |
| `%%clipper:separator%%` | Divides the annotated body from the summary section. |
| `%%clipper:group:N:RANGES%%` | Group label in the summary; `N` is the group number, `RANGES` is a comma-separated list of 1-based line ranges covering every selected line in the group. The next non-empty line after the header is the annotation text. |

### Line range encoding

All line numbers selected into a group are collected, sorted, and compressed into a minimal set of contiguous ranges before being written into the `%%clipper:group%%` line. A run of consecutive line numbers is expressed as `START-END`; a single isolated line is expressed as `L`. Multiple ranges are joined with `,` and no spaces.

Examples:

| Selected lines | Encoded ranges |
|---|---|
| 5 | `5` |
| 3, 4, 5 | `3-5` |
| 3, 4, 5, 10, 11, 20 | `3-5,10-11,20` |
| 1, 3, 5, 7 | `1,3,5,7` |

This gives a downstream consumer the complete set of relevant locations without requiring it to scan the body for `%%clipper:mark%%` lines.

### Machine-readable pattern

All clipper-generated lines match:

```
^%%clipper:[^%]+%%
```

This is sufficient to strip all markers and recover the original source.

---

## XDG config file

Clipper reads defaults from `$XDG_CONFIG_HOME/clipper/config` (falling back to `~/.config/clipper/config` when `XDG_CONFIG_HOME` is unset). The file stores persistent defaults for CLI flags so that per-user or per-workflow preferences do not need to be repeated on every invocation.

### Format

The config file has two kinds of lines:

**Flag lines** — one CLI flag per line, same syntax as the CLI. Blank lines and lines beginning with `#` are ignored.

**Preset lines** — named group lists in the form `name: group1,group2,...`. Presets are referenced by `--preset NAME` on the CLI and expand to the equivalent `--groups` value.

Example:

```
# default prompt for code review workflow
--prompt code review

# named group presets
testing: bug,critical,security
reading: quote
priorities: p1,p2,p3,p4,p5
cr: bug,critical,minor,praise,question
```

Dipper ships with the following built-in presets that are available without any config file:

| Preset | Groups |
|---|---|
| `priorities` | `p1,p2,p3,p4,p5` |
| `cr` | `bug,critical,minor,praise,question` |

User-defined presets in the config file take precedence over built-in presets with the same name.

CLI flags always take precedence over values in the config file. When the same flag appears in both, the CLI value wins. Flags that accept a list (e.g. `--groups`) are not merged; the CLI value replaces the config value entirely.

### Constraints

- The config file must not be required. Clipper runs without it.
- Parsing must use the same argument parser as the CLI so that config values go through identical validation.
- The config path must respect `XDG_CONFIG_HOME`; hard-coding `~/.config` is not acceptable.

---

## `--preset <name>`

`--preset` selects a named group list from the config file, expanding it as if `--groups` had been passed with that CSV. It exists so that a frequently-used group set does not need to be retyped on every invocation.

### Motivation

A reviewer running the same workflow repeatedly (e.g. `testing: bug,critical,security`) should not have to pass `--groups bug,critical,security` every time. Defining the preset once in the config file and referencing it by name keeps invocations short and consistent.

### Behaviour

`--preset NAME` looks up `NAME` in the preset lines of the config file and uses its CSV as the value of `--groups`. If `--groups` is also passed explicitly on the CLI, the CLI value wins and `--preset` is ignored. If `NAME` does not exist in the config file, dipper exits with an error.

### Constraints

- Preset names are case-sensitive.
- A preset line in the config must follow the form `name: group1,group2,...` — no leading `--`.
- `--preset` and `--groups` are mutually exclusive when both are passed on the CLI; `--groups` takes precedence.

---

## Output mode flags: `--summary` and `--lines`

By default dipper writes the full annotated file — all source lines, inline marks, separator, and summary block. Two flags narrow the output to relevant context only, for use in pipelines and LLM prompts where the full file is noise.

### `--summary`

Writes only the summary block: one entry per group, containing the group header (with line ranges) and its annotation text. The source body and separator are omitted.

```
%%dipper:group:1:3-5,10%%
This block handles auth token refresh.

%%dipper:group:2:22%%
Possible null dereference here.
```

Use when the consumer needs the annotations and locations but not the source lines themselves — e.g. generating a structured report or feeding findings into another tool.

### `--lines`

Writes only the selected source lines, each immediately followed by its mark line. Unselected lines are omitted. The separator and summary block are omitted.

```
token = generate_token(user)
%%dipper:mark:1:3%% ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
result = cache.get(key)
%%dipper:mark:2:22%% ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

Use when the consumer needs the exact source text of the findings with their group and position, but not the surrounding context or annotations — e.g. feeding selected lines into a code review prompt.

### Combining the flags

The flags are additive. Each one independently includes its section in the output; passing both gives selected lines with marks followed by the summary block, still omitting unselected source lines and the full-file body.

| Flags | Output |
|---|---|
| neither | full annotated file (default) |
| `--lines` | selected lines + marks only |
| `--summary` | summary block only |
| `--lines --summary` | selected lines + marks, then summary block |

### Constraints

- Neither flag affects the TUI — output mode is applied at write time when `w` is pressed.
- Both flags still respect `--groups`, `--header-group`, and all other selection flags.
- If no lines are selected, both flags produce empty output.
