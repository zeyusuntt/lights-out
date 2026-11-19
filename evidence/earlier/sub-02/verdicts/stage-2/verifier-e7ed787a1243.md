VERDICT: PASS
REVISION: e7ed787a12437953b46e9b8f37b008fb9688547c

# Verifier verdict: stage 2, round 4

Seal in force: SEAL AMENDED 2 sha256:a9e16be3a8836ac49e3acd172e7bb60e5f455eec3e2eabe0a5591a56a3396ff1, 221 tests. Code had been seen.

## Seal amendment this round (post-seal addition)

I added `manyprefix-co.test`, for the SR2-4 generic-prefix variant: 15 supporting pages, 3 of them with a generic opening longer than the 300-character snippet before their fact.
- It does **not** reproduce the reporter's variant on ae61f6b: it passed there. So it adds coverage but is not proof of this fix.
- For proof I also ran the reporter's own probe (below).

## Reported problems, retested first

- **SR2-4, both variants:** the second-reader's probe `SECOND_READER_ONLY=candidates-cap …/second-reader/probes/stage-2/run.sh clone-e7ed/stage-2` gave PASS for candidates-capstone.test and PASS for candidates-capedge.test (2 tests, 285 assertions).
- **My SR2-4 tests:** `-k many_supporting` gives 2 passed. manyfacts-co.test has 16 of 16 candidates and manyprefix-co.test 15 of 15, each at 80 units.
- **F1, SR2-1, the hung write and the signed-out header:** 7 passed.

## Whole run (clean clone `fclone e7ed787… clone-e7ed`)

1. **Build and start:** no-cache build at 2 vCPU / 3 GiB. Healthy in 1 s; about 246 MiB of memory.
2. **Check command, isolated mode** (`checks/verifier-s2-e7ed-r4`): "claimed stage: 2". This is a sample only and not evidence on its own.
3. **Sealed suite:** **221 passed, 0 failed** (309 s). This includes the upgrade path from the real stage-1 image (6 of 6) and every browser test.
4. **Cost, and whether the cap cut any evidence.** I compared each build's candidates with every (page, value) pair that Appendix A gives over the evidence pages. I read the sample corpus's page files only, not key.json.
   - **Sample corpus: 731 units for 69 supported fields, 10.59 units per supported field.** No candidate was missing or extra.
   - **My corpus, 9 companies: 502 units for 37 supported fields, 13.57 units per supported field.** No candidate was missing or extra. The two cap-pressure companies each spent exactly 80.
   - No build exceeded 80 units.
5. **Code read:** the diff since ae61f6b is planner.py only (budget split across unread cut-short pages). No answers keyed to fixtures.
6. **Fault planting:** done on 166ae1a. All 8 planted faults were caught.

## Findings

None.

## Notes

- RUN.md still tags the image `dossier-stage-1`.
