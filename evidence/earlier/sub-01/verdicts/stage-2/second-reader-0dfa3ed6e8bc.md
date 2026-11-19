VERDICT: BLOCK
REVISION: 0dfa3ed6e8bcb58a63c4211d2aeee117e6ca559e

# Independent second-reader audit — Stage 2, round 3

The complete audit has **177 passes, 4 failures and 0 budget-waived notes**: 172 passing and four failing black-box probes plus five passing narrow source checks. All four failures are avoidable completeness/wrong-selection cases under **R2-12**. I executed a preserving WebRouter plan for each, at **60, 69, 41 and 38 units** respectively; these are observed provider costs, not estimates. Browser, upgrade, rate-limit and timing checks pass.

## Exact revision and reproduction

```sh
fclone 0dfa3ed6e8bcb58a63c4211d2aeee117e6ca559e /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-0dfa3ed6e8bc
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-0dfa3ed6e8bc/stage-2
```

The single-argument runner builds/starts the supplied stage, real immutable Stage 1 upgrade source and supplied mock with the sample corpus plus authored cases. Reported failures run first, followed by the full audit. It then executes the R2-12 plans through WebRouter inside this candidate's image, on the same mock corpus, with 2-vCPU/3-GiB limits. It prints `TOTAL COUNTS 177 passed 4 failed 0 notes` and exits **1**. Plans and safe witnesses are in `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/results.json`; the revision archive is `results-0dfa3ed6e8bc.json` in that directory.

`fclone`/`fserve` used this exact hash. Clone status is clean, and `git diff --exit-code e391dd0b4280ee518d358387614110bebf90c116 HEAD -- stage-1` exits 0. No product code/tests were edited, and no supplied test/check source, `key.json` or future-stage specification/log was opened. All owned containers were removed. Probes remain private until all stages close.

## F1 — Reachable evidence is missed while budget goes to lower-yield work

Units: **S2-005, S2-007, S2-008, S2-054, S2-080**, interpreted by R1-03/R2-06 and the new **R2-12**.

Every row below was tested on a fresh fixture/epoch. Each actual build spent **80 units**: 13 lite searches, one research run and 14 unique rendered extracts. Only two rendered pages contributed the company's candidates. Each verified alternative retains those candidates and obtains the missing ones within 80.

| Probe / company | Actual CEO candidates | Actual selected value | Complete expected value | Verified plan |
|---|---:|---|---|---:|
| `generic-nondomain-result` / `shadowbrook.test` | 2 of 11 | Dana Ruiz | Lina Chen | 60 |
| `beyond-ten-results` / `deepwell.test` | 2 of 14 | Dana Ruiz | Lina Chen | 69 |
| `authority-instant-url` / `rankforge.test` | 2 of 5 | Sam Ortiz | Lina Chen | 41 |
| `metadata-fallback` / `nullkind.test` | 2 of 4 | Dana Ruiz | Iris Cole | 38 |

Shadowbrook and Deepwell are the reported problems retested first. In this revision their missing pages generally are not discovered by the small-result searches; this is no longer the preceding revision's post-search snippet filter. The probe records whether the generic Shadowbrook page was returned, without inventing a requirement that this particular query plan return it. The obligation and finding are the feasible missing candidates, demonstrated below.

Rankforge's missing `a-filing` candidate wins over `b-filing` by the URL tie-break at the same publication instant. Nullkind's missing www-host candidate is kind own and newer than the undated own candidate. The metadata, provenance, ordering and selected-value/citation consistency of the **records actually obtained** pass independent checks before the separate completeness assertion fails. These are not four distinct parser failures; the candidate sets are incomplete and therefore yield the wrong complete-set winner.

Reproduce all four with the full runner. Failure names are `candidates/generic-nondomain-result`, `candidates/beyond-ten-results`, `candidates/authority-instant-url` and `candidates/metadata-fallback`.

## Executed plans satisfying R2-12

All plans use **Nimble through Python WebRouter**. They make exactly one successful search whose query is the normalized domain, at `search_depth="lite"`, `max_results=10`. Shadowbrook and Deepwell make one additional lite query, respectively `shadowbrook.test chief executive officer` and `deepwell.test chief executive officer`, also asking for ten results. These are domain/statement-word queries; they do **not** require knowing a missing value.

