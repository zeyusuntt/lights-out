VERDICT: BLOCK
REVISION: b8e28857cc9398ee5b95985a50fd891b9e984be0

# Independent second-reader audit — Stage 2, round 1

The complete audit has **174 passes and 5 failures**: 169 passing and five failing black-box probes, plus five passing narrow source checks. The five failures form the two completeness findings below. Browser behavior passed at 375 and 1280 CSS pixels, including contested data beyond the first 200 dossiers and real Stage 1 upgrade retries. The inherited 80-unit cap was respected; reaching that cap did not make the missing evidence/candidates correct.

## Revision and reproduction

```sh
fclone b8e28857cc9398ee5b95985a50fd891b9e984be0 /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-b8e28857cc93
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-b8e28857cc93/stage-2
```

The runner takes only the stage folder argument, builds and starts it and its immutable sibling Stage 1 upgrade source, starts the supplied mock with its sample corpus plus authored cases, runs every probe, prints counts, and exits **1** for these failures. It uses an internal network, Nimble alone and 2-vCPU/3-GiB service limits. `fserve` also started this exact revision on port 20080. The clone is clean, and `git diff --exit-code e391dd0b4280ee518d358387614110bebf90c116 HEAD -- stage-1` exits 0: the upgrade source is the accepted Stage 1 tree.

Probes and safe results are private at `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/` until final publication under `acceptance/second-reader/stage-2/`. Provider keys, bearer tokens and export objects are not written to the repository or reports. No product code or product tests were edited. Product tests, supplied check sources, `key.json` and later-stage specifications were not opened. Narrow product-source reading occurred only after probes ran and only for otherwise unobservable provider routing, hashing, conditional provider/null-kind ranking and timing/accounting configuration.

## F1 — Screening static text misses browser-supported and whitespace-normalized candidates

Units: **S2-002, S2-005, S2-016, S2-019, S2-054**, plus the inherited Appendix A and citation-whitespace rules; rulings R1-03/R2-06.

Three reproducible cases:

- `candidates/browser-only-short`: `veilwave.test` has short static prose `Veilwave makes software.` Its loaded browser text is `Veilwave CEO: Dana Ruiz.` The dossier completes ready with no CEO candidate/value. The provider witness shows no extract of `https://veilwave.test/about`.
- `candidates/browser-only-long`: `veilstream.test` has long administrative static text and loaded browser text `Veilstream CEO: Dana Ruiz.` The dossier again has no CEO candidate/value. The witness shows a one-unit plain extract of its page and no three-unit rendered extract.
- `prose/hq-phrase-whitespace`: a page says the company's name followed by `headquartered\tin Zürich.` A supporting excerpt may collapse that whitespace to one space under the inherited citation rules; the Stage 1 probe passed on the accepted revision. Stage 2 reports hq_city unknown.

No clicks are required for these facts. The two browser-only cases spend 80 units on the full test corpus while failing to obtain their own supporting browser text. A snippet/plain-text predicate cannot safely decide that the loaded page has no supported fact. Preserve supported whitespace normalization when screening as well as when extracting.

Reproduce all three with the complete command above. Their failure names are listed verbatim; the two browser-only failures report an empty candidates array instead of the one supported `Dana Ruiz` candidate, and the whitespace failure reports null instead of `Zürich`.

## F2 — Query crowding and budget allocation leave supported pages/values missing

Units: **S2-002, S2-005, S2-054**, R1-03/R2-06.

`candidates/beyond-ten-results` uses independently authored `deepwell.test` evidence on 14 pages, plus another company's field-keyword pages that compete with broad queries. The ready result contains **13 of 14** CEO candidates. It omits `Sam Ortiz` on `https://reports.test/news-c`, whose prose is `Deepwell chief executive officer: Sam Ortiz.` The provider witness shows no extract attempt for that URL. The build spends exactly **80 units**. Its selected `Lina Chen` value happens to remain correct; that does not satisfy the separate requirement to retain every supported page/value candidate.

This is a feasible evidence set within the cap: 14 rendered pages cost 42 units; seven searches plus research cost 32, totaling 74, with room for a further targeted query. The service spends budget on unrelated screening work instead of collecting all target evidence. The fixture does not demand an impossible number of rendered pages.

