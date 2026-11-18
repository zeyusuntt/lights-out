# Stage 2 rulings

Ledger: ledger/stage-2.jsonl at a519e123341479a80d07696c91c075f76ed40257. Spec: stage-2.md (stage-1.md continues to apply; rulings R1-1..R1-7 continue to apply).

## R2-1 — S2-050: three-429 maximum versus the one-second cooldown

Readings: (a) the fourth attempt is never 429, even if it comes early; (b) the maximum covers attempts that respect the cooldown, and an attempt less than 1 s after a 429 may still get 429.
Chosen: **(b)**. Basis: **CONFLICT**, resolved by the reading under which both sentences hold.
Why: "made again less than one second after a 429 ... is answered 429 again" is the specific rule for early retries, and the three-in-a-row cap is the general guarantee. Builder: after a 429, wait at least 1 s (measured from when the 429 was answered) before making the same call again. A 429 costs nothing and does not count toward the 10 s bound. A session-open 429 while 4 sessions are open lasts until one closes, so release sessions promptly. Tests may not require a fourth early attempt to succeed.

## R2-2 — S2-090 / S2-100: browser routes and authentication

Readings: (a) HTML shells are served for `Accept: text/html` without a bearer header, and the data they load goes through the bearer-protected API; (b) only signup/login are public, and other routes need a browser session.
Chosen: **(a)**. Basis: **IMPLIED**.
Why: "The following screens must be reachable by URL", and a browser navigating by URL sends no bearer header. §6 protects endpoints, which here means the API data. An HTML shell holds no dossier data.
- Any request whose `Accept` header includes `text/html` (as a browser's does, e.g. `text/html,application/xhtml+xml,...`) to `/dossiers/{domain}` gets the UI with 200, signed in or not. A request without `text/html` in `Accept` gets the stage-1 JSON behaviour unchanged, including 401 `unauthenticated` when unauthenticated and 422/404 as before.
- `/`, `/dossiers/{domain}/evidence`, `/contested`, `/signup` and `/login` are served as HTML without a bearer header.
- A signed-out browser on a protected screen is taken to `/login` (redirect or in-page), and goes back to the screen it came from after login. It is never shown a raw JSON error.

## R2-3 — S2-141: `dossier-researched-at` "Text contains researched_at, formatted"

Readings: (a) human formatting only; (b) the literal RFC 3339 string must appear.
Chosen: **both are satisfied**. Basis: **IMPLIED**: the one rendering that every reading accepts.
The element's visible text shows a people-first format of the same instant in the timestamp's own offset (for example `1 Mar 2026, 09:00 (UTC+00:00)`, not converted to the browser's zone). It also contains the exact API string, for example as secondary text `2026-03-01T09:00:00+00:00`, and carries `datetime` or `data-value` with that string. The same goes for candidate `published_at` and `retrieved_at` shown on the evidence screen. `data-published-at` is the exact RFC 3339 API string, or empty.

## R2-4 — S2-180: a browser signed in before the stage-1 → stage-2 upgrade

Readings: (a) the stage-2 UI must also run against the stage-1 API; (b) session continuity only: a browser holding a token that the stage-1 export carries stays signed in on the stage-2 service after import.
Chosen: **(b)**. Basis: **IMPLIED** (stage 1 had no UI; nothing asks stage 2's UI to talk to a stage-1 server).
The browser's whole session is its bearer token, together with whatever display data it re-reads. Nothing server-side that a stage-1 export lacks may be required to stay signed in: no server session table and no stage-2-only cookie secret. After an import made between requests, the next request with the old token succeeds and `current-user` still shows the display name. A request whose response was lost before export, and is retried with the same key and body after import, returns the original response (stage-1 §10 preserves replays). The UI keeps the pending key and body in memory to make that retry. The UI signs out only on 401 or on logout.

## R2-5 — S2-182: migrating stage-1 dossiers into candidates

Foreman finding (from reading the accepted stage-1 export code, stage-1/app/state.py `export`): the stage-1 export holds, per dossier, only the six fields with value, status and citations (url, excerpt, provider). It holds no full page texts, no Kind and no Published. Stage 1 is frozen, and import may make no provider call.
Ruling: **the text the providers served to the last ready stage-1 build, as far as it survives, is the set of citation excerpts in the export.** Each one is a verbatim span of served text. Basis: **SILENT → assumption** (the specification does not contemplate an export that kept less than all served text).
- For each imported dossier, every exported citation excerpt is tested against Appendix A (and R1-7) for **every** field, not only the field it was cited for. Each (value, url) pair it supports becomes one candidate: `provider` from the citation, `kind` null (aggregator authority), `published_at` null, and `retrieved_at` the dossier's `researched_at`. One candidate per page per value: when two exported excerpts from the same URL support the same value, keep the one that ranks first under the selection rule's tie order (smallest excerpt by code point, after URL and provider).
- `value`, `status` and `citations` are then recomputed by the selection rule and Status. Import makes no provider call.
- Supported values that were in served text the stage-1 export did not keep cannot be recovered. This is a limitation of the accepted stage-1 folder, and the final report will name it. Tests must not require candidates beyond what the exported excerpts support.
- An export from a stage-2 service is a different format (format_version may stay 1, the state is opaque). Import accepts both stage-1 and stage-2 exports, and a stage-2 export round-trips candidates, kinds and publication times exactly.
