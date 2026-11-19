VERDICT: BLOCK
REVISION: b1d974f410eae3d2f9c1b1053cfca3bc82cc5e1e

Served with fserve for the exact hash; providers = local mock web (sample corpus) on the same docker network. Browser: Playwright chromium at 1440 and 375 px. Screenshots and scripts: journey/stage-2/b1d974f410ea/ (scripts/walk1-4.py).

## Findings (block)

1. **Research request that never gets an answer: stuck forever, no way forward.** Screen `/`, state "request sent, no response ever arrives". Reach: sign in, intercept `POST /dossiers` so it never answers (`walk4.py`), enter `corvid-security.test`, press Research. After 40 s the button still reads "Sending" and is disabled; neither `research-uncertain` nor `research-error` appears, and the user cannot retry or do anything else on the form. Screenshot: `d-32-hang-40s.png` (also `d-30-hang-1.5s.png`, `d-31-hang-10s.png`). Spec: "Provide considered ... error states", lost response -> `research-uncertain` and keep request retryable with the same key and body; mandate: a response that never arrives must leave the user a way forward. Fix idea: client-side timeout (~5-8 s, matching the 5 s per-request limit) that aborts the fetch and shows `research-uncertain` with the same key/body retry. The same likely applies to refresh (not separately exercised for a hang).

2. **Stray literal text `null` in the header on every signed-out screen.** Screens `/`, `/login`, `/signup` (and any page while signed out), both widths. The nav DOM is `<a class="brand">Dossier.</a>null<div class="who">…`; it renders as the word "null" between the brand and the Sign in link. Screenshot: `d-01-home-anon.png`, `m-01-home-anon.png`. Broken/unfinished text on screen; one-line fix.

## Passed (walked at 1440 and 375, no horizontal overflow anywhere: scrollWidth == innerWidth on every screen)
- Signup (validation error shown in `auth-error`), login (wrong password error), logout, `current-user` on every signed-in screen.
- `/` empty state, invalid-domain `research-error` (422 -> refused), search with no match -> `empty-dossiers`, research opens `/dossiers/{normalised domain}`; existing domain opens existing dossier.
- Dossier screen: building banner + auto-update to ready without reload, known / unknown / contested visually distinct (colour bar, badge, text; not colour alone), citations quoted with links, evidence link, reload, refresh, failed state (all providers faulted: banner "latest research failed", old fields kept, state `failed`), not-found state, slow build (8 s provider delay) keeps `building` and following to the end.
- Out-of-order reads: a delayed stale read (faked `failed`/spent 1) arriving after a later read did not overwrite it.
- Uncertain: response dropped after commit -> `research-uncertain` / `refresh-uncertain` with text, no error element; retry with same key shows dossier, clears both; fresh domain case produced 1 build and exactly 1 exact-domain search (mock log). 503 response also shown as uncertain (builder's stated assumption).
- Evidence and contested screens: all fields, selected first, kind/date/provider readable, readable at 375.
- Export/import while signed in: browser stayed signed in and the next research action worked.
- Browser loaded nothing from outside the service origin. Focus ring visible (3 px). Only small target: brand link 27 px tall.

## Notes (do not block)
- Excerpts that themselves begin with a quote mark render as `““Our customers asked…”` (doubled opening quote), e.g. ashgrove-solar CEO citation (`m-22-failed.png`).
- On the evidence screen, non-selected candidate rows are indented slightly differently from the selected row (selected row has a left bar and inset); alignment of value column shifts by ~10 px.
- A dossier for a domain with no company in the web is shown as `ready`, "Legal name not found" in the list: acceptable per spec, but a one-line "nothing found" hint on its screen would help.
- Not exercised: 429 behaviour from the UI side, upgrade from a real stage-1 export with candidates, refresh hang.
