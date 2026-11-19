VERDICT: PASS
REVISION: 00c0c224d637ab25653e709f869ac209ac747c3e

# Verifier verdict — stage 2, candidate 00c0c224d637 (round 5)

Seal: SEAL AMENDED 2 sha256:87b255a20d282b8309aff4ae99710fd06e24ca6b88760746f419558cc2e4f4e5 (138 tests), unchanged. Code had been seen. Rulings R2-01 to R2-16 apply.

## Reported problems first

- vega-motors.test (F3, a note on 770529f8): **now complete**. hq_city is `contested` "Milan", cited to registry.test/vega, at 80 units. `vega_selection_rule_every_step`, `throttle_every_first_attempt_still_correct`, `nimble_only_service_selection` and `contested_screen` all pass.
- orbit-labs.test, full corpus: still `unknown` founded_year. This remains a note under R2-12. No answer-blind query reaches the digest page.

## Steps

1. Clean clone, built with `docker build --no-cache`. RUN.md start works.
2. Check command, isolated mode, output in `checks/verifier-s2-00c0-1`: "claimed stage: 2". This is a sample only.
3. Sealed suite, with the accepted stage-1 image as the upgrade source: **136 passed, 1 failed, 1 xfailed** (317 s).
   - The failure is `test_evidence_page_only_in_a_non_domain_search`, the orbit note.
   - The xfail is the R2-09 note.
4. Upgrade from the real stage-1 image (e391dd0b): passes. Tokens, logins, IDs, researched_at and spent_units survive. Candidates are one per (page, value) of the exported excerpts. Lost-response keys replay, and the next build replaces the candidates.
5. Cost: 80 units per build on the verifier corpus, within the cap. See N3.
6. Code read of the diff from 770529f8 (gathering only):
   - The 13 queries are built from the domain, the name and the A.3 phrases.
   - Page order uses served title, snippet and URL only, the same for every field. Nothing keyed to a fixture.
   - Every provider call still goes through web_router.
7. Fault planting: done on 770529f8, the first revision with no blocking finding. 8 faults planted, 6 caught; the 2 survivors are now caught by post-seal tests. All post-seal tests pass here.

## Notes (non-blocking)

- N1: orbit-labs.test founded_year, as above (R2-12).
- N2: R2-09, a residual stage-1 export defect (twin-forge Boulder).
- N3: spend (R2-14). Builds read until the budget is spent, including pages that name neither the company nor its domain.
