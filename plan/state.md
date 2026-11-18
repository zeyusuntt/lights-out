# Run state

## Stage 1 — ACCEPTED a8789dcd65a18ca385d968116c51d23590913c33 (4 rounds, 3 BLOCK). accepted/stage-1.txt.

## Stage 2
- stage-2/ copy committed by builder fd99d6f (pure copy; seal excludes it).
- Ledger a519e12 (188 units). Seal sha256:7206b9c1ce8df10a3a0bdca0461d42a0e0dea245d0804ae7706a2029e3262ca8 (216, 0 product commits). Rulings R2-1..R2-5.
- Opened to builder + product-user with plan/stage-2-note.md; ledger + rulings sent to verifier.
- Round: 1. BLOCK count: 1.
- Candidate: 3cf3cef0862c212f6f572712876ad700e9e0e381. Foreman check: claimed stage 2 (checks/foreman-s2-r1/report.json)
- SEAL AMENDED 2 sha256:5e65df495d997ee6ef6380094df32116a4f96308ba5ab5bec548f5eff9e48b8c (220, no code seen).
- product-user PASS on 3cf3cef0 (b080afd), 6 non-blocking UI notes.
- verifier PASS on 3cf3cef0 (02e2f67), 222/222, 92/92 fields, 11.3 u/field. SEAL AMENDED sha256:a2d3420bb708d27b82630c18e8d3568c27b8782a408ef1c7a1482559a0bb22df. Notes: RUN.md tags image dossier-stage-1; 8 searches per build; UI timeout 10s.
- second-reader BLOCK on 3cf3cef0 (4197e89): S2-F1 throttled extract after slow research not retried. FIX 2 1 sent (plan/fix-2-1.md), with 7 polish notes.
- Round 2 candidate: bc19abf8cbde23c3a2fa50f23baa55dbfe48d731. Foreman check: claimed stage 2 (checks/foreman-s2-r2/report.json).
- product-user PASS on bc19abf8 (478ec11); residual note: nav links 27-37px, evidence back link 18px at 375.
- Outstanding: VERDICT verifier, second-reader on bc19abf8
- UI: yes -> VERIFY to verifier, second-reader, product-user; accept-check --ui.
- Known stage-1 limitation (final report): stage-1 export keeps only citations; upgrade candidates are limited to exported excerpts (R2-5).
