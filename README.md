

# Dipper

[![CI](https://github.com/rgrannell1/dipper/actions/workflows/ci.yml/badge.svg)](https://github.com/rgrannell1/dipper/actions/workflows/ci.yml)

Interactive file annotation.

![Demo](demo.gif)

## Name

Dipper is named after a common river-bird here in Ireland. It was named this for no reason at all, but I suppose you could find some metaphoric connection to dipping into streams selectively.

## Installation

Clone the repository and install with `uv`:

```sh
git clone https://github.com/rgrannell1/dipper.git
cd dipper
uv sync
uv tool install .
```

## Uses

Dipper is useful for quickly annotating code bases and text documents with whatever groupings and note you'd like. It can add:

- TODOs / fixmes / refactor annotations
- Complaints about complexity
- Notes like `citation needed` in a knowledge-base

There are some preset groupings:

- `cr`; `bug`, `critical`, `minor`, `question`, `note`
- `priorities`: `p1` ... `p5`

## Examples

```sh
dipper <file> --preset cr
dipper --groups "todo,bug" < file
```

```sh
dipper <file> --lines --summary --output <somewhere custom>
```

**Save and resume a session**

Use `--output` to write an annotations file (optionally add your own named)
```sh
dipper src/app.py --preset cr --output
# writes src/app.py.annotations
```

edit with `--load`

```sh
dipper src/app.py --load src/app.py.annotations
```

**Batch annotation**

`--files` annotates every file matching a glob that does not yet have a `.annotations` file.

```sh
dipper --files 'src/**/*.py' --preset cr --output
```

Each file is opened in turn; finished files are skipped on re-runs.

## Output Format

All metadata lines are prefixed with `%%dipper:`

**Structure**

```
%%dipper:meta:filepath:{path}%%
{source line 1}
{source line 2}
%%dipper:mark:{group}:{line}%% {underline}
...

%%dipper:separator%%

%%dipper:group:{group}:{ranges}%% {name}
{annotation text}

```

Mark lines immediately follow each annotated source line. 

Mark lines follow each annotated source-code line.
The separator divides the document body from our group summarise. Headers are followed by a text command.

**Fields**

| Token | Meaning |
|---|---|
| `{path}` | path of the source file |
| `{group}` | integer 1–9 identifying the group (common category of comment) |
| `{line}` | line numbere |
| `{underline}` | `^` pointing to the line above |
| `{ranges}` | run-length encoded line numbers, e.g. `1-3,7,12-15` |
| `{name}` | group label from `--groups` / `--preset`, if set |

## Yazi Integration

`integrations/yazi/dipper-annotate` is a wrapper script that runs dipper and saves output to `<file>.annotations`.

```sh
cp integrations/yazi/dipper-annotate ~/.local/bin/
```

Then configure yazi to use it as the default opener for text files in `~/.config/yazi/yazi.toml`:

```toml
[opener]
dipper = [
  { run = 'dipper-annotate "$@"', block = true, desc = "Annotate with dipper" }
]

[open]
prepend_rules = [
  { mime = "text/*", use = ["dipper", "edit", "reveal"] },
]
```

Pressing `o` on a text file opens it in dipper. Writes `<file>.annotations` alongside the source.

## Shell Completions

Zsh completions are in `completions/_dipper`. Install with:

```sh
rs install-completions
```

## Licence

Copyright © 2026 Róisín Grannell

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
