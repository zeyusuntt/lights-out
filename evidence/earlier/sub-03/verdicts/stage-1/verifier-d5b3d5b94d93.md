VERDICT: PASS
REVISION: d5b3d5b94d938f30847c7db818f6582785fb2b39

# Verifier, stage 1, round 3 (after FIX 1 2)

Sealed suite unchanged: sha256:3c4498b6914768e7feaa760844d9e6b77325c489b5267e2c89ba8f2474ee5cfe (161 tests).

## Reported problem first: S1-245 / S1-280 / S1-281 (my N3, queued calls charged)
- Code read (only gateway.py `_attempts` changed since 56b72c3): `dispatched` is set just before `wait_for(call(...))`. If the task is cancelled before that point (still queued on the semaphore, or before the slot check), the reservation is released at cost 0. If it is cancelled after dispatch, the full cost is charged. Timeouts and lost calls are charged in full, and refusals cost 0. The accounting no longer charges an undispatched call.
- Experiment, live mode: a sdk.nimbleway.com alias pointing at a server that never answers. 5 concurrent builds, 45 calls against 32 slots, so 13 calls queue. Result: 45 connections reached the server, each held 90.0 s. Each build had spent_units 37 = its 9 sent calls (fast 5 + 7 lite + research 25). Total 185 = the cost of exactly the 45 calls sent. Queued calls were dispatched later and charged once. Builds ended `failed` at 90.7 s and 181.1 s (≤300 s, S1-227), and no call was abandoned before 30 s (S1-226). No 5xx.
- The exact N3 window, a call still queued when the 285 s cut-off arrives, cannot be reached black-box: the client's 90 s timeout frees slots long before 285 s. That branch is confirmed by code read.
- Status: fixed.

## Whole stage
1. Clean clone, `docker build --no-cache`, RUN.md mock section (host port 19080). Health 200 in 2 s.
2. Check command, isolated (`checks/verifier-s1-d5b3d5b-r1`): stage 1 pass, "claimed stage: 1". A sample only.
3. Sealed suite: 161 passed, 0 failed, 2 vCPU / 3 GiB, internal network, peak 238 MiB.
4. Upgrade path: none (stage 1). Restart survival: not required (§2).
6. Cost, from the mock call log, 12 sample companies: **487 units for 69 known fields = 7.06 units per field my checks confirm as supported** (unchanged). 39–43 units per build.
7. Code read: the four-line accounting change only. No timing code changed (confirmed by diff).
8. Fault planting was done on round 1 and not repeated.

## Findings
None.

## Notes (non-blocking)
- N1 (carried): short lite/fast results are treated as complete pages. Correct for the mock; may under-gather on live Nimble.
- N4 (carried): the Nimble client's 90 s timeout also bounds research. That is allowed (≥30 s).
