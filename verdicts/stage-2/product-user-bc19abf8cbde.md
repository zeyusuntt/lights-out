VERDICT: PASS
REVISION: bc19abf8cbde23c3a2fa50f23baa55dbfe48d731

Round 2. Image built from a clean clone, run against the mock web (sample corpus). Full walk repeated at 1440 and 375 px; screenshots and scripts are in journey/stage-2/bc19abf8cbde/.

## Retest of round-1 notes
1. Wrong-password login now reads "Email or password is incorrect." (m-04-login-wrong.png): fixed.
2. First build shows "Research in progress" / "Not researched yet" per field (m-24-first-build.png): fixed.
3. Desktop Research button is aligned with its input (d-12-home-list.png): fixed.
4. Tap targets: partly fixed. Citation links on the dossier screen and the primary buttons are now about 43-44 px. Still under 44 px: the top nav (Dossier 27, Dossiers/Contested 33, Sign out 37) and the "Back to <domain>" link on the evidence screen (18 px at 375 px). The claim "at least 44 px" is not fully true. Not blocking.
5. Contested item keeps the field key as secondary text: accepted.
6. The nav is hidden when signed out (m-04-login-wrong.png): fixed.

## Whole walk, regression
- All routes render, with no horizontal overflow at either width. Minimum font 12 px. All required test ids present.
- Research, refresh, building follow-through, uncertain handling and retry, hung request (turns uncertain), out-of-order reads, search and empty state, logout, and the signed-out redirect to /login all behave as in round 1.
- Not checked: the stage-1 export/import upgrade path, which the other seats cover.

## Notes
- Header nav links and the evidence "Back to" link are still small tap targets. Give them at least 44 px of padding.
