FIX 4 2 — stage 4, round 2, on 010b35ad7282e9b4018daee982a1846a5af8301e

Verdicts: product-user PASS, second-reader BLOCK (S4-F5), verifier BLOCK (V4-2). Both findings have one root, under R4-9: in a batch whose budget cannot cover the whole plan, research is reserved before the page work.
- S4-F5 (second-reader): batch-reader-aa.test at budget 30 ends ready, spent 30, with all fields unknown. One searchable page supplies all eight. Reproduce: SECOND_READER_ONLY=stage4-shared-budget-boundaries-and-affordable-evidence SECOND_READER_NO_BROWSER=1 /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-4/run.sh <clean-clone>/stage-4
- V4-2 (verifier): quillon-dynamics.test at budget 41 ends spent 41 with founded_year unknown (1998 unbatched). Searches and renders alone cost 19u and find every field. Cause: research starts alongside the searches whenever affords(25) holds. Reproduce: the verifier's run.sh <clone>/stage-4 -k short_batch_budget (case [3]).
The builder's a7228733, committed before this FIX, implements the R4-9 ordering and is taken as the round-2 fix. No further change is requested, unless the retest shows it misses either case.
