"""The service's whole replaceable state, and its export format (§10, stage 3 and 4 Upgrades)."""

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
SCHEMA = 4


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
class Batch:
    """Builds started together under one shared budget, owned by one user (stage 4)."""

    id: str
    owner: str
    domains: list[str]
    budget_units: int
    builds: list[tuple[str, int]] = field(default_factory=list)

    def _builds(self, dossiers: dict[str, Dossier]) -> list[Build]:
        return [dossiers[d].builds[i] for d, i in self.builds
                if d in dossiers and i < len(dossiers[d].builds)]

    def spent_units(self, dossiers: dict[str, Dossier]) -> int:
        return sum(b.spent for b in self._builds(dossiers))

    def view(self, dossiers: dict[str, Dossier]) -> dict:
        running = any(b.outcome == "building" for b in self._builds(dossiers))
        return {"batch_id": self.id, "state": "running" if running else "done",
                "budget_units": self.budget_units, "spent_units": self.spent_units(dossiers),
                "dossiers": [{"domain": d, "state": dossiers[d].state if d in dossiers else "failed"}
                             for d in self.domains]}

    def to_record(self, dossiers: dict[str, Dossier], settled: bool) -> dict:
        builds = [[d, i] for d, i in self.builds
                  if not (settled and dossiers[d].builds[i].outcome == "building")]
        return {"batch_id": self.id, "owner": self.owner, "domains": self.domains,
                "budget_units": self.budget_units, "builds": builds}

    @classmethod
    def from_record(cls, data: dict) -> Batch:
        obj(data, {"batch_id": str, "owner": str, "domains": list, "budget_units": int, "builds": list})
        return cls(data["batch_id"], data["owner"], list(data["domains"]), data["budget_units"],
                   [(d, i) for d, i in data["builds"]])


@dataclass
class State:
    users: dict[str, User] = field(default_factory=dict)
    tokens: dict[str, str] = field(default_factory=dict)
    dossiers: dict[str, Dossier] = field(default_factory=dict)
    replays: dict[tuple[str, str, str, str], Replay] = field(default_factory=dict)
    feed: list[dict] = field(default_factory=list)
    batches: dict[str, Batch] = field(default_factory=dict)
    next_user: int = 1
    next_dossier: int = 1
    next_seq: int = 1
    next_batch: int = 1

    def new_batch_id(self) -> str:
        self.next_batch += 1
        return f"b_{self.next_batch - 1}"

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

    def export(self, settled: bool = True) -> dict:
        """The state as an export. Settled (§10), a running build is left out (R1-4, R4-7);
        otherwise, to survive a stop, it is kept as a failed build holding its spending (R4-0)."""
        return {"track": TRACK, "format_version": FORMAT_VERSION, "state": {
            "schema": SCHEMA,
            "users": [vars(u).copy() for u in self.users.values()],
            "tokens": dict(self.tokens),
            "dossiers": [{"dossier_id": d.id, "domain": d.domain, "state": d.recorded_state(settled),
                          "builds": [b.to_record() for b in d.recorded_builds(settled)],
                          "history": {f: [e.to_record() for e in d.history[f]] for f in ALL_FIELDS}}
                         for d in self.dossiers.values()],
            "batches": [b.to_record(self.dossiers, settled) for b in self.batches.values()],
            "next_batch": self.next_batch,
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
                      history={f: [Entry.from_record(e) for e in value["history"].get(f, [])]
                               for f in ALL_FIELDS})
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
    require(schema in (1, 2, 3, SCHEMA))
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
        dossier = _native_dossier(d) if schema >= 3 else legacy_dossier(d, schema == 2)
        require(dossier.domain not in state.dossiers)
        state.dossiers[dossier.domain] = dossier
    for r in data["replays"]:
        obj(r, {"user_id": str, "method": str, "path": str, "key": str, "status": int,
                "response": dict})
        require("body" in r and r["user_id"] in state.users)
        state.replays[(r["user_id"], r["method"], r["path"], r["key"])] = Replay(
            r["body"], r["status"], r["response"])
    if schema >= 3:
        obj(data, {"feed": list, "next_seq": int})
        state.feed = [obj(e, {"seq": int, "domain": str, "field": str, "type": str}) for e in data["feed"]]
        state.next_seq = data["next_seq"]
        require(all(e["seq"] < state.next_seq for e in state.feed))
    if schema == SCHEMA:
        obj(data, {"batches": list, "next_batch": int})
        for record in data["batches"]:
            batch = Batch.from_record(record)
            require(batch.owner in state.users and batch.id not in state.batches)
            require(all(d in state.dossiers and 0 <= i < len(state.dossiers[d].builds) for d, i in batch.builds))
            state.batches[batch.id] = batch
        state.next_batch = data["next_batch"]
    return state