Each plan also starts one 25-unit research run naming the domain and all six output-schema properties (`legal_name`, `hq_city`, `ceo`, `founded_year`, `headcount_range`, `funding_total`), and collects its result at no further cost. These four fixtures return no research citation requiring another page. Every listed page is then obtained once with `provider_options={"render": True}` at three units per URL, with at most four concurrent extracts. Full expected browser prose is checked against the returned document; no snippet/header is substituted for a supporting browser excerpt.

| Company | Lite searches | Research | Rendered URLs | Actual total |
|---|---:|---:|---:|---:|
| Shadowbrook | 2 | 25 | 11 × 3 = 33 | **60** |
| Deepwell | 2 | 25 | 14 × 3 = 42 | **69** |
| Rankforge | 1 | 25 | 5 × 3 = 15 | **41** |
| Nullkind | 1 | 25 | 4 × 3 = 12 | **38** |

The finite extract lists are:

- **Shadowbrook:** `https://shadowbrook.test/a/0` through `/a/9` (all ten integer suffixes), and `https://registry.test/record-late`.
- **Deepwell:** `https://deepwell.test/a/0` through `/a/9`, `https://registry.test/filing`, and `https://reports.test/news-a`, `/news-b`, `/news-c`.
- **Rankforge:** `https://rankforge.test/a-filing`, `/aggregator`, `/b-filing`, `/news`, `/z-own`.
- **Nullkind:** `https://nullkind.test/about`, `https://blog.nullkind.test/blog`, `https://register.test/register`, `https://www.nullkind.test/www`.

`feasible_plan.py` actually issued the calls, checked the mock's cost log and the one-successful-exact-domain-query rule, confirmed each requested URL had been discovered by those searches, and compared every planned `(field, value, URL)` key with the candidate's obtained keys. **All four plans preserve every obtained candidate.** They took approximately 0.2–0.4 seconds on the mock under the resource limits. The full response/call/URL/cost evidence is rerunnable with the one command above; each plan is generated in `r2_12_plans` in the safe report. No optional Kernel service is required.

R2-12's burden is therefore met. None of these four misses is an unreachable-budget note. The budget cap was respected by the product, but its avoidable misses and wrong winners remain blocking.

## Passing checks and observation limits

All four preceding non-crowded regressions still pass: browser-only short/long text, whitespace-normalized headquarters support and the late generic registry support case. Standard API/auth/idempotency/concurrency, clock, reset/import cancellation, field/citation integrity and conditional source checks pass.

The rate probe now isolates planned-call recovery and zero refusal cost from full-corpus completeness, which is assessed separately with the R2-12 plans. It reaches the fourth opportunity. A controlled **0.8-second provider delay** test also passes the inherited ten-second bound: at approximately 10.2 seconds the dossier is ready, without any 429 waiting exemption.

All 375/1280 browser checks pass: signup/login/logout, confirmed refusal versus uncertainty, identical-key/body retries, normalized/existing research, polling, reload/latest-read-wins, complete hooks and ordered records for available API data, zero-dollar values, and contested fields after 201 completed earlier-sorting dossiers. Both lost create and refresh responses survive real accepted-Stage-1 export/import with the same open browser and old token. Failed post-import refresh preserves candidates, and the next ready build replaces them. The R2-08/R2-09 unavailable-legacy-text residual stays non-blocking and remains recorded for the final report.

After my own probes/plans ran, I read the other verdicts. Product-user is PASS on this exact revision and owns the visual judgement under R2-11. The verifier independently reports a blocked Vega case with a 70-unit plan and treats its unproved Orbit miss as a note under R2-12. I did not use its test source/corpus or promote its note into my own finding; this BLOCK relies on the four executed plans above.

## Ledger and kit sample

R2-12 has been recorded on the affected ledger units, preserving their original requirements. Every **153 normative/ambiguous unit** has exact-revision evidence. Obtained-record metadata/order checks are explicitly scoped; they do not claim a partial candidate set is complete. The audit command:

```sh
ledger-check 2 --phase audit --revision 0dfa3ed6e8bcb58a63c4211d2aeee117e6ca559e
```

exits **1** with exactly S2-005, S2-007, S2-008, S2-054 and S2-080 failing. There are no units without an evidence entry.

The kit sample command, on this clean clone and a fresh directory, exits **0** and claims Stage 2:

```sh
cd /Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026
env BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/docker-buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-0dfa3ed6e8bc --stage 2 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s2-0dfa3ed6-01
```

The sample result does not override the demonstrated R2-12 failures.
