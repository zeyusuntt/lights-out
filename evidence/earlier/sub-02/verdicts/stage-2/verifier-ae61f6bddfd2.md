VERDICT: PASS
REVISION: ae61f6bddfd23c08039c3b2ef17a91acf19f9270

# Verifier verdict: stage 2, round 3

Seal in force: SEAL AMENDED 2 sha256:edf50ab3530b53f85e23e3d3620168de5cacf05685b6b8a126d0aa1ae250275d, 220 tests. Code had been seen.

## Seal amendments this round (post-seal additions)

My suite missed SR2-4, which the second-reader found on 166ae1a. I added `manyfacts-co.test`: 16 supporting pages across the six fields. Planned spend reads them all within the cap (7 searches + 25 research + 16 rendered extracts = 80).
- With 14 pages (amendment 4) the test did not reproduce SR2-4. With 16 (amendment 5) it does.
- Check of the test: on 166ae1a, `-k many_supporting` fails; on ae61f6b it passes.

## Reported problems, retested first

- **SR2-4:** `NOCACHE=0 sealed/stage-2/run.sh clone-ae61/stage-2 -k many_supporting` passes: all 16 candidates, spent 80, no unit over the cap.
- **F1, SR2-1, the hung write and the signed-out header:** `-k "orbit or longread or hung or raw_null"` passes, all 7 tests.

## Whole run (clean clone `fclone ae61f6b… clone-ae61`)

1. **Build and start:** no-cache build at 2 vCPU / 3 GiB. Healthy in 1 s; about 246 MiB of memory.
2. **Check command, isolated mode** (`checks/verifier-s2-ae61-r3`): "claimed stage: 2". This is a sample only and not evidence on its own.
3. **Sealed suite:** **220 passed, 0 failed** (309 s). This includes the 10 s build bound under 0.9 s delays on every call, and every browser test.
4. **Upgrade from the real stage-1 image** (`clone-ae61/stage-1`): all 6 upgrade tests passed.
5. **Cost, and whether the cap cut any evidence.** I compared each build's candidates with every (page, value) pair that Appendix A gives over the evidence pages. I read the sample corpus's page files only, not key.json.
   - **Sample corpus, 12 companies: 728 units for 69 supported fields, 10.55 units per supported field.** Builds cost 51–71 units, down from 52–76. No candidate was missing or extra.
   - **My corpus, 8 companies: 422 units for 31 supported fields, 13.61 units per supported field.** No candidate was missing or extra. manyfacts-co.test used exactly 80 units.
6. **Code read:** only the diff since 166ae1a (planner ordering: known pages read before speculative calls). No answers keyed to fixtures.
7. **Fault planting:** done on 166ae1a, the first stage-2 revision to pass. All 8 planted faults were caught.

## Findings

None.

## Notes

- RUN.md still tags the image `dossier-stage-1`.
- Spend on the sample corpus is 10.55 units per supported field (stage 1: 5.35), mostly rendered extracts at 3 units per URL.
