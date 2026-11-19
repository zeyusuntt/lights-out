VERDICT: BLOCK
REVISION: 56b72c3a7f749b788b119895b55f980bf9e26be5

# Second-reader, stage 1, round 2

The original S1-227 finding is fixed, and S1-226 passes. One new blocking finding remains: **S1-245: queued operations are charged before they invoke a provider.**

Start one dossier, wait 60 seconds, then start 15 different dossiers against 82-second searches. Later builds hold the shared 32 provider slots when the older window expires. The older dossier finishes ready at 286.159 seconds but reports **47 units**. Its actual calls cost **37**: research 25, fast search 5, seven lite searches 7. No extract from any build occurred, and none of its follow-up searches reached the adapter. Ten units came from canceling local semaphore waiters before invoking WebRouter.

Reproduce on a clean exact-revision clone:

```sh
fclone 56b72c3a7f749b788b119895b55f980bf9e26be5 /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-56b72c3a7f74-queue
SECOND_READER_CASE=live-queued-call-accounting /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-56b72c3a7f74-queue/stage-1
```

It builds and starts itself, uses an internal network and the dispatched mock, and exits 1 after just under five minutes with `queued calls never sent must not be charged`: reported 47, confirmed 37, all-extract allowance 0, old follow-up calls received 0. At most 15 HTTP requests are in flight together, within the specified 50. The default runner also includes the case.

Source corroboration: gateway.py:139 reserves before semaphore acquisition at line 142; its CancelledError handler at lines 148–150 charges cost even if `call(timeout)` at line 147 never executes. Build.py:83–87 cancels such waiters when the older window expires. Work canceled before it begins a provider call must release its reservation without charging it; genuine in-flight timeouts still cost full units.

Validation:

- Reported deadline reproduction first: 128/128 checks passed; final state observed at 288.50 seconds.
- Whole existing suite afterward: 7,628/7,628 passed. Improved live measurements: ready at 285.099 seconds, gathering after 120 seconds, and two interrupted calls waited 36.073/36.074 seconds. Spending of 39 matched actual calls plus those cancellations. Thus S1-226 and S1-227 pass.
- New queued-call case: 339 checks, 338 passed, one failure above. No other finding remains.
- Clean fclone/fserve and health passed; no product file or test was edited. All service containers used the exact revision and 2 CPU/3 GiB.
- Verifier PASS was read only after these probes. Its N3 notes the same possibility of charging a request never sent; this reproduction supplies the blocking evidence. Findings were not changed to agree with that PASS.

Commands, source-review scope and all ledger evidence: `ledger/stage-1-audit-56b72c3a7f74.md`. Reports remain private under `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/`: `deadline-first-56b72c3a7f74.json`, `results-56b72c3a7f74.json`, and `queued-56b72c3a7f74.json`. Probe sources remain unpublished until all stages close.

Reading validation exits 0. Audit validation exits 1 with only S1-245 open; all other normative and ruled ambiguous rows have passing evidence on this exact revision.
