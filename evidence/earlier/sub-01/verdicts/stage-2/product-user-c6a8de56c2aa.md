VERDICT: PASS
REVISION: c6a8de56c2aac958122e5d30806f7dbf6858dd09

Re-walked the whole journey at 1440 and 375 px against the mock web (sample corpus); screenshots in journey/stage-2/c6a8de56c2aa/.

Round-1 notes retested:
1. Unknown-while-building wording: now "Not found yet: research is still running." (m-20-building.png). Fixed.
2. Post-signup URL: the URL becomes / about 1 s after submit (polled every 0.5 s: /signup at 0.5 s, / from 1.0 s). It never stays on /signup; brief lag only. No finding.
3. Mobile header: now two rows (brand+nav, user+logout), clearly shorter. Fixed. Logout button is 30 px high at 375 (all other controls >=32): note only.

Whole journey re-walked, all working as in round 1: signup/login/logout and their errors, research with invalid domain/URL, normalised domain, existing domain (no new build), building state auto-updating to ready, refresh, reload, search and empty list, evidence, contested, not-found, lost response on research and refresh showing uncertain (not error) and clearing on same-key retry. No horizontal overflow on any screen at either width; focus outline visible.
Observed spend per build 74-80 units on the sample (spent doubles on refresh), within the 80 cap; spend-efficiency is not a screen matter and is left to the foreman.
Not walked: failed-build state, stage-1 import, out-of-order read races.

No blocking findings.
