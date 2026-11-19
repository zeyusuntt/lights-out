VERDICT: BLOCK
REVISION: 3b729f1aec21154fa42fc5ca79d95e86f90f8768

# Independent second reading audit, fix round 4

## Previously reported findings: resolved

SR1-04 was retested first: reset during a partial POST body returns 401 for the old request and leaves the new state empty; unchanged import retaining the token still permits 202. SR1-01, SR1-02 and SR1-03 then passed their first retests and the full run. The six-claim case is complete within 80 units, and the delayed citation case rejects header text while preserving valid prose inside the live deadline.

## Blocking finding SR1-05 — S1-224/S1-312: 50 distinct builds miss the ten-second fast-provider bound

S1-224 requires a build whose provider calls each answer within one second to finish within ten seconds of its initiating request. S1-054 allows 50 requests in flight. With 50 ordinary concurrent creates for different companies, all 50 dossiers remain building more than ten seconds after every create response has already returned.

The test uses the unchanged official mock and valid independent companies: ten searchable administrative pages with no supported values, plus six unsearchable pages with supported Nimble research claims. A transparent proxy forwards exact mock answers and delays charged POST responses about 0.6 seconds. It measures direct replies and full research start-through-result intervals. The submission remains under 2 vCPU/3 GiB on an internal network; no provider errors or refusals occur.

Observed on this exact revision:

| Measurement | Full run |
|---|---:|
| Single-company control reaches ready | 3.385 s |
| 50 concurrent POST responses, all 202 | 0.056 s batch |
| Still building 10.1 s after the last 202 | **50 of 50** |
| All 50 finally ready after the last 202 | **16.604 s** |
| Maximum provider HTTP reply interval | **0.614 s** |
| Maximum whole research start-through-result interval | **0.692 s** |
| Provider HTTP requests | 1,300 |
| Total units, agreeing with provider log | 2,400 |

All 50 eventually become ready with six known fields; no build exceeds 80 units. This is a completion-time defect. There are no service requests between the create batch and the first 10.1-second checkpoint. Each initiating request was received before its 202 response, so that checkpoint conservatively gives every build more than ten seconds. S1-312 requires the stated constraints at each read; those reads still return building.

The same case failed standalone: single control 3.378 seconds, all 50 still building at the checkpoint, all ready after 15.988 seconds, maximum HTTP reply 0.610 seconds and maximum whole research interval 0.695 seconds. This confirms the one-second premise for research as well as search/extract, including its polls/result.

Reproduce from a fresh exact clone:

```sh
fclone 3b729f1aec21154fa42fc5ca79d95e86f90f8768 /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-05
SECOND_READER_ONLY=fifty-distinct-fast-provider-builds /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-05/stage-1
```

The command builds/starts everything, prints the timing summary and `COUNTS total=1 passed=0 failed=1`, exits 1, and removes its resources. The root run.sh takes only the stage-folder argument and includes this case by default. Its extra data retains the supplied sample/traits and lives in a separate mock/source pair. It never reads the key, kit tests, product tests or shipped check sources. The proxy preserves provider bodies; all submission provider traffic still goes through WebRouter.

## Complete audit evidence

The full run completed **46 cases: 45 passed and one failed**. SR1-05 is the only blocking finding. Both epochs of all 12 supplied companies pass independently checked support/provenance/costs: 24 builds, 138 supported known fields, 669 research units, maximum sample build 40 units.

Other passing coverage includes JSON/auth errors, clock behavior, domain/query validation, idempotency scope/precedence, 50 duplicate/alias races, reset and retained-token import during request bodies, reset during provider work, refresh failure/recovery, listings, active spending, source-stopped replacement import and charged first/later-build snapshots. PORT=8089 and default-port instances served health. The clone remained clean; no product file or product test was edited.

The verifier's PASS on 104 sealed tests and isolated stage-1 claim was read only after independent execution. The distinct-company load case provides additional concrete evidence and does not change to agree with that report.

All 379 ledger units remain recorded with exact-revision evidence for all 318 normative/ruled units. `ledger-check 1 --phase audit --revision 3b729f1aec21154fa42fc5ca79d95e86f90f8768` exits 1 with exactly **S1-224 and S1-312** open. Details are in `ledger/stage-1-audit-3b729f1aec21.md` and `ledger/stage-1-probe-results-3b729f1aec21.md`. Private probes remain unpublished until all stages close; owned resources were removed.
