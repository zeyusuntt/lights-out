VERDICT: BLOCK
REVISION: 166ae1aa16e33c2b6cb0684d305aafb21bbaf41a

One new confirmed finding, with two reproducing variants. The prior reported failures pass. The complete independent run is **174 passed, two failed out of 176** (7344 assertions).

## SR2-4 — Query spending cuts already returned supporting pages at the cap

**Units:** S2-054 and S2-080 (complete candidate set); S2-078 (all selected-value citations); S2-005/S2-008/S2-077/S2-084 (the omitted alternative changes selection and status in the capedge variant).

Each controlled company has 16 supporting pages across the six fields. The service's seven domain-inclusive searches already return all 16 URLs, but it also spends six units on name-only field searches and two on plain extracts. After research and 13 rendered extracts, it finishes ready at **79 units**, with only **13 of 16 candidates**. The next three-unit extraction cannot fit. All provider calls succeeded.

The same seven observed domain-inclusive queries, the research run, and all 16 rendered extracts fit exactly:

```text
7 searches + 25 research + 16 * 3 rendered extracts = 80 units
```

This case is feasible under the cap. The defect is avoidable spending that prevents the build from retaining supporting evidence it already found; exceeding the cap is not requested.

**capstone.test:** omits `hq_city-0`, `ceo-1`, and `founded_year-2`, losing required candidates and corroborating citations.

**capedge.test:** omits `ceo-1`, `founded_year-2`, and `funding_total-1`. The missing own-page funding sentence supports **25000000**, published February 1; the retained own-page **12000000** value is dated January 1. Actual funding is **12000000, known**. Required is **25000000 selected, contested**, with both candidates. The later page's generic opening appears before its supporting sentence, but the page was returned and its full text is valid evidence.

**Reproduce on the exact clean clone:**

```sh
SECOND_READER_ONLY=candidates-cap /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/166ae1aa16e3/stage-2
```

The runner builds/starts that stage and the documented mock itself. The full command without the selector also reproduces both failures. Diagnostics: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/artifacts/candidate-capstone.test.json`, `candidate-capedge.test.json`, and `budget-summary.json` beside it; they contain controlled full page text, expected/actual candidates, actual searches/costs, and proof the seven domain queries cover all 16 URLs.

## Reported problems retested first

The generic-prefix candidate omissions, raw null header, and hung research/refresh recovery now pass. Both never-answer write paths show uncertainty and retry with their original key/body; complete probe runtimes are about 11 seconds for each timeout/recovery. More-than-ten-page discovery is present: every supporting URL in the new 16-page cases is returned. The remaining failure is gathering within the budget after that discovery.

## Audit evidence

All 154 inherited checks and the normal ranking, rate-limit, browser, latest-read, and real Stage 1 upgrade/session/retry checks pass. The isolated sample claims Stage 2 with **122 Stage 1 + 12 Stage 2** checks passed. Verifier and product-user PASS reports were read only after this full independent run; their smaller corpora do not cover this new boundary case and do not override it.

The sentence ledger has exact-revision evidence for every normative/ruled unit. Audit-check exits **1** with seven failed units and no missing rows. No product code/tests were edited; private probes remain unpublished until all stages close.

Complete record: `ledger/stage-2-audit-166ae1aa16e3.md`.
