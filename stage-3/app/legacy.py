"""Dossiers from stage-1 and stage-2 exports (R2-5, R3-3): one ready build at researched_at."""

from __future__ import annotations

from datetime import timezone
from typing import Any

from .builds import Build, Version
from .candidates import ALL_FIELDS, KINDS, Candidate
from .clock import parse_rfc3339
from .dossier import Dossier
from .support import FIELDS, citable
from .validate import obj, require


def typed_value(value: Any, name: str) -> None:
    kind = int if name in ("founded_year", "funding_total") else str
    require(isinstance(value, kind) and not isinstance(value, bool))


def _stage1_citations(value: Any, name: str) -> list[dict]:
    obj(value, {"status": str, "citations": list})
    require("value" in value)
    known = value["value"] is not None
    require(value["status"] == ("known" if known else "unknown"))
    require(bool(value["citations"]) == known)
    if known:
        typed_value(value["value"], name)
    for c in value["citations"]:
        obj(c, {"url": str, "excerpt": str, "provider": str})
    return value["citations"]


def migrate_citations(citations: list[dict], domain: str, retrieved_at: str) -> dict[str, list[Candidate]]:
    """Candidates rebuilt from the citation excerpts a stage-1 export kept (R2-5): each
    excerpt is tested against every field; one candidate per field, value and page."""
    found: dict[str, dict[tuple, Candidate]] = {f: {} for f in FIELDS}
    for c in citations:
        for name in FIELDS:
            hit = citable(c["excerpt"], name, domain)
            if hit is not None and (hit[0], c["url"]) not in found[name]:
                found[name][(hit[0], c["url"])] = Candidate(
                    hit[0], c["url"], hit[1], c["provider"], None, None, retrieved_at)
    return {f: list(v.values()) for f, v in found.items()}


def _utc_date(published: str | None) -> str | None:
    moment = parse_rfc3339(published) if published else None
    return moment.astimezone(timezone.utc).date().isoformat() if moment else None


def _stage2_candidates(value: Any, name: str) -> list[Candidate]:
    obj(value, {"candidates": list})
    candidates = []
    for c in value["candidates"]:
        obj(c, {"url": str, "excerpt": str, "provider": str, "retrieved_at": str})
        require("value" in c and c.get("kind") in (*KINDS, None))
        require(c.get("published_at") is None or isinstance(c["published_at"], str))
        typed_value(c["value"], name)
        candidates.append(Candidate(c["value"], c["url"], c["excerpt"], c["provider"], c.get("kind"),
                                    c.get("published_at"), c["retrieved_at"],
                                    _utc_date(c.get("published_at"))))
    return candidates


def legacy_dossier(value: Any, stage2: bool) -> Dossier:
    """A dossier from a stage-1 or stage-2 export, as one build holding all its spending."""
    obj(value, {"dossier_id": str, "domain": str, "state": str, "spent_units": int,
                "fields": dict, "researched_at": (str, type(None))})
    require(value["state"] in ("ready", "failed") and value["spent_units"] >= 0)
    require(set(value["fields"]) == set(FIELDS))
    researched_at = value["researched_at"]
    require(researched_at is None or parse_rfc3339(researched_at) is not None)
    if stage2:
        candidates = {f: _stage2_candidates(value["fields"][f], f) for f in FIELDS}
    else:
        citations = [c for f in FIELDS for c in _stage1_citations(value["fields"][f], f)]
        candidates = migrate_citations(citations, value["domain"], researched_at or "")
    require(researched_at is not None or not any(candidates.values()))
    dossier = Dossier(id=value["dossier_id"], domain=value["domain"], state=value["state"])
    if researched_at is None:
        if value["spent_units"]:
            dossier.builds.append(Build(None, "failed", value["spent_units"]))
        return dossier
    urls = list(dict.fromkeys(c.url for cs in candidates.values() for c in cs))
    versions = []
    for url in urls:
        mine = {f: [c for c in candidates.get(f, []) if c.url == url] for f in ALL_FIELDS}
        dates = [c.true_from for cs in mine.values() for c in cs]
        versions.append(Version(url, dates[0] if dates else None, mine))
    dossier.builds.append(Build(researched_at, "ready", value["spent_units"], versions))
    dossier.record_transitions(None, 0)
    return dossier
