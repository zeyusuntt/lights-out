VERDICT: BLOCK
REVISION: 0dfa3ed6e8bcb58a63c4211d2aeee117e6ca559e

# Verifier verdict — stage 2, candidate 0dfa3ed6e8bc (round 3)

Seal: SEAL AMENDED 2 sha256:f7ddd0342e025798c5008487ea949e49d6c8b47b80bf680b0dd3c01fbf2e2a03 (134 tests). Unchanged this round. Ruling R2-12 is applied below.

## Reported problems first

- F2 (orbit-labs, a page returned only by a non-domain search):
  - Fixed on its own corpus (`probes/corpus-b`): founded_year is 2016, cited to digest.test/issue-12, at 80 units.
  - In the full suite corpus it fails again: `test_postseal_2` gets `unknown`. There, every field query the build makes, and also "Orbit Labs" and "Orbit Labs founded", return other pages instead of the digest. I could not find a plan, made without knowing the value, that reaches the page within 80 units. Under R2-12 this is a **note**, not a block.
- Round-1 F1 (vega-motors candidates): **regressed**. See F3.

## Steps

1. Clean clone, built with `docker build --no-cache`. RUN.md start works.
2. Check command, isolated mode, output in `checks/verifier-s2-0dfa-1`: "claimed stage: 2". This is a sample only.
3. Sealed suite: **128 passed, 5 failed, 1 xfailed** (506 s). The failures:
   - `vega_selection_rule_every_step`, `throttle_every_first_attempt_still_correct`, `nimble_only_service_selection` and `contested_screen` all come from F3.
   - `postseal_2` is the note above.
   - The xfail is the R2-09 note.
4. Upgrade from the real stage-1 image: passes.
5. Cost: 77 to 80 units per build. See F3 and N2 for where the units go.
6. Code read: every provider call goes through web_router. No external assets, no fixture keys.

## Finding F3 — vega-motors.test: reachable candidates missed while units go to repeats (BLOCK under R2-12)

Sentences broken: stage 2 Candidates, point 3 (selection), §8 "known exactly when the evidence supports". Rulings R1-03, R2-06 and R2-12.

This build at 77 units:
- founded_year is `unknown`; expected `contested` 1988.
- hq_city is `known` "Turin"; expected `contested` "Milan".
- The headcount candidates lack vega-motors.test/jobs and jobs-board.test/vega.

Where its units went:
- The exact-domain search asked for only **2** results, at 1 unit. Ten cost the same.
- Every field query was repeated at max_results 1, then 2, then 3. Each repeat returned the results already seen: 18 searches.
- 5 rendered reads (15 units) went to pages of another company (wide-net.test), which name neither Vega nor its domain.

R2-12 plan. It uses only the spec's calls and costs, keeps one successful exact-domain search, and every citation still comes from served browser text:

| Call | Units |
|---|---|
| Nimble research for vega-motors.test (cites vault.test/vega) | 25 |
| Nimble lite search, query exactly `vega-motors.test`, 10 results. Returns: vega-motors.test/blog, /team, www.vega-motors.test/legal, vega-motors.test/jobs, /about, a-data.test/vega, b-data.test/vega, blog.vega-motors.test/post, c-data.test/vega, jobs-board.test/vega | 1 |
| Nimble lite search `Vega Motors registered office` (statement phrases only, no value). Adds registry.test/vega, news.test/vega-2 | 1 |
| Nimble lite search `Vega Motors based`. Adds news.test/vega | 1 |
| Rendered Nimble extract of those 13 pages plus vault.test/vega: 14 × 3 | 42 |
| **Total** | **70** |

This plan obtains every candidate this build obtained, plus Milan, Rome, Naples, 1988, 1987 and both missing headcount pages. That is all 15 candidates of the company.

I checked the result lists by querying the mock directly, with the same corpus and noise 0 for both providers, so Nimble and Tavily rank alike. This build's own round-1 predecessor got the identical 10-result domain list.

Reproduce:
- `bash $FACTORY_WORK/verifier/probes/probe-full.sh <stage-2 image> $FACTORY_WORK/verifier/sealed/stage-2/corpus vega-motors.test` prints every call, its max_results, cost and returned URLs.
- Or `run.sh <stage-2> -k vega_selection`.

## Notes (non-blocking)

- N1: R2-09 xfail, as before.
- N2: spend. The 18 repeated searches are deepening by max_results. One search with max_results 10 returns the same pages for 1 unit. The domain search asked for 2 results when 10 cost the same.
- N3: orbit-labs in the full corpus, as above. No plan found under R2-12.
