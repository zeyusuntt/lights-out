VERDICT: PASS
REVISION: c772508d90a96c5214a26528c59a93ba38336cd3

# Verifier verdict: stage 1, round 1

Seal in force: SEAL AMENDED 1 sha256:05e10a6eec3d0b7bfd94ec9b84566d81f458316cb732863586f972083d75938a, 170 tests.
History: SEALED c9a824d2… (160 tests, no code seen) → amendment 1 b7f7a9ad… (ledger and rulings, no code seen) → amendment 2 aaa3cc36… and amendment 3 05e10a6e… (code seen, below).

## What I ran (clean clone `fclone c772508… clone-c772`)

1. **RUN.md:** I ran its build-and-start command word for word in an empty environment (`env -i`). The image built and `/health` answered 200 `{"status":"ok"}` within 3 s. The image also has to start with only `-e PORT` and a port mapping. Under run.sh it did so at 2 vCPU / 3 GiB with the provider variables pointed at the mock, and was healthy in 0–1 s.
2. **Check command, isolated mode:** output in `checks/verifier-s1-c772-r1`. It printed "stage 1: pass" and "claimed stage: 1". Stage 2 failed there, as expected for a stage-1 folder. This is a sample only and not evidence on its own.
3. **Sealed suite:** `sealed/stage-1/run.sh clone-c772/stage-1` builds with no cache, runs the service at 2 vCPU / 3 GiB with -e PORT, and uses the mock web with my own corpus. Result: **170 passed, 0 failed** (178 s). Service memory was about 250 MiB.
4. **Upgrade path:** none; this is stage 1.
5. **Cost:** I read the mock's priced call log. Every known field below was checked: its citations were served prose, single sentences, and support the value (Appendix A as I read it). None were unsupported.
   - My corpus, 5 companies: **141 units for 18 supported fields, 7.83 units per supported field**. 2 of the 5 companies have nothing supportable, by design.
   - The kit's sample corpus, 12 companies: **369 units for 69 supported fields, 5.35 units per supported field**. Builds cost 7 to 46 units.
   - No build exceeded 80 units. That includes `sprawl-hub.test`, 66 pages that support nothing, where the build stopped at the cap.
   - The 25-unit research run is spent only while a field is still unknown. That is needed for fields only a research claim supports (`lumen-grid.test` ceo).
6. **Code read:**
   - No answers keyed to fixtures. The app contains no corpus domains or names.
   - Units are reserved before each call (budget.py) and refused calls are charged 0.
   - Builds are cancelled when reset or import replaces the state, and a build's result is dropped if the state was replaced (builds.py).
   - Idempotency records are keyed by (user, method, path as received, key), as R1-3 rules. The check and the write happen with no await between them.
   - Live timing settings (call 60 s, research 200 s, deadline 285 s) fit the §8 30 s / 120 s / 300 s bounds.
7. **Planted faults (8, one per throwaway copy, frozen suite, stopped at first failure):**
   - **Caught (6):** negation check removed; replay answering with the current state; header not stripped from prose; has_more off by one; the Tavily fallback for the exact-domain search removed; a failed build wiping fields.
   - **Survived (1): the 80-unit cap raised to 400.** I added a post-seal test (`sprawl-hub.test`, many pages that support nothing) in amendment 2. It catches the fault, and the real revision passes it.
   - **Equivalent (1):** reset/import no longer cancelling builds and no longer checking whether the state was replaced. In this design an old build only writes to objects the new state no longer holds, so nothing changes that any test can see. No sentence is broken.

## Test amendments made after seeing this revision (my misreadings, not product faults)

- A clock test set `now` to 09:30+02:00 (07:30Z), which is earlier than the fixture's 09:00Z. The service was right to answer 422. The test now uses 11:30+02:00.
- The `Authorization: "Bearer "` case (trailing space) was dropped: the HTTP client refuses to send that header.
- The check that nimble extracts don't use `render` (cost equals the number of URLs) now looks only at calls that succeeded. A refused call costs 0 (§9).
- A missing import in the amendment-1 file.
- Isolation: the mock logs a delayed call when it answers, so calls from builds a previous test had cancelled landed in the next test's log. The env fixture now waits after any test that set a delay fault.

## Findings

None.

## Notes (do not block)

- **RUN.md:** its command passes `-e NIMBLE_BASE_URL="$NIMBLE_BASE_URL"`. In a shell where the variable is unset, that sets it to an empty string inside the container (seen with `docker exec … env`). Its own table says "never set it empty", and the mock README says an empty value makes every call fail. The deployment supplies the variables, so this is not a breach. Suggest dropping the flag when it is unset, or treating empty as unset.
- **Rejections the specification does not list (question for the foreman):**
  - Signup rejects a display_name of only spaces with 422; §6 lists only empty or longer than 100.
  - Signup rejects emails containing whitespace.
  - A reset fixture with two users sharing an id is 422; §4 names only a shared email.
- **One transient timeout:** on the first full run, one `GET /dossiers` in the 50-in-flight test took longer than 5 s. It did not happen again in 4 later full runs, 3 separate runs of the concurrency tests, or a standalone test of 50 in flight (half logins, half lists) over 3 rounds: slowest login 0.33 s, slowest list 0.07 s. I put it down to the test environment.
- **Not tested offline:** the clock before the first reset (R1-1, first half), and the live-provider timing in §8 beyond reading the code.
