VERDICT: BLOCK
REVISION: b928822534e8f8b9b7ce8dbf555bfbda1a42deab

# Stage 4, round 1

Four independently reproduced failures block this revision. Final complete independent suite: **300 passed, 4 failed**, including **all16 browser journeys passing**. The isolated sample harness exits0 and claims stage4; it does not exercise away these counterexamples. No unit lacks evidence.

## S4-F1 — Corroboration time carries across a scalar value change

Units: **S4-038/S4-039/S4-040**.

On reader-standing.test, Dana Ruiz's selected-value stint has accumulated two standing origins since **2026-03-05T09:00:00+00:00**. Subsequent builds keep Dana selected. At **2026-03-08T09:00:00+00:00**, a ready build selects Sam Ortiz with two current origins. The API correctly reports Sam, learned_at March8, and corroborated true, but reports **corroborated_since March5**.

Sam's new selection stint starts on March8. Its earliest qualifying ready build is March8, not a March5 build that selected Dana. Sam's own-page candidate having an older candidate learned_at from a previous stint does not change the new selected-value history boundary. This is distinct from the member-field collective-run ruling R4-4.

Actual new field: value Sam Ortiz; origins reader-standing.test and standing-e.test; learned_at March8; corroborated_since March5. Expected since: **March8**. The probe also checks that a subsequent corroborated return to Dana begins a new stint, once this earlier assertion is fixed.

Reproduce, exits1:

```sh
SECOND_READER_ONLY=stage4-scalar-standing-origins-and-selection-reset SECOND_READER_NO_BROWSER=1 /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-4/run.sh <clean-clone>/stage-4
```

## S4-F2 — Unused lineage headroom hides two affordable evidence pages

Unit: **S4-002**, inheriting Stage2's complete candidate set (**S2-054**) and **R1-2**.

reader-reserve-pages.test has15 searchable own pages: five legal names, five headquarters values and five CEO values. **All15 URLs are returned by this build's searches**. None has a Canonical original to fetch. The service gathers13 candidates, finishes at **74 units**, and omits these two supported legal-name candidates:

- https://reader-reserve-pages.test/legal_name-3 — `Reader Reserve Pages legal name is Reader Reserve Pages Delta, LLC.`
- https://reader-reserve-pages.test/legal_name-4 — `Reader Reserve Pages legal name is Reader Reserve Pages Epsilon, LLC.`

The missing prose was already served in the search snippets, and the two full rendered pages cost3 units each. Ten lite searches cost10, research25, and13 rendered pages39: total74. The remaining6 pays both pages exactly, completing at80. This is not genuine exhaustion of the80-unit cap.

Source corroboration, read after the independent probes: app/research.py keeps LINEAGE_ROOM=6 in every render reservation; app/budget.py rejects when units+keep exceeds remaining. That headroom is never released when no original needs it, leaving affordable supported candidates out.

Reproduce, exits1 and prints searched15/candidates13/spent74/remaining6:

```sh
SECOND_READER_ONLY=stage4-lineage-reserve-keeps-affordable-evidence-complete SECOND_READER_NO_BROWSER=1 /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-4/run.sh <clean-clone>/stage-4
```

## S4-F3 — Completed refused calls reappear as35 charged units after restart

Units: **S4-109/S4-118**, under **R4-8**.

The kit mock answers the initial ten searches and one research attempt with500, each billed0. The forwarding trace has all11 answers; the service then returns **spent_units0, state building**, while its calls wait before retry. No retry starts before the kill, as the unchanged11-call log confirms.

After abrupt kill/start, the dossier is failed with **spent_units35**, although total provider billing remains0. These are the old ten1-unit search reservations and one25-unit research reservation. They were completed, refused attempts, not unanswered calls in flight at the stop. Expected spending on this trace is **0**.

The probe uses the actual mock's500 responses and billing, with a200ms forwarding delay to expose the response/settlement boundary; payloads and status codes are not synthesized. Every call still answers within one second. It records the live refund and complete answers before killing, then checks that no new call raced the stop.

