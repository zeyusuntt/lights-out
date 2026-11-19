VERDICT: PASS
REVISION: 00c0c224d637ab25653e709f869ac209ac747c3e

Re-walked the whole journey at 1440 and 375 px against the mock web (sample corpus); screenshots in journey/stage-2/00c0c224d637/.

Walked and working: signup/login/logout and their errors, research with invalid domain/URL, normalised and existing domains, building state auto-updating to ready, refresh, reload, search and empty list, evidence, contested, not-found, lost response on research and refresh showing uncertain (not error) and clearing on same-key retry. No horizontal overflow at either width; no control under 32 px; focus outline visible. Each build spends 80 units on the sample (spent 160 after one refresh); spend efficiency is not visible on a screen and is left to the foreman.
Not walked: failed-build state, stage-1 import, out-of-order read races, candidate completeness.

No blocking findings.
