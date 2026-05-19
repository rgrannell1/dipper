"""Prefix-based tab completion with cycling for repeated presses."""


class TabCompleter:
    """Cycles through completions that start with the current prefix.

    Resets when the input changes between Tab presses.
    """

    def __init__(self, completions: list[str]) -> None:
        self._completions = completions
        self._matches: list[str] = []
        self._index: int = -1
        self._last: str | None = None

    def advance(self, current: str) -> str | None:
        """Return the next prefix match for current, or None if no matches exist."""
        if current != self._last:
            self._matches = sorted({text for text in self._completions if text.startswith(current) and text != current})
            self._index = -1
        if not self._matches:
            return None
        self._index = (self._index + 1) % len(self._matches)
        self._last = self._matches[self._index]
        return self._last
