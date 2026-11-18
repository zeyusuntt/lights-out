Stage 4 handoff note (foreman). This is the last stage.

- Ledger: /Users/sunzeyu/dev/band-factory/work/result/ledger/stage-4.jsonl (+ stage-4.md, stage-4-dangers.md with 36 sequences), at bbd39040608627394ff3b60e24d958e7cd9a6214.
- Rulings: /Users/sunzeyu/dev/band-factory/work/result/rulings/stage-4.md, R4-0..R4-7. All earlier rulings still apply, except R3-4, which R4-0 supersedes.
  - R4-0: a build running at a kill must end ready or failed within 10 s of the first healthy /health. Every billed unit counts in dossier and batch spent_units, so reserve units and record them durably before each call.
  - R4-1: a Canonical original fetched for lineage gives no candidates unless it is itself evidence.
  - R4-2: reserve original fetches first. If the budget still forbids one, the origin is the host of the unfetched URL.
  - R4-3: origins, corroborated and corroborated_since are required on dossier fields (with and without as_of), and not required on /values.
  - R4-4: corroborated_since is the first build after which every then-current member had at least 2 standing origins; it never backdates.
  - R4-5: budget_units must be a JSON integer literal; 1.0, 1e0, 1.5, true and "1" are 422.
  - R4-6: the first unaffordable call latches the whole batch, so order high-value calls first and reserve atomically.
  - R4-7: native exports hold batches; running builds are settled per R1-4; imported batches are done.
- Own pages require registrant = the company domain, including the stage-2 no-Kind fallback (verifier D3).
- Provider failure: a 5xx or 429 costs nothing. Keep researching through other calls and providers. Tavily stays optional; Nimble alone must suffice.
- Budget: the 80-unit cap per build, the batch budget, and cost per correct field are judged. Stage 3 ran at 11.8 u per correct field, with the heaviest build at 70/80. Investors and lineage fetches must fit, so plan carefully.
- Builder: stage-4/ already holds the copy (1949353). Build there and send CANDIDATE 4 <full hash>.
- Product-user: screens persist, with an eighth field (investors) and origin/corroboration display. You will get VERIFY 4. Walk all routes at 375 px and desktop again, including how sources, corroboration, investors and batches (if the UI exposes them) read. The UI polish notes from stages 2-3 are still open (tap targets under 44 px, doubled quote mark, executives row baseline), and the builder should fix them here.
