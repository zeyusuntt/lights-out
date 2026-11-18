VERDICT: PASS
REVISION: cd24f51fb21b312aac2398adff8813a1b6276b57

Image built from a clean clone and run against the mock web (sample corpus). I walked every route at 1440 and 375 px, then built all ten sample companies to see executives in the one-, two- and three-title cases and in a contested state. Screenshots and scripts are in journey/stage-3/cd24f51fb21b/ (d- = desktop, m- = 375 px). The stage-2 walk was repeated in full as a regression.

## Verified
- No horizontal overflow on any screen at either width, including dossier, evidence and contested with the seventh field. Minimum text size is 12 px.
- All stage-2 test ids are still present and correct, and the six-field `data-*` contract is unchanged.
- The executives row has its own consistent markup: title label, then the person's name, then status, "Holds from … Learned …", and citations beside it (d-30-tidemark.png, m-09-ready.png). Three titles stack cleanly. A contested executives field reads "Contested — sources disagree on CTO" with Compare sources.
- "Holds from 14 Mar 2025. Learned 1 Mar 2026, 09:00 (UTC+00:00)" reads clearly. "Start date not stated. Learned …" is used when true_from is null. The evidence screen gives First learned, Holds from, Retrieved and Published, each people-first plus the exact RFC 3339 string.
- Executives appear on the evidence screen grouped by title, with the selected one marked (m-10-evidence.png, d-31/m-31).
- /contested lists only the six data fields. Executives-only contested dossiers (ostrava, tidemark) don't appear for that reason, which matches the spec. Money is shown people-first plus raw.
- Research, refresh, building follow-through, uncertain / hung request, out-of-order read, search, empty state, logout and the signed-out redirect all behave as in stage 2.
- Not checked in the browser: as_of, values, history, changes and restart behaviour, which have no screens in this stage.

## Notes (not blocking)
1. Excerpts that already begin with a straight quote render as a doubled opening mark (`“"Our customers asked…`, d-30-tidemark.png, ceo). Trim or restyle the wrapper when the excerpt already starts with a quote.
2. On the executives row at desktop, the small title label and the large name sit on different baselines. Stacking the title above the name, as on mobile, would look tidier.
3. Tap targets: the top nav links (27-37 px), the evidence "Back to" link and the citation links (42 px) are still under 44 px. This is unchanged from stage 2.
4. The contested list still shows the raw field key (`field headcount_range`) as muted text. This was accepted in stage 2.
