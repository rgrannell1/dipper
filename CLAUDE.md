# dipper

## Testing

To open a live test window (dipper editing its own source):

```
kitty --directory /home/rg/Code/dipper /home/rg/Code/dipper/.venv/bin/python3 -m dipper dipper/app.py &
```

Or via the popup skill: `/popup dipper dipper/app.py`

Run the test suite:

```
/home/rg/Code/dipper/.venv/bin/python3 -m pytest tests/test_app.py -x -q
```

## Linting

Run all lint checks:

```
uv run ruff check dipper/
python3 /home/rg/Agents/skills/rg-pylint/scripts/private_methods.py dipper/*.py
python3 /home/rg/Agents/skills/rg-pylint/scripts/single_letter_vars.py dipper/*.py
python3 /home/rg/Agents/skills/rg-pylint/scripts/line_complexity.py dipper/*.py
```

## Code conventions

- **No private methods or functions.** Do not prefix any `def` with `_`. All callables are public. Enforced by `private_methods.py`.
- **No functions longer than 14 statements.** Enforced by ruff `PLR0915`.
- **No single-letter variable names** (except `_` throwaway). Enforced by `single_letter_vars.py`.
- **CSS in `.tcss` files only.** No inline `CSS = """..."""` strings in Python classes.
