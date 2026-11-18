VERDICT: PASS
REVISION: 3cf3cef0862c212f6f572712876ad700e9e0e381

Seat: verifier. Stage 2, round 1. Worked from a clean clone (fclone) of the exact hash.
- stage-2/ was built fresh with no cache (`docker build .`, `docker run -e PORT=<port>`, per RUN.md).
- The accepted stage-1 folder in the same clone was built as the previous-stage image for the upgrade path.
- Both ran under --cpus 2 --memory 3g on an internal network with no outbound access, with the kit mock web (sample corpus + suite corpus).

## Evidence
- Sealed suite `run.sh <clone>/stage-2`: 220/220 passed (seal sha256:5e65df49…). After the fault planting below, the 2 post-seal additions pass too: 222/222 (seal of the amendment printed in SEAL AMENDED).
- Check command, isolated: `harness run --track dossier --repo <clone> --stage 2 --mode isolated --out work/checks/verifier-s2-3cf3-r1` → "claimed stage: 2". This is a sample, not a verdict.

Covered:
- All stage-1 tests still in force.
- The candidate set on 21 companies equals the evidence oracle exactly (one per page per supported value, read from browser text, research-cited pages included).
- Selection rule, hand-checked (rankford-tools.test): authority, recency, missing or invalid Published, unlisted Kind and the www host fallback, URL tie, value tie. Status (known/contested/unknown); citations are every candidate carrying the selected value.
- retrieved_at; browser text versus static text (veilmoor-labs.test).
- Weather and throttle on every method: builds stay exact within 80 units.
- Browser (chromium) on every required route and testid: signup, login and logout with auth-error; the research flow with polling until ready; invalid domain; an existing domain opens with no build; list order, search and empty state; field order, status, values and citations; evidence attributes; contested ordering; refresh, including a competing client; a refused refresh; lost research and refresh responses shown as uncertain and retried with the same key in one build; latest read wins; no horizontal scroll and visible labels at 375 and 1280 px.
- R2-2 HTML shells and the signed-out redirect back; R2-3 timestamps.
- Upgrade: stage-1 image populated over its API, exported, imported here.
  - Imported over the API: tokens, logins and same-key retries survive; no provider call is made; imported candidates are exactly what the exported excerpts support across all six fields (R2-5); the next build replaces them.
  - In the browser (same service): a signed-in session and a lost research request survive an export/import.
  - A stage-2 export round-trips exactly.

## Cost
Mock call log over 21 first builds: 1038 units for 92 correct fields of 92 supportable, 11.3 units per correct field. Per build 36–63 units (max 63 of 80): 8 lite searches + 1 research run (33 units) + 1–10 rendered extracts at 3 units.

## Fault planting (tests of the tests), first passing revision of stage 2
9 copies:
- Caught: authority filing ≠ own; recency reversed; www host not normalised for Kind; status known with 2 distinct values; stage-1 migration testing only one field; research-cited pages not rendered.
- Survived, now covered: dossier reads with no latest-wins sequence (my earlier test held the stale read past the UI's 10 s request timeout, so the UI dropped it by itself). I added test_post_seal_reload_out_of_order_stale_response, which catches it.
- Survived, now covered: polling every 3.5 s. I added test_post_seal_poll_gap_at_most_2s, which catches it.
- Survived, outside the requirement: the list screen's own sequence check removed. No sentence requires latest-wins for the list.
Both additions pass on this revision.

## Notes (no sentence broken)
- N1 RUN.md still tags the image `dossier-stage-1`, and it does not list KERNEL_*/BROWSERBASE_* (they are unused). This is cosmetic.
- N2 Every build makes all 8 lite searches even when the first two already returned every page naming the company (6 units). It also renders a page even when its whole snippet prose was already served; that is required whenever browser text may differ from served text (stage 2 "Page text").
- N3 The UI request timeout is 10 s; a slower API read is shown as a failed load.
- N4 scrypt still runs on the event loop. The concurrency tests stay under 5 s.
