VERDICT: BLOCK
REVISION: b8e28857cc9398ee5b95985a50fd891b9e984be0

# Verifier verdict — stage 2, candidate b8e28857cc93 (round 1)

Seal: SEAL AMENDED 2 sha256:9a42dfbc810411f40d3207d30cc5563fba0fc32f6c819814d85c77dfa6644ddc (133 tests). Code had been seen. After seeing the code I fixed two tests that misread the spec (see "Test amendments").

## Steps

1. Clean clone via `fclone`, built with `docker build --no-cache`. Started as RUN.md says against the mock web; healthy after about 1 s. No finding on RUN.md.
2. Check command, isolated mode, output in `checks/verifier-s2-b8e2-1`: "claimed stage: 2". As the task says, this is a sample only.
3. Sealed suite, `run.sh <clone>/stage-2`, with the accepted stage-1 image as the upgrade source: **126 passed, 6 failed, 1 xfailed**.
   - Two of the six failures were faults in my tests; both now pass on this revision.
   - The remaining four share one root cause, F1.
   - The xfail is R2-09 (served text that a stage-1 export cannot carry), reported as a note.
4. Upgrade path from the real stage-1 image (e391dd0b). Export from it after builds, a refresh and a lost-response key, then import. Passes after the R2-08 test fix:
   - tokens and logins survive;
   - IDs, researched_at and spent_units are preserved;
   - candidates are derived from the exported excerpts, with retrieved_at equal to researched_at;
   - the lost-response key replays with the original body;
   - the next build replaces the candidates;
   - import makes no provider call.
5. Cost: 65 units for vega-motors.test, within 80. See note N2.
6. Code read:
   - every provider call goes through web_router;
   - the UI has no external assets, so everything is served from the image;
   - I found no fixture-keyed answers.

## Finding F1 — supported candidates missing, so the wrong value is selected (BLOCK)

Sentences broken:
- stage 2 Candidates: "Every value that a page of the evidence (§4) supports for a field is a candidate of that field, once for each such page."
- stage 2 point 3: "A field's selected value is the one the selection rule below picks from the field's candidates."
- §4 evidence is "every page that some search … for any query naming the company … returns". Rulings R1-03 and R2-06 say a missing candidate is a defect.

Trigger: vega-motors.test has 14 searchable pages; the corpus also holds another company's pages. The bare-domain search returns 10 of vega's pages. The build's six field-keyword queries ("vega motors headquartered headquarters head office based", and so on) are each answered entirely by another company's pages. Those pages repeat the field words; this is wide-net.test in the verifier corpus.

Pages the build never obtains:
- https://registry.test/vega (filing): "Vega Motors has its registered office in Milan."
- https://news.test/vega: "Vega Motors is based in Rome."
- https://news.test/vega-2: "Vega Motors is headquartered in Naples."

A query naming the company returns them, so they are evidence. The build stopped at 65 of 80 units.

Result:
- hq_city is `known` "Turin", with one candidate. Expected: `contested` "Milan", with candidates Milan, Turin, Rome, Naples (filing 2026 ranks above own 2025).
- /contested then lacks vega-motors hq_city.

Reproduce:
- `bash $FACTORY_WORK/verifier/probes/probe-served.sh <stage-2 image> $FACTORY_WORK/verifier/sealed/stage-2/corpus vega-motors.test` prints each search's returned URLs and the dossier.
- In the suite: `run.sh <stage-2> -k "vega_selection or throttle_every or nimble_only_service or contested_screen"`.

## Notes (non-blocking)

- N1 (R2-09): test_upgrade_candidates_from_all_served_text is xfail. Stage-1 twin-forge was served the Boulder sentence, but the export does not carry it. This is a residual stage-1 defect for the final report.
- N2: spend. Every extract in the vega build was a rendered extract at 3 units, 11 URLs × 3 = 33 units. No page in the mock corpus differs between plain and rendered text, so plain extracts (1 unit) would have saved 22 units. RUN.md and the builder's assumption say pages are rendered only when needed; the call log shows every one rendered.
- N3: a 5xx answer to research or refresh shown as "uncertain": acceptable. The outcome is unknown, and the service itself must never answer 5xx.

## Test amendments (my errors, fixed and re-run on this revision)

- The upgrade test asked for one candidate per stage-1 citation. Northwind's ceo had two citations on one page, and R2-08 asks for one candidate per (page, value). Fixed; passes.
- The polling out-of-order test held one poll until the screen showed ready. That deadlocks a poller that waits for each answer before sending the next. It now holds the poll for a bounded 6 s. Fixed; passes.
