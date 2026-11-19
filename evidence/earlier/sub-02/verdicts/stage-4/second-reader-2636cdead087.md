VERDICT: BLOCK
REVISION: 2636cdead087f5d718627149e942ba9b953364e2

**R4-8a update:** SR4-3 is withdrawn. Import-envelope null track/format_version/state correctly returns 422 under Stage 1 §10. The verdict remains **BLOCK for SR4-4 only**. Historical commands/counts below are preserved from the original execution; the corrected probe has not been rerun in this ruling-update turn.

Original SR4-1 (domains:null) and SR4-2/F1 (total-provider-failure deadline) pass their first retests. The original audit recorded two broader cases; only SR4-4 remains a finding after R4-8a:

1. **SR4-3 — WITHDRAWN by R4-8a (14546e021d7ec5608e624a3d4ad1adb9c74d2ccc).** The recorded null track/format_version/state responses, 422 validation_failed with unchanged destination and no provider calls, are correct. The original expectation of 400 followed unrefined R4-8 and is superseded by the import endpoint-specific exception. All other null/absent fields and key/body controls passed.
2. **SR4-4 — S4-002; inherited S1-223, S2-005/054/078.** Seven already-discovered ranker.test pages, with searches/research answering normally. Refuse only the first attempt of each exact extract call with 503; each later identical call would serve the normal mock page. The service makes seven first extract attempts and no second attempts, finishes ready in **0.314 s**, spends **40**, and loses **all 13 supported candidates**, making all six original fields unknown. The same no-fault build returns all 13 candidates at 77 units. Time and budget remain. This is a transient-failure completeness regression, independently reproduced first with two refusals and again with just one. The current default probe uses one refusal. Final full-run confirmation: **0.349 s**, ready, 40 units, zero candidates, seven one-off 503 responses. Total-provider failure remains fixed at **1.192 s**, zero cost, 13 refused calls, with no calls after the terminal result.

Reproduce:

```sh
SECOND_READER_ONLY=stage4-null-fields /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/2636cdead087/stage-4
SECOND_READER_ONLY=stage4-transient-many /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/2636cdead087/stage-4
```

Reported-problems-first command (selectors both-provider-failure,batch-validation,null-fields) returned **two passed, one failed, 83 assertions**, exit 1: original triggers fixed; the import null variants fail. Total-provider failure takes **1.219 s** (13 refused calls, zero cost); final whole run also confirms no calls after it ends.

Full command:

```sh
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/2636cdead087/stage-4
```

**285 tests: 283 passed, two failed, 22593 assertions, exit 1.** The failures are exactly stage4-null-fields (SR4-3) and stage4-transient-many (SR4-4).

All 224 inherited cases pass. Small transient controls (three initial global 503s; two refusals per extract on a two-page company), optional Tavily failure while Nimble answers, and research-only failure all retain full evidence. Other origin/investor/batch/budget/concurrency/upgrade/transfer/restart/browser checks pass. The sixteen-page eight-field case retains all 20 candidates at 80 units; earlier boundaries remain complete. Required browser routes at 375/1280 pass. Twenty-four DOM audits cover 660 visible text elements, with no contrast/visible-label findings or horizontal overflow; current investor/origin/date screenshots were reviewed again. Exactly six original field hooks remain.

The isolated sample claims Stage 4 with 122+12+9+10 passing. The ledger audit has **exit 1 for S4-002 only, failing exact-revision evidence for the inherited null-type and candidate-completeness obligations; no missing rows among all 111 normative/ruled units**. Details and commands: `ledger/stage-4-audit-2636cdead087.md`; safe diagnostics: `probes/stage-4/artifacts/null-fields.json` and `transient-ranker.test-True.json` in the second-reader workspace.

Only after the full independent run were the other exact-revision verdicts read. Verifier reports 301 earlier tests passing and four added transient-outage cases failing (F2), independently corroborating SR4-4; its original null matrix did not cover the three import cases. Product-user reports PASS after a complete 375/1440 re-walk. Neither seat's test sources were opened. R4-8a subsequently withdrew the separate import-null finding; SR4-4 remains independently reproduced.

No product code/tests edited; no supplied/other-seat test sources read. Narrow source-only checks refreshed after independent full probes. Accepted Stage 1/2/3 unchanged; probes remain private; exact owned resources stopped.
