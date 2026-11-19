VERDICT: PASS
REVISION: a7228733bd425af053de0063ec2a3fc1ef68d873

# Stage 4, round 3

No blocking findings or evidence gaps. The five prior findings pass their first targeted retest and the complete independent suite. Final result: **305 passed, 0 failed**, including **all 16 browser journeys**. The dispatched isolated sample exits 0 and claims stage 4. The ledger audit exits 0 for this exact revision.

## Retested first

```sh
SECOND_READER_ONLY=stage4-shared-budget-boundaries-and-affordable-evidence,stage4-affordable-research-only-evidence-in-batch,stage4-scalar-standing-origins-and-selection-reset,stage4-lineage-reserve-keeps-affordable-evidence-complete,stage4-refused-call-refunds-survive-interrupted-retry-wait SECOND_READER_FIRST=stage4-shared-budget-boundaries-and-affordable-evidence SECOND_READER_NO_BROWSER=1 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-4-a7228733bd42/stage-4
```

Exit 0, **6 passed, 0 failed**: sample plus all five reported findings. Private work directory: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/runs-stage-4/second-reader-audit-6809182f-k7zy6qiz/`.

- F5: batch-reader-aa stays complete at budget 30, as at 14 and 20. All thirteen shared-budget ceiling/billing controls pass under R4-6/R4-9.
- F4: hidden-cedar's research-only CEO is known in the affordable 49-unit batch. Fixing F5 does not lose research-only evidence.
- F1: a newly selected scalar value and a return to a former value each begin a new corroboration stint; equal-time build order is respected.
- F2: all 15 searched supporting pages are gathered within 80 units without unused lineage headroom.
- F3: all 11 completed refused attempts show zero before the kill and zero after restart. The trace excludes a racing retry; no old reservation reappears.

All five pass again in the full run.

## Exact-revision commands and results

- `fclone a7228733bd425af053de0063ec2a3fc1ef68d873 /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-4-a7228733bd42` — exit 0, clean clone.
- `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx fserve a7228733bd425af053de0063ec2a3fc1ef68d873 4 20010 --container-port 8097` — exit 0, health 200. The exact owned container was removed with `fstop` afterwards.
- `SECOND_READER_FIRST=stage4-unconfirmed-investor-still-needs-affordable-research /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-4-a7228733bd42/stage-4` — exit 0, **305 passed, 0 failed**. FIRST changes order only; all probes run. Private artifacts: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/runs-stage-4/second-reader-audit-1270bb22-y2r9jzps/`.
- From `/Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026`: `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-4-a7228733bd42 --stage 4 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s4-a7228733-round3` — exit 0, **claimed stage 4**. This is a sample, separate from the independent evidence.
- `ledger-check 4 --phase audit --revision a7228733bd425af053de0063ec2a3fc1ef68d873` — exit 0, all 125 units accounted for and all 106 required rows evidenced.

The one-argument root runner builds and starts the supplied folder, the documented public mock sample, private authored corpora, and real accepted legacy services. Services use 2 vCPU and 3 GiB. Builds/browser work use `with-slot`; Chromium runs in df-harness-runner. No product module runs on the host. The runner cleans up its owned containers/networks and prints counts.

## Inherited contract

All inherited API, error/boundary, idempotency, concurrency, evidence/support, sentence/span, complete-candidate/rank, temporal, transfer, control, durable-state and browser regressions pass with stage-4 overrides. The new investor case distinguishes a real candidate from a confirmed member: one news source initially cannot establish membership, but an affordable research-cited own page supplies it. Its unbatched and 49-unit batch builds both return Bluebird Capital. No oracle was weakened after seeing code.

Requirements, constraints and password hashing remain unchanged from earlier audited revisions: requirements SHA256 `6e94dab8b2f77a2a420f3e3a77f92faeacee84bdbd9973e93d83bd37b9bc3de4`, constraints `8bd3602d0c3d64635e1d960c31eee12df702356e2b7bde2898daa9203a83481d`, passwords.py `7ae7952a14c1eaa3e8c654eee14c51173ac8b8ed672c5005f7bb28f690e0904b`. Hashing calls use `asyncio.to_thread`. Docker includes dependencies/assets and its writable state directory in one image; PORT 8097 is exercised. Actual live providers are not contacted.

## Lineage planning and originals

Passing traces cover normalized registrant/first-publisher handling, own downgrade and the separate lookalike predicate, first-publisher precedence, self Canonical, cycles, missing originals, root-specific three-hop depth despite cached pages, eight independent originals within 80, and lineage-only originals excluded from candidate evidence. Rendered text is reused for metadata; otherwise plain Nimble extracts obtain original headers. Missing/unaffordable originals use their normalized URL host under R4-2. No fixed reserve suppresses affordable candidate pages.

