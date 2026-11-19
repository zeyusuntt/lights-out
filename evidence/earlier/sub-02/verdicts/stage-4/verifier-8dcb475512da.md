VERDICT: BLOCK
REVISION: 8dcb475512daa1a4e5acd24ea52818d9724dd780

# Verifier verdict: stage 4, round 5 (revised after RULING R4-10)

**This replaces my PASS for this revision** (commit eff7520). RULING R4-10 (0ad5fed) arrived after that PASS. It puts a graceful `docker stop` in scope of Restarts. Under it, this revision breaks two sentences; see F4 below. Everything else in this file is unchanged evidence from the same clean clone.

Seal now in force: SEAL AMENDED 4 sha256:835c75671e3febf21f2809011acad81389466c230dc8ee38c18ffafdd6caca40, 309 tests. Amendment 9, a post-seal addition for R4-10, is test_post_seal_graceful_stop_counts_billed_units.

Seal in force: SEAL AMENDED 4 sha256:5da0d8ff9961d1e4575df6bc4e94cbd7f85c99474298aa1270cfea69424b01d1, 308 tests. Code had been seen.

## Seal amendment this round (post-seal addition)

SR4-6 (second-reader on 237fef5) was not covered by my suite. I added a test:
- Every nimble call answers 429 at once. Create lumen-grid.test, then SIGKILL and start the service 0.5 s into the 429 waits, and clear the faults.
- The build must end within 10 s of health, with spent_units between the provider bill and the bill plus 5. The 5 allows at most one cheap call in flight; refused calls cost nothing.
- Check of the test: on 237fef5 it fails; on 8dcb475 it passes.

## Reported problems, retested first

- **SR4-6:**
  - The reporter's probe (`SECOND_READER_ONLY=stage4-refused-restart …/second-reader/probes/stage-4/run.sh clone-8dcb/stage-4`) gave PASS, 139 assertions.
  - My own probe killed the container during 429 waits 3 times. spent equalled billed each time: lumen-grid 52 = 52, orbit-forge 76 = 76, zephyr 49 = 49, each build ending 1.0 s after health.
  - My post-seal test passes.
- **Every earlier reported problem and the restarts:** 39 of 39 pass.
  - Command: `-k "live_host or transient_5xx or every_provider_fails or total_failure or r4_8 or batch_validation or every_research or tavily_fails or rate_limit or weather or throttle or restart or r4_6"`.
  - That covers live-host fast failure, transient outages, total failure alone and concurrent, the R4-8 / R4-8a matrix, failure handling, restarts (with batches, during builds, at rest, the clock) and export during a batch.
- **Slow-call protection on the live host:** the product diff since 237fef5 does not touch gateway.py. Round 4's probe stands: every call delayed 10 s, ready after 30.4 s with every expected value.

## Whole run (clean clone `fclone 8dcb475… clone-8dcb`)

1. **Build and start:** no-cache build, 2 vCPU / 3 GiB, -e PORT. Healthy in 1 s; about 298 MiB of memory.
2. **Check command, isolated mode** (`checks/verifier-s4-8dcb-r5`): "claimed stage: 4". This is a sample only and not evidence on its own.
3. **Sealed suite:** **308 passed, 0 failed** (405 s, final seal). This covers every stage-1 to stage-4 test, the browser tests, and upgrades from the real stage-1, stage-2 and stage-3 images.
4. **Cost, and whether the cap cut any evidence.** I compared each build's candidates with every (page, value) pair the evidence pages support. I read the sample corpus's page files only, not key.json.
   - **Sample corpus: 838 units for 93 supported fields, 9.01 units per supported field.** No candidate was missing or extra.
   - **My corpus: 683 units for 48 supported fields, 14.23 units per supported field.** No candidate was missing or extra.
   - No build exceeded 80 units.
5. **Code read:** the diff since 237fef5 is budget.py and builds.py only. The running-build record is written before each call and again as soon as the call's cost is known, refusals included. No answers keyed to fixtures.
6. **Fault planting:** done on 237fef5, the first stage-4 revision to pass. 7 of 8 were caught, and the one survivor is covered by a post-seal test.

## Findings

### F4 (under RULING R4-10): a `docker stop` during a build loses the units of the calls in flight, and the build then spends more than 80 units across the stop

- **Sentences broken:**
  - stage-4 Restarts: each running build "Is one build across the restart: its calls before and after the stop together spend at most 80 units (§9)".
  - stage-4 Restarts: each running build "Has every unit a provider billed for its calls, before and after the stop, counted in its dossier's `spent_units`".
  - RULING R4-10: "a shutdown/cancellation path must never release the reservation of a call a provider may have billed".
- **Scenario:**
  - Every nimble call is delayed 2 s. POST /dossiers lumen-grid.test.
  - 1 s later run `docker stop -t 10 <container>` (SIGTERM), then `docker start`, and clear the delay.
- **Observed:**

  | Domain, stop | spent_units | Provider bill (mock log) |
  |---|---|---|
  | lumen-grid.test, docker stop | **52** | **84** |
  | orbit-forge.test, docker stop | **76** | **108** |
  | zephyr-dynamics.test, SIGKILL, control | 73 | 73 |

  - With SIGTERM the 32 units of the calls in flight (7 lite searches and 1 research run) are released and not counted.
  - The resumed build then spends again, so one build's calls across the stop exceed 80.
  - SIGKILL is unaffected.
- **Reproduce:** `NOCACHE=0 sealed/stage-4/run.sh clone-8dcb/stage-4 -k graceful_stop` fails: `84 <= 80`.
- **Likely cause** (code read, budget.py and builds.py): cancelling the build at shutdown settles in-flight reservations to 0 (`except asyncio.CancelledError: self._budget.settle(cost, 0)`) and persists that, instead of keeping the reservation as possibly billed.
