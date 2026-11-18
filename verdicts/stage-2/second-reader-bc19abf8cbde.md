VERDICT: PASS
REVISION: bc19abf8cbde23c3a2fa50f23baa55dbfe48d731

# Stage 2, round 2

No blocking finding. The reported S2-F1 failure passes its first focused retest and the complete independent suite: **205 passed, 0 failed**, including all **12 browser journeys**. The isolated sample harness exits 0 and claims stage 2. Every normative and ruled ambiguous Stage 2 unit has passing evidence for this exact revision.

## Reported problem retested first

S2-F1 (S2-002/S2-005/S2-054): research is delayed seven seconds, then the first rendered extract receives 429. The service now retries, obtains the supporting page, and returns all six fields with their candidates. The strengthened full-suite case requires extract statuses **[429, 200]**, at least one second between the first answer and retry, and spent_units equal to the independently logged provider cost, at most 80 (36 units here). The case passes in 8.321 seconds in the complete run. This is the same corpus and fault sequence that failed on 3cf3cef0862c212f6f572712876ad700e9e0e381.

Focused reproduction:

```sh
SECOND_READER_ONLY=stage2-slow-research-then-throttled-extract SECOND_READER_NO_BROWSER=1 /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-2/run.sh <clean-clone>/stage-2
```

Result: sample plus focused case **2 passed, 0 failed**, exit 0. The full run executes that regression before the other API cases.

## Exact-revision commands and results

- `fclone bc19abf8cbde23c3a2fa50f23baa55dbfe48d731 /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-2-bc19abf8cbde` — exit 0, clean clone.
- `BUILDX_CONFIG=/Users/sunzeyu/dev/band-factory/work/second-reader/buildx fserve bc19abf8cbde23c3a2fa50f23baa55dbfe48d731 2 20010 --container-port 8097` — exit 0, health 200.
- `SECOND_READER_FIRST=stage2-slow-research-then-throttled-extract /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-2-bc19abf8cbde/stage-2` — **205 passed, 0 failed**, exit 0. Results identify this exact clone. Artifacts: `/Users/sunzeyu/dev/band-factory/work/second-reader/probes/runs-stage-2/second-reader-audit-95e3c14d-bg_0hegf/`.
- From `/Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026`: `BUILDX_CONFIG=/Users/sunzeyu/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-2-bc19abf8cbde --stage 2 --mode isolated --out /Users/sunzeyu/dev/band-factory/work/checks/second-reader-s2-bc19abf8-round2` — exit 0, **claimed stage: 2**. This is supplementary sample evidence.
- `ledger-check 2 --phase audit --revision bc19abf8cbde23c3a2fa50f23baa55dbfe48d731` — exit 0, all 188 units accounted for and all 144 normative/ruled ambiguous rows evidenced.

The runner builds and starts the supplied stage itself with 2 vCPU and 3 GiB, uses the documented kit mock and sample corpus, and runs Chromium in df-harness-runner through with-slot. A forwarding proxy timestamps the real mock's answers; it does not synthesize status codes or log credentials. No product modules are imported on the host.

## Behavioral coverage

The complete inherited API set covers authentication, input/error boundaries, exact normalized domains, idempotency precedence and original responses, concurrent create/refresh, frozen clock, reset cancellation, pagination, provider failure/spending, budget reservation, citation grammar and provenance, safe long spans, export/import replacement, cross-process tokens/retries, and pre-build snapshots.

Stage 2 probes compare complete candidate sets and independent ranking, including multiple values per page, duplicate excerpts, own/filing equivalence, publication offsets/null/invalid/future values, URL and numeric value ties, zero funding, all winning-value citations, unsupported research claims whose cited pages support other fields, and gathering remaining pages after every field already has a value. Refusals cost zero; ordinary repeated 429s respect cooldown and logged spending. Rendered text supplies the candidates and refreshed candidates replace the previous build's set.

Browser journeys cover every required route at 1280 and 375 pixels, signup/login/logout and return navigation, visible labels/focus, required test IDs and raw data attributes, list filtering and ordering, evidence/contested ordering, zero and unknown values, timestamps in their own offset plus exact RFC3339, empty/loading/not-found/failed states, polling while building, latest manual and poll reads winning, other-client builds, confirmed refusals, committed lost responses and original-key/body retries.

## Upgrade and R2-5 limitation

