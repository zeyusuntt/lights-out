VERDICT: PASS
REVISION: 52f4f877c4cf853d78515f431a8b58a950ee1da0

Seat: verifier. Round 1. Worked from a clean clone (fclone) of the exact hash.

## Evidence
- Fresh build, no cache, of stage-1/ per RUN.md (`docker build` . then `docker run -e PORT=<port>` with NIMBLE_* only); started under --cpus 2 --memory 3g on an internal network with no outbound access, beside the kit mock web (sample corpus + suite corpus). Healthy well inside 60 s. Peak memory about 320 MiB.
- Check command (isolated): `harness run --track dossier --repo <clone> --stage 1 --mode isolated --out work/checks/verifier-52f4-r1` → "claimed stage: 1". This is a sample, not a verdict.
- Sealed suite `run.sh stage-1`: 171/171 passed (seal sha256:27bb5f23…). Then 2 post-seal additions passed too, 173/173 in all (seal sha256:72e44618…).
- Covered: health/PORT; reset and clock, including the R1-1 freeze before reset; auth, all error codes and bearer precedence; domain normalisation and bounds; §7 idempotency, including 25-way concurrent same-key and claim-before-validation; builds checked against an independent Appendix A oracle on 15 companies (fields known exactly where the evidence supports, every citation served by that provider for that URL, from prose, supporting); refresh across epochs; failed builds keep fields; Tavily faulted, and Tavily not configured at all; a throttled exact-domain search retried (exactly one success); 0.9 s provider delay gives a build within 10 s; reads make no provider call; list q/order/pagination/422s; export/import, including into a second container, mid-build export (R1-4) and invalid imports; 50 in flight with no 5xx, every request under 5 s.
- Upgrade path: not applicable (stage 1). Restart survival: not required (§2 "state need not survive a container restart").

## Cost (§9, dispatch "spend per correct field")
Mock call log over one first build of each of 15 companies: 438 units for 81 correct fields out of 81 supportable, which is 5.4 units per correct field. Per build 27–33 units (max 33, budget 80). Every build: 2 lite searches + 1 research run (27), then 0–5 one-unit extracts, plus field searches when something is still missing.

## Fault planting (tests of the tests)
8 faults, one per copy: 5 caught at once (dropped "not" negator; extract not charged; idempotency body ignored; build time read at completion; has_more off by one). 3 survived:
- domain length 254 accepted: hole. I added test_post_seal_254_char_domain_rejected, which catches it.
- mid-build export keeping live spent_units: hole (the export came before any charge). I added test_post_seal_export_after_spending_keeps_prebuild_units, which catches it.
- reset no longer fencing an old build: equivalent fault, since reset cancels builds and swaps the whole State, so an orphaned build writes nowhere.
Both additions pass on this revision.

## Suite amendments after seeing code (test misreadings, not findings)
1. The oracle read the corpus `text`, but the mock serves `static_text` when present. Fixed, so 4 build tests that wrongly failed now pass.
2. A `Bearer ` header with a trailing space can't be sent by the HTTP client. Case dropped.
3. In the www.www. case the test looked itself up again by a path, which §4 normalises again. It now waits via the list.

## Notes (no sentence broken; do not block)
- N1 Avoidable spend: when a research claim's page was not served in full by a search, the build extracts the URL (1 unit) to re-find the excerpt, though the research run itself served that excerpt (§4 "an excerpt of text a provider served"). Example: tarnwick-labs.test, 1 unit. Small.
- N2 Builder assumption (1): lite snippets under 290 chars are taken as whole prose in the mock only. This is consistent with the mock README (snippet = first 300 chars of prose). It is a mock-shaped shortcut; live snippets are always treated as truncated.
- N3 scrypt (N=2^14) runs on the event loop in login/signup. The 20-way concurrent signup and 50-in-flight mixed tests stayed under 5 s, but heavy login bursts compete with everything else.
- N4 Emails compare case-insensitively, a wrong method gives 405 method_not_allowed, and Tavily is not used. No sentence forbids any of these.
- Code read: no provider route other than web_router (nimble_python is imported only for exception classes); no fixture-keyed branches; replay/claim handling is atomic on one event loop; reset/import cancel builds and fence writes by state identity.
