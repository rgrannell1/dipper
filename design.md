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
| `%%clipper:group:N%%` | Group label in the summary; the next non-empty line is the annotation text. |

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

One flag per line, using the same syntax as the CLI. Blank lines and lines beginning with `#` are ignored. Example:

```
# default group names for code review workflow
--groups findings,context,questions
--header-group findings
--prompt code review
```

CLI flags always take precedence over values in the config file. When the same flag appears in both, the CLI value wins. Flags that accept a list (e.g. `--groups`) are not merged; the CLI value replaces the config value entirely.

### Constraints

- The config file must not be required. Clipper runs without it.
- Parsing must use the same argument parser as the CLI so that config values go through identical validation.
- The config path must respect `XDG_CONFIG_HOME`; hard-coding `~/.config` is not acceptable.

---

## `--header-group <name>`

`--header-group` designates one named group as the *header group*. Lines assigned to the header group are rendered as section dividers in the output rather than as annotated source lines. The header group does not appear in the summary section.

### Motivation

When annotating a long file for a structured review, the reviewer may want to label sections (e.g. "Auth flow", "Error handling") without those label lines being treated as findings. The header group provides this without requiring a separate pass or a second tool.

### Output behaviour

A line in the header group produces a `%%clipper:header:N:L%%` marker instead of a `%%clipper:mark:N:L%%` marker. Downstream tools can use this to render the line as a heading rather than an annotated finding.

```
def authenticate(user, password):
%%clipper:header:1:1%% ── Auth flow ────────────────────────
    token = generate_token(user)
%%clipper:mark:2:3%% ^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

The header group is excluded from the summary block. Its lines do not receive an annotation prompt in the TUI.

### Constraints

- The value passed to `--header-group` is a group name, not a number. It must match a name set via `--groups` or assigned interactively. If no group with that name exists at write time, the flag has no effect.
- Only one group may be designated as the header group.
- Header lines still appear inline in the body in their original position; they are not moved or hoisted.