The legacy service is built from the clone's frozen stage-1 tree, hash **442c1d6ff697325d2da3a6798b0d51f340cb9772**, equal to accepted Stage 1 at a8789dcd65a18ca385d968116c51d23590913c33. Cross-field migration tests pass: every surviving citation excerpt is checked against every field, page/value candidates are deduplicated, null kind/publication metadata and researched_at retrieval time are preserved, and selection/status/citations are recomputed. Existing tokens and original keyed responses survive; import makes no provider call; Stage 2 state round-trips; the next ready refresh replaces legacy candidates.

The browser upgrade journey retains a legacy bearer token and a pending committed write whose response was lost. Import occurs between requests, then the existing browser retries with the same body/key, recovers the original response and displays imported data without signing in again, manually reloading or starting an extra build.

This evidence follows **R2-5**: accepted Stage 1 exports retained citation excerpts rather than all served page text and metadata. Values absent from those surviving excerpts are unrecoverable and are excluded by the ruling. This limitation remains for the foreman's final report; the accepted stage-1 folder is unchanged.

## Peer results read after independent probes

Only after the complete independent run, read `verdicts/stage-2/verifier-bc19abf8cbde.md` and `product-user-bc19abf8cbde.md`. Verifier reports PASS, 222 original tests plus the new slow-research/throttled-extract regression, with all 13 post-seal tests passing. Product-user reports PASS after the full desktop/375px walk; its remaining small navigation/back-link tap-target note is nonblocking. No other seat's test or walk-script source was read.

## Visual review

Viewed fresh independent screenshots under the run's `browser-shots/`: desktop dossier, mobile building feedback and mobile contested fields. Values/statuses are prominent, quoted citations sit beside selected values on desktop, and the mobile hierarchy wraps without horizontal scrolling. First-build fields now say “Research in progress” and “Not researched yet.” Known/unknown/contested, building/failed, refusal and uncertainty remain distinct. The typography, spacing, navigation, controls and metadata form a coherent research interface. Automated browser journeys also verify labels, keyboard focus and every required route at both widths. The product-user's exact-revision screenshot review supplements this evidence.

## Source evidence after probes

### Inherited contract

Read delivery/dependency files and checked unchanged hashes against the earlier audit: requirements `6e94dab8b2f77a2a420f3e3a77f92faeacee84bdbd9973e93d83bd37b9bc3de4`, constraints `8bd3602d0c3d64635e1d960c31eee12df702356e2b7bde2898daa9203a83481d`, passwords.py `7ae7952a14c1eaa3e8c654eee14c51173ac8b8ed672c5005f7bb28f690e0904b`, support.py `f9795b8f7c5f6d460ffc4494b43934c6d154d8b0e74c1a29b9edc06a0d7a89a9`. Password hashing/verification call sites use asyncio.to_thread. Docker installs dependencies during build and copies application assets into one image. Live timing configuration is statically inspected; real providers are not contacted.

### Provider boundary

Read app/providers.py and searched backend network imports after the probes. Provider requests use AsyncWebRouter.search/extract/research with Nimble; SDK retries are disabled. Rendered extract passes provider_options={"render": True}. The manifest lists webrouter>=0.12.0 and required extras. Provider logs and candidate provenance independently corroborate the served text; reads and import make no provider calls.

### Optional providers and cost

Tavily, Kernel and Browserbase are unused, so their optional configuration/session/cost clauses have no operational trigger. The implementation's candidate provider order was unchanged from the prior source audit. Nimble calls use lite search, rendered extract and research; the active costs are reconciled against logs, including no-page responses, refusals and connection losses.

### Retry timing and budget

The exact diff in app/providers.py separates maximum attempts from elapsed time: a throttled failure bypasses retry_window_s and waits 1.1 seconds before retrying, up to five attempts. The elapsed-time window now applies only to other retryable failures. The 429 waiting intervals are excluded without double-counting concurrent waits. app/budget.py reserves spent plus outstanding units before each awaited call and settles charged versus refused outcomes. Independent ordinary and late-throttle cases pass the cooldown, completeness and cost assertions. S2-F1 is resolved.

## Ledger and privacy

All 139 normative and five ruled ambiguous rows have exact-revision passing evidence; no unit remains open. Historical failing evidence remains tied to its historical revision. R2-1..R2-5 are recorded, and the original broader migration reading is retained separately from the ruled requirement.

Exports/tokens remain private in memory. The exact clone stays clean; no product code/tests were edited. Probes remain private until every stage closes. All owned containers/networks are removed before handoff. Private TaskCreate was blocked by the runtime approval policy; no shared-board fallback was used.
