VERDICT: PASS
REVISION: 0dfa3ed6e8bcb58a63c4211d2aeee117e6ca559e

Re-walked the whole journey at 1440 and 375 px against the mock web (sample corpus); screenshots in journey/stage-2/0dfa3ed6e8bc/.

Retested: logout button no longer under 32 px at 375 (no small controls reported on any screen). Building wording and signup redirect as in round 2.
Walked and working: signup/login/logout and their errors, research with invalid domain/URL, normalised and existing domains, building state auto-updating to ready, refresh, reload, search and empty list, evidence, contested, not-found, lost response on research and refresh showing uncertain (not error) and clearing on same-key retry. No horizontal overflow on any screen at either width; focus outline visible. Spend 79 per build on the sample.
Not walked: failed-build state, stage-1 import, out-of-order read races. Candidate completeness (R2-12) is outside what a screen shows and is left to the other seats.

No blocking findings.
