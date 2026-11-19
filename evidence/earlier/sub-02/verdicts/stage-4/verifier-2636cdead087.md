VERDICT: BLOCK
REVISION: 2636cdead087f5d718627149e942ba9b953364e2

# Verifier verdict: stage 4, round 2

Seal in force: SEAL AMENDED 4 sha256:ff76e7fd8ebba8aa7d382347d3c25f64be37564297ae05a5fe20cd97692954fa, 305 tests. Code had been seen.

## Seal amendments this round (code seen)

- **Amendment 3, RULING R4-8:** a field present with value null is 400 malformed_request. 7 cases, unchanged since the round-1 verdict.
- **Amendment 4, post-seal addition.** The foreman asked me to check that transient 5xx answers still give ready with full evidence. I added a test in 4 cases: nimble answers 500 for the first 1.5 s of a build, on extract, on search, on research, or on all three. The build must still end ready with the expected values and every candidate.
  - Check of the test: it passes on the round-1 revision bcda0f2 (4 of 4) and fails on this revision (4 of 4). Both requirements can be met at once.

## Reported problems, retested first

- **F1 / SR4-2, total provider failure:** passes. A build with every call failing ended failed in 1.2 s.
- **SR4-1 and the R4-8 matrix:** passes.
- Command: `-k "every_provider_fails or r4_8 or batch_validation or every_research or tavily_fails or rate_limit or weather or throttle"` gave 27 passed.

## Whole run (clean clone `fclone 2636cde… clone-2636`)

1. **Build and start:** no-cache build, 2 vCPU / 3 GiB, -e PORT. Healthy in 1 s; about 248 MiB of memory.
2. **Check command, isolated mode** (`checks/verifier-s4-2636-r2`): "claimed stage: 4". This is a sample only and not evidence on its own.
3. **Sealed suite:** the 301 tests sealed before amendment 4 all passed, 0 failed (326 s). The 4 post-seal cases fail; that is F2.
4. **Cost, and whether the cap cut any evidence.** I compared each build's candidates with every (page, value) pair the evidence pages support. I read the sample corpus's page files only, not key.json.
   - **Sample corpus: 838 units for 93 supported fields, 9.01 units per supported field.** No candidate was missing or extra.
   - **My corpus: 680 units for 47 supported fields, 14.47 units per supported field.** No candidate was missing or extra.
   - No build exceeded 80 units.
5. **Code read:** gateway.py `_call`. One counter of consecutive 5xx answers is kept per provider operation, shared by the build's concurrent calls. At GIVE_UP_AFTER = 6 the operation is given up for the rest of the build. Retries pause only ERROR_PAUSE_S = 0.25 s, at most ERROR_ATTEMPTS = 3 per call. So 6 failures across parallel calls give the operation up about 0.25–0.5 s into a build. This is the cause of F2.
6. **Fault planting:** not run. This revision does not pass.

## Findings

### F2: a brief 5xx outage of one Nimble operation makes the build give the operation up and lose evidence; the build ends ready with fields unknown that the evidence supports

- **Sentences broken:**
  - stage-1 §8: "When a build completes `ready`, each field is `known` exactly when the evidence (§4) supports a value for it."
  - stage-2 Candidates: "Every value that a page of the evidence (§4) supports for a field is a candidate".
  - stage-4 Provider failure: "A provider may answer a call with an error (any 5xx status, or 429). The build continues: it may make the same request again, through that provider or another."
  - The total-failure exception applies only when every call to a provider fails. Here Nimble answers again 1.5 s into the build.
- **Observed** (probe on a clean build of this revision, mock web with my corpus):

  | Nimble answers 500 for the first 1.5 s on | Result |
  |---|---|
  | extract | orbit-forge.test ready after 0.5 s with **0 of 16 candidates**, all six fields unknown, spent 40 |
  | search | orbit-forge.test ready with 15 of 16 candidates, a wrong selected value |
  | research | lumen-grid.test ready with 6 of 7 candidates; the ceo, which only the research-cited page supports, is unknown |
  | search, extract and research | zephyr-dynamics.test ready after 1.1 s with **0 of 6 candidates**, spent 8 |

- The same test passes on the round-1 revision bcda0f2, which retried with a longer pause.
- **Reproduce:**
  - `NOCACHE=0 sealed/stage-4/run.sh clone-2636/stage-4 -k transient_5xx`, which fails 4 of 4.
  - Or with the mock web: POST `/_mock/faults {"provider":"nimble","methods":["extract"],"mode":"error"}`, POST /dossiers orbit-forge.test, and 1.5 s later POST `/_mock/faults {"provider":"nimble","methods":["extract"],"mode":"none"}`. The dossier ends ready with no candidates.
- **What would satisfy both requirements** (a note, not a prescription): keep retrying a failing operation for a bounded window, a few seconds measured from the build's start, rather than giving it up after 6 consecutive failures. That still ends a total-failure build within 10 s.

## Notes

- Spend per supported field on the sample corpus is 9.01, the same as round 1.
