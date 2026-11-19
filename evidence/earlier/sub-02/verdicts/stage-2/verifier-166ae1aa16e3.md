VERDICT: PASS
REVISION: 166ae1aa16e33c2b6cb0684d305aafb21bbaf41a

# Verifier verdict: stage 2, round 2

Seal in force: SEAL AMENDED 2 sha256:f4b164546ae3797e06da04e927bbe884472431f31f48d8d3cce195ab40dfe78e, 219 tests. `seal --verify` returned ok before the run.

## Seal amendments this round (code had been seen)

- **Amendment 2: a test misreading.** My citation check tested each candidate's excerpt against the field's *selected* value. It now tests each candidate against its own value (stage-2 Candidates). This bug had been hidden in round 1 behind F1.
- **Amendment 3: tests for the problems other seats reported in round 1.**
  - SR2-1: a page whose fact comes after the first 300 characters of prose (`longread-media.test`).
  - A research write that never answers: the screen must show research-uncertain, and the retry must reuse the same key and start one build.
  - Signed out, the screens show no raw `null` or `undefined`, and current-user is absent.

## Reported problems, retested first

- **F1 (gathering pages the evidence needs):** passed. `NOCACHE=0 sealed/stage-2/run.sh clone-166a/stage-2 -k orbit` gives 4 passed. orbit-forge.test funding is now [25M, 10M, 99M] with 25M selected.
- **SR2-1, the hung write, and raw null when signed out:** `-k "longread or hung or raw_null"` gives 3 passed.

## Whole run (clean clone `fclone 166ae1a… clone-166a`)

1. **Build and start:** no-cache build, started with -e PORT plus provider variables at 2 vCPU / 3 GiB. Healthy in 1 s; about 256 MiB of memory.
2. **Check command, isolated mode** (`checks/verifier-s2-166a-r2`): "claimed stage: 2". This is a sample only and not evidence on its own.
3. **Sealed suite:** `sealed/stage-2/run.sh clone-166a/stage-2`. Result: **219 passed, 0 failed** (256 s). This covers the stage-1 tests still in force, candidates and the selection rule, rate limits, the upgrade path, and every browser test.
4. **Upgrade path from the real stage-1 image** (`clone-166a/stage-1`): it was populated through its API, exported and imported. All 6 upgrade tests passed:
   - tokens and logins;
   - dossier identity;
   - imported candidates per R2-6;
   - replay of lost keys;
   - a failed refresh keeps imported candidates (R2-5);
   - the next successful build replaces them.
5. **Cost, and whether the cap cut any evidence.** I compared each build's candidates with every (page, value) pair that Appendix A gives over the corpus's evidence pages: searchable pages plus pages that research claims cite. I read the sample corpus's page files only, not key.json.
   - **Sample corpus, 12 companies: 742 units for 69 supported fields, 10.75 units per supported field.** Builds cost 52–76 units. No candidate was missing and none was extra. So no build's evidence was cut by the cap. The tightest build was quillmate.test at 76 units.
   - **My corpus, 7 companies: 342 units for 25 supported fields, 13.68 units per supported field.** Builds cost 38–74. No candidate was missing and none was extra.
   - Every citation and candidate was served page text that supports its value (sealed checks).
6. **Code read:**
   - No answers keyed to fixtures.
   - The selection rule (selection.py) matches the specification's order.
   - The browser's latest-read guard (`latestReads`) and same-key retry (`Write`) are present in app.js.
7. **Fault planting** (first stage-2 revision to pass; 8 faults, one per throwaway copy, frozen suite, stopped at first failure). **All 8 were caught.** No post-seal additions were needed.
   - authority ignored in ranking;
   - status always known;
   - citations taken from every candidate, not only the selected value's;
   - a missing Kind always read as aggregator;
   - polling every 5 s;
   - latest-read guard removed;
   - a new key on retry;
   - imported candidates given kind "own". This one is caught by the upgrade tests when the previous stage is supplied (`PREV=`).

## Findings

None.

## Notes (do not block)

- **Spend has risen.** Units per supported field on the sample corpus went from 5.35 (stage 1) to 9.19 (round 1) to 10.75 now, for the same 69 fields. The largest build, 76 units, is 4 under the cap.
  - Correctness comes first and no evidence was lost here. But a company with more pages could reach the cap before its evidence is complete.
  - Most of the spend is rendered extracts at 3 units per URL.
- RUN.md still tags the image `dossier-stage-1`.
