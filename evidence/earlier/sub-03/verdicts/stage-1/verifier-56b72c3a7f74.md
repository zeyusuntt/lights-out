VERDICT: PASS
REVISION: 56b72c3a7f749b788b119895b55f980bf9e26be5

# Verifier, stage 1, round 2 (after FIX 1 1)

Sealed suite unchanged since round 1: sha256:3c4498b6914768e7feaa760844d9e6b77325c489b5267e2c89ba8f2474ee5cfe (161 tests).

## Reported problem first: S1-227 (live build ends within 300 s) and S1-226
- Experiment: NIMBLE_BASE_URL=http://sdk.nimbleway.com:8080/nimble. The host `sdk.nimbleway.com` is an alias on an internal network for a server that accepts connections and never answers, so the service runs in live mode. Image started with --cpus 2 --memory 3g; one POST /dossiers.
- Result: the build ended `failed` 90.5 s after the request (≤300 s). spent_units=37: fast search 5 + 7 lite 7 + research 25, lost calls charged in full per §9. All 9 provider connections were held 90.0 s before the service gave up (≥30 s, S1-226). No 5xx while polling.
- Code read of the fix (gateway.py, build.py): one window per build. Calls are cut at 285 s and the outer wait cancels stragglers at remaining+1 s. No call or retry starts with <30 s left, and each call's timeout is min(limit, remaining) ≥ 30 s. Retries stop after 200 s (live) / 8 s (mock), so gathering is not stopped for time within the first 120 s. Cancelled in-flight calls are charged in full.
- Status: fixed.

## Whole stage
1. Clean clone, `docker build --no-cache`, RUN.md mock section (host port 19080). Health 200 in 2 s.
2. Check command, isolated (`checks/verifier-s1-56b72c3-r1`): stage 1 pass, "claimed stage: 1". A sample only.
3. Sealed suite: 161 passed, 0 failed, 2 vCPU / 3 GiB, internal network, peak 238 MiB.
4. Upgrade path: none (stage 1). Restart survival: not required (§2).
6. Cost, from the mock call log, 12 sample companies: **487 units for 69 known fields = 7.06 units per field my checks confirm as supported**. That is identical to round 1; 39–43 units per build.
7. Code read: only gateway.py and build.py changed since 49a2c1a. Nothing in them is keyed to a fixture.
8. Fault planting was done on round 1 (6/8 caught first time; F1 closed by a post-seal addition; F2 equivalent on this plan). Not repeated, since this is not the stage's first passing revision.

## Findings
None.

## Notes (non-blocking)
- N1 (carried): short lite/fast results are treated as complete pages. Correct for the mock; may under-gather on live Nimble.
- N3: a task cancelled at the window's end while still waiting for the 32-call semaphore is also charged in full, though no request was sent. Only possible on live after 285 s with >32 calls queued. spent_units could then overstate cost.
- N4: the Nimble client's 90 s timeout also bounds the research HTTP call: research was abandoned at 90 s, not 240 s. That is allowed (≥30 s). A live research run of about a minute still fits.
