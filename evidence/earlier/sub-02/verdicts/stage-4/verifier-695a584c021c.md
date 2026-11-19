VERDICT: BLOCK
REVISION: 695a584c021cd5d61c09568504bedcbd3afae63a

# Verifier verdict: stage 4, round 3

Seal in force: SEAL AMENDED 4 sha256:6929852985e0377f98643aed1194b593ae30cf4807e9f307a4aa75903ddf77e8, 307 tests. Code had been seen.

## Seal amendments this round (post-seal additions, code seen)

- **Amendment 5:** total provider failure must still end failed within 10 s while a batch of three and three single builds run at the same time.
- **Amendment 6, for RULING R4-9:** the service is started with NIMBLE_BASE_URL on the live host name, `http://sdk.nimbleway.com:8080/nimble`. That name is an alias of the mock web on the suite's network; run.sh adds the alias. With every Nimble call answered 500 at once, the build must end failed within 10 s.

## Reported problems, retested first

- **F2 / SR4-4, a brief outage:** passes. Nimble 500 for the first 1.5 s on extract, search, research, or all three: all 4 cases end ready with full evidence.
- **Total failure:** passes. One build alone, and three builds plus a batch of three at once, all end failed within 10 s.
- **The R4-8 / R4-8a matrix:** passes.
- **Earlier failure handling** (research failing, Tavily failing, rate limits, weather, throttle): passes.
- Command: the retest selection gave 32 of 32.

## Whole run (clean clone `fclone 695a584… clone-695a`)

1. **Build and start:** no-cache build, 2 vCPU / 3 GiB, -e PORT. Healthy in 1 s; about 247 MiB of memory.
2. **Check command, isolated mode** (`checks/verifier-s4-695a-r3`): "claimed stage: 4". This is a sample only and not evidence on its own.
3. **Sealed suite** (seal of amendment 5): **306 passed, 0 failed** (390 s). The one test added in amendment 6 fails; that is F3.
4. **Cost, and whether the cap cut any evidence.** I compared each build's candidates with every (page, value) pair the evidence pages support. I read the sample corpus's page files only, not key.json.
   - **Sample corpus: 838 units for 93 supported fields, 9.01 units per supported field.** No candidate was missing or extra.
   - **My corpus: 680 units for 47 supported fields, 14.47 units per supported field.** No candidate was missing or extra.
   - No build exceeded 80 units.
5. **Code read:** gateway.py `Timing.for_environment`. In live mode (`is_live()`: NIMBLE_BASE_URL unset or host sdk.nimbleway.com), `error_retry_s=120.0`. A fast-answered 5xx is retried until 120 s into the build. This is the cause of F3.
6. **Fault planting:** not run. This revision does not pass.

## Findings

### F3: in the live-host configuration, a build whose every call is answered 500 at once takes about 120 s to end failed

- **Sentences broken:**
  - stage-1 §8: "A build whose provider calls each answer within one second ends within 10 seconds of the request that started it."
  - stage-4 Provider failure: "A build in which every call to every provider fails completes `failed` (§8), within the time bound of §8."
  - RULING R4-9: the 10 s bound "applies on any host, live included, when every call is answered within one second (5xx included) ... fast-answered errors must fit 10 s."
- **Scenario:**
  - Start the image with `NIMBLE_BASE_URL=http://sdk.nimbleway.com:8080/nimble`, where that name resolves to the mock web.
  - Set the mock fault nimble search, extract and research to `error`, then POST /dossiers.
- **Observed:**
  - `failed` after **119.9 s**, with 976 refused calls.
  - The same image with no faults ends ready in 0.3 s, so the live configuration itself works.
- **Reproduce:** `NOCACHE=0 sealed/stage-4/run.sh clone-695a/stage-4 -k live_host` fails (still building at 10 s). Or start the image as above beside the mock web with that network alias.

## Notes

- Spend per supported field on the sample corpus is 9.01, unchanged.
- Per R4-9, a longer live retry window may still apply to calls that are themselves slow.
