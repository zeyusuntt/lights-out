VERDICT: BLOCK
REVISION: bcda0f227468c5eac1ca2901cc4a30fdec12d489

# Verifier verdict: stage 4, round 1

Seal in force: SEAL AMENDED 4 sha256:8d2f2896b97badfd7a1c15a72b117f202297e342cd01b234bf5b4cbd034cf1be, 294 tests. Code had been seen.

## Seal amendment this round (code seen): test errors of mine

- `check_citations` treated an investors member citation as a candidate and raised a TypeError on the list value. Member citations are now checked through their candidates, as for executives.
- The R3-4 stop-during-build test is rewritten for R4-0, which supersedes R3-4.
  - The running build must end ready or failed within 10 s of /health 200 after the restart.
  - If it ends failed, the fields, history and feed are unchanged.
  - If it ends ready, it is the build made at the request's time, and each change appears once.

## What I ran (clean clone `fclone bcda0f2… clone-bcda`)

1. **Build and start:** no-cache build, 2 vCPU / 3 GiB, -e PORT. Healthy in 1 s; about 236–263 MiB of memory.
2. **Check command, isolated mode** (`checks/verifier-s4-bcda-r1`): "claimed stage: 4", highest contiguous stage 4. This is a sample only and not evidence on its own.
3. **Sealed suite:** **293 passed, 1 failed** (427 s). The failure is F1. Everything else passed:
   - origins and lineage (a First-Published-By domain normalised, a Canonical copy, a lookalike, a five-URL chain, a Canonical URL no provider serves);
   - investors (membership, selected flags, citations, true_from);
   - corroborated_since with standing origins;
   - batches: shape, order, a shared budget of 1, 30 or 500, existing dossiers cost nothing, idempotency including 100 == 1e2, visibility, validation, concurrent batches;
   - research runs failing; Tavily failing entirely;
   - a restart with batch builds running: they ended within 10 s of health, stayed within their caps, and spent_units ≥ billed;
   - export during a running batch (R4-6);
   - upgrades from the real stage-1, stage-2 and stage-3 images;
   - every stage-1 to stage-3 test and every browser test.
4. **Cost, and whether the cap cut any evidence.** I compared each build's candidates (executives titles and investors included) with every (page, value) pair the evidence pages support. I read the sample corpus's page files only, not key.json.
   - **Sample corpus: 838 units for 93 supported fields, 9.01 units per supported field.** No candidate was missing or extra. ferncliff-foods.test and tidemark-energy.test each spent exactly 80 with nothing missing.
   - **My corpus: 680 units for 47 supported fields, 14.47 units per supported field.** No candidate was missing or extra. The R4-1 lineage-only original (copy2.test, which names a founding year) gave no candidate.
   - No build exceeded 80 units.
5. **Code read:** gateway.py retries a refused call up to 5 times with a 1.1 s pause (`ATTEMPTS = 5`, `RETRY_PAUSE_S = 1.1`, `RETRY_STATUSES` including 500). This is the cause of F1. No answers keyed to fixtures.
6. **Fault planting:** not run. This revision does not pass.

## Findings

### F1: a build in which every call to every provider fails does not end within the time bound of §8

- **Sentences broken:**
  - stage-4 Provider failure: "A build in which every call to every provider fails completes `failed` (§8), within the time bound of §8."
  - stage-1 §8: "A build whose provider calls each answer within one second ends within 10 seconds of the request that started it."
- **Scenario:**
  - The mock answers every call from nimble (search, extract, research) and tavily (search, extract) with 500, at once.
  - POST /dossiers for any domain: zephyr-dynamics.test, or nothing-here.test, which has no pages.
- **Observed:** the dossier stays `building` for **13.8 s**, then ends `failed`. The build made 170 calls: 150 nimble searches, 10 research starts and 10 tavily searches, all refused.
- **Expected:** `failed` within 10 s. Each call answers in well under a second. The stage-2 exclusion covers only waiting after a 429, not after a 500.
- **Reproduce:** `NOCACHE=0 sealed/stage-4/run.sh clone-bcda/stage-4 -k every_provider_fails`, or with the mock web:

  ```sh
  POST /_mock/faults {"provider":"nimble","methods":["search","extract","research"],"mode":"error"}
  POST /_mock/faults {"provider":"tavily","methods":["search","extract"],"mode":"error"}
  ```

  then POST /dossiers and poll GET until the state is not building.
- **Side effect:** a build that keeps retrying after its test ends kept calling the mock once its faults were cleared. It spent 4 units into the next test's log (seen as echo-chamber's spent_units 71 against a log of 75 when the tests ran in that order). In isolation echo-chamber's spent_units equals the log, 71 = 71.

## Notes

- Spend per supported field on the sample corpus: 9.01 (stage 3: 9.94). Builds cost 61–80 units, and two reach the cap with no evidence lost.
