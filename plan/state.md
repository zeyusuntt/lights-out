# Run state

## Stage 1 — ACCEPTED a8789dcd65a18ca385d968116c51d23590913c33 (4 rounds, 3 BLOCK). accepted/stage-1.txt.

## Stage 2
- Opened to second-reader + verifier.
- stage-2/ created in the working tree by stage-copy from a8789dcd. It is uncommitted: the builder owns it and must commit it on its own as the first stage-2 commit.
- Round: 0
- Candidate: none
- Outstanding: LEDGER READY 2 (second-reader), SEALED 2 (verifier)
- UI: yes (screens) -> accept-check --ui, product-user verifies.
- Watch: the upgrade import needs the served text of the last stage-1 ready build. Check whether the stage-1 export holds it; if not, record it as a stage-1 limitation.
