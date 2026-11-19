VERDICT: BLOCK
REVISION: 3cf3cef0862c212f6f572712876ad700e9e0e381

# Stage 2, round 1

One reproducible candidate-completeness failure blocks this revision. Normal candidate/ranking, browser and upgrade journeys pass; the isolated sample harness claims stage 2. The late-throttle case below fails in a focused run and in the complete suite.

## S2-F1 — A first extract 429 is abandoned after a slow research response

Broken units: **S2-002, S2-005 and S2-054**, including inherited evidence completeness under R1-2. The build has enough time and research budget to obtain an ordinary supporting page but stops after its first throttled extract.

Using the required kit mock with the independent one-page `reader-full.test` fixture:

1. Delay the Nimble research operation by **7 seconds**, using the documented mock delay mode.
2. Set Nimble extract to **throttle**, which answers the first occurrence of that call with 429 and subsequent attempts normally.
3. Submit authenticated `POST /dossiers` for `reader-full.test` and read until terminal.

Observed: **ready**, **33 spent_units**, every field unknown with no candidates. The extract trace is exactly **[429]**: the service makes no retry. Its sole page supports the six fields, including `Reader Full CEO: Dana Ruiz.`; the same fixture completes normally elsewhere in the suite. The successful search/research calls cost 33, the refused extract costs zero, and the required successful rendered extract would cost 3, well within 80. Waiting the required second and retrying would also fit within ten seconds; the slower research call does not turn the fast-provider bound into a deadline.

Reproduce from any clean clone of this exact revision:

```sh
SECOND_READER_ONLY=stage2-slow-research-then-throttled-extract SECOND_READER_NO_BROWSER=1 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh <clean-clone>/stage-2
```

The command builds/starts the supplied stage, accepted Stage 1 service and kit mock, runs the required public sample, and exits 1 for the stated case. It prints ready/33/unknown/empty candidates and extract statuses [429]. No external provider is contacted.

The provider-boundary/timing review prompted this focused probe after the initial complete set passed. Source corroboration: `Timing.for_environment` gives non-live endpoints a **6.5-second retry_window_s**. `Gateway._call` returns on any retryable failure when the **whole build's elapsed time** exceeds that window, even if this is the first attempt for the extract and the failure is a free 429. This cutoff is earlier than the available build time/budget and is not an evidence-completeness exception. The finding itself is established by the HTTP/mock trace.

## Exact-revision commands and results

