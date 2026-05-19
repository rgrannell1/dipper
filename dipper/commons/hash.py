"""Hashing utilities for source content."""

import hashlib


def source_hash(source: str) -> str:
    """Return a hex SHA-256 digest of the source text."""
    return hashlib.sha256(source.encode()).hexdigest()
