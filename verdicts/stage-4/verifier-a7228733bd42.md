VERDICT: PASS
REVISION: a7228733bd425af053de0063ec2a3fc1ef68d873

Seat: verifier. Stage 4, round 3, after FIX 4 2. Worked from a clean clone (fclone) of the exact hash.
- stage-4/ was built fresh with no cache per RUN.md.
- The clone's accepted stage-1/2/3 folders were built as previous-stage images for every upgrade path.
- All ran under --cpus 2 --memory 3g on an internal network with the kit mock web.

## Reported problems retested first
- V4-2 (R4-9): fixed. quillon-dynamics.test in a batch with budget = unbatched cost − 3 (41) and − 23 (21) ends with every supported field known and the exact candidate set, spent ≤ budget.
- V4-1: fixed and still passing. tarnwick-labs.test in a batch with budget 49 gets founded_year 1987 with the exact candidate set.
- Reproduce: `run.sh <clone>/stage-4 -k "short_batch_budget or post_seal_batch_budget"` → 3/3.

## Whole suite
- `run.sh <clone>/stage-4`: 306/306, including restart phase B (idle `docker kill`/start) and phase C (a kill while a refresh and a batch run).
  - Phase C: interrupted builds are terminal within 10 s of /health; a failed end leaves fields unchanged; billed units are counted in the dossier and in the batch; the batch stays within its budget.
- After the post-seal corpus addition (below), the affected tests pass: 23/23.
- Check command, isolated: `harness run ... --stage 4 --mode isolated --out work/checks/verifier-s4-a722-r3` → "claimed stage: 4". This is a sample, not a verdict.
- Upgrade paths from the real stage-1, stage-2 and stage-3 images all pass.

## Code read (diff from 010b35ad)
- research.run: unbatched builds are unchanged.
- In a batch, research runs alongside the pages only when the remainder affords research plus every planned render plus one. Otherwise the searched pages are rendered first, and research runs only while a field is unsupported and 25 + 3 still fit; then the cited pages are rendered.
- The R4-6 latch is unchanged and is decided at reservation time.
- Originals' 1-unit lineage fetches are not in the plan estimate. Near the limit, an original can be refused, and the origin then falls back to the host (R4-2).

## Fault planting (first passing revision of stage 4), 7 copies
- Caught: 4 canonical hops instead of 3; Kind own kept without a registrant match; lookalike origin = registrant; investor membership ignoring own/filing kind; batch latch disabled (budget exceeded); corroborated at one origin.
- Survived: the "led by" investor rule applied without an amount. That was a hole: the suite corpus had no "led by" sentence without an amount. I added "Lumen Forge is led by Ivo Grant." to the corpus as a post-seal addition. It catches the fault and passes on this revision.

## Cost
1302 units over 24 first builds, for 103 correct of 103 supportable fields: 12.6 units per correct field. Per build 38–74 units (max 74 of 80).

## Notes (no sentence broken)
- N1 The heaviest build spends 74 of its 80 units.
- N2 The batch plan estimate leaves out lineage fetches (R4-2 fallback applies).
- N3 scrypt runs on the event loop.
