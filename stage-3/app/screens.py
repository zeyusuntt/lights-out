"""The browser screens: one HTML shell and its script and stylesheet, all served from the image."""

from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import Response

from .web import not_found

_ROOT = Path(__file__).with_name("web")
_ASSETS = {
    "app.js": "text/javascript; charset=utf-8",
    "app.css": "text/css; charset=utf-8",
}
_SHELL = (_ROOT / "index.html").read_bytes()
_FILES = {name: (_ROOT / name).read_bytes() for name in _ASSETS}


def wants_html(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "").lower()


def shell() -> Response:
    return Response(_SHELL, media_type="text/html; charset=utf-8",
                    headers={"Cache-Control": "no-cache"})


async def asset(request: Request) -> Response:
    name = request.path_params["name"]
    if name not in _FILES:
        raise not_found()
    return Response(_FILES[name], media_type=_ASSETS[name], headers={"Cache-Control": "no-cache"})
