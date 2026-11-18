# Run state

## Stage 1 — ACCEPTED a8789dcd65a18ca385d968116c51d23590913c33 (4 rounds, 3 BLOCK). accepted/stage-1.txt.
## Stage 2 — ACCEPTED bc19abf8cbde23c3a2fa50f23baa55dbfe48d731 (2 rounds, 1 BLOCK). accepted/stage-2.txt.
## Stage 3 — ACCEPTED cd24f51fb21b312aac2398adff8813a1b6276b57 (1 round, 0 BLOCK). accepted/stage-3.txt.

## Stage 4 (last)
- stage-4/ placed by stage-copy from cd24f51f, uncommitted; builder commits it unchanged.
- Opened to second-reader + verifier.
- Round: 0. BLOCK count: 0. Candidate: none.
- Outstanding: LEDGER READY 4 (second-reader), SEALED 4 (verifier)
- UI: yes -> accept-check --ui.
- Watch: stage-4 Restarts supersedes R3-4 rollback-without-spend: billed units must be counted durably, and running builds end ready/failed within 10 s after health. The stage-3 export does keep builds (schema 3), so the 3->4 upgrade should be exact.
- Known limitations for final report: stage-1 export citations only (R2-5); stage-2 export lacks build history and Effective (R3-3).
