"""The HTTP API (§3, §6, §8, §10)."""

from __future__ import annotations

import asyncio
import re
import secrets
from urllib.parse import unquote

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from .clock import parse_rfc3339
from .domains import normalise
from .idempotency import idempotency_key, run_once
from .passwords import hash_password, verify_password
from .screens import asset, shell, wants_html
from .service import Service
from .state import Dossier, InvalidState, State, User, from_export
from .web import (ApiError, bearer_token, error_response, invalid, json_object, json_response,
                  malformed, no_content, not_found, parse_json, typed, unauthenticated)

_EMAIL = re.compile(r"[^@\s]+@[^@\s]+")
_DIGITS = re.compile(r"[0-9]+")
MAX_ID = 64


def build_app(service: Service) -> Starlette:
    def user_of(request: Request) -> str:
        token = bearer_token(request)
        user_id = service.state.tokens.get(token) if token else None
        if user_id is None:
            raise unauthenticated()
        return user_id

    def domain_of(raw: str) -> str:
        domain = normalise(raw)
        if domain is None:
            raise invalid("domain is not a valid host name")
        return domain

    def issue_token(user: User) -> dict:
        token = secrets.token_urlsafe(32)
        service.state.tokens[token] = user.id
        return {"user_id": user.id, "display_name": user.display_name, "token": token}

    async def shell_route(request: Request) -> Response:
        return shell()

    async def health(request: Request) -> Response:
        return json_response({"status": "ok"})

    async def reset(request: Request) -> Response:
        fixture = await json_object(request)
        moment = _moment(fixture, "now")
        users = typed(fixture, "users", list, required=False) or []
        state = State()
        for entry in users:
            if not isinstance(entry, dict):
                raise malformed("each user must be an object")
            uid, email, password, name = (typed(entry, k, str) for k in
                                          ("id", "email", "password", "display_name"))
            if not 1 <= len(uid) <= MAX_ID:
                raise invalid("a user id must be 1 to 64 characters")
            if uid in state.users or state.user_by_email(email) is not None:
                raise invalid("two users share an id or an email")
            state.users[uid] = User(uid, email, name, password)
        hashes = await asyncio.gather(*(asyncio.to_thread(hash_password, u.password_hash)
                                        for u in state.users.values()))
        for user, hashed in zip(state.users.values(), hashes):
            user.password_hash = hashed
        service.replace(state)
        service.clock.set(moment)
        return no_content()

    async def set_clock(request: Request) -> Response:
        moment = _moment(await json_object(request), "now")
        if moment < service.clock.now():
            raise invalid("now is earlier than the clock")
        service.clock.set(moment)
        return no_content()

    async def signup(request: Request) -> Response:
        body = await json_object(request)
        email, password, name = (typed(body, k, str) for k in ("email", "password", "display_name"))
        if not _EMAIL.fullmatch(email):
            raise invalid("email must look like local@domain")
        if len(password) < 8:
            raise invalid("password must be at least 8 characters")
        if not 1 <= len(name) <= 100:
            raise invalid("display_name must be 1 to 100 characters")
        hashed = await asyncio.to_thread(hash_password, password)
        state = service.state
        if state.user_by_email(email) is not None:
            raise ApiError(409, "email_taken", "that email is already registered")
        user = User(state.new_user_id(), email, name, hashed)
        state.users[user.id] = user
        return json_response(issue_token(user), 201)

    async def login(request: Request) -> Response:
        body = await json_object(request)
        email, password = (typed(body, k, str) for k in ("email", "password"))
        state = service.state
        user = state.user_by_email(email)
        if user is None or not await asyncio.to_thread(verify_password, password, user.password_hash):
            raise unauthenticated()
        if service.state is not state:
            raise unauthenticated()
        return json_response(issue_token(user))

    async def create_dossier(request: Request) -> Response:
        user_id = user_of(request)
        key = idempotency_key(request)
        body = await json_object(request)
        user_id = user_of(request)
        compared = {"domain": body["domain"]} if "domain" in body else {}

        def create() -> tuple[int, dict]:
            domain = domain_of(typed(body, "domain", str))
            state = service.state
            existing = state.dossiers.get(domain)
            if existing is not None:
                return 200, existing.summary()
            dossier = Dossier(id=state.new_dossier_id(), domain=domain)
            state.dossiers[domain] = dossier
            service.start_build(dossier)
            return 202, dossier.summary()

        return run_once(service.state, user_id, request, key, compared, create)

    async def dossier_path(request: Request) -> Response:
        segments = _dossier_segments(request)
        if request.method == "GET" and len(segments) == 2 and segments[1] == "evidence":
            return shell()
        if request.method == "GET" and len(segments) == 1 and wants_html(request):
            return shell()
        if request.method == "GET" and len(segments) == 1:
            return await get_dossier(request, segments[0])
        if request.method == "POST" and len(segments) == 2 and segments[1] == "refresh":
            return await refresh_dossier(request, segments[0])
        raise not_found()

    async def get_dossier(request: Request, raw_domain: str) -> Response:
        user_of(request)
        dossier = service.state.dossiers.get(domain_of(raw_domain))
        if dossier is None:
            raise not_found("no dossier for that domain")
        return json_response(dossier.view())

    async def refresh_dossier(request: Request, raw_domain: str) -> Response:
        user_id = user_of(request)
        key = idempotency_key(request)
        await request.body()
        user_id = user_of(request)

        def refresh() -> tuple[int, dict]:
            dossier = service.state.dossiers.get(domain_of(raw_domain))
            if dossier is None:
                raise not_found("no dossier for that domain")
            if dossier.state != "building":
                service.start_build(dossier)
            return 202, dossier.summary()

        return run_once(service.state, user_id, request, key, None, refresh)

    async def list_dossiers(request: Request) -> Response:
        user_of(request)
        limit = _count(request, "limit", 50, 1, 200)
        offset = _count(request, "offset", 0, 0, None)
        q = request.query_params.get("q", "").casefold()
        matches = [d for _, d in sorted(service.state.dossiers.items())
                   if not q or q in d.domain.casefold()
                   or q in (d.fields["legal_name"]["value"] or "").casefold()]
        page = matches[offset:offset + limit]
        return json_response({"dossiers": [d.listing() for d in page],
                              "has_more": offset + limit < len(matches)})

    async def export_state(request: Request) -> Response:
        return json_response(service.state.export())

    async def import_state(request: Request) -> Response:
        document = parse_json(await request.body())
        try:
            state = from_export(document)
        except InvalidState:
            raise invalid("not an export of this service") from None
        service.replace(state)
        return no_content()

    async def on_api_error(request: Request, exc: ApiError) -> Response:
        return error_response(exc)

    async def on_http_error(request: Request, exc: HTTPException) -> Response:
        if exc.status_code == 405:
            return error_response(ApiError(405, "method_not_allowed", "method not allowed"))
        return error_response(not_found())

    async def on_crash(request: Request, exc: Exception) -> Response:
        return error_response(ApiError(500, "internal", "internal error"))

    routes = [
        Route("/health", health, methods=["GET"]),
        Route("/", shell_route, methods=["GET"]),
        Route("/login", shell_route, methods=["GET"]),
        Route("/signup", shell_route, methods=["GET"]),
        Route("/contested", shell_route, methods=["GET"]),
        Route("/assets/{name}", asset, methods=["GET"]),
        Route("/_test/reset", reset, methods=["POST"]),
        Route("/_test/clock", set_clock, methods=["POST"]),
        Route("/_test/export", export_state, methods=["GET"]),
        Route("/_test/import", import_state, methods=["POST"]),
        Route("/auth/signup", signup, methods=["POST"]),
        Route("/auth/login", login, methods=["POST"]),
        Route("/dossiers", create_dossier, methods=["POST"]),
        Route("/dossiers", list_dossiers, methods=["GET"]),
        Route("/dossiers/{rest:path}", dossier_path, methods=["GET", "POST"]),
    ]
    return Starlette(routes=routes, exception_handlers={
        ApiError: on_api_error, HTTPException: on_http_error, Exception: on_crash})


def _dossier_segments(request: Request) -> list[str]:
    """The path segments after /dossiers/, each decoded on its own so that an encoded
    slash stays inside its segment."""
    raw = request.scope.get("raw_path") or request.url.path.encode()
    rest = raw.split(b"?", 1)[0][len(b"/dossiers/"):]
    return [unquote(part.decode("latin-1")) for part in rest.split(b"/")]


def _moment(body: dict, name: str):
    moment = parse_rfc3339(typed(body, name, str))
    if moment is None:
        raise invalid(f"{name} must be an RFC 3339 timestamp with an offset")
    return moment


def _count(request: Request, name: str, default: int, low: int, high: int | None) -> int:
    raw = request.query_params.get(name)
    if raw is None:
        return default
    if not _DIGITS.fullmatch(raw):
        raise invalid(f"{name} must be written in plain digits")
    value = int(raw)
    if value < low or (high is not None and value > high):
        raise invalid(f"{name} is out of range")
    return value
