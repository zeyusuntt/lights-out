VERDICT: PASS
REVISION: 3befa4f40b1e66f6f38ed325043183970bc770fa

# Verifier, stage 1, round 6 (after FIX 1 5: ledger.py and pace.py)

Sealed suite: sha256:3b433448f4885f4ed9f30916724cf3cbbec16e9fc54a362f1ee479015f0de785 (166 tests). It adds a post-seal never-answering provider endpoint.

## Requested retests first
- Throttle that clears (429 then normal; completeness required, R1-7): `test_transient_throttle_complete[brightwater, quillmate]` pass.
- Persistent rate_limit (invariants only): `test_throttled_providers_keep_invariants[rate_limit]` passes.
- Live deadline, with a sdk.nimbleway.com alias pointing at a server that never answers, 5 concurrent builds: 100 calls, each held 90 s (≥30 s, S1-226). Every build ended `failed` at 273.6 s (≤300 s, S1-227) with spent_units 80 (≤80). No 5xx.
- 50 concurrent builds (no delay; 0.9 s delay): both pass. Resource peak over the whole suite: 100% CPU of a 200% (2 vCPU) allowance, 255 MiB of 3 GiB.
- No provider calls after reset or import: both pass.
- WebRouter route: search, extract and `submit_research` go through AsyncWebRouter, and research status checks go through the WebRouter job (`job.astatus()`). No direct provider call.

## Whole stage
1. Clean clone, `docker build --no-cache`, RUN.md mock section (host port 19080). Health 200 in 2 s.
2. Check command, isolated (`checks/verifier-s1-3befa4f-r1`): stage 1 pass, "claimed stage: 1". A sample only.
3. Sealed suite: 165/165 passed in the full run (sha256:41fb…). The one post-seal test (`test_lost_answers_are_charged`) also passed on this revision, run separately: `run.sh <clone>/stage-1 /suite/test_amend_dangers.py -k lost_answers` → 1 passed.
4. Upgrade path: none (stage 1). Restart survival: not required (§2).
6. Cost, from the mock call log, 12 sample companies: **487 units for 69 known fields = 7.06 units per field my checks confirm as supported** (unchanged).
7. Code read: ledger.py (each reservation settled exactly once: refusal 0, undispatched 0, answered or lost full) and pace.py (fast mode: dispatch cut-off at 9 s, short pauses; slow mode: ≥30 s per call, retries to 200 s, end 285 s). Nothing keyed to a fixture.
8. Fault planting in the new code, 7 faults, one copy each:
   - Caught: G3 (refusals charged), G5 (fast dispatch cut-off 9→60 s), G6 (double charge), G7 (no retries).
   - G1 (lost answers charged 0) survived. Hole closed by a post-seal addition (never-answering endpoint plus `test_lost_answers_are_charged`), now caught. The new test passes on this revision.
   - G4 (no extra pause after a 429) and G8 (dispatch-time fit check removed) survived. No sentence requires either: the mock's 429 sequence ends after three refusals, and retries re-check the window. They behave the same in every scenario tested. Notes only.

## Findings
None.

## Notes (non-blocking)
- N1, N5, N6 carried.
- N7: in G4 and G8 the 1.05 s pause after a 429 and the dispatch-time fit check have no observable effect under the mock. They are kept for the live provider's rate limits.