Source corroboration: Gateway._call durably records the reservation before sending, but BuildBudget.settle refunds only memory. The error path then waits1.1 seconds before a retry without recording the refund. R4-8 explicitly requires a refund/final cost to be durable no later than it becomes visible in any response.

Reproduce, exits1 and prints before_stop_spent0/billed0/after_restart_spent35/refused_calls11:

```sh
SECOND_READER_ONLY=stage4-refused-call-refunds-survive-interrupted-retry-wait SECOND_READER_NO_BROWSER=1 /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-4/run.sh <clean-clone>/stage-4
```

## S4-F4 — A49-unit batch skips research that a38-unit build completes

Unit: **S4-002**, with **R1-2** completeness and the caller-budget rules. This independently reproduces the verifier's V4-1 root cause using a different authored company and field.

hidden-cedar.test has one non-searchable own page, served through a Nimble six-field research claim: `Hidden Cedar CEO: Dana Ruiz.` An unbatched build obtains Dana Ruiz for **38 units**. After reset, a batch with this one domain and **budget_units49** finishes ready at **10 units**, with CEO unknown and **zero research calls**.

The caller's49 covers the complete38-unit build. After the ten searches,39 units remain, enough for research25 plus its one rendered page3. No unaffordable reservation or real budget exhaustion explains the omission.

Source corroboration: BuildResearch._research requires RESEARCH_UNITS+PAGE_ROOM, a fixed25+30=55, before it will start research in a batch. This rejects a49-unit batch even when its actual complete evidence costs38. Affordable research-only evidence must not be lost to that fixed estimate.

Reproduce, exits1 and prints unbatched38/budget49/batch_spent10/CEO null/research_calls0:

```sh
SECOND_READER_ONLY=stage4-affordable-research-only-evidence-in-batch SECOND_READER_NO_BROWSER=1 /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-4/run.sh <clean-clone>/stage-4
```

## Exact-revision commands and results

- `fclone b928822534e8f8b9b7ce8dbf555bfbda1a42deab /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-4-b928822534e8` — exit0, clean clone.
- `BUILDX_CONFIG=/Users/sunzeyu/dev/band-factory/work/second-reader/buildx fserve b928822534e8f8b9b7ce8dbf555bfbda1a42deab 4 20010 --container-port 8097` — exit0, health200.
- Final complete runner: `/Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-4-b928822534e8/stage-4` — **300 passed, 4 failed**, exit1. Only the four cases above fail. Final private artifacts: `/Users/sunzeyu/dev/band-factory/work/second-reader/probes/runs-stage-4/second-reader-audit-1ac8cd5c-2xaz7wzi/`.
- The focused reproductions also fail on this exact hash. F4's focused run independently confirms the peer finding without opening its test source; F3's focused trace was separately ruled under R4-8.
- From `/Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026`: `BUILDX_CONFIG=/Users/sunzeyu/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-4-b928822534e8 --stage 4 --mode isolated --out /Users/sunzeyu/dev/band-factory/work/checks/second-reader-s4-b9288225-round1` — exit0, **claimed stage:4**. This is a sample only.
- `ledger-check 4 --phase audit --revision b928822534e8f8b9b7ce8dbf555bfbda1a42deab` — exit1 for S4-002/S4-038/S4-039/S4-040/S4-109/S4-118, with no missing evidence.

The one-argument runner builds/starts the supplied stage itself, the documented mock and actual accepted Stage1/2/3 images. Services run at2vCPU/3GiB. Builds and browser jobs use with-slot. Browser work runs Chromium in df-harness-runner. No product module is imported on the host. Each run includes the public sample before independent fixtures. It removes its containers/networks and prints counts.

## Passing coverage

