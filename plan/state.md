# Run state

## Stage 1 — ACCEPTED a8789dcd65a18ca385d968116c51d23590913c33 (4 rounds, 3 BLOCK). accepted/stage-1.txt.
## Stage 2 — ACCEPTED bc19abf8cbde23c3a2fa50f23baa55dbfe48d731 (2 rounds, 1 BLOCK). accepted/stage-2.txt.
## Stage 3 — ACCEPTED cd24f51fb21b312aac2398adff8813a1b6276b57 (1 round, 0 BLOCK). accepted/stage-3.txt.

## Stage 4 (last)
- stage-4/ copy committed by builder 1949353 (pure copy).
- Ledger bbd3904 (125 units). Rulings R4-0..R4-7. Opened to builder + product-user with plan/stage-4-note.md; rulings sent to verifier + second-reader.
- Round: 3. BLOCK count: 2. Candidate: b928822534e8f8b9b7ce8dbf555bfbda1a42deab. Foreman check: claimed stage 4 (checks/foreman-s4-r1/report.json).
- SEALED 4 sha256:9363e05a0c20b9f7879889ef7e30f65e28b58befd8e7b6ea2cd86d5b700410c2 (296, 0 product commits). Readings D1-D7.
- SEAL AMENDED 4 sha256:d996aff2c3bd07ce52ea3b9d2c65a5d1a85bc9ba64db4a5db679645f7775747e (300, no code seen).
- product-user PASS on b9288225 (fa0052f); notes: nav <44px, exec name wrap/baseline, per-field single-source line.
- verifier BLOCK on b9288225 (5be490c): V4-1 batch research gated on 25+30 page room, skipped though affordable (tarnwick, budget 49 -> founded_year unknown). SEAL AMENDED sha256:438bf8f9fcdc2e8cdc1558abcb243c180dc31e4db48e5acbfbd956482d1506ec.
- Builder committed 79b12c07 early (R4-8 fix only, not verified). Told to wait for FIX 4 1.
- second-reader BLOCK on b9288225 (fb02ed7): F1 corroborated_since stint reset, F2 lineage reserve, F3 R4-8 refunds, F4 = V4-1. FIX 4 1 sent (plan/fix-4-1.md).
- Round 2 candidate: 010b35ad7282e9b4018daee982a1846a5af8301e. Foreman check: claimed stage 4 (checks/foreman-s4-r2/report.json).
- product-user PASS on 010b35ad (6a1804b); residual: brand link 27px, login/signup inline links <44px.
- second-reader BLOCK on 010b35ad (bfdb26b): S4-F5 under R4-9 (budget-30 research displaces page evidence). R4-8, R4-9 issued.
- Builder committed a7228733 early (R4-9 fix), held pending verifier verdict on 010b35ad.
- verifier BLOCK on 010b35ad (6006491): V4-2 (same root as S4-F5). SEAL AMENDED sha256:b53596ffbf945ef6dbbaa522437702a7e0c348b3a176d835540a7d599adc2828. FIX 4 2 (plan/fix-4-2.md).
- Round 3 candidate: a7228733bd425af053de0063ec2a3fc1ef68d873. Foreman check: claimed stage 4 (checks/foreman-s4-r3/report.json).
- Outstanding: VERDICT verifier, second-reader, product-user on a7228733 (VERIFY sent)
- UI: yes -> accept-check --ui.
- Watch: stage-4 Restarts supersedes R3-4 rollback-without-spend: billed units must be counted durably, and running builds end ready/failed within 10 s after health. The stage-3 export does keep builds (schema 3), so the 3->4 upgrade should be exact.
- Known limitations for final report: stage-1 export citations only (R2-5); stage-2 export lacks build history and Effective (R3-3).