Source inspection after the targeted probes confirms the remaining provider/budget boundaries. In a batch, searches precede the constrained page-gathering decision. The constrained branch renders searched pages before considering research and checks 25 plus one three-unit render; a full affordable plan can still research and render its cited pages. Unbatched behavior remains unchanged. Black-box F5/F4 and the investor case cover both affordable page-first work and research-only evidence. Origin resolution retains per-root hop counts while sharing fetched text.

## Budget reservations and durability

Build and shared live reservations remain synchronous before any await; batch admission latches atomically on the first unaffordable call. Internal accounting uses live spending, while responses publish spending only after persistence. A free refusal settlement is persisted before retry/return. The new shared-budget property changes planning, not the reserve-before-send boundary.

The store remains SHA256 `12fae8ce0f66e940fa3c4c688e9cd741aea9893a23607605ff1d24cd1021aa7d`: snapshot, temporary write, flush/fsync, rename and directory fsync, then its publication callback. Write responses wait for persistence. Completed idle dossier/list/batch reads repeatedly match provider billing without drift. All tested build ceilings remain at most 80 and batch ceilings at most the caller budget.

Abrupt idle and in-progress restarts preserve unrelated acknowledged writes, tokens, completed replies, clock, temporal data and sequences. Running standalone/batch builds become terminal within 10 seconds of health; all billed units remain counted; failed builds leave fields/history/feed unchanged. The completed-refund kill test passes separately. Fifty concurrent durable signup responses take at most **0.687 seconds**; all **37 acknowledged writes** captured before the separate mid-write kill survive. A later explicit refresh is new work, while replaying the original operation starts no build and retains its original JSON reply.

## Provider boundary and failure

Only the in-container Python AsyncWebRouter boundary reaches providers. The manifest lists webrouter>=0.12.0 and required extras. Research still asks for the six original schema fields. Candidate text comes from Nimble rendered extracts; lineage originals use plain extracts. Optional Tavily/Kernel/Browserbase paths are unused. Cooldown, late throttle, all-research refusal, all-provider failure, missing extracts, uncertain connection costs and free error settlement regressions pass. Builds retain all reachable supported fields when research refuses and end failed when every provider call fails.

## Temporal data, members and transfer

Current versus standing origins, historical source isolation, scalar selection resets, retained/removed/rejoining members and weak-member removal under R4-4 all pass. Investor grammar, suffix/amount/negation/Unicode cases, membership, all member-candidate selected flags, candidate versus member order, grouped citations, member/field dates, valid-time versions, correction typing and investor-last feed order pass.

The accepted earlier folders remain exact: stage 1 tree `442c1d6ff697325d2da3a6798b0d51f340cb9772`, stage 2 `11571675c10451ddda8d0cc92ec56468a6230b07`, stage 3 `1e3d3070c891f8aa4e69be40ca391e5a2bfbb29f`. Real exports from all three preserve recoverable state, tokens and idempotent responses; origin fallback uses URL hosts. Stage-3 builds/page versions retain as_of/values/history/feed answers and reconstruct standing history. Investors is unknown in legacy builds until a later qualifying build.

R2-5/R3-3 limitations remain for the final report: the frozen stage-1 export omitted unselected full evidence, and the stage-2 export omitted old builds/Effective/empty-page versions. Imports cannot recover that missing material; the ruled synthetic legacy views pass. Native stage-4 transfer preserves full temporal state, origins, batches, ownership, costs and original replies. A running control export excludes unfinished builds/spending under R1-4/R4-7; import makes no provider calls and imports batches done. Reset and replacement remove old state durably.

## Visual review

All 16 browser journeys pass at 1280/375: routes/test IDs, authentication, search, status/empty/loading/error feedback, latest reads, polling, competing clients, lost-response retries and legacy sessions. Executives/investors do not collide with the six-field test-ID contract. Exact-revision mobile investor dossier and desktop evidence screenshots were viewed in the full run: per-member independent sources, unconfirmed mentions, dates and quoted linked citations remain legible; no horizontal overflow is observed.

Only after the complete independent run, read `verdicts/stage-4/product-user-a7228733bd42.md`: PASS for the full 1440/375 regression walk, with unchanged minor small-link target notes. No exact-revision verifier verdict existed when checked. No peer test or walk-script source was opened. Peer results did not alter any independent finding or oracle.

## Ledger and privacy

All 125 units remain accounted for: 99 normative, 7 ruled ambiguous and 19 informative. All 106 required rows have passing exact-revision evidence; no gaps remain. R4-0 through R4-9 and inherited migration assumptions are retained. The only added probe this round is the candidate-versus-member investor research case, written before reading this revision's product code.

The exact clone is clean; no product code/tests were edited. Every owned container/network has been removed. Exports and tokens stay private, and temporary browser configuration is deleted. Probes remain private until the foreman closes every stage and requests publication. Private TaskCreate failed under the runtime approval policy; no shared-board fallback was used.