Lineage probes pass normalized registrant/first-publisher handling, own downgrade versus the separate lookalike predicate, first-publisher precedence, a self Canonical with a different registrant, missing originals, cycles, root-specific three-hop depth despite cached pages, eight independent original fetches within80, and Canonical-only originals contributing lineage rather than candidate facts. Current origins, duplicate-source collapse and member-field corroboration/weak-member removal pass outside F1's scalar transition.

Investor probes pass every allowed suffix, long/maximal and Unicode names, company/phrase removal, multiple names per sentence, amount-based one-word/nonsuffix names, fractional-dollar amounts, absence/negation/foreign-currency controls, and safe long excerpts. A one-origin lower-authority field retains candidates while unknown. Membership, all-candidate selected flags, rank order versus member order, grouped citations, earliest member/latest field dates, valid-time membership, corrections/equal-date additions/removals, and investor-last eight-field feed order pass.

Batch probes pass atomic validation, strict1.0/1e0 rejection, key boundaries and precedence, ownership,50 identical concurrent requests, original-response replay, same key on other paths/users, normalized duplicate rejection, input order,50-domain limit, existing/building dossiers free, dynamic item states independent of batch terminality, overlapping batches/standalone creates, tight shared budgets and per-build80 ceilings. Search/extract evidence remains complete with research refusing, and all-provider failures end failed free within the bound. The distinct research-only affordability failure is F4.

Positive-billing restart probes pass: every billed pre/post-stop unit remains counted in dossier and batch, interrupted builds become terminal within10 seconds of health, fields remain unchanged on failure, completed unrelated writes survive, idle batch state/replies persist, and a new explicit refresh is new work without recharging the old batch. Fifty concurrent durable signup responses meet the five-second bound; crash-atomic signups preserve every acknowledged response. The completed-refusal refund exception is F3.

## Upgrades and native snapshots

The accepted legacy trees match exactly: stage1 `442c1d6ff697325d2da3a6798b0d51f340cb9772`, stage2 `11571675c10451ddda8d0cc92ec56468a6230b07`, stage3 `1e3d3070c891f8aa4e69be40ca391e5a2bfbb29f`.

All three real legacy export paths pass token/idempotent continuity, candidate preservation and URL-host origin fallback. Stage3 build/version and as_of/values/history/feed results survive with the new keys; standing origins reconstruct from each old build time. Investors remains unknown in every old build and first later membership has the required change/initial type. R2-5/R3-3 unrecoverable earlier-export limitations remain explicit for the final report.

Native Stage4 round-trip preserves origins, standing history, batch ownership/state/cost and original POST replies. A running batch export retains only completed member spending and pre-build snapshots for interrupted members; import makes no provider call, imports batches done, and replays the original POST response. Reset/replacement removes old batches, dossiers, histories, feed, credentials and keys durably.

## Visual review

All16 browser journeys pass at1280/375 pixels, covering required routes, authentication, retry/uncertainty, latest reads, competing clients, polling, loading/empty/failed feedback, legacy session continuity, executive/investor markup and the six-field contested contract. Viewed exact-revision mobile investor dossier and desktop evidence images: confirmed and single-source-mentioned names are distinguished, source/origin metadata is human-readable, excerpts are quoted/linked, and multi-member qualification is explained. No horizontal overflow is observed. Final images are regenerated in the printed run's browser-shots folder; same-revision images reviewed also include `/Users/sunzeyu/dev/band-factory/work/second-reader/probes/runs-stage-4/second-reader-audit-ead7dd1e-u4qppc_5/browser-shots/`.

## Peer results after independent probes

Only after the complete303-case independent run, read `verdicts/stage-4/verifier-b928822534e8.md` and `product-user-b928822534e8.md`. Verifier BLOCK V4-1 describes affordable research being skipped; F4 independently reproduces that root with hidden-cedar.test/CEO, rather than using its corpus or test source. Product-user PASS covers the full desktop/mobile walk and remaining nonblocking polish notes. The final304-case independent run then includes F4. No peer test/walk-script source was opened, and the three earlier own findings were not changed to match a peer verdict.

