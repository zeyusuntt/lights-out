VERDICT: PASS
REVISION: bc19abf8cbde23c3a2fa50f23baa55dbfe48d731

Seat: verifier. Stage 2, round 2, after FIX 2 1. Worked from a clean clone (fclone) of the exact hash.
- stage-2/ was built fresh with no cache per RUN.md; the clone's accepted stage-1/ was built as the previous-stage image.
- Both ran under --cpus 2 --memory 3g on an internal network with the kit mock web.

## Reported problems retested first
- S2-F1, a throttled extract after slow research: fixed. New post-seal test test_post_seal_throttled_extract_after_slow_research (research delayed 8 s, every nimble extract throttled; exact candidate set, within 80 units, spent_units = log cost).
  - On 3cf3cef0 it fails: legal_name, funding_total and other candidates of https://tarnwick-labs.test/ are missing.
  - On this revision it passes.
  - Reproduce: `run.sh <clone>/stage-2 -k throttled_extract_after_slow`.
- Product-user notes 1–6 (UI copy, layout, nav when signed out): the automated UI tests pass on all of them. Whether they look right is for the product-user to judge.

## Whole suite
- `run.sh <clone>/stage-2`: 222/222 in the full run, plus the new S2-F1 test with all post-seal tests (13/13). The full suite is 223 tests (seal sha256 printed in SEAL AMENDED).
- Check command, isolated: `harness run ... --stage 2 --mode isolated --out work/checks/verifier-s2-bc19-r2` → "claimed stage: 2". This is a sample, not a verdict.

## Code read (diff from 3cf3cef0)
- providers.py: a 429 is now retried up to 5 attempts with no time cut-off; the retry window applies to 5xx and lost calls only.
- The rest is UI copy and layout in app.js/app.css: nav hidden when signed out, people-first auth errors, "Research in progress" during a first build.
- No change to candidates, the selection rule or migration.

## Cost
1038 units for 92 of 92 correct fields over 21 first builds: 11.3 units per correct field. Per build 36–63 units. Unchanged.

## Notes (no sentence broken)
- N1 RUN.md still builds the image tagged dossier-stage-1. N2 Every build makes all 8 lite searches. N3 The UI request timeout is 10 s. N4 scrypt runs on the event loop.
