VERDICT: BLOCK
REVISION: 010b35ad7282e9b4018daee982a1846a5af8301e

# Stage 4, round 2

The four previous findings pass their first targeted retest and the complete suite. One budget-planning regression blocks this revision under R4-9. Complete independent suite: **303 passed, 1 failed**, including **all 16 browser journeys passing**. The dispatched isolated sample exits 0 and claims stage 4. No required ledger unit lacks evidence.

## S4-F5 — Research consumes the budget before affordable evidence is rendered

Units: **S4-002/S4-098**, under **R4-9** and the dispatch's correctness-first rule.

`batch-reader-aa.test` has one searchable own page supporting all eight fields. A single-company batch with budget 14 gathers that page and returns every field; budget 20 does too. With budget **30**, the service starts a **25-unit research run**, spends the remaining five units on lite searches, and finishes `ready` at 30 units with **every field unknown**, no candidates, and no rendered page. The larger budget loses every supported answer. The previous revision passed this unchanged probe.

The source corroborates the trace: `BuildResearch.run` schedules research before gathering its search results, and `_research` starts whenever the shared remainder can pay 25. It neither waits to see which fields the returned pages support nor leaves the three units needed to render one cited page.

R4-9 resolves the interpretation explicitly: when the remainder cannot pay the whole plan, do company-naming searches and render returned pages first; start research only while a field remains unsupported and after reserving its 25-unit cost there is room for at least one three-unit rendered page. The reservation-time latch remains required. This case must retain all supported fields, and the research-only F4 case must continue to pass.

Reproduce on this exact revision, exits 1:

```sh
SECOND_READER_ONLY=stage4-shared-budget-boundaries-and-affordable-evidence SECOND_READER_NO_BROWSER=1 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-4-010b35ad7282/stage-4
```

The runner builds and starts the supplied folder and documented mock itself. Its one required argument can be any clean copy's `stage-4` folder. The focused reproduction passes the public sample, then independently repeats this failure. The full run and focused run both report budget 30, spent 30, ready, and eight unknown fields. The earlier ceiling/billing assertions in this same case pass for all thirteen two-company budgets and the 14/20-unit completeness controls; the failure is the final completeness assertion at 30. Ledger rows for those successful ceiling subphases identify them separately, rather than describing a budget overrun.

## Previous findings, retested first

```sh
SECOND_READER_ONLY=stage4-scalar-standing-origins-and-selection-reset,stage4-lineage-reserve-keeps-affordable-evidence-complete,stage4-refused-call-refunds-survive-interrupted-retry-wait,stage4-affordable-research-only-evidence-in-batch SECOND_READER_NO_BROWSER=1 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-4-010b35ad7282/stage-4
```

