"""The service's whole replaceable state, and its export format (§10)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .research import unknown_fields
from .support import FIELDS

TRACK = "dossier"
FORMAT_VERSION = 1
STATES = ("building", "ready", "failed")


class InvalidState(ValueError):
    pass


@dataclass
class User:
    id: str
    email: str
    display_name: str
    password_hash: str


@dataclass
class Dossier:
    id: str
    domain: str
    state: str = "building"
    fields: dict[str, dict] = field(default_factory=unknown_fields)
    researched_at: str | None = None
    spent_units: int = 0
    before_build: tuple[str, int] = ("failed", 0)

    def summary(self) -> dict:
        return {"dossier_id": self.id, "domain": self.domain, "state": self.state}

    def view(self) -> dict:
        return {**self.summary(), "researched_at": self.researched_at,
                "spent_units": self.spent_units, "fields": self.fields}

    def listing(self) -> dict:
        return {**self.summary(), "legal_name": self.fields["legal_name"]["value"],
                "researched_at": self.researched_at, "spent_units": self.spent_units}

    def settled(self) -> dict:
        """The dossier as its last completed build left it (an export taken mid-build)."""
        data = self.view()
        if self.state == "building":
            data["state"], data["spent_units"] = self.before_build
        return data


@dataclass
class Replay:
    body: Any
    status: int
    response: dict


@dataclass
class State:
    users: dict[str, User] = field(default_factory=dict)
    tokens: dict[str, str] = field(default_factory=dict)
    dossiers: dict[str, Dossier] = field(default_factory=dict)
    replays: dict[tuple[str, str, str, str], Replay] = field(default_factory=dict)
    next_user: int = 1
    next_dossier: int = 1

    def user_by_email(self, email: str) -> User | None:
        key = email.casefold()
        return next((u for u in self.users.values() if u.email.casefold() == key), None)

    def new_user_id(self) -> str:
        while f"u_{self.next_user}" in self.users:
            self.next_user += 1
        self.next_user += 1
        return f"u_{self.next_user - 1}"

    def new_dossier_id(self) -> str:
        taken = {d.id for d in self.dossiers.values()}
        while f"d_{self.next_dossier}" in taken:
            self.next_dossier += 1
        self.next_dossier += 1
        return f"d_{self.next_dossier - 1}"

    def export(self) -> dict:
        return {"track": TRACK, "format_version": FORMAT_VERSION, "state": {
            "users": [vars(u).copy() for u in self.users.values()],
            "tokens": dict(self.tokens),
            "dossiers": [d.settled() for d in self.dossiers.values()],
            "replays": [{"user_id": k[0], "method": k[1], "path": k[2], "key": k[3],
                         "body": r.body, "status": r.status, "response": r.response}
                        for k, r in self.replays.items()],
            "next_user": self.next_user,
            "next_dossier": self.next_dossier,
        }}


def _require(condition: bool) -> None:
    if not condition:
        raise InvalidState()


def _obj(value: Any, keys: dict[str, type | tuple]) -> dict:
    _require(isinstance(value, dict))
    for key, kind in keys.items():
        _require(key in value and isinstance(value[key], kind) and not
                 (isinstance(value[key], bool) and kind is int))
    return value


def _field(value: Any, name: str) -> dict:
    _obj(value, {"status": str, "citations": list})
    _require("value" in value)
    known = value["value"] is not None
    _require(value["status"] == ("known" if known else "unknown"))
    _require(bool(value["citations"]) == known)
    if known:
        kind = int if name in ("founded_year", "funding_total") else str
        _require(isinstance(value["value"], kind) and not isinstance(value["value"], bool))
    for c in value["citations"]:
        _obj(c, {"url": str, "excerpt": str, "provider": str})
    return {"value": value["value"], "status": value["status"],
            "citations": [{"url": c["url"], "excerpt": c["excerpt"], "provider": c["provider"]}
                          for c in value["citations"]]}


def _dossier(value: Any) -> Dossier:
    _obj(value, {"dossier_id": str, "domain": str, "state": str, "spent_units": int,
                 "fields": dict, "researched_at": (str, type(None))})
    _require(value["state"] in ("ready", "failed") and value["spent_units"] >= 0)
    _require(set(value["fields"]) == set(FIELDS))
    return Dossier(id=value["dossier_id"], domain=value["domain"], state=value["state"],
                   fields={f: _field(value["fields"][f], f) for f in FIELDS},
                   researched_at=value["researched_at"], spent_units=value["spent_units"])


def from_export(document: Any) -> State:
    """The state an unchanged export describes; InvalidState for anything else."""
    _obj(document, {"track": str, "format_version": int, "state": dict})
    _require(document["track"] == TRACK and document["format_version"] == FORMAT_VERSION)
    data = _obj(document["state"], {"users": list, "tokens": dict, "dossiers": list,
                                    "replays": list, "next_user": int, "next_dossier": int})
    state = State(next_user=data["next_user"], next_dossier=data["next_dossier"])
    for u in data["users"]:
        _obj(u, {"id": str, "email": str, "display_name": str, "password_hash": str})
        _require(u["id"] not in state.users and state.user_by_email(u["email"]) is None)
        state.users[u["id"]] = User(u["id"], u["email"], u["display_name"], u["password_hash"])
    for token, user_id in data["tokens"].items():
        _require(user_id in state.users)
        state.tokens[token] = user_id
    for d in data["dossiers"]:
        dossier = _dossier(d)
        _require(dossier.domain not in state.dossiers)
        state.dossiers[dossier.domain] = dossier
    for r in data["replays"]:
        _obj(r, {"user_id": str, "method": str, "path": str, "key": str, "status": int,
                 "response": dict})
        _require("body" in r and r["user_id"] in state.users)
        state.replays[(r["user_id"], r["method"], r["path"], r["key"])] = Replay(
            r["body"], r["status"], r["response"])
    return state
