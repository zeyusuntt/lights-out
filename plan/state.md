# Run state

## Stage 1 — ACCEPTED a8789dcd65a18ca385d968116c51d23590913c33 (4 rounds, 3 BLOCK). accepted/stage-1.txt.

## Stage 2
- Opened to second-reader + verifier.
- stage-2/ committed by builder as fd99d6f400ecbfe58166ebd42af066f560db793a: pure copy of a8789dcd, before seal. seal excludes pure-copy commits from product_commits, so ordering is valid.
- Round: 0
- Candidate: none
- Ledger READY 2 a519e12. Rulings R2-1..R2-5 committed.
- Outstanding: SEALED 2 (verifier)
- UI: yes (screens) -> accept-check --ui, product-user verifies.
- Watch: the upgrade import needs the served text of the last stage-1 ready build. Check whether the stage-1 export holds it; if not, record it as a stage-1 limitation.