Exit 0: sample plus all four reproductions pass. Private work directory: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/runs-stage-4/second-reader-audit-9d5726d8-zne4shxj/`.

- F1: scalar selection changes reset `corroborated_since`, including the following return to a former selected value. Same-time selection stints also pass.
- F2: all 15 searched supporting pages are gathered without the unused six-unit hold, within 80 units.
- F3: all 11 completed refused attempts show zero before the kill and zero after restart; no retry races the stop. The old 35 units do not reappear.
- F4: the research-only hidden-cedar CEO remains known in a 49-unit batch, with provider spending reconciled and within the caller budget.

Each also passes in the complete run. No earlier finding remains open.

## Exact-revision commands and results

- `fclone 010b35ad7282e9b4018daee982a1846a5af8301e /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-4-010b35ad7282` — exit 0; clone remains clean.
- `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx fserve 010b35ad7282e9b4018daee982a1846a5af8301e 4 20010 --container-port 8097` — exit 0, health 200. Exact owned container stopped with `fstop` after verification.
- `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-4-010b35ad7282/stage-4` — exit 1, **303 passed, 1 failed**. Private artifacts: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/runs-stage-4/second-reader-audit-6ea21b2e-mhmplycp/`.
- Focused F5 reproduction above — exit 1, sample passes and F5 fails. Private artifacts: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/runs-stage-4/second-reader-audit-2d083a5c-kpjxhryh/`.
- From `/Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026`: `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-4-010b35ad7282 --stage 4 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s4-010b35ad-round2` — exit 0, claimed stage 4. The sample does not invalidate the independent counterexample.
- `ledger-check 4 --phase audit --revision 010b35ad7282e9b4018daee982a1846a5af8301e` — exit 1 for S4-002 and S4-098; no missing evidence among 106 required rows.

## Inherited contract

Every inherited API, citation/grammar/span, candidate/ranking, temporal, control, idempotency, concurrency, transfer and browser regression reran with the stage-4 overrides. The runner uses the public mock sample first, private authored corpora, and real accepted stage-1/2/3 containers for upgrades. Services run with 2 vCPU and 3 GiB, and Docker builds/browser work use `with-slot`. No submitted module is imported on the host.

The dependency, constraints and hashing manifests remain unchanged from prior audits: requirements SHA256 `6e94dab8b2f77a2a420f3e3a77f92faeacee84bdbd9973e93d83bd37b9bc3de4`, constraints `8bd3602d0c3d64635e1d960c31eee12df702356e2b7bde2898daa9203a83481d`, passwords.py `7ae7952a14c1eaa3e8c654eee14c51173ac8b8ed672c5005f7bb28f690e0904b`. Password calls remain offloaded with `asyncio.to_thread`. The self-contained image uses PORT and includes its dependencies/assets and writable state directory.

## Lineage planning and originals

R4-1/R4-2 probes pass lineage-only originals, registrant normalization, false-own/lookalike handling, first-publisher precedence, self Canonical, cycles, missing originals, root-specific three-hop depth despite cached text, and eight independent original fetches within 80. The fixed hold is removed. Needed originals are fetched through plain Nimble extracts; rendered page metadata is reused and a missing/unaffordable original falls back to its normalized URL host under R4-2. Canonical-only fetched facts remain excluded unless independently evidence. Source inspection covers this boundary after the independent targeted probes.

## Budget reservations and durability

`BuildBudget.reserve` still synchronously checks the build's live held units and shared live budget before any await. `SharedBudget.admits` atomically latches the batch on its first unaffordable reservation, and all later members stop making calls. Actual reservations are persisted before provider requests. A free error settlement now awaits persistence before retry/return. Responses use the last persisted spending; internal batch admission uses live spending, so delayed publication does not permit overspending.

The atomic store takes a snapshot and a completion callback; only after temp-file flush/fsync, rename and directory fsync does the callback advance visible spending. Completed write responses await persistence. Reviewed store.py SHA256: `12fae8ce0f66e940fa3c4c688e9cd741aea9893a23607605ff1d24cd1021aa7d`.

Positive-billing standalone/batch kills retain all billed units and terminalize within 10 seconds of health. Failed recovery leaves fields/history/feed unchanged. Original completed POST responses replay unchanged; unrelated acknowledged writes survive. Fifty concurrent durable signup responses take at most **0.654 seconds**; the mid-write crash probe retains all acknowledged writes. Idle reads of completed dossier/list/batch spending are strengthened with repeated exact billing comparisons; they pass without drift. All shared-budget ceilings and billing reconciliation pass. F5 is a planning/completeness defect, not an overspend.

## Provider boundary and failure

Only in-container Python AsyncWebRouter search/extract/research reaches providers. The manifest lists webrouter>=0.12.0 with required extras; candidate pages use Nimble rendered extract, lineage originals plain extract, and research schema asks for only the original six fields. Optional providers remain unused. Error/refusal/429 cooldown, late throttling, missing pages and uncertain connection accounting regressions pass. Research refusal still leaves search/extract-supported fields complete. All-provider failures finish failed free, preserving prior ready state.

## Upgrades and native snapshots

Actual stage-1/2/3 exports preserve tokens, keyed replies and recoverable evidence under R2-5/R3-3. Imported origin fallback is URL host; stage-3 retained builds reconstruct standing origins and keep as_of/values/history/feed results with the new keys. Investors stays unknown in legacy builds and first later membership gets its required event type. The frozen earlier-export limitations remain explicit for the final report: omitted stage-1 full evidence and omitted stage-2 historical builds/Effective/empty pages cannot be recovered.

Native transfer preserves batches, owner visibility, spending, origins, standing history and original POST replies. Running control exports retain pre-build dossier snapshots and only completed member spending; import makes no provider calls and imports batches done. Reset/import replacement removes old credentials, keys, batches, dossiers, history and feed durably.

## Visual review

All 16 independent browser journeys pass at 1280/375, including required route/test-id contracts, search, known/unknown/contested/building/failed feedback, read ordering, competing-client refreshes, lost-response retries and legacy sessions. Executives/investors use separate markup from the six required fields. Exact-revision mobile investor dossier and desktop evidence screenshots were viewed from the full run: per-member source counts, confirmed versus single-source-mentioned names, dates, quoted linked excerpts and source metadata remain legible, with no horizontal overflow.

Only after the complete independent run, read `verdicts/stage-4/product-user-010b35ad7282.md`: PASS, full 1440/375 walk, with minor brand/auth-link target notes. It also observes stable idle spending and no build above 80. No exact-revision verifier verdict existed at the time checked. No peer test or walk-script source was opened; F5 was already independently observed and disputed before reading a peer verdict.

## Ledger and privacy

All 125 units are accounted for: 99 normative, 7 ruled ambiguous and 19 informative. All 106 required rows carry exact-revision evidence; R4-9 is attached to S4-002/S4-098. The shared-budget case's ceiling/billing subphase is explicitly distinguished from its later completeness failure. The independent oracle was retained after R4-9, not amended to match the implementation. The only probe change this round strengthens repeated idle spending reads.

No product code/tests were edited. The exact clone is clean and every owned container/network is removed. Tokens/exports remain private; temporary browser configuration is removed. Probes remain private until all stages close. Native TaskCreate failed under the runtime approval policy; no shared-board fallback was used.
