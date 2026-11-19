VERDICT: PASS
REVISION: cd24f51fb21b312aac2398adff8813a1b6276b57

# Stage 3, round 1

No blocking finding. Final complete independent suite: **246 passed, 0 failed**, including **39 Stage 3 cases** and **14 browser journeys**. The dispatched isolated sample harness exits 0 and claims stage 3. Ledger audit passes with exact-revision evidence for all 127 normative/ruled ambiguous units.

## Exact-revision commands and results

- `fclone cd24f51fb21b312aac2398adff8813a1b6276b57 /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-3-cd24f51fb21b` — exit 0; clean clone.
- `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx fserve cd24f51fb21b312aac2398adff8813a1b6276b57 3 20010 --container-port 8097` — exit 0; health 200.
- `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-3/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-3-cd24f51fb21b/stage-3` — **246 passed, 0 failed**, exit 0. Private final artifacts: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/runs-stage-3/second-reader-audit-e5d5f344-v8xrql0m/`.
- From `/Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026`: `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-3-cd24f51fb21b --stage 3 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s3-cd24f51f-round1` — exit 0, **claimed stage: 3**. This sample is supplementary evidence, not the verdict.
- `ledger-check 3 --phase audit --revision cd24f51fb21b312aac2398adff8813a1b6276b57` — exit 0; all 150 units accounted for, all 121 normative and six ruled ambiguous rows evidenced, no gaps.

The runner takes one stage-folder argument, builds/starts that supplied service itself, builds the documented mock web and the accepted Stage 1/2 legacy services, runs the public sample before authored fixtures, prints counts and exits nonzero on failure. Every service uses 2 vCPU and 3 GiB. Chromium runs in df-harness-runner through with-slot. The timestamping proxy forwards to the actual mock rather than inventing answers; exports and credentials remain private in memory.

## Temporal and candidate evidence

Effective-date fixtures cover valid leap dates, malformed/impossible Effective values, UTC publication fallback on both sides of midnight, missing dates and a header-shaped line occurring only in prose. The unchanged authority/publication/URL/provider/value ranking is rerun independently; effective and learned dates do not replace it.

Candidate identity and selected-value identity are tested separately: metadata-only changes update retrieved_at/true_from but retain candidate and selected learned_at; removing/regathering the same candidate preserves its first acquisition time while reselecting its value records a new transition time. History remains immutable. A selected date can change without a history/feed row, then affect the classification of a later real value transition. Disappearance rows use the build time while current unknown fields have null temporal metadata, as R3-2 requires.

Historical dossier reads select the last ready build at/before as_of, with equal instants and differing offsets resolved in build order. Later corrections do not leak into earlier fields/candidates/metadata. State is ready even while the current dossier is building or failed. Spending includes qualifying in-flight incurred units (R3-1) and charged failed-build units; earlier snapshots exclude later-started spending.

The valid-time matrix covers first effective dates, retroactive insertion replacing later URL versions, a later same-value version, candidate-free rendered versions, undated versions wiping prior support while holding on no date, later dated recovery, and an old URL absent from the latest gathering. Active versions from different builds are pooled and ranked, so current and valid-time winners may differ. Boundary dates and historical knowledge cutoffs are queried independently. Missing/invalid parameters, nonexistent/never-ready dossiers, normalized domains and ready-but-no-active-fact200 responses are distinguished.

## Executives, history and feed

Executive support probes exercise both phrases for each title, Unicode/two-/three-/four-word names, negation, partial phrase matches, a CEO-only control, missing company naming in the supporting sentence and a long supporting span. Members, candidates, per-title selected flags and citation order are independently checked. The research request schema stays at the original six fields.

Each title ranks independently. One disputed title makes executives contested; distinct uncontested names across different titles do not. Aggregate true_from is the latest selected member date or null when any member is undated. Correction typing uses only differing titles and their member dates: one CFO correction remains correction even when an unchanged COO's date pushes the aggregate into the future; removals and mixed transitions are changes. Valid-time executive answers follow the same per-title rules.

First-ready values receive initial history only; earlier failures do not consume that exception. Fields unknown after the first ready build later enter history/feed as change from null. Unchanged values and failed builds add no rows. A seven-field transition produces events in scalar-table order then executives; concurrent refreshes and multiple dossiers produce unique increasing seq values without missing/duplicate entries. Exclusive cursors, limit validation, a 63-entry default50 page, has_more and replay after later changes all pass.

## Upgrade and native transfer

The legacy folders are byte-for-tree equal to their accepted revisions: stage-1 tree `442c1d6ff697325d2da3a6798b0d51f340cb9772`; stage-2 tree `11571675c10451ddda8d0cc92ec56468a6230b07`. Both are built from the clean candidate clone, never imported as host code.

Actual Stage 1 and Stage 2 exports import successfully with old tokens, dossier IDs, spending and original idempotent responses. Stage 1 candidates derive from surviving excerpts under R2-5, with null true_from. Stage 2 candidates derive true_from from the UTC date of exported published_at, not omitted Effective headers; candidate learned_at equals retrieved_at. Current legacy state becomes one synthetic ready build at researched_at with all exported spend, one initial row per valued field and an empty feed. Earlier as_of is404. Never-ready imports have no snapshot. Executives stays unknown throughout imported legacy state; its first later selection is change unless it is the dossier's first ready build, then initial. The Stage1→Stage2→Stage3 chain also passes.

**R2-5/R3-3 limitations remain explicit:** frozen Stage 1 exports omitted full evidence beyond citations; frozen Stage 2 exports omitted older builds, Effective lines and candidate-free pages. Those facts cannot be recovered and are excluded by the foreman's assumptions. The final report must retain these earlier-stage limitations. No refetch or invented legacy history is used.

A native Stage 3 export/import preserves the query matrix over corrected, empty and undated page versions, current/as_of dossier data, values, candidate learning times, immutable histories and feed sequence. Replacement removes destination sessions, repeated import duplicates nothing, the destination clock is unchanged, and later events continue beyond the imported sequence. Import and completed replays make no provider calls.

## Abrupt restart and response durability

The runner kills and restarts the exact owned container without mounting an external state volume. Idle current/list/as_of/values/history/feed responses, users/password login, tokens, idempotent responses, clock and seq survive unchanged. Post-restart changes get larger sequence numbers.

Both a first build and a later refresh are killed during provider work. Recovery rolls back fields/candidates/researched_at/history/feed, reaches failed/unknown or the prior completed state, preserves completed users and the initiating202 response, and permits a new refresh. Interrupted spending satisfies R3-4's permitted range. Replaying the interrupted operation does not restart it.

Immediate kills after signup, login, clock, import and reset responses preserve their completed effects. Fifty concurrent signup responses are all durable after an abrupt restart; the slowest response in the final run is **0.694 seconds**, below the five-second requirement. A separate kill during concurrent signups preserves **all 50 acknowledged writes** and starts with valid uncorrupted state. Earlier same-revision runs also passed with43/49 acknowledged writes, so the observation is not limited to a single completion count.

After the clock-mode question was raised, **R3-5** ruled that a pre-reset clock retains system-time mode across restart rather than freezing. A fresh separate container, with no reset/clock calls, passes that case. Standing-clock persistence remains required and passes independently. No interpretation question remains open.

## Visual review and peer evidence

All 14 browser journeys pass. The inherited flows cover every route at1280/375 pixels, authentication and return navigation, polling, competing clients, latest read wins, refusal versus uncertainty, original-key/body retries, lost legacy responses across upgrade, and loading/failed/empty states. Executive-only contention does not appear in the six-field contested screen or reuse its field/evidence test IDs.

Viewed fresh desktop/mobile executive dossier, evidence and dated-value screenshots in the final run's browser-shots directory. Titles and names form a clear member group, sources are quoted and linked, candidates group by title with selected markers, and Holds from/First learned/Retrieved/Published are understandable. Undated members produce “Start date not stated”; dated selected values show “Holds from … Learned …”. Screens remain coherent and have no horizontal overflow at375 pixels.

Only after the complete independent probes, read `verdicts/stage-3/product-user-cd24f51fb21b.md`: PASS after the full1440/375 route/flow walk and sample-company executive cases. Its minor quote-wrapper, baseline and tap-target notes are nonblocking. No exact-revision verifier verdict existed when checked; no peer test or walk-script source was read.

Early probe iterations corrected inherited six-field/exact-cost expectations, an all-empty evidence-render wait and the null-date UI wording. A candidate-free temporal fixture was tightened to contain an ordinary CEO statement phrase so its page is actually rendered; that gathered empty version passes. These were probe refinements, not product edits or confirmed product findings. The final default runner includes all cases and exits0.

## Inherited contract

All inherited API, evidence/grammar/span, candidate/rank, rate-limit/budget, concurrency, reset/import/export and browser regressions rerun against Stage 3. Delivery/dependency files and password call sites were checked after probes. Requirements/constraints/password hashing are unchanged from the accepted earlier implementation; requirements SHA256 `6e94dab8b2f77a2a420f3e3a77f92faeacee84bdbd9973e93d83bd37b9bc3de4`, passwords.py `7ae7952a14c1eaa3e8c654eee14c51173ac8b8ed672c5005f7bb28f690e0904b`. Password operations run through asyncio.to_thread. The Dockerfile installs dependencies at build time, copies all assets and gives its nonroot user a writable /srv/data directory. Runtime assets come from the image. Live-provider timing is inspected statically; no real endpoint is called.

## Durability and provider boundary

Source was read after the independent probes only for persistent-store/write-boundary and provider/resource obligations that finite external tests cannot establish for every interleaving. app/store.py serializes save requests by ticket, writes a temporary file, flushes and fsyncs it, atomically replaces state.json and fsyncs its directory. app/routes.py awaits service.persist before returning every non-GET/HEAD response. A grouped save only releases a covered ticket after the durable write. app/service.py loads state and clock at startup, snapshots via the running-build-excluding export and persists after build publication. This corroborates the HTTP/kill tests; a successful write response is not sent before its save completes.

Provider requests use only AsyncWebRouter.search/extract/research, select Nimble, pass render=True for extracts and retain the fixed six-property research schema. The manifest lists webrouter>=0.12.0 and required extras. Tavily/Kernel/Browserbase are unused optional paths. The active cost table and reserve-before-call budget were inspected; actual logs independently reconcile calls, free refusals, uncertain delivery and the80-unit limit. The late-throttle fix remains: 429 retries wait1.1 seconds without an elapsed cutoff, up to five attempts; other retryable failures use the separate window. Backend network-import search finds no direct provider HTTP client path.

## Ledger and privacy

R3-1..R3-5 are attached to affected rows, with original reading requirements retained separately where an assumption changes them. Every normative/ruled ambiguous row has passing evidence for this exact hash. Probes remain private until all stages close; no later-stage spec was read. The clone stays clean; no product code/tests were edited. Exports and tokens stayed private. All owned containers/networks are removed before handoff. Private TaskCreate was blocked by the runtime approval policy; no shared-board fallback was used.
