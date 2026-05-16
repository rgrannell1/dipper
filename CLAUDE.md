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
