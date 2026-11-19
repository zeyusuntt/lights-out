VERDICT: PASS
REVISION: 770529f8f7995579f2c655b66a7107b19b7ac240

Re-walked the whole journey at 1440 and 375 px against the mock web (sample corpus); screenshots in journey/stage-2/770529f8f799/.

Walked and working: signup/login/logout and their errors, research with invalid domain/URL, normalised and existing domains, building state auto-updating to ready, refresh, reload, search and empty list, evidence, contested, not-found, lost response on research and refresh showing uncertain (not error) and clearing on same-key retry. No horizontal overflow at either width; no control under 32 px; focus outline visible.
Not walked: failed-build state, stage-1 import, out-of-order read races. Candidate completeness (R2-12/R2-13) is not visible on a screen and is left to the other seats.

Note on spend (as asked): the UI shows every build ending at exactly 80 units (spent 80 after research, 160 after one refresh) on sample companies. A screen cannot tell whether the last reads were useful; spending the full cap on every build, including for companies whose fields were all known early, looks avoidable and is for the foreman to weigh against the event rule.

No blocking findings.
