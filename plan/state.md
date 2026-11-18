# Run state

## Stage 1 — ACCEPTED a8789dcd65a18ca385d968116c51d23590913c33 (4 rounds, 3 BLOCK). accepted/stage-1.txt.
## Stage 2 — ACCEPTED bc19abf8cbde23c3a2fa50f23baa55dbfe48d731 (2 rounds, 1 BLOCK). accepted/stage-2.txt.

## Stage 3
- stage-3/ placed by stage-copy from bc19abf8, uncommitted; builder commits it unchanged (a pure copy, so the seal excludes it).
- Opened to second-reader + verifier.
- Round: 0. BLOCK count: 0. Candidate: none.
- Outstanding: LEDGER READY 3 (second-reader), SEALED 3 (verifier)
- UI: yes (stage-2 screens persist) -> accept-check --ui.
- Watch: the stage-2 export keeps only the current dossier view (last-ready candidates with kind/published_at), with no build history, Effective lines or per-build spending. The stage-3 "Upgrades" sentences about stage-2 builds will need a ruling (a stage-2 limitation).
- Known stage-1 limitation (final report): stage-1 export keeps only citations (R2-5).
