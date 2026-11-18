VERDICT: PASS
REVISION: a7228733bd425af053de0063ec2a3fc1ef68d873

Round 3, regression walk. Image built from a clean clone and run against the mock web (sample corpus). I repeated the full walk at 1440 and 375 px and built all ten sample companies. Screenshots and scripts are in journey/stage-4/a7228733bd42/. No product source was read.

## Result
- The UI is unchanged from 010b35ad7282. Every screen, flow, test id and state behaves as in my round-2 verdict.
- No horizontal overflow at either width.
- Unbatched build spend is identical to round 2 (all ten sample companies 53-71, brightwater 142 after build plus refresh, none above 80 per build).
- Small links: unchanged. The "Dossier" brand link is 27 px, and the inline login/signup links are 18-27 px ("Sign in" 18, "Create an account" 23). Everything else is at least 44 px. This is a note only.
- Batches have no UI. Not checked: batch ordering (R4-9), restart and upgrade behaviour, which the other seats cover.
