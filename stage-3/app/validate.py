"""Structural checks for imported state."""

from __future__ import annotations

from typing import Any


class InvalidState(ValueError):
    pass


def require(condition: bool) -> None:
    if not condition:
        raise InvalidState()


def obj(value: Any, keys: dict[str, type | tuple]) -> dict:
    """The value, when it is an object whose keys hold values of the given JSON types."""
    require(isinstance(value, dict))
    for key, kind in keys.items():
        require(key in value and isinstance(value[key], kind)
                and not (isinstance(value[key], bool) and kind is int))
    return value
