VERDICT: BLOCK
REVISION: 010b35ad7282e9b4018daee982a1846a5af8301e

Seat: verifier. Stage 4, round 2, after FIX 4 1. Worked from a clean clone (fclone) of the exact hash.
- stage-4/ was built fresh with no cache per RUN.md.
- The clone's stage-1/2/3 folders were built as previous-stage images for the upgrade paths.
- All ran under --cpus 2 --memory 3g on an internal network with the kit mock web.

## Reported problem retested first
- V4-1: fixed. With `POST /batches {"domains":["tarnwick-labs.test"],"budget_units":49}` (unbatched cost 44), founded_year is 1987 and the candidate set is exact. `run.sh <clone>/stage-4 -k post_seal_batch_budget` passes.

## Finding V4-2 — a batch that cannot afford its whole plan reserves research before its pages and loses a field (RULING R4-9)

Sentence: RULING R4-9 "When the remaining budget cannot cover the whole plan: 1. Do the company-naming searches and render the returned pages first. 2. Start research only while some field is unsupported, and only if the remainder after 25u can still render at least one cited page"; §8 / R1-2.

Case:
- quillon-dynamics.test has every field on searchable pages; its research claims nothing.
- Its unbatched build costs 44 units (research 25).
- `POST /batches {"domains":["quillon-dynamics.test"],"budget_units":41}` ends ready with 41 spent and founded_year unknown (1998 unbatched).
- Searches and renders alone cost 19 units and would have found every field.

Cause (code read): research.py `run` starts `_research()` alongside the searches whenever `affords(25)` holds, so research is reserved before the pages and a later render latches the batch (R4-6).

Reproduce: `run.sh <clone>/stage-4 -k "short_batch_budget"`. Case [3] fails: (budget 41, spent 41, founded_year None vs 1998). Case [23], where research is unaffordable from the start, passes.

## Whole suite
- `run.sh <clone>/stage-4` (before the R4-9 test was added): 304/304, including restart phases B and C with real `docker kill`/`start`.
- Spending as last persisted (R4-8): idle reads equal live spending. In every build test spent_units equals the mock call log's cost after completion, and batch spent_units equals the sum of its dossiers'. The 80-unit cap and the batch budget hold in every run (max build 74).
- Check command, isolated: `harness run ... --stage 4 --mode isolated --out work/checks/verifier-s4-010b-r2` → "claimed stage: 4". This is a sample, not a verdict.

## Code read (diff from b9288225)
- Fixed reserves are removed. Research is gated on `affords(25)`, which fixes V4-1 but causes V4-2.
- Refunds are persisted before they are visible: `Build.shown` reports what is on disk.

## Suite
SEAL AMENDED 4 (R4-9): test_post_seal_short_batch_budget_pages_before_research[23,3]; 303 tests.

## Cost
1302 units for 103 of 103 supportable fields: 12.6 units per correct field. Per build 38–74 units.

## Notes
Fault planting is deferred to the first stage-4 revision that passes.
