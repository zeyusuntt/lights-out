VERDICT: PASS
REVISION: 7eac8a66d4239f624bac647bfebd084257121341

# Verifier, stage 1, round 5 (after FIX 1 4 and addendum)

Sealed suite: sha256:41fb35808b8f94d1d9926c334f47246d1fb1bb51592bbbd3dc7ec598fd548e2f (165 tests; R1-8 and R1-9 applied).

## Reported problems first
- Orphaned child calls (R1-9 / FIX 1 4): `test_no_provider_calls_after_reset_or_import[reset|import]` pass. After a reset or import cuts 3 running builds, no provider call reaches the mock in the next 6 s. On 9221aaa both cases failed. Code read: `State.stop_builds` calls `Build.stop()`, which cancels every child. Fixed.
- Lost answers retried (R1-9): live mode, with a sdk.nimbleway.com alias pointing at a server that never answers, 5 concurrent builds. 99 connections, every one held 90 s before the service gave up (≥30 s, S1-226). Lost calls were retried until each build reached the 80-unit cap: spent_units 80 each, never more (§1.2). All builds ended `failed` at 273.3 s (≤300 s, S1-227); the last connection closed at 276 s. No 5xx. Fixed.
- 50 concurrent builds (S1-224) with the 1000-connection pool: both `fifty_concurrent` variants pass (no delay, 0.9 s delay). Resource peak over the whole suite run, sampled every 1 s by docker stats: 161% CPU of a 200% (2 vCPU) allowance, 255 MiB of 3 GiB.
- WebRouter route: Nimble's AsyncNimble client is handed to WebRouter through its supported `async_client` provider option (web_router/constants.py AUTO_CLIENT_OPTION). Every call still goes through `router.search/extract/research`. No direct provider call.

## Whole stage
1. Clean clone, `docker build --no-cache`, RUN.md mock section (host port 19080). Health 200 in 2 s.
2. Check command, isolated (`checks/verifier-s1-7eac8a6-r1`): stage 1 pass, "claimed stage: 1". A sample only.
3. Sealed suite: 165 passed, 0 failed, 2 vCPU / 3 GiB, internal network.
4. Upgrade path: none (stage 1). Restart survival: not required (§2).
6. Cost, from the mock call log, 12 sample companies: **487 units for 69 known fields = 7.06 units per field my checks confirm as supported** (unchanged).
7. Code read: build.py, gateway.py, service.py, state.py diffs. Nothing in them is keyed to a fixture.
8. Fault planting was done on round 1 and not repeated.

## Findings
None.

## Notes (non-blocking)
- N1, N5 carried.
- N6: against an unreachable provider, each build now spends the full 80 units on lost calls before failing (as R1-9 requires: lost calls are charged and retried). For live use that is the most a dead endpoint can cost per build.
