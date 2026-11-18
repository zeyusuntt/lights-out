# Run state

## Stage 1 — ACCEPTED a8789dcd65a18ca385d968116c51d23590913c33 (4 rounds, 3 BLOCK). accepted/stage-1.txt.
## Stage 2 — ACCEPTED bc19abf8cbde23c3a2fa50f23baa55dbfe48d731 (2 rounds, 1 BLOCK). accepted/stage-2.txt.
## Stage 3 — ACCEPTED cd24f51fb21b312aac2398adff8813a1b6276b57 (1 round, 0 BLOCK). accepted/stage-3.txt.

## Stage 4 (last)
- stage-4/ copy committed by builder 1949353 (pure copy).
- Ledger bbd3904 (125 units). Rulings R4-0..R4-7. Opened to builder + product-user with plan/stage-4-note.md; rulings sent to verifier + second-reader.
- Round: 1. BLOCK count: 0. Candidate: b928822534e8f8b9b7ce8dbf555bfbda1a42deab. Foreman check: claimed stage 4 (checks/foreman-s4-r1/report.json).
- SEALED 4 sha256:9363e05a0c20b9f7879889ef7e30f65e28b58befd8e7b6ea2cd86d5b700410c2 (296, 0 product commits). Readings D1-D7.
- SEAL AMENDED 4 sha256:d996aff2c3bd07ce52ea3b9d2c65a5d1a85bc9ba64db4a5db679645f7775747e (300, no code seen).
- product-user PASS on b9288225 (fa0052f); notes: nav <44px, exec name wrap/baseline, per-field single-source line.
- Outstanding: VERDICT verifier, second-reader on b9288225
- UI: yes -> accept-check --ui.
- Watch: stage-4 Restarts supersedes R3-4 rollback-without-spend: billed units must be counted durably, and running builds end ready/failed within 10 s after health. The stage-3 export does keep builds (schema 3), so the 3->4 upgrade should be exact.
- Known limitations for final report: stage-1 export citations only (R2-5); stage-2 export lacks build history and Effective (R3-3).
