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
%%clipper:mark:1%% ^^^^^^^^^^^^^^^^^^^
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
| `%%clipper:mark:N%%` | Follows a selected line; `N` is the group number. The `^` characters after the prefix are a visual underline and are not parsed. |
| `%%clipper:separator%%` | Divides the annotated body from the summary section. |
| `%%clipper:group:N%%` | Group label in the summary; the next non-empty line is the annotation text. |

### Machine-readable pattern

All clipper-generated lines match:

```
^%%clipper:[^%]+%%
```

This is sufficient to strip all markers and recover the original source.
