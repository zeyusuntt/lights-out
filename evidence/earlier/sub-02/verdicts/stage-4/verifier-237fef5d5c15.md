VERDICT: PASS
REVISION: 237fef5d5c152b310842a64be097aeaba0c99809

# Verifier verdict: stage 4, round 4

Seal in force: SEAL AMENDED 4 sha256:c27bebb783b682fa6c619fa6d4570c4b4e5f75437f018a5aee785373aa2d2c52, 307 tests. Code had been seen.

## Reported problems, retested first

- **F3 / SR4-5, live-host fast failure:** `NOCACHE=0 sealed/stage-4/run.sh clone-237f/stage-4 -k live_host` passes: failed within 10 s.
- **The rest of the retest selection** passes 33 of 33:
  - transient outages: 4 cases with full evidence;
  - total failure, alone and with a batch plus concurrent builds, within 10 s;
  - the R4-8 / R4-8a matrix and batch validation;
  - research failing, Tavily failing, rate limits, weather, throttle.
- **Slow-call protection on the live host** (probe): every nimble call delayed 10 s, NIMBLE_BASE_URL on sdk.nimbleway.com. lumen-grid.test ended **ready after 30.4 s with every expected value**. The build did not abandon calls that had waited under 30 s.

## Whole run (clean clone `fclone 237fef5… clone-237f`)

1. **Build and start:** no-cache build, 2 vCPU / 3 GiB, -e PORT. Healthy in 1 s; about 248 MiB of memory.
2. **Check command, isolated mode** (`checks/verifier-s4-237f-r4`): "claimed stage: 4". This is a sample only and not evidence on its own.
3. **Sealed suite:** **307 passed, 0 failed** (403 s, final seal). It covers:
   - every stage-1 to stage-3 test and every browser test;
   - origins and lineage, investors, corroborated_since;
   - batches;
   - provider failure: transient, partial, total, concurrent and on the live host;
   - restarts with batch builds running;
   - export during a batch;
   - upgrades from the real stage-1, stage-2 and stage-3 images.
4. **Cost, and whether the cap cut any evidence.** I compared each build's candidates (executives titles and investors included) with every (page, value) pair the evidence pages support. I read the sample corpus's page files only, not key.json.
   - **Sample corpus: 838 units for 93 supported fields, 9.01 units per supported field.** No candidate was missing or extra. Two builds reach exactly 80 units with nothing missing.
   - **My corpus: 683 units for 48 supported fields, 14.23 units per supported field.** No candidate was missing or extra.
   - No build exceeded 80 units.
5. **Code read:**
   - gateway.py: fast 5xx answers use the 6 s window on every host; only slow 5xx answers use the live slow window.
   - origins.py: hop limit 3, then the host of the fourth URL or of an unserved URL.
   - pages.py: own kind by registrant; lookalike origin is the company's domain.
   - selection.py and dossier.py: investor membership and standing origins.
   - No answers keyed to fixtures.
6. **Fault planting** (first stage-4 revision to pass; 8 faults, one per throwaway copy, frozen suite, stopped at first failure). **7 caught; 1 survivor now covered by a post-seal test.**
   - Caught:
     - First-Published-By ignored;
     - Canonical hop limit 4;
     - lookalike origin taken as its registrant;
     - investor membership with one origin;
     - batch budget not enforced;
     - own kind regardless of registrant;
     - a missing budget_units accepted.
   - Survivor: standing origins reset each build. I added a post-seal test (amendment 7): echo-chamber.test's legal name comes from one origin in epoch 0 and another in epochs 1–2, so it must be corroborated_since the second build while `corroborated` is false. The fault now fails the test; this revision passes it, and the whole suite passes (307 of 307).

## Findings

None.

## Notes

- Spend per supported field on the sample corpus is 9.01 (stage 3: 9.94; stage 1: 5.35, with six fields and no candidates).
