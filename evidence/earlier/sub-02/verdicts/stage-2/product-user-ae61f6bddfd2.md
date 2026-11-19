VERDICT: PASS
REVISION: ae61f6bddfd23c08039c3b2ef17a91acf19f9270

fserve of the exact hash against the local mock web (sample corpus); Playwright chromium at 1440 and 375 px. Screenshots/scripts: journey/stage-2/ae61f6bddfd2/. Full journey re-run from scratch.

## Retests (UI-visible)
- Hung research and refresh requests: `research-uncertain` / `refresh-uncertain` appear at ~10 s (absent at 4 s), no error element; retry sends the same Idempotency-Key and recovers (dossier opens / state ready, uncertainty cleared), both widths.
- Signed-out header has no stray `null`.
- Build outcome on the sample unchanged in the UI: halvorsen-robotics.test ready, 63 units, all six fields as before (legal_name AS known, hq_city contested Valencia/Utrecht, ceo, founded 2019, headcount 1,001 to 5,000, funding $75,000,000). SR2-4/F1/SR2-1 are evidence/cost matters for the verifier; the UI shows no regression.

## Whole walk
No horizontal overflow at either width on any screen; signup/login/logout/errors; `/` empty/search-empty/invalid-domain refused; building auto-updates to ready; known/unknown/contested distinct; evidence and contested screens; failed state keeps old fields with banner; slow build followed to its end; lost-response uncertain flow with same-key retry; stale out-of-order read does not overwrite a later one; export/import keeps the browser signed in; nothing loaded outside the service origin; focus ring visible.

## Notes (do not block)
Doubled opening quote when an excerpt itself starts with a quote mark; slight selected/non-selected row misalignment on Evidence; no-company domain shows `ready` with "Legal name not found". Not exercised: 429 from the UI, upgrade from a real stage-1 export.
