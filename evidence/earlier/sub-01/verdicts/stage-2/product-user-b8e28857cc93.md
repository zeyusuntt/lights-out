VERDICT: PASS
REVISION: b8e28857cc9398ee5b95985a50fd891b9e984be0

Walked at 1440 and 375 px against the mock web (sample corpus), screenshots in journey/stage-2/b8e28857cc93/ (d-* desktop, m-* mobile).

Walked and working: signup (empty, bad email, short password errors shown in auth-error), logout, login (bad password error, success), home empty state, research with invalid domain / URL (research-error), research of a mixed-case www. domain with trailing dot (opens normalised dossier), building state with banner and automatic update to ready without reload, refresh (building then ready, spent units grows), reload, existing domain opens that dossier without new build, search filter + empty-dossiers, evidence page (six fields, selected marked, kind/date readable), contested page, dossier-not-found, lost response on research and on refresh shows the uncertain banner (not an error) and a retry with same key clears it and opens the dossier.
Measured: no horizontal overflow on any screen at 1440 or 375; no interactive control under 32 px high; visible 3px focus outline; status badges distinct (known green, contested amber double border, unknown dashed grey, building blue dot).
Not walked: failed-build state, stage-1 export import, out-of-order read races (no way to force them through the UI here).

No blocking findings.

Notes (taste, not blocking):
1. While a first build is running, the unknown fields read "No source the service read supports a value for this field." (m-20-building.png); better "Not found yet" during building.
2. After signup the URL stays /signup although the home content is shown (d-05-after-signup.png); push / to the history for back-button sanity.
3. Mobile header stacks brand, nav and user over three rows, using about 150 px before content; could be compacted.
