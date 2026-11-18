# Run state

## Stage 1 — ACCEPTED a8789dcd65a18ca385d968116c51d23590913c33 (4 rounds, 3 BLOCK). accepted/stage-1.txt.

## Stage 2
- stage-2/ copy committed by builder fd99d6f (pure copy; seal excludes it).
- Ledger a519e12 (188 units). Seal sha256:7206b9c1ce8df10a3a0bdca0461d42a0e0dea245d0804ae7706a2029e3262ca8 (216, 0 product commits). Rulings R2-1..R2-5.
- Opened to builder + product-user with plan/stage-2-note.md; ledger + rulings sent to verifier.
- Round: 1. BLOCK count: 0.
- Candidate: 3cf3cef0862c212f6f572712876ad700e9e0e381. Foreman check: claimed stage 2 (checks/foreman-s2-r1/report.json)
- SEAL AMENDED 2 sha256:5e65df495d997ee6ef6380094df32116a4f96308ba5ab5bec548f5eff9e48b8c (220, no code seen).
- Outstanding: VERDICT verifier, second-reader, product-user on 3cf3cef0 (VERIFY sent)
- UI: yes -> VERIFY to verifier, second-reader, product-user; accept-check --ui.
- Known stage-1 limitation (final report): stage-1 export keeps only citations; upgrade candidates are limited to exported excerpts (R2-5).
