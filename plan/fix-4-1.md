FIX 4 1 — stage 4, round 1, on b928822534e8f8b9b7ce8dbf555bfbda1a42deab

Verdicts: product-user PASS (verdicts/stage-4/product-user-b928822534e8.md); verifier BLOCK (verdicts/stage-4/verifier-b928822534e8.md); second-reader BLOCK (verdicts/stage-4/second-reader-b928822534e8.md).
Build the fix on top of 79b12c07, which already holds your R4-8 fix, and offer ONE new candidate covering everything below.

Common root of three findings (V4-1, F2, F4): **fixed static reserves** (PAGE_ROOM=30 before research, LINEAGE_ROOM=6 for originals) hold back calls that are affordable and needed. Replace them with need-based decisions. Reserve for an original only when a gathered page actually has a Canonical URL other than its own (R4-2 says to reserve for *needed* originals). Run research whenever its 25u can actually be reserved within both the per-build cap and the batch remainder. Keep the R4-6 latch at reservation time. Correctness first (R1-2, the dispatch): a saving that leaves out affordable evidence is a defect.

## V4-1 (verifier) / F4 (second-reader) — a batch skips affordable research, so a research-only field stays unknown

Units: stage-4 Batches ("When the budget would be exceeded by a further call"), stage-1 §8, R1-2.
- Verifier: unbatched, tarnwick-labs.test costs 44u and founded_year is 1987, reachable only via research. POST /batches {"domains":["tarnwick-labs.test"],"budget_units":49} ends ready at 16u with founded_year unknown. Cause: research._research requires 25+PAGE_ROOM(30)=55. Reproduce: the verifier's run.sh <clone>/stage-4 -k post_seal_batch_budget.
- Second-reader: hidden-cedar.test gets its research-only CEO for 38u unbatched, but a one-domain batch with budget 49 skips research, ends at 10u and leaves CEO unknown.
  Reproduce: SECOND_READER_ONLY=stage4-affordable-research-only-evidence-in-batch SECOND_READER_NO_BROWSER=1 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh <clean-clone>/stage-4

## F2 (second-reader) — the unused lineage reserve blocks affordable evidence

Units S4-002, S2-054, R1-2, R4-2.
15 searched own pages without Canonical originals give only 13 candidates at 74u. The remaining 6u would pay for both missing rendered pages, but the unused LINEAGE_ROOM blocks them.
Reproduce: SECOND_READER_ONLY=stage4-lineage-reserve-keeps-affordable-evidence-complete SECOND_READER_NO_BROWSER=1 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh <clean-clone>/stage-4

## F1 (second-reader) — corroborated_since carries over from the previous selected value

Units S4-038, S4-039, S4-040 ("The standing origins of a selected value are the origins of every candidate with that value that any ready build has gathered since the value became the selected value ... A new selected value starts with none").
Sam Ortiz becomes the selected ceo with two origins on March 8, but corroborated_since stays March 5 from the previous Dana Ruiz stint. Expected: March 8. When the selected value changes, both the standing origins and corroborated_since reset, and the time is computed within the new stint only.
Reproduce: SECOND_READER_ONLY=stage4-scalar-standing-origins-and-selection-reset SECOND_READER_NO_BROWSER=1 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh <clean-clone>/stage-4

## F3 (second-reader) — refused-call refunds not durable across a kill (R4-8)

All 11 attempts were answered 500 and live spending was 0, with no retry before the kill; after the restart the build reports failed with 35 spent. Your 79b12c07 addresses this; keep it, and make sure the probe passes.
Reproduce: SECOND_READER_ONLY=stage4-refused-call-refunds-survive-interrupted-retry-wait SECOND_READER_NO_BROWSER=1 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh <clean-clone>/stage-4

## Non-blocking (product-user) — fix if cheap

1. Top nav links are 27-37 px and primary buttons 43 px; make them at least 44 px.
2. Executives names wrap at desktop width (the name column is narrow), and the title/name baselines differ.
3. Executives and Investors show one "Single source" line per field; show it per member.
