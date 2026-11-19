VERDICT: PASS
REVISION: 09e577017151e34e8d1f72aadf78f48bdf3f680e

fserve of the exact hash against the local mock web (sample corpus); Playwright chromium at 1440 and 375 px. Screenshots/scripts: journey/stage-3/09e577017151/.

## New in stage 3
- Dossier screen: a seventh "Executives" row after the six fields, with other markup (title label "Chief technology officer", name, Known badge, "In effect since 6 Oct 2023", quoted citation linking to its URL). Exactly six `field-*` test ids remain (executives takes none). Every other field now shows "In effect since <date>" beside its status badge, formatted for people. Readable and unbroken at 375 and 1440, no overflow.
- Evidence screen: Executives section added (title and name, selected marker, kind, published, "in effect since", "first seen", retrieved, provider); six `evidence-*` containers unchanged; no overflow at 375.
- /contested: only the six fields counted (corvid-security legal_name, halvorsen hq_city listed), no executives item.
- Persistence: container killed abruptly and started again; the browser stayed signed in, the dossier list and dossier screen unchanged (state, spent, values), and a refresh then worked.

## Stage-2 flows re-walked (both widths), all as in the accepted stage 2
Signup/login/logout/errors, `/` empty/search-empty/invalid-domain, building -> ready auto-update, known/unknown/contested distinct, failed state keeps fields, slow build followed, lost-response `research-uncertain`/`refresh-uncertain` with same-key retry, hung research/refresh -> uncertain at ~10 s with same-key retry, stale out-of-order read ignored, export/import keeps session, no `null` in header, no horizontal overflow anywhere, nothing loaded outside the service origin.

## Notes (do not block)
Doubled opening quote when an excerpt itself starts with a quote mark; slight selected/non-selected row misalignment on Evidence; no UI for history/feed/as_of (not required by the stage). Evidence-row meta lines at 375 are long (five dates wrapped over four lines): consider trimming "retrieved" since it equals "first seen" in most rows. Not exercised: 429 from the UI, upgrade from a real stage-1/2 export; API-only behaviour (as_of, values, history, changes) is the verifier's.

## Round 2 (this revision)
Diff is the clock only. The full UI walk above was re-run from scratch on this hash at both widths: no regression; abrupt kill and restart again kept the browser signed in with dossiers, spent units and values unchanged.
