VERDICT: PASS
REVISION: 264a6a2b51ab10ff2e56c372e6d7e3671cdfbf00

# Verifier verdict: stage 3, round 1

Seal in force: SEAL AMENDED 3 sha256:df72a87c8c2de92999964f35d0db650b639cc6fd0f5f7d73b9be71a266c729c8, 262 tests. `seal --verify` returned ok before the final run.

## Seal amendments this round (code had been seen)

- **Amendment 2: three test misreadings of mine.** All were product-correct behaviour.
  - as_of learned_at and true_from now come from history (R3-3), not from the live selected candidate. At as_of T1, hq_city's true_from is that of its T0 history entry, 2020-01-01.
  - The stage-3 round-trip test now sets the clock again after reset plus import. Reset moved the clock and import does not, and /values defaults to the clock.
  - The stage-2 upgrade /values query now passes as_of=T1. The destination clock stood at T0, before the imported build, so the 404 was correct.
- **Amendment 3: a post-seal addition from fault planting.**
  - The executives correction rule with an equal true_from survived the suite.
  - I added exec-fix.test, where a CFO is renamed with the same Effective date. The fault now fails the new test; this revision passes it.
- **RULING R3-6** (a URL seen only in search results makes no version): consistent with my tests. The cto page not gathered in epoch 2 keeps holding.

## What I ran (clean clone `fclone 264a6a2… clone-264a`)

1. **Build and start:** no-cache build, 2 vCPU / 3 GiB, -e PORT. Healthy in 0–1 s; about 263–279 MiB of memory.
2. **Check command, isolated mode** (`checks/verifier-s3-264a-r1`): "claimed stage: 3", highest contiguous stage 3. This is a sample only and not evidence on its own.
3. **Sealed suite:** `sealed/stage-3/run.sh clone-264a/stage-3`. Result: **262 passed, 0 failed** (374 s). This covers:
   - every stage-1 and stage-2 test still in force, including all browser tests;
   - tempo-labs.test over three epochs: true_from and learned_at, history, the feed with since/limit/has_more, as_of including same-time builds and equivalent offsets, and /values with version replacement and ending;
   - a failed build adds nothing, and concurrent refreshes add each entry once;
   - stage-3 export/import round trip.
4. **Restarts:** `docker kill -s KILL` then `docker start`.
   - At rest: logins, tokens, GET with and without as_of, values, history, list, feed, replays and clock all intact; new feed entries have larger seq; two restarts and a reset after them behave.
   - During a build (R3-4): ready at the pre-build state, history and feed unchanged, replay returns the original 202, clock persisted (R3-5).
5. **Upgrade paths, real images:** both run from the clone's own stage folders.
   - stage-1 → stage-3: tokens; ids; R2-6 candidates; initial history with learned_at = researched_at and true_from null; empty feed; as_of 404 before researched_at; /values null; the first build compares.
   - stage-2 → stage-3 (R3-1): tokens and replays; one build at researched_at with the whole spent_units; null true_from everywhere; learned_at = retrieved_at; initial history; executives unknown with no history; the first build's feed has ceo change and executives change.
6. **Cost, and whether the cap cut any evidence.** I compared each build's candidates, executives titles included, with every (page, value) pair that Appendix A gives over the evidence pages. I read the sample corpus's page files only, not key.json.
   - **Sample corpus, 12 companies: 805 units for 81 supported fields, 9.94 units per supported field.** Builds cost 58–80 units. No candidate was missing or extra. tidemark-energy.test reached exactly 80 with nothing missing.
   - **My corpus, 10 companies: 557 units for 41 supported fields, 13.59 units per supported field.** No candidate was missing or extra.
   - No build exceeded 80 units.
7. **Code read** (dossier.py, store.py, state.py):
   - No answers keyed to fixtures.
   - State is written whole to a temporary file and moved into place with os.replace, so a restart reads either the old or the new state.
   - Version holding/ending and the as_of history lookup match the specification and rulings.
8. **Fault planting** (first stage-3 revision to pass; 8 faults, one per throwaway copy, stopped at first failure). **6 caught, 1 survivor now covered, 1 equivalent.**
   - Caught: correction strictness (< in place of <=); as_of build cutoff (< in place of <=); a version end treated as inclusive; feed seq not advancing; persistence disabled; the wrong build chosen among same-time builds.
   - Survivor: the executives correction rule made strict. The post-seal test (amendment 3) now catches it, and this revision passes it.
   - Equivalent: not replacing an equal-dated earlier version. The kept version ends on its own start date and so never holds, so nothing changes that a test can see. No sentence is broken.

## Findings

None.

## Notes

- Spend per supported field on the sample corpus is 9.94 (stage 2: 10.59), with executives now among the fields.
- RUN.md and DESIGN.md were read for the run steps only.
