VERDICT: PASS
REVISION: a34bf561b2bc5cdb5233e6cf26f4cae44098dd85

No findings. The reported problems were retested first, then the entire independent suite was rerun from a clean clone of exactly this revision.

## Regressions first

```sh
SECOND_READER_ONLY=strict-json /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/a34bf561b2bc/stage-1
```

**4/4 passed, 40 assertions, exit 0.** SR1-1's three invalid JSON literals now return `400 malformed_request` without provider work. Under R1-5, nonempty whitespace-only display names are accepted and preserved, including exactly 100 spaces. Empty and over-100-character names remain rejected in the full validation checks.

## Whole audit

```sh
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/a34bf561b2bc/stage-1
```

**154/154 passed, 5861 assertions, exit 0.** The runner builds and starts the supplied stage-folder, the documented mock and sample corpus with independent additional cases, and runs on an internal network with each service limited to 2 vCPU/3 GiB. Coverage includes the field-support grammar and citation provenance, cost/budget accounting, a live-host response delayed 31 seconds, lost connections, 50 concurrent requests, idempotency, failed refreshes, reset races, and cross-process migration with original tokens/responses and in-flight snapshots.

The prescribed isolated sample harness also completed on this clean clone: **claimed stage 1; 122/122 Stage 1 checks passed; exit 0**. Report: `/Users/[REDACTED]/dev/band-factory/work/checks/second-reader-a34bf561b2bc-1/report.json`.

`ledger-check 1 --phase audit --revision a34bf561b2bc5cdb5233e6cf26f4cae44098dd85` returns **0**: all **379 units**, including **291 normative and four ambiguous units as ruled**, have no open evidence gaps on this revision.

The verifier's PASS verdict was read only after these independent probes completed; its reported 176/176 sealed-suite result provides corroboration. No other seat's tests, supplied check sources, key.json, or later-stage specifications were opened. Narrow source review confirms unchanged WebRouter routing, packaging, and scrypt derivation plus the candidate's hash-storage call sites. Product code and product tests were not edited. Probes remain private until all stages close.

Detailed commands, evidence, source-review limits, and rulings: `ledger/stage-1-audit-a34bf561b2bc.md` and the per-unit ledger.
