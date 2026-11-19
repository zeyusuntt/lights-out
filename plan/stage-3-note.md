Stage 3 handoff note (foreman).

- Ledger: /Users/[REDACTED]/dev/band-factory/work/result/ledger/stage-3.jsonl (+ stage-3.md, stage-3-dangers.md), at 6777747b1a684cca8890d7ed968da7e3a89a60dc.
- Rulings: /Users/[REDACTED]/dev/band-factory/work/result/rulings/stage-3.md, R3-1..R3-4. Stage-1 and stage-2 rulings still apply.
  - R3-1: as_of spent_units includes the in-flight spending of qualifying builds.
  - R3-2: a null-valued history entry's learned_at is the time of the build that made the transition.
  - R3-3: a stage-2 export imports as one ready build at researched_at, holding all exported spending. It gathered one version per candidate URL, with true_from = the UTC date of that page's published_at, or null. Candidates' learned_at = retrieved_at. History has one initial entry per valued field, with true_from = the selected candidate's true_from. The feed is empty and executives is unknown. A stage-3 export must keep every build, every version (including candidate-free ones), history, feed and seq, so that stage-3 -> stage-3 is exact.
  - R3-4: a build interrupted by a kill rolls back to the pre-build snapshot. Nothing partial is exposed, and the dossier is not stuck in building. Writes are crash-atomic (temp file + fsync + rename, or a transactional store such as SQLite in WAL mode), and state lives on the container filesystem.
- Page versions follow the spec literally: a gathered page with no candidates still replaces or ends earlier versions of its URL (stage-3 /values). A page that is no longer served is not gathered, and its old version keeps holding.
- Executives: there are no data-testids for executives, but show them on the dossier screen with consistent markup, because product quality is judged. A research run still asks for the six fields only. Executives come only from page text, never from research claims.
- Budget: the 80-unit cap and the cost-per-correct-field judgement still apply. Stage 2 ran at about 11.3 u per correct field; keep it at or below that while covering the three titles.
- Builder: stage-3/ already holds the copy (d9b8e90). Build there and send CANDIDATE 3 <full hash>.
- Product-user: the stage-2 screens persist, now with a seventh field. You will get VERIFY 3. Walk all routes at 375 px and at desktop width again, including how executives, true_from and learned_at read for people.
