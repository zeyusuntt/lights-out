VERDICT: PASS
REVISION: b928822534e8f8b9b7ce8dbf555bfbda1a42deab

Image built from a clean clone and run against the mock web (sample corpus). I walked every route at 1440 and 375 px, built all ten sample companies, and repeated the stage-2/3 walk in full as a regression. Screenshots and scripts are in journey/stage-4/b928822534e8/ (d- = desktop, m- = 375 px). No product source was read.

## Verified
- No horizontal overflow on any screen at either width, including the dossier with eight fields, evidence and contested. Minimum text size is 12 px.
- All stage-2 test ids are still present, and the data-* contract is unchanged. Research, refresh, uncertain and hung requests, out-of-order reads, search, empty state, logout and the signed-out redirect behave as before.
- Sources and corroboration read well for people: "Single source: tidemark-energy.test", or "Corroborated by 2 independent sources: pressline.test, tidemark-energy.test, since 1 Mar 2026, 09:00 (UTC+00:00)". Three syndicated copies of one article show as one origin (pressline.test) on the evidence screen, each with an "Origin" line (d-31-tidemark-evidence.png).
- Investors has its own row after Executives: names, "Known — 1 investor", holds from/learned, source line and citations (d-30-tidemark.png, m-30-tidemark.png). The evidence screen explains membership ("A name counts as an investor when a company site or filing states it, or two independent sources do"), and members are marked "Investor".
- /contested still lists only the six data fields.
- Polish: the doubled opening quote mark is gone (m-30, d-30). Citation links are now at least 44 px tall.
- Batches have no UI in this build, so there was nothing to walk.
- Not checked: the batch, restart and upgrade behaviour, which the other seats cover.

## Notes (not blocking)
1. The top nav links are still under 44 px at both widths (Dossier 27, Dossiers/Contested 33, Sign out 37), and the primary buttons are 43 px. This was carried over from stages 2-3. Pad the nav links.
2. Executives row at desktop: the name column is narrow, so "Mirela Beaumont" and "Rowan Kerrigan" wrap onto two lines. Titles and names also still sit on different baselines (d-30-tidemark.png). Give the name column more width, or stack title over name as on mobile.
3. The Executives and Investors rows show a single "Single source" line for the whole field. A per-member origin would be more informative when members differ.
4. The contested list still shows the raw field key as muted text (accepted earlier).
