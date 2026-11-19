VERDICT: PASS
REVISION: 20e75d5ba02fceddfb7ef9f0ea23c3278e6efc34

# Verifier, stage 1, round 7 (after FIX 1 6, R1-10)

Sealed suite: sha256:9b4b0f022c2351e3cb137ab87e95c6054aa5e85525c785ce9633b07fcabd7bd8 (167 tests; R1-8, R1-9 and R1-10 applied).

## Reported problem first: R1-10 clipped research excerpts
- `test_build_correct[clipworth-labs.test]` passes: founded_year stays unknown. The research claim cites "Clipworth Labs was founded in 2016", a clipped, unterminated part of a negated page sentence. On 3befa4f this test failed (value 2016 asserted).
- Code read: `_is_page_sentence` takes the excerpt whole. When the build holds the page's complete text, the excerpt must equal one of its A.1 sentences; otherwise it must be a single sentence ending in a terminator. Fixed.

## Diff since 3befa4f
`git diff --stat 3befa4f..20e75d5 -- stage-1`: dossier/evidence.py (+16/-3), dossier/text.py (the terminator/closer constants made public, no logic change), tests/test_evidence.py (builder tests). gateway.py, ledger.py, pace.py and build.py are untouched, as the builder said.

## Whole stage
1. Clean clone, `docker build --no-cache`, RUN.md mock section (host port 19080). Health 200 in 2 s.
2. Check command, isolated (`checks/verifier-s1-20e75d5-r1`): stage 1 pass, "claimed stage: 1". A sample only.
3. Sealed suite, run whole: **167 passed, 0 failed**. 2 vCPU / 3 GiB, internal network. It includes:
   - fifty_concurrent (both variants)
   - throttle and rate_limit
   - no calls after reset or import
   - lost answers charged (never-answering endpoint)
   - the crafted negator, 46-page and clipped-research companies
   Service peak: 179% CPU of a 200% allowance, 267 MiB of 3 GiB.
4. Upgrade path: none (stage 1). Restart survival: not required (§2).
5. Live never-answering run: not repeated, since gateway, ledger and pace are unchanged since round 6 (273.6 s, 80 units, 90 s per call). The suite's lost-answer test passed on this revision.
6. Cost, from the mock call log, 12 sample companies: **487 units for 69 known fields = 7.06 units per field my checks confirm as supported** (unchanged).
7. Code read: the evidence.py change only. Nothing keyed to a fixture.
8. Fault planting: done on rounds 1 and 6 and not repeated.

## Findings
None.

## Notes (non-blocking)
N1, N5, N6, N7 carried.
