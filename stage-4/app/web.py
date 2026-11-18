"""HTTP plumbing shared by every route: JSON bodies, errors (§5), bearer tokens (§6)."""

from __future__ import annotations

import json
from typing import Any

from starlette.requests import Request
from starlette.responses import Response

MEDIA_TYPE = "application/json; charset=utf-8"


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def malformed(message: str = "the body is not valid JSON") -> ApiError:
    return ApiError(400, "malformed_request", message)


def invalid(message: str) -> ApiError:
    return ApiError(422, "validation_failed", message)


def not_found(message: str = "no such resource") -> ApiError:
    return ApiError(404, "not_found", message)


def unauthenticated() -> ApiError:
    return ApiError(401, "unauthenticated", "a valid bearer token is required")


def json_response(body: Any, status: int = 200) -> Response:
    return Response(json.dumps(body, separators=(",", ":")).encode(),
                    status_code=status, media_type=MEDIA_TYPE)


def no_content() -> Response:
    return Response(status_code=204)


def error_response(error: ApiError) -> Response:
    return json_response({"error": {"code": error.code, "message": error.message}}, error.status)


def _reject_constant(name: str) -> None:
    raise ValueError(name)


def parse_json(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), parse_constant=_reject_constant)
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise malformed() from None


async def json_object(request: Request) -> dict:
    body = parse_json(await request.body())
    if not isinstance(body, dict):
        raise malformed("the body must be a JSON object")
    return body


def bearer_token(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def typed(body: dict, name: str, kind: type, required: bool = True) -> Any:
    """A body field of the given JSON type: 422 when missing, 400 when of another type."""
    if name not in body:
        if required:
            raise invalid(f"{name} is required")
        return None
    value = body[name]
    if not isinstance(value, kind) or (kind is int and isinstance(value, bool)):
        raise malformed(f"{name} has the wrong type")
    return value
