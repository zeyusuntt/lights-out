VERDICT: PASS
REVISION: 49a2c1ad8429f77703a233d9f6e9bab8a42793b3

# Verifier, stage 1

Sealed suite: `seal --verify 1` digest sha256:3c4498b6914768e7feaa760844d9e6b77325c489b5267e2c89ba8f2474ee5cfe (161 tests).

## Steps
1. Clean clone (`fclone 49a2c1a...`). Built with `docker build --no-cache`. Started by the RUN.md mock-web section with the mock on a Docker network, `--cpus 2 --memory 3g`. The only change was host port 19080 for 8080, to stay in the verifier's port range. Health was 200 after 2 s. Every step RUN.md needs is in it.
2. Check command, isolated: `... harness run --track dossier --repo <clone> --stage 1 --mode isolated --out checks/verifier-s1-49a2c1a-r1`. Stage 1 passed, and the check claims stage 1 (`claimed stage: 1`). A sample run only.
3. Sealed suite: `with-slot sealed/stage-1/run.sh <clone>/stage-1` → 161 passed, 0 failed. It runs on an internal network, 2 vCPU, 3 GiB, with a second container that has no TAVILY_* variables. Peak memory 222–270 MiB.
4. Upgrade path: none, this is stage 1.
5. Restart survival: stage 1 does not require any (§2 "state need not survive a container restart"). Not tested.
6. Cost, from the mock call log, 12 sample companies at epoch 0: **487 units for 69 known fields = 7.06 units per field confirmed as supported**. My oracle and citation checks confirm all 69. The 3 unknown fields are all unsupported by the evidence: ashgrove hq_city (epoch 0), quillmate ceo, and a third tied to ferncliff's research-only trap. Each build cost 39–43 units: research 25, fast domain search 5, 9 lite searches 9, plus 0–4 extracts. Each finished in ≤0.3 s. No build came near 80. The 46-page crafted company also stayed ≤80.
7. Code read. passwords.py uses scrypt. No answer is keyed to a fixture. Budget reserves units before every call (`Gateway._attempts`). Reset and import cancel builds and switch to a new state object, so a late worker writes to an orphaned object. Idempotency check-then-claim happens with no await in between, on one event loop.
8. Fault planting, 8 faults, each in its own copy, relevant suite part only:
   - Caught: F3 (replay returned 202), F4 (no trailing-dot strip), F5 (second build during refresh), F6 (has_more off by one), F7 (export not pre-build), F8 (second successful bare-domain search).
   - F1 (negator "plans to" removed) survived at first. Hole closed with a post-seal crafted company (`trapline-systems.test`), now caught.
   - F2 (cap 80→200) survives. The candidate's plan spends at most ~43 units, so this fault changes no behaviour on any corpus, including the 46-page one. The cap is confirmed by code read only.
   - Post-seal additions: 2 corpus companies + 2 tests. The seal was amended. Every new test passes on this revision.

## Suite amendments made after seeing code (all disclosed)
- The harness mounted temp dirs empty (the oracle had no companies). Fixed by mounting from a shared path.
- Dropped the `Bearer ` header case, which the HTTP client cannot send.
- Test misread: the oracle read corpus `text`. The mock serves `static_text` where a page has one, so the oracle now uses the served text. This was my error, not the candidate's: the candidate's Austin/Brno/Ingrid Brennan/Holdings values are supported by served text.

## Findings
None.

## Notes (non-blocking)
- N1: a lite snippet shorter than 300 chars, or a fast body shorter than 1500, is treated as the complete page. That is right for the mock's documented truncation. Against live Nimble a short snippet may not be the whole prose, so some evidence could go unread on live. No sentence about the mock is broken.
- N2: research (25 of ~40 units per build) added the only support for few fields in the sample (halvorsen and windrush founded_year come from non-searchable register pages). It is needed for completeness under R1-2. No avoidable spend found.
