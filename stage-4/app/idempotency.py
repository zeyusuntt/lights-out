"""Idempotent write paths (§7)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from starlette.requests import Request
from starlette.responses import Response

from .state import Replay, State
from .web import ApiError, invalid, json_response

MAX_KEY = 255


def idempotency_key(request: Request) -> str:
    key = request.headers.get("idempotency-key")
    if not key:
        raise ApiError(400, "missing_idempotency_key", "the Idempotency-Key header is required")
    if len(key) > MAX_KEY:
        raise invalid("Idempotency-Key is longer than 255 characters")
    return key


def same_json(a: Any, b: Any) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same_json(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same_json(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    return type(a) is type(b) and a == b


def run_once(state: State, user_id: str, request: Request, key: str, body: Any,
             handler: Callable[[], tuple[int, dict]]) -> Response:
    """The handler's response, or the stored one for a replay; 409 for another body."""
    claim = (user_id, request.method, request.url.path, key)
    stored = state.replays.get(claim)
    if stored is not None:
        if not same_json(stored.body, body):
            raise ApiError(409, "idempotency_key_reuse", "this key was used with another body")
        return json_response(stored.response, 200)
    status, response = handler()
    state.replays[claim] = Replay(body, status, response)
    return json_response(response, status)
