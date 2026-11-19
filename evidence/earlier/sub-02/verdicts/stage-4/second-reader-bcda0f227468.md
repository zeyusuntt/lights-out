VERDICT: BLOCK
REVISION: bcda0f227468c5eac1ca2901cc4a30fdec12d489

Two confirmed findings, no other findings:

1. **SR4-1 — S4-086/S4-002, inherited S1-156/S1-166:** authenticated POST /batches with an unused valid key and `{"domains":null,"budget_units":1}` returns **422 validation_failed**. It must return **400 malformed_request**, because domains is the wrong JSON type; only budget_units has the special 422 override. No state or provider effects occur. Other wrong-typed containers and entries return 400 correctly. Focused confirmation: one failed, 34 assertions, exit 1.
2. **SR4-2 — S4-108/S4-002, inherited Stage 1 §8 fast-call bound:** when both configured Nimble and Tavily answer every provider operation immediately with 500, a build ends failed at zero cost but takes **13.722 seconds** in the first independent focused run. Expected completion within ten seconds; only waits after 429s are excluded. This independently corroborates verifier F1. The focused log contains 85 refused calls (75 Nimble searches, five research runs, five Tavily searches). Final whole-run confirmation: **13.830 seconds**, 85 refused calls, zero spending.

Reproduce each with the self-contained private runner:

```sh
SECOND_READER_ONLY=stage4-batch-validation /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/bcda0f227468/stage-4
SECOND_READER_ONLY=stage4-both-provider-failure /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/bcda0f227468/stage-4
```

Full command (no selector):

```sh
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/bcda0f227468/stage-4
```

**281 tests: 279 passed, two failed, 23863 assertions, exit 1.** The two failures are exactly SR4-1 and SR4-2; all 224 inherited cases pass.

All 224 inherited probes pass under the Stage 4 rulings. All new lineage/origin/member/investor semantics, batch budgets/ownership/idempotency/concurrency, real Stage 1/2/3 upgrades, native transfer, reset, billed-cost-preserving restarts and browser checks pass apart from the two findings. Eight-field boundary retains all 20 candidates on sixteen pages at 80 units; earlier boundaries remain complete. Explicit configured optional-provider failure with Nimble answering passes.

Required browser routes at 375/1280 pass; 24 DOM audits, 660 visible text elements, no contrast/label/overflow findings; current investor/origin/date screenshots reviewed. Prescribed isolated sample claims Stage 4 with 122+12+9+10 passing. The sample does not override either reproduced failure.

`ledger-check 4 --phase audit --revision bcda0f227468c5eac1ca2901cc4a30fdec12d489`: **exit 1, exactly three failing-evidence units (S4-002, S4-086, S4-108), no missing evidence rows**. Every one of the 111 normative/ruled units has exact-revision evidence; S4-002, S4-086 and S4-108 have failing evidence. No missing rows. Details, execution chronology and limitations: `ledger/stage-4-audit-bcda0f227468.md`.

The other seats' verdicts were read after the original independent full run (278/279, 23534 assertions), before independently adding/reproducing the combined-provider case and the final whole rerun. Verifier reports 293/294 BLOCK for F1; product-user PASS. No test sources of either seat were opened. Narrow source-only packaging/WebRouter/scrypt/durable-reservation checks are recorded in the audit; no product code/tests were edited. Accepted Stage 1/2/3 unchanged. Probes remain private until every stage closes; exact owned resources stopped.
