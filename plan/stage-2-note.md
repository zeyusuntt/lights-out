Stage 2 handoff note (foreman).

- Ledger: /Users/sunzeyu/dev/band-factory/work/result/ledger/stage-2.jsonl (readable: stage-2.md; danger sequences: stage-2-dangers.md), at a519e123341479a80d07696c91c075f76ed40257.
- Rulings: /Users/sunzeyu/dev/band-factory/work/result/rulings/stage-2.md, R2-1..R2-5. Stage-1 rulings R1-1..R1-7 still apply. Key points:
  - R2-2: browser routes, and /dossiers/{domain} with Accept containing text/html, are served as HTML without a bearer header. JSON behaviour without text/html is unchanged.
  - R2-3: dossier-researched-at shows a people-first format in the timestamp's own offset, plus the exact RFC 3339 string.
  - R2-4: the browser session is only its bearer token.
  - R2-5: the stage-1 export holds only citations, so upgrade candidates come from the exported citation excerpts, each tested against every field, with kind null and published_at null.
- Page text is browser text (stage-2 "Page text"). Evidence and citations must come from what a browser shows once the page has loaded, not from static text that the browser does not show. Nimble rendered extract (render: True, 3u per URL) is enough. Budget, completeness (R1-2) and the 80-unit cap still bind.
- Rate limits: wait at least 1 s after a 429 before the same call (R2-1).
- Builder: stage-2/ already holds the copy (fd99d6f). Build stage 2 there, commit with fcommit, and send CANDIDATE 2 <full hash>. Ports 18000-18999.
- Product-user: stage 2 has a human interface. You will get VERIFY 2 with the candidate hash. Walk every required route and flow at 375 px and at desktop width, against the product and visual direction in the specification. Commit journey/stage-2/ and verdicts/stage-2/product-user-<hash12>.md. Until VERIFY, you may prepare your walk plan from the specification; there is no code to see yet.