- `fclone 3cf3cef0862c212f6f572712876ad700e9e0e381 /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-3cf3cef0862c` — exit 0; clean clone.
- `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx fserve 3cf3cef0862c212f6f572712876ad700e9e0e381 2 20010 --container-port 8097` — exit 0; health 200.
- Complete independent runner: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-3cf3cef0862c/stage-2` — **204 passed, 1 failed**, exit 1. Only S2-F1 fails. All 12 browser journeys pass, including initial loading and failed-build recovery.
- The focused delayed-research/throttled-extract run also fails with the exact outcome above. A separate 375px failed-build/recovery journey passes.
- From the kit directory: `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-3cf3cef0862c --stage 2 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s2-3cf3cef0-round1` — exit 0, **claimed stage: 2**. This sample is further evidence, not the stage verdict.

The previous complete run, before the focused late-throttle and final feedback checks, passed 202/202. The full run including the late-throttle and failed-build cases passed 203 and failed only S2-F1. Probe corrections were limited to matching actual mock-rendered text, preserving the legacy source transcript when the destination is reset, and waiting for asynchronous UI completion. No product file or test was edited.

## Independent behavioral coverage

The root run.sh takes one stage-folder argument, builds/starts all services itself, runs every default probe, prints counts and exits nonzero on failure. Product code is never imported on the host. Each service runs with 2 vCPU and 3 GiB. The browser runs Chromium through with-slot in df-harness-runner. A forwarding proxy records provider request/answer times and canonical argument identity while forwarding to the real kit mock; it does not synthesize provider statuses or record credentials.

API probes include all inherited Stage 1 controls/error/idempotency/concurrency/clock/spending/transfer regressions, plus exact complete candidate sets, duplicate excerpt deduplication, multiple values per page, authority/recency/URL/value ranking, own/filing equivalence, invalid/missing metadata, www-host fallback, future publication dates, integer 0/9/10 sorting, winning-value citation order, unsupported research claims whose pages support other fields, gathering after all fields already have values, and fresh candidate replacement.

The normal rate-limit case passes: all used operations can receive three 429s, retries respect at least one second from the answer, refusals cost zero, and actual cost stays within 80. Timestamping is performed in the forwarding proxy, independently of product timing code.

Browser probes cover every required route at 1280 and 375px, signup/login/logout, signed-out return navigation, visible input labels/focus, exact data-testid/data attributes, zero values, selected legal-name search, empty/not-found states, field/evidence/contested order, timestamp display in its own offset plus exact RFC3339, at-most-two-second building polling, latest manual and poll reads winning over delayed predecessors, confirmed research/refresh refusals, concurrent-client create/refresh, committed lost research/refresh responses, original key/body retries, and recovery without an extra build.

## Upgrade and R2-5 limitation

The legacy image is built from stage-1 in the clean candidate clone. Its git tree hash **442c1d6ff697325d2da3a6798b0d51f340cb9772** equals stage-1 at accepted revision a8789dcd65a18ca385d968116c51d23590913c33.

The upgrade fixture makes a legacy legal-name citation also support an unselected CEO. Import tests every surviving excerpt against every field, creates that additional CEO candidate, deduplicates page/value pairs using the first exported excerpt, assigns null kind/publication metadata and preserved researched_at as retrieved_at, and recomputes selection/status/citations. Old tokens and original keyed responses remain usable, import makes no provider call, a Stage 2 export round-trips metadata exactly, and the next ready refresh replaces imported candidates.

The browser holds a token present in the legacy export. Its committed research response is lost at the legacy backend, state is imported between requests, and the same existing browser retries with its original key/body. It recovers the original response, displays the imported dossier/evidence/list, and remains signed in without a manual page reload or another build.

This pass is explicitly limited by **R2-5**: accepted stage-1 exports retained citation excerpts, not all served page text or metadata. Values that did not survive in those excerpts are unrecoverable and are not required by the ruling. The accepted stage-1 folder remains unchanged; this limitation must remain in the foreman's final report.

## Peer results read after independent probes

After the initial complete independent API/browser run, read `verdicts/stage-2/verifier-3cf3cef0862c.md` and `product-user-3cf3cef0862c.md`. The verifier reports PASS, 222/222 after amendments, exact candidate sets on its corpus and passing browser/upgrade tests. Product-user reports PASS with route/flow screenshots at desktop and 375px. Those results are attached as further evidence, not substituted for the independently reproduced S2-F1 counterexample. No other seat's test or walk-script source was read.

## Visual review

Viewed the exact candidate's desktop dossier, 375px evidence/contested screens, 375px failed-build feedback and uncertainty feedback. The layout has a consistent navigation/card/typography system; values and statuses are clear; quoted sources sit beside the selected values on desktop and wrap below them on mobile; candidate rank/selection and human metadata are scannable. Known/contested/unknown, building/failed, refusal and uncertainty have distinct text/markers/feedback. Inputs have visible labels and focus; the browser journeys find no horizontal overflow.

Independent images are regenerated by the runner under its printed PROBE_WORK/browser-shots directory. Reviewed the full-run directory `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/runs-stage-2/second-reader-audit-f449de09-l9w4mh04/browser-shots`, including the explicit initial-loading screen, plus earlier same-revision desktop/mobile/failed-state images. Public corroborating screenshots are in `journey/stage-2/3cf3cef0862c/`, including d-10-evidence.png, m-11-contested.png and m-17-refresh-uncertain.png. Product-user's copy/alignment/tap-target suggestions remain nonblocking notes; no new visual finding is asserted here.

## Source evidence after probes

### Inherited contract

The inherited API regression set was rerun against stage-2 with its explicit candidate/status/render changes. Delivery and dependency files were read. Requirements/constraints/passwords/support are byte-identical to the accepted Stage 1 files. Requirements SHA-256 is `6e94dab8b2f77a2a420f3e3a77f92faeacee84bdbd9973e93d83bd37b9bc3de4`; passwords.py SHA-256 is `7ae7952a14c1eaa3e8c654eee14c51173ac8b8ed672c5005f7bb28f690e0904b`; support.py SHA-256 is `f9795b8f7c5f6d460ffc4494b43934c6d154d8b0e74c1a29b9edc06a0d7a89a9`. Fresh hashing call-site search shows asyncio.to_thread for reset/signup/verification. Dockerfile installs dependencies at build time and copies the application, including app/web assets, into the single image. Live-provider timing configuration was inspected statically; no real provider was called. S2-F1 remains a failure of the inherited completeness obligation.

### Provider boundary

Read app/providers.py for routing/configuration/timing and searched backend network imports. Provider operations use only AsyncWebRouter.search/extract/research, select Nimble and its environment configuration, and disable hidden SDK retries. Rendered extract passes provider_options={"render": True}; its requested-URL cost is 3. Dependency manifest explicitly lists webrouter>=0.12.0 and required extras. API fixtures and provider logs corroborate loaded text and actual citation origins. No provider request is made by import or ordinary reads.

### Optional providers and cost

Kernel, Browserbase and Tavily operation paths are unused; their optional environment/configuration/cost clauses have no runtime trigger in this implementation. The backend candidate provider-order table lists nimble, tavily, kernel, browserbase in the required order; actual generated candidates use Nimble. Active costs are independently reconciled against logs, including missing pages and free refusals.

### Retry timing and budget

Read app/providers.py and app/budget.py after the initial probe set. Reservations include spent plus outstanding units and occur before each awaited provider call. Settlement distinguishes provider refusals from uncertain delivery. The 429 pause waits 1.1 seconds and records the union of concurrent wait intervals, avoiding double subtraction; the ordinary throttled-build probe passes. S2-F1 is the separately attached failure caused by the global non-live 6.5-second retry cutoff, not a pricing or cooldown violation.

## Ledger and privacy

R2-1..R2-5 are attached to affected rows; the R2-5 migration interpretation replaces the original all-text expectation in the audit while retaining that original reading. Every normative/ruled ambiguous unit receives exact-revision evidence. Failing evidence remains on S2-002/S2-005/S2-054, so audit ledger-check must remain nonzero and no stage PASS is claimed.

Exports and tokens stayed in memory; temporary browser configuration was removed. Probes remain private until every stage closes. The exact clone is unmodified. Private TaskCreate was rejected by the runtime approval policy; no shared-board fallback was used.

`ledger-check 2 --phase audit --revision 3cf3cef0862c212f6f572712876ad700e9e0e381` reports the three failing units above, with no missing evidence among all 139 normative and five ruled ambiguous units. All probe containers/networks and the fserve container have been removed.
