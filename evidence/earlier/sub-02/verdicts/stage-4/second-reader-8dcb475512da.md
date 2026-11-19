VERDICT: BLOCK
REVISION: 8dcb475512daa1a4e5acd24ea52818d9724dd780

**SR4-7 — S4-002/S4-009/S4-112/S4-117; S1-245; R4-0/R4-10:** warned container stop/start loses billed units. With provider replies delayed 0.7 s, start a refresh of a ready batchone.test dossier; after billed calls while still building, `docker stop --time 1` and `docker start`. The refresh becomes ready with **70 added spent_units**, but its full provider bill is **73**. Baseline 49 becomes 119; expected at least 122. R4-10 confirms this stop mode is in scope and cancellation must retain potentially billed reservations.

```sh
SECOND_READER_ONLY=stage4-settlement-stop /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/8dcb475512da/stage-4
```

SR4-6 was retested first and passes: one test, 145 assertions, spending **49 = 49 billed**. The corrected targeted regression set returns **17 tests, 16 passed, one failed, 3430 assertions**, exit 1. Every earlier targeted problem passes; only SR4-7 fails. A report-filename issue in an earlier combined attempt was corrected and is not a product finding.

The 292-probe whole run was started, then intentionally stopped on the foreman's BLOCKED 4 instruction. Its completed inherited phase recorded **180 passed, 9793 assertions**; no complete whole-run result or complete round-5 ledger audit is claimed. The isolated sample claims Stage 4 with 122+12+9+10 passing.

The verdict is based on the completed targeted counterexample and R4-10. Verifier F4 independently corroborates the cancellation/billing defect and reports over-budget totals in its own fixtures; no other-seat test sources were opened. Details, collected scope and source corroboration: `ledger/stage-4-audit-8dcb475512da.md`. Safe proof: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/artifacts/settlement-stop.json`.

No product code/tests edited. Accepted Stage 1/2/3 unchanged. Full-run resources stopped on instruction. Probes published only after the foreman closed the line and explicitly requested publication.
