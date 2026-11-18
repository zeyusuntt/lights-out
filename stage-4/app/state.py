"""The service's whole replaceable state, and its export format (§10, stage 3 Upgrades)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .builds import Build
from .candidates import ALL_FIELDS
from .dossier import Dossier, Entry
from .legacy import legacy_dossier
from .validate import InvalidState, obj, require

TRACK = "dossier"
FORMAT_VERSION = 1
SCHEMA = 3


@dataclass
class User:
    id: str
    email: str
    display_name: str
    password_hash: str


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
    feed: list[dict] = field(default_factory=list)
    next_user: int = 1
    next_dossier: int = 1
    next_seq: int = 1

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

    def publish(self, entries: list[dict]) -> None:
        """Append feed entries, numbering them in the order given."""
        for entry in entries:
            self.feed.append({"seq": self.next_seq, **entry})
            self.next_seq += 1

    def changes(self, since: int, limit: int) -> dict:
        after = [e for e in self.feed if e["seq"] > since]
        return {"changes": after[:limit], "has_more": len(after) > limit}

    def export(self) -> dict:
        return {"track": TRACK, "format_version": FORMAT_VERSION, "state": {
            "schema": SCHEMA,
            "users": [vars(u).copy() for u in self.users.values()],
            "tokens": dict(self.tokens),
            "dossiers": [{"dossier_id": d.id, "domain": d.domain, "state": d.settled_state(),
                          "builds": [b.to_record() for b in d.settled_builds()],
                          "history": {f: [e.to_record() for e in d.history[f]] for f in ALL_FIELDS}}
                         for d in self.dossiers.values()],
            "replays": [{"user_id": k[0], "method": k[1], "path": k[2], "key": k[3],
                         "body": r.body, "status": r.status, "response": r.response}
                        for k, r in self.replays.items()],
            "feed": list(self.feed),
            "next_user": self.next_user,
            "next_dossier": self.next_dossier,
            "next_seq": self.next_seq,
        }}


def _native_dossier(value: Any) -> Dossier:
    obj(value, {"dossier_id": str, "domain": str, "state": str, "builds": list, "history": dict})
    require(value["state"] in ("ready", "failed"))
    dossier = Dossier(id=value["dossier_id"], domain=value["domain"], state=value["state"],
                      builds=[Build.from_record(b) for b in value["builds"]],
                      history={f: [Entry.from_record(e) for e in value["history"][f]] for f in ALL_FIELDS})
    require(all(b.outcome in ("ready", "failed") for b in dossier.builds))
    return dossier


def from_export(document: Any) -> State:
    """The state an unchanged export of a stage-1, stage-2 or stage-3 service describes;
    InvalidState for anything else."""
    obj(document, {"track": str, "format_version": int, "state": dict})
    require(document["track"] == TRACK and document["format_version"] == FORMAT_VERSION)
    data = obj(document["state"], {"users": list, "tokens": dict, "dossiers": list,
                                   "replays": list, "next_user": int, "next_dossier": int})
    schema = data.get("schema", 1)
    require(schema in (1, 2, SCHEMA))
    try:
        return _state(data, schema)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise InvalidState() from exc


def _state(data: dict, schema: int) -> State:
    state = State(next_user=data["next_user"], next_dossier=data["next_dossier"])
    for u in data["users"]:
        obj(u, {"id": str, "email": str, "display_name": str, "password_hash": str})
        require(u["id"] not in state.users and state.user_by_email(u["email"]) is None)
        state.users[u["id"]] = User(u["id"], u["email"], u["display_name"], u["password_hash"])
    for token, user_id in data["tokens"].items():
        require(user_id in state.users)
        state.tokens[token] = user_id
    for d in data["dossiers"]:
        dossier = _native_dossier(d) if schema == SCHEMA else legacy_dossier(d, schema == 2)
        require(dossier.domain not in state.dossiers)
        state.dossiers[dossier.domain] = dossier
    for r in data["replays"]:
        obj(r, {"user_id": str, "method": str, "path": str, "key": str, "status": int,
                "response": dict})
        require("body" in r and r["user_id"] in state.users)
        state.replays[(r["user_id"], r["method"], r["path"], r["key"])] = Replay(
            r["body"], r["status"], r["response"])
    if schema == SCHEMA:
        obj(data, {"feed": list, "next_seq": int})
        state.feed = [obj(e, {"seq": int, "domain": str, "field": str, "type": str}) for e in data["feed"]]
        state.next_seq = data["next_seq"]
        require(all(e["seq"] < state.next_seq for e in state.feed))
    return state
