Stage 1 handoff note (foreman).

- Sentence ledger: /Users/[REDACTED]/dev/band-factory/work/result/ledger/stage-1.jsonl (readable: ledger/stage-1.md; danger sequences: ledger/stage-1-dangers.md), committed at 976ad55b8fc5504eb2071ec26279aa305d76fd36.
- Rulings: /Users/[REDACTED]/dev/band-factory/work/result/rulings/stage-1.md, R1-1..R1-5. They are binding: R1-2 means every field the evidence supports must come out known, and no saving that loses evidence is acceptable. R1-3 means exactly one successful exact-domain search per ready build.
- Builder: deliver stage-1/ as a complete service (Dockerfile, RUN.md, manifest listing webrouter>=0.12.0, your own tests), commit it with fcommit, and send CANDIDATE 1 <full hash>. Develop against the mock web per vendor/.../dossier/web/README.md with its sample corpus. key.json and the kit's test/ folders are closed. Ports 18000-18999.
- Product-user: stage 1 requires only the HTTP API (§1 "Only the HTTP API is required"). There is no human interface to walk in this stage, so no VERIFY will come to you for stage 1 unless the build ships a UI. Nothing is owed until then.
