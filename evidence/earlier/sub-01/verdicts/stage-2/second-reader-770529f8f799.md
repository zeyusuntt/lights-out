VERDICT: BLOCK
REVISION: 770529f8f7995579f2c655b66a7107b19b7ac240

# Independent second-reader audit — Stage 2, round 4, reissued under R2-14

**179 passed, 2 failed, 0 budget-waived notes**, reproduced again on this same revision: 174 passing/two failing black-box probes and five passing narrow source checks. **Shadowbrook and Deepwell still block**, now supported by field-symmetric, Nimble-only plans costing **65 and 74**. Rankforge and Nullkind remain fixed. This revision of the verdict supersedes the earlier CEO-only plan justification committed at `c82c2f60185e046fbf6646512461c4557794f71b`.

R2-14 rejects the previous 60/69/57/57-unit policy because its extra query singled out CEO. Those costs no longer establish a fair completeness or saving claim. I replaced that policy, reran the four reported problems first and then the entire audit, and retained the spending observation as a non-blocking note. R2-15/R2-16 were also read and applied.

## Reproduction and exact revision

```sh
fclone 770529f8f7995579f2c655b66a7107b19b7ac240 /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-770529f8f799-r14
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-770529f8f799-r14/stage-2
```

The single-argument runner builds/starts that folder, the supplied mock with sample corpus plus independently authored cases, and the real accepted Stage 1 upgrade source. It retests my four reported cases first, runs every probe and executes the plans inside the same candidate image with **2 vCPU/3 GiB**. It prints `TOTAL COUNTS 179 passed 2 failed 0 notes` and exits **1**.

Safe report: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/results-770529f8f799-r14.json`. `r2_12_plans` holds all seven queries, complete served-result metadata, pooled-page selection traces, rendered URLs, actual costs, `field_symmetric=true`, validation and preservation flags. `witnesses` holds the service's candidate keys and calls. The earlier report remains archived separately, with its superseded policy; it is not this proof.

Clean `fclone` and `fserve` used the exact full hash. Clone status is clean; the accepted Stage 1 tree matches `e391dd0b4280ee518d358387614110bebf90c116` unchanged. No product code/tests were edited. No supplied check/test sources, `key.json`, another seat's tests/corpus or future-stage specifications/logs were opened. All owned containers were removed. Probes stay private until final publication.

## F1 — Two candidate sets remain incomplete within a fair 80-unit plan

Units: **S2-005, S2-008, S2-054, S2-080**, interpreted by R1-03/R2-06 and **R2-12 through R2-16**.

| Probe / domain | Actual CEO candidates | Actual selected value | Missing evidence | New symmetric plan |
|---|---:|---|---|---:|
| `generic-nondomain-result` / `shadowbrook.test` | 10/11 | Dana Ruiz | Lina Chen, `https://registry.test/record-late` | **65** |
| `beyond-ten-results` / `deepwell.test` | 13/14 | Lina Chen | Sam Ortiz, `https://reports.test/news-c` | **74** |

Both service builds spend 80: seven lite searches, one 25-unit research run and sixteen rendered extracts. Every obtained candidate passes provenance, metadata, ordering, selected-flag, status and citation-consistency checks before the separate completeness assertion fails.

Shadowbrook's missing filing is dated 2026 and states `Shadowbrook chief executive officer: Lina Chen.` It outranks ten own-site Dana Ruiz candidates dated 2025. The service should select Lina Chen and mark the field contested; it selects Dana Ruiz with only that value represented. Its own query `shadowbrook CEO chief executive` actually returns the filing, but the service never extracts it.

Deepwell's missing news page states `Deepwell CEO: Sam Ortiz.` The selected Lina Chen is already correct, but every feasible supported candidate is still required. This build neither discovers nor extracts that page. The other thirteen expected candidates remain present.

The one command above reproduces both failures and all passing checks. These are two instances of one gathering/completeness finding, not claims of two parser defects.

## Field-symmetric plan and a priori justification

The policy uses a **specification-order default**, fixed before these new executions: take the **first statement phrase listed in Appendix A.3 for each field**. All six fields receive exactly the same treatment. I did not try first/second/third variants and keep whichever succeeded; no missing value or fixture URL selects a query. The reason for first-listed phrases is independent of their fixture outcome: it is the same deterministic way to select one published phrase from each field's list.

For either domain, the exact seven Nimble lite searches, each requesting ten results, are:

```text
<domain>
<domain> legal name
<domain> headquartered in
<domain> chief executive officer
<domain> founded
<domain> employs
<domain> raised
```

The plan also runs Nimble research naming the domain and all six output-schema properties. Queries contain only the normalized domain and specification-published words. Exactly one successful query is the bare normalized domain. These fixtures return no research citations.

Pool and deduplicate **every returned URL** from all seven searches plus research citations. The shared budget is at most sixteen Nimble rendered extracts. If ranking is needed, rank research-cited pages first, company-naming served title/URL/snippet next, generic results next, and titles explicitly naming another valid hostname last; within a class use best served result rank across **all** queries, then Unicode URL. This is a field-independent relevance rule; external URL hosts alone do not demote a page, and no short/static snippet excludes it. All provider calls go through Python WebRouter, with extracts using `provider_options={"render": True}`.