## Inherited contract

All inherited API, evidence/grammar/span, candidate/rank, temporal, idempotency, controls, transfer, concurrency, browser and durability regressions rerun with Stage4's explicit overrides. The inherited equal-date correction/version boundary is also checked. Requirements, constraints, password hashing and atomic store remain unchanged from the earlier audited files: requirements SHA256 `6e94dab8b2f77a2a420f3e3a77f92faeacee84bdbd9973e93d83bd37b9bc3de4`; passwords.py `7ae7952a14c1eaa3e8c654eee14c51173ac8b8ed672c5005f7bb28f690e0904b`; store.py `a0811289c78b177121f73f6a03aa1e68843ffa8a9066712a7dde69e4dbc63c5c`. Password call sites use asyncio.to_thread. Docker includes dependencies/assets and writable /srv/data in one image. Live timing configuration is inspected statically; actual providers are not contacted. F2 and F4 remain failures of inherited completeness.

## Lineage planning and originals

After initial independent probes, read app/lineage.py, research.py and the gateway/budget boundary for the R4-2/R4-6 requirements that external traces cannot expose at every failed reservation. Origins caches fetched Lineage text/futures, not a depth-independent final origin; each root carries its own hop count. Needed missing/unaffordable originals fall back to that URL host. Plain original extracts cost1, render is omitted, rendered pages are reused for metadata, and originals remain lineage-only. These behaviors have passing black-box coverage. The fixed unused six-unit hold separately causes F2.

## Budget reservations and durability

SharedBudget.admits latches atomically on a failed shared reservation; all later member reserves fail. Reserve/check/account occurs synchronously on one event loop before awaiting anything. Gateway._call awaits durable recording before sending each WebRouter call. The store uses a temp file, flush/fsync, atomic rename and directory fsync; write middleware awaits persistence before returning non-GET/HEAD responses. Disk snapshots retain interrupted builds as failed with recorded spending, while control exports use settled pre-build snapshots. Positive billed-unit and batch-ceiling probes pass.

The same source inspection identifies F3's gap: refunds are applied by settle only in memory, followed by retry sleep or return without immediate durable settlement. The pre-send record does not establish refund durability. F4 is the separate fixed55-unit research affordability gate. These source observations corroborate the reproductions rather than replacing them.

## Provider boundary and failure

Provider operations use only AsyncWebRouter.search/extract/research with Nimble. The dependency manifest lists webrouter>=0.12.0 and its required extras. Rendered page requests use render=True; plain lineage fetches omit it. The research schema stays at the original six properties. Backend network-import search finds no direct provider HTTP client path. Tavily/Kernel/Browserbase are unused optional paths, so their session/configuration costs are untriggered. Ordinary provider refusals, cooldowns, uncertain delivery, late throttles and reachable-evidence failure cases pass; F3 concerns only retaining a completed refund across a kill.

## Ledger, probe corrections and privacy

R4-0..R4-8 are attached to affected rows. R4-8 makes the formerly informative permission at S4-118 an operative conditional restriction; the audit promotes it to normative while retaining reading_class/reading_requires. Audit totals are99 normative,7 ruled ambiguous and19 informative, with evidence for all106 required rows. The original125-unit reading remains recorded. Failing evidence is retained for exactly the six units listed above.

Probe corrections were limited to a duplicate cross-company fixture URL, a negative company name that itself contained the investor phrase, attribution of late unrelated provider calls, and expected partial HTTP bodies during a deliberate kill. The crash helper now always restarts its owned container; its interrupted infrastructure run is excluded. These are not product findings. The final default runner executes all304 cases and has only F1–F4 failures.

The clean clone is unchanged; no product code/tests were edited. Exports and tokens remain private in memory; temporary browser configuration is removed. Probes stay private until all stages close. All owned containers/networks are removed before handoff. Private TaskCreate was blocked by the runtime approval policy; no shared-board fallback was used.
