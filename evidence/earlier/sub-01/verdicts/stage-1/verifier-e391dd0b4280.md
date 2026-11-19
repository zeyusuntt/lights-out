VERDICT: PASS
REVISION: e391dd0b4280ee518d358387614110bebf90c116

# Verifier verdict — stage 1, candidate e391dd0b4280 (fix round 1)

Seal: SEAL AMENDED 1 sha256:d37e75eb5c7b32bca8548fd0d95fe95955150cc471884344f8a29d99f6278336 (102 tests). Code had been seen; the post-seal additions are listed under step 7.

## Reported problem first

- F1 (from 408ebd53): fixed. The probe `bash $FACTORY_WORK/verifier/probes/probe.sh <image> $FACTORY_WORK/verifier/probes/corpus-a lumen-grid.test` now returns `founded_year` 2011, cited to https://weekly.test/issue-7, at 34 units. The post-seal test passes.

## Steps

1. Clean clone via `fclone`, built with `docker build --no-cache`. The build and run commands in RUN.md are unchanged from round 1, where I followed them word for word. They work.
2. Check command, isolated mode, output in `checks/verifier-s1-e391-1`: "claimed stage: 1", and stage 1 passed. As the task says, this is a sample only.
3. Sealed suite, `run.sh <clone>/stage-1`, on an internal network at 2 vCPU / 3 GiB, with a Nimble-only container and a container that is never reset: **102 passed, 0 failed** (215 s).
4. Upgrade path: none (stage 1).
5. Cost: the 80-unit cap holds. On a 70-page company, `spent_units` equals the summed mock log costs, and both are 80 or less. Ordinary companies in the verifier corpus cost 34 to 55 units.
6. Code read of the diff from 408ebd53:
   - Every returned page is now extracted after the pages that name the company. Each extract reserves its units through `Budget.hold` before the call, so the cap is enforced on that path as well.
   - Path routes now take `{domain:path}`, and invalid path domains give 422.
   - Call timeout is 60 s.
   - I found no special cases and no fixture-keyed answers.
7. Fault planting, on throwaway copies of this revision, each checked against the relevant part of the frozen suite with `-x`:
   - M2 negation check removed: caught.
   - M3 replay answered 202: caught.
   - M4 `has_more` off by one: caught.
   - M5 `www.` not stripped: caught.
   - M6 tokens dropped from export: caught.
   - M7 two exact-domain searches per build: caught.
   - M8 raw research claim asserted without support: caught.
   - M1 no spending cap: **survived**, because my corpus companies were too small to reach 80 units. I added the post-seal test `test_budget_cap_with_many_candidate_pages` with the wide-net corpus company (70 pages). It catches M1, and this revision passes it.
   - Result: 7 of 8 caught by the frozen suite. 1 post-seal test added, and it passes on this revision.

## Notes (non-blocking)

- Spend: every returned page is read while the budget lasts, including pages from searches that do not name the company. This is allowed by R1-03 and within budget, but it is the main reason the builder reports 54 to 80 units on the sample corpus. If the stage-4 spend-per-correct-field workload matters, the order in which pages are read is worth tuning.
