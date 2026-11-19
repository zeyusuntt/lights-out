VERDICT: PASS
REVISION: 166ae1aa16e33c2b6cb0684d305aafb21bbaf41a

fserve of the exact hash against the local mock web (sample corpus); Playwright chromium at 1440 and 375 px. Screenshots/scripts: journey/stage-2/166ae1aa16e3/.

## Retest of round-1 findings
1. Hung write: research and refresh requests that never answer now show `research-uncertain` / `refresh-uncertain` after ~10 s (none at 4 s, present at 12 s, no error element), at both widths. Retry sends the same Idempotency-Key, opens the dossier / returns to `ready`, removes the uncertainty (hang-research / hang-refresh screenshots in `c/`). FIXED.
2. Signed-out header: no stray `null`; header reads "Dossier. | Sign in | Create account" at both widths. FIXED.

## Whole walk (unchanged areas re-run)
No horizontal overflow on any screen at either width. Signup/login/logout and errors; `/` empty, invalid-domain `research-error`, search-empty; building -> ready auto-update; known/unknown/contested distinct; evidence and contested screens; failed state keeps old fields with a banner; slow build follows to the end; lost-response uncertain flow with same-key retry; stale out-of-order read does not overwrite a later one; export/import keeps the browser signed in and the next action works; nothing loaded from outside the service origin; focus ring visible.

## Notes (do not block, unchanged from round 1)
Doubled opening quote when an excerpt itself starts with a quote mark; slight misalignment between selected and non-selected candidate rows on Evidence; domain with no company shows `ready` with only "Legal name not found". Not exercised: 429 from the UI, upgrade from a real stage-1 export.