**For the two blocking cases no page-choice filter or ranking is needed:** Shadowbrook's seven searches return only **eleven distinct URLs** and Deepwell's return only **fourteen**. The plan renders **every one**, including the generic filing and every news page. Nothing returned is discarded. Selection cannot depend on knowing which of those pages carries the missing candidate.

| Company | Lite searches | Research | All returned rendered pages | Actual cost | Preserves every service candidate |
|---|---:|---:|---:|---:|---|
| Shadowbrook | 7 | 25 | 11 × 3 = 33 | **65** | yes |
| Deepwell | 7 | 25 | 14 × 3 = 42 | **74** | yes |

The finite unions are:

- Shadowbrook: `https://shadowbrook.test/a/0` through `/a/9` and `https://registry.test/record-late`.
- Deepwell: `https://deepwell.test/a/0` through `/a/9`, `https://registry.test/filing`, and `https://reports.test/news-a`, `/news-b`, `/news-c`.

These URL lists describe the observed results of the stated rule; they are not inputs to it. The helper imports its expected-answer fixture **only after every call has completed**. It then verifies that the served browser documents contain the full expected prose. The host compares all actual `(field, value, URL)` keys against the obtained plan keys. `verified=true`, `field_symmetric=true` and `preserves_actual_candidates=true` hold for both cases. Actual provider-log fees are 65 and 74, and executions take approximately 0.3 seconds each under resource limits.

The same rule also runs unchanged for Rankforge and Nullkind. They have larger mixed-result unions, so the relevance rank and sixteen-page bound apply; both cost 80 and preserve their now-complete service candidate sets. Those two passing cases are not used as cheaper-spend proofs. The bound is always **7 + 25 + 16 × 3 = 80**.

This proof uses Nimble alone (R2-15), applies the corresponding first-listed query to every field (R2-14), and has a specification-order justification independent of which phrase variant wins on a fixture (R2-16). R2-12's preserving-plan burden is met for both remaining failures, so neither is a budget-waived note.

## Spending note — non-blocking under R2-14

All fifteen detailed candidate-case builds spend 80, including simple one-page cases. This is **not an independent Stage 2 block**. The earlier 57-unit Rankforge/Nullkind comparisons used the now-rejected CEO-only policy and are withdrawn as fair saving proofs.

Observed spending remains worth recording: in this rerun Shadowbrook, Rankforge and Nullkind have respectively **3, 15 and 18 paid units** after the final candidate-contributing extract in provider call-log order; Deepwell has zero. These tail values vary with concurrent-call interleaving, so they are recorded with this run rather than treated as fixed performance bounds. Noncontributing rendered URL lists are retained in `spending_note`. The new symmetric plan obtains strictly more correct evidence for Shadowbrook/Deepwell at 65/74 instead of 80, showing avoidable spend in those cases as well as the completeness defect. No global optimum or Stage 4 workload result is claimed; the future spend-per-correct-field judgement remains unopened.

## Other checks and peer evidence

The complete audit was rerun, not merely the helper. Rankforge now has all five candidates and selected Lina Chen; Nullkind has all four and selected Iris Cole. Browser-only/static replacement, late generic prose, whitespace-normalized support, all obtained-record ranking/metadata/status/dedup/citation checks, API/auth/idempotency, fifty-request races, clock, reset/import cancellation, portable sessions/original replay responses/reusable failed keys and cost accounting pass. Fourth-attempt 429 recovery and the controlled 0.8-second-provider ten-second-bound probe pass. Five narrow source checks pass for delivery/dependencies, WebRouter routing, hashing and live timing.

All 375/1280 browser flows pass again, including confirmed refusal versus uncertainty, identical-key/body lost create and refresh retries, polling/latest-read-wins, known zero, contested entries after more than 200 completed dossiers and actual Stage 1 export/import with the browser/token alive. Failed imported refresh preserves fields; next-ready completion replaces candidates. Optional-provider ordering and null authority have narrow source evidence.

After my own probes and plans ran, I read the exact-revision product-user PASS and verifier verdict. The verifier's file discussed a second-listed-phrase Vega plan and disclosed its outcome-based variant choice; R2-16 rules that case a note. I neither adopted that plan nor opened its tests/corpus. This BLOCK rests solely on the two independent first-listed-phrase executions above. Product-user owns visual judgement under R2-11.

The **R2-08/R2-09 accepted Stage 1 export evidence limitation** remains a non-blocking final-report residual. Every actually exported excerpt is re-evaluated; unavailable unexported text is not recovered through import research.

## Ledger and kit

All **153 normative/ambiguous units** have refreshed evidence for this exact revision. R2-14/R2-15/R2-16 and historical policy limitations are recorded in ledger/dangers. Reading validation exits 0 for all 188 units. The audit command:

```sh
ledger-check 2 --phase audit --revision 770529f8f7995579f2c655b66a7107b19b7ac240
```

exits **1** with exactly **S2-005, S2-008, S2-054, S2-080** failing and no missing evidence entries.

The unchanged exact revision's prior isolated kit run remains valid: it exits **0** and prints **`claimed stage: 2`** at `checks/second-reader-s2-770529f8-01`. It was not rerun merely for this helper/ruling change. Command:

```sh
cd /Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026
env BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/docker-buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-770529f8f799 --stage 2 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s2-770529f8-01
```

The sample result does not override the two complete, field-symmetric reproductions.
