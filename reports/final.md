# FINAL REPORT — Dossier, stages 1–4

All four stages are closed and accepted. The line never stopped: the most blocks on any one stage was 3, against the limit of 5. Each stage was accepted only after the kit check claimed it on a clean clone in isolated mode, all verifying seats passed that exact revision, the ledger audit showed evidence for every required unit, and `accept-check` exited 0.

Result repository: /Users/sunzeyu/dev/band-factory/work/result. Sealed acceptance suites are in `acceptance/stage-<n>/`, published at c359185. Second-reader probes are in `acceptance/second-reader/stage-<n>/`, published at be6c018 and 47183d8.

## Per stage

| Stage | Accepted revision | Rounds (BLOCKs) | Kit check (foreman, isolated, clean clone) | Verifier | Second-reader | Product-user |
|---|---|---|---|---|---|---|
| 1 Company profiles | a8789dcd65a18ca385d968116c51d23590913c33 | 4 (3) | claimed stage 1 — checks/foreman-s1-r4 | PASS 186/186 | PASS 183/183, ledger audit 0 | n/a (API only) |
| 2 Competing sources & screens | bc19abf8cbde23c3a2fa50f23baa55dbfe48d731 | 2 (1) | claimed stage 2 — checks/foreman-s2-r2 | PASS 223 | PASS 205/205, audit 0 | PASS |
| 3 Change over time | cd24f51fb21b312aac2398adff8813a1b6276b57 | 1 (0) | claimed stage 3 — checks/foreman-s3-r1 | PASS 271 | PASS 246/246, audit 0 | PASS |
| 4 Independent sources, batches, failure | a7228733bd425af053de0063ec2a3fc1ef68d873 | 3 (2) | claimed stage 4 — checks/foreman-s4-r3 | PASS 306/306 | PASS 305/305, audit 0 | PASS |

The kit check runs only a sample of the graded checks. A green run is not evidence that a stage is complete, and the stage verdicts above rest on the seats' own suites.

Measured cost on the verifier's corpus (all fields correct in every stage):

| Stage | Units | Correct fields | Units per correct field | Units per build |
|---|---|---|---|---|
| 1 | 429 | 81/81 | 5.3 | 27–33 |
| 2 | 1038 | 92/92 | 11.3 | 36–63 |
| 3 | 1132 | 96/96 | 11.8 | 37–70 |
| 4 | 1302 | 103/103 | 12.6 | 38–74 |

No build exceeded 80 units.

## Findings that changed the work

- **Stage 1**
  - Encoded-slash path domains returned 404 instead of 422.
  - Fixture user ids over 64 characters were accepted.
  - Research excerpts that look like header lines but sit in a page's prose were dropped, leaving fields unknown.
  - A research citation of 1,056 characters was asserted.
  - The search for a short span inside a long sentence was capped, so late supporting spans were missed. The builder was told to change approach, and replaced the scan with occurrence-anchored spans.
  - The builder also stopped re-extracting text the research run had already served.
- **Stage 2**
  - A 429 refusal after slow research was never retried, because a 6.5 s internal window cut it off. The build then ended with no candidates.
  - UI polish requested by the product-user: people-first auth errors, wording during a first build, alignment, tap targets, and the navigation shown when signed out.
- **Stage 3**: no blocking findings. The design was fixed up front by rulings R3-1 to R3-5.
- **Stage 4**
  - Fixed reserves held back affordable evidence. A batch skipped research it could afford, and an unused 6-unit lineage reserve blocked page renders.
  - `corroborated_since` carried over from the previously selected value.
  - Refunds for refused calls were not durable, so a kill counted them as spent.
  - The fix for the reserves overcorrected: in a short batch, research then displaced page evidence (R4-9). The final revision renders the searched pages first when the budget is tight.

## Rulings that were assumptions (SILENT or IMPLIED beyond the text)

- **R1-1**: a clock call before the first reset freezes the clock.
- **R1-3**: if the exact-domain search never succeeds while other calls do, the build ends per §8.
- **R1-6 / R1-7**: a supporting sentence over 500 characters is cited by an edge-intact span of at most 500 characters. Shorter sentences are judged and cited whole.
- **R2-3**: `researched_at` on screen shows both a people-first format and the exact RFC 3339 string.
- **R2-4**: the browser session is only its bearer token.
- **R2-5**: a stage-1 export keeps only citations, so upgrade candidates come only from the exported excerpts.
- **R3-3**: a stage-2 export keeps only the current view. It imports as one ready build at `researched_at`, with `true_from` taken from `published_at` and nothing from Effective lines.
- **R3-4**: a kill mid-build rolls back to the pre-build state. Stage 4 superseded this with R4-0.
- **R3-5**: a restart before any reset or clock call keeps following system time.
- **R4-2**: if the budget forbids fetching an original, the origin is the host of that URL.
- **R4-3**: the origin and corroboration keys are not required on `/values`.
- **R4-5**: `budget_units` 1.0 and 1e0 are rejected with 422.
- **R4-7**: a native export holds batches, running builds are settled, and imported batches are done.
- **R4-9**: under a tight caller budget, page evidence is gathered before research.

The full basis for every ruling is in `rulings/stage-<n>.md`.

## What remains unverified or known limited

1. **The stage-1 export keeps only citations.** This lives in stage-1/, which is frozen. When a stage-1 export is imported (into stage 2 or later), only the values supported by the exported excerpts become candidates. Other values that the last stage-1 build saw cannot be recovered (R2-5).
2. **The stage-2 export keeps no build history, Effective dates or candidate-free pages.** This lives in stage-2/, which is frozen. A stage-2 → stage-3/4 upgrade therefore yields one synthetic build, not the original build sequence (R3-3).
3. **Live providers.** Everything was verified only against the local mock web with the sample corpus and the seats' own corpora. The live Nimble timing paths (30 s per call, 120 s, 300 s) were not exercised.
4. **Batch latch and lineage fallback (R4-6, R4-2).** These were confirmed by reading the code and by spending equalling billing within budget. They are not fully observable from outside the service.
5. **Remaining UI notes (non-blocking).**
   - The "Dossier" brand link and the inline links on login and signup are under 44 px.
   - The contested list shows the raw field key next to the label, which was accepted.
   - There is no batch UI, because the specification requires none.
6. **Cost headroom.** The heaviest stage-4 build spends 74 of 80 units, and the batch plan estimate leaves out lineage fetches (R4-2 covers that).
7. **Record correction.** accepted/stage-4.txt repeats an earlier note that scrypt runs on the event loop. The second-reader found that stage-4/app/routes.py runs hashing and verification through `asyncio.to_thread`, so that note is not accurate for the accepted revision.
8. **Process note.** In stages 2 and 3 the builder committed the pure stage copy before the seal, and in stage 4 it committed two fix revisions before their FIX was issued. The seal tool excludes pure copies. Every accepted revision was verified as an exact hash by all seats.
