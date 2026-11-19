VERDICT: PASS
REVISION: 9221aaaa96fb8310b2e221d7b8b360f0e3725107

# Verifier, stage 1, round 4 (after FIX 1 3)

Sealed suite: sha256:eefd826347f382fb8b25700389460034a7e814cb0611e6a478bfee0afb520198 (163 tests). It includes the R1-8 citation rule (each citation must equal one complete A.1 sentence of the served prose; sentences over 500 chars give no support) and the S1-224 fifty-build tests.

## Reported problem first: S1-224 (50 concurrent builds within 10 s)
- `run.sh <clone>/stage-1 /suite/test_concurrency.py -k fifty_concurrent`: 2 passed (no delay, and every provider call delayed 0.9 s). Each of the 50 builds ended `ready` within 10.5 s of its own POST. On d5b3d5b the same test failed with 14–16 s.
- Resources during those 50 builds, sampled every 1 s by `docker stats`: peak CPU 88% of a 200% (2 vCPU) allowance, peak memory 134 MiB of 3 GiB.
- Code read: the global 32-slot semaphore is replaced by a 12-slot semaphore per build Window. The window, dispatch-only charging and reservations are unchanged (diff: gateway.py only, 16 lines).
- Status: fixed.

## Regression: live deadline and queued-call accounting
Live mode, with a sdk.nimbleway.com alias pointing at a server that never answers, 5 concurrent builds:
- 45 connections, each held 90.0 s, so no call was abandoned before 30 s (S1-226).
- All 5 builds ended `failed` at 90.8 s, ≤300 s (S1-227).
- spent_units 37 each, 185 in total = the cost of exactly the 45 calls sent (S1-245).

## Whole stage
1. Clean clone, `docker build --no-cache`, RUN.md mock section (host port 19080). Health 200 in 2 s.
2. Check command, isolated (`checks/verifier-s1-9221aaa-r1`): stage 1 pass, "claimed stage: 1". A sample only.
3. Sealed suite: 163 passed, 0 failed, 2 vCPU / 3 GiB, internal network, peak 250 MiB.
4. Upgrade path: none (stage 1). Restart survival: not required (§2).
6. Cost, from the mock call log, 12 sample companies: **487 units for 69 known fields = 7.06 units per field my checks confirm as supported** (unchanged). 39–43 units per build.
7. Code read: the per-build semaphore change only.
8. Fault planting was done on round 1 and not repeated.

## Findings
None.

## Notes (non-blocking)
- N1 (carried): short lite/fast results are treated as complete pages. Correct for the mock; may under-gather on live Nimble.
- N4 (carried): the Nimble client's 90 s timeout also bounds research. That is allowed.
- N5: with no global cap, 50 builds can hold up to 600 provider requests at once. That is fine on the mock. Against live Nimble it may draw 429s, which are retried within the window and cost 0.