The same noisy corpus also reproduces `prose/late-support-generic-page`: a searchable generic registry page has a supporting company/CEO sentence beyond its opening snippet, yet the ready field is null. This is an inherited completeness regression under the added query pressure.

Reproduce with the complete command above; failure names are `candidates/beyond-ten-results` and `prose/late-support-generic-page`. Safe `results.json` includes per-company candidate counts, spending and provider method/query/URL/cost/status witnesses. The corpus is constructed by the runner; no secret or separately supplied fixture is needed.

After my initial independent probes ran, I read the verifier's consolidated verdict. Its F1 reports a different query-crowding case with a wrong selected headquarters value. I then authored this additional 14-page fixture and reproduced missing-candidate completeness independently. My original browser-text/whitespace findings were not changed to agree with the other verdict; I do not claim my Deepwell winner was wrong.

## Passing evidence

- Complete ranking/status checks passed: own/filing equality, authority over recency, offset-equivalent publication instants, absent/invalid metadata, normalized host and subdomain fallback, URL ordering, numeric and Unicode value ties, per-page/value deduplication, every selected-value citation in rank order, known versus contested and refresh replacement.
- 429 recovery reached the fourth attempt. Answered refusals cost zero; provider costs match spent_units. Normal, in-flight and cumulative accounting passed. Witnessed workloads reached 80 without crossing it. Live read/connection timeouts are 60 seconds; retry pause is 1.1 seconds after a refusal; live upper bounds remain 285/240 seconds. Optional browser vendors are unused; their conditional costs/session behavior are not claimed as exercised.
- Browser flows passed at 375 and 1280: signup/login/logout, visible confirmed errors, empty/search/list/existing dossier, normalized research, every field/citation/candidate hook, evidence/contested/not-found screens, refresh, reload, automatic polling, latest-read-wins including full navigation, and unknown-outcome retries with identical keys/bodies. A delayed older read did not overwrite the newer state. Zero-dollar values remained present with data-value="0". The contested screen found the target after 201 earlier-sorting dossiers.
- Both create and refresh responses were lost after committing against the real accepted Stage 1 source; its export was imported between requests into Stage 2 while the same browser stayed open. Existing browser tokens/current user, original body/key and saved original response survived without a new login or manual reload, with no import/replay provider call. Migrated kind/publication were null with empty HTML attributes. A failed first post-import refresh preserved candidates, and a later ready refresh replaced null-kind legacy candidates.
- The product-user verdict is PASS on this exact revision, with its journey images under `journey/stage-2/b8e28857cc93/`. R2-11 assigns visual judgement there. My own browser flows reproduced the required screens and narrow/desktop no-overflow observations. Its taste notes are non-blocking.

Test helper corrections before the final run were not product findings: rendered extraction uses three units rather than the old plain-extract fee; `urllib.parse` is not an outbound HTTP client; a contested row may itself be a link and may target an evidence-page fragment; refresh retries must be awaited until their uncertainty elements clear rather than relying on an already-ready old state. No product result was relaxed to match another seat.

## Legacy residual and ledger closure

R2-08/R2-09 explicitly limit legacy reconstruction to excerpts actually carried by the accepted Stage 1 export. Unexported last-ready served text cannot be recovered and remains a **non-blocking residual of accepted Stage 1 revision e391dd0b4280ee518d358387614110bebf90c116** for the final report. The original S2-182 obligation and this residual remain in the ledger; passing the available-evidence migration probe does not assert that the missing text was recovered.

All **153 normative/ambiguous units** have evidence for this revision. The command:

```sh
ledger-check 2 --phase audit --revision b8e28857cc9398ee5b95985a50fd891b9e984be0
```

exits **1** with exactly five failing units: S2-002, S2-005, S2-016, S2-019, S2-054. No unit lacks an evidence entry. The Stage 2 product must not pass with these completeness failures.

The required kit command was run only through its entry point, on this clean clone and a new output directory:

```sh
cd /Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026
env BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/docker-buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-b8e28857cc93 --stage 2 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s2-b8e28857-01
```

It exits **0** and prints `claimed stage: 2 on the shipped checks`. That sample result does not override the independent failures. No later-stage check log was opened. All owned service/probe containers were removed.
