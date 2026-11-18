VERDICT: PASS
REVISION: 010b35ad7282e9b4018daee982a1846a5af8301e

Round 2. Image built from a clean clone and run against the mock web (sample corpus). I repeated the full walk at 1440 and 375 px and built all ten sample companies. Screenshots and scripts are in journey/stage-4/010b35ad7282/. No product source was read.

## Retest of round-1 notes
1. Nav, buttons and inputs: fixed except for the brand link. Nav links, Sign out, Refresh/Reload/All evidence, citation links and the home and dossier inputs are all at least 44 px. Still under 44 px: the "Dossier" brand link (27 px), and the inline links on /login and /signup ("Create an account" 23 px, "Sign in" 18 px, the Create account header link). These are minor.
2. Executives: the title now sits above the name, with no wrapping at desktop (d-30-tidemark.png): fixed.
3. Executives, investors and legal-name rows now show per-member "Single source: <domain>" lines (d-30-tidemark.png): fixed.
4. The contested list keeps the muted raw field key (accepted earlier).

## Regression
- No horizontal overflow at either width. All stage-2 test ids are present.
- Research, refresh, uncertain and hung requests, out-of-order reads, search and empty states, logout and the signed-out redirect all behave as before.
- Spending read idle after a build matches what the earlier revision showed for the same corpus (for example halvorsen 65, tidemark 71, brightwater 142 after build plus refresh). I saw no drift between a completed read and live spending, and no build above 80.
- Investors, sources/corroboration and syndicated-copy origins still read well. /contested still lists only the six data fields.
- Batches have no UI. Not checked: batch, restart and upgrade behaviour.

## Notes (not blocking)
- Pad the brand link and the inline auth links to 44 px.
