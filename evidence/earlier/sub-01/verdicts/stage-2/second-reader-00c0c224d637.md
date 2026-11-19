VERDICT: PASS
REVISION: 00c0c224d637ab25653e709f869ac209ac747c3e

# Independent second-reader audit — Stage 2, round 5, reissued under R2-17

**PASS under R2-17: 181 passing checks, zero blocking failures, one retained completeness note.** The raw Budgetedge 14-versus-16 observation remains unchanged. The fixed seven-query policy loses candidates obtained by this build on other sample companies, so it does not dominate the build across the workload. R2-17 explicitly makes Budgetedge a note in that situation. This verdict supersedes the BLOCK conclusion committed at `f235c5a94352fb8a52a6fd8b3dd914f54968059f`; the product revision has not changed.

All earlier reported cases are fixed: Shadowbrook 11/11, Deepwell 14/14, Rankforge 5/5 and Nullkind 4/4, with correct selected values and spending at or below 80. API, race, clock, idempotency, reset/import, rate, timing, browser and actual Stage 1 upgrade probes pass. The original 181-check suite passed before the added boundary; the complete expanded audit had 181 passes and the one raw boundary mismatch. R2-17 changes that mismatch's classification; no raw result has been erased.

## Workload comparison requested by R2-17

I executed the **unchanged** `feasible_plan.gather()` policy against every company in the sample corpus and the exact sample-plus-authored mock corpus used by my probes. Both epochs were tested. For each company/epoch: reset mock/service; build on this exact revision; record every `(field, value, URL)` candidate key and actual cost; reset the mock; execute the fixed policy; derive supported keys independently from the browser documents it served; compare inclusion in both directions.

The independent support reader follows Appendix A, uses no product imports and ignores Facts headers. It was cross-checked against **every authored legacy and Stage 2 fixture**, with zero mismatches. It also verified that every build candidate counted in the comparison had support in actual served browser prose. No `key.json`, supplied check/test source or verifier test/corpus was opened.

Observed totals are:

| Corpus / membership | Epoch | Build candidates | Seven-query rule candidates | Build keys lost by rule | Rule-only keys |
|---|---:|---:|---:|---:|---:|
| Sample alone, 12 companies | 0 | **100** | **72** | **29** | 1 |
| Sample alone, 12 companies | 1 | **102** | **74** | **29** | 1 |
| Authored subset, 151 companies, in my mixed mock | 0 | **180** | **182** | **0** | 2 |
| Authored subset, 151 companies, in my mixed mock | 1 | **178** | **180** | **0** | 2 |
| Entire mixed mock used by my probes, 163 companies | 0 | **264** | **245** | **22** | 3 |
| Entire mixed mock used by my probes, 163 companies | 1 | **264** | **245** | **22** | 3 |
| Verifier corpus, 9 companies (verifier execution) | 0 | **37** | **37** | **0** | 0 |

The authored-subset and entire-mixed rows overlap; they are not additive corpora. The mixed mock includes the twelve supplied sample companies plus all 151 authored companies, exactly as the original probe setup does. Sample-alone is a separate mock containing only the published sample. These are measured counts for the recorded executions, rather than the builder's unverified 18-of-101 estimate.

For a concrete independent counterexample, on sample epoch 0 **Ashgrove Solar** has seven build candidates versus three rule candidates. The rule loses these build-supported keys:

- CEO Marcus Mensah and funding total 21,500,000 at `https://businessbeat.test/2025/09/ashgrove-solar-eyes-new-markets`.
- Founded year 2019 and headcount `11-50` at `https://startupindex.test/companies/ashgrove-solar`.

These losses alone disprove global key inclusion. Gains on Budgetedge cannot compensate for losses elsewhere under R2-17. The rule also adds one Quillmate funding candidate on the sample; aggregate totals do not hide that trade-off.

The verifier independently ran this same helper in the candidate image on its nine-company private corpus and reported exact key equality, total **37/37**. Its addressed report is message `6870a943-e1a8-4939-9e32-b194d91c3895`; the reported command was `$FACTORY_WORK/verifier/probes/r217/compare.py <domains...>` using the image's Python, with its workspace mounted read-only. I did not open that source/corpus or claim to reproduce the verifier-owned run. Its result is relayed as peer evidence. Sample and mixed results above are my independent executions and already decide the classification.

After publication was authorized, the verifier supplied `/Users/[REDACTED]/dev/band-factory/work/verifier/probes/r217/out/r217-verifier-corpus.json`, with command/setup and candidate keys represented only by truncated SHA-256 hashes. I read that safe outcome artifact and independently checked equality of all nine reported hash sets and their 37/37 sum; I did not rerun provider execution or open sealed corpus values. A credential-free receipt, including its source SHA-256 and per-company hash sets, is published at `acceptance/second-reader/stage-2/r217-verifier-receipt.json`.

## Fixed rule and reproducible comparison

The provider policy is still the round-4 specification-order default: six-field Nimble research; one normalized-domain lite search; one `<domain> <first Appendix A.3 phrase>` lite search for **each** field (`legal name`, `headquartered in`, `chief executive officer`, `founded`, `employs`, `raised`), all requesting ten results. Pool/deduplicate every returned/cited URL. Share at most sixteen rendered reads by research-cited > company-naming served metadata > generic > title names another host, then best rank across all queries and Unicode URL. Every provider request goes through WebRouter and Nimble. No variant, URL or field priority was changed per company or corpus.

The only helper plumbing change allows the mock epoch to be set for the epoch-1 comparison; provider arguments, ranking and budget policy are identical. Expected fixtures are never consulted during provider-call selection. Both the service and helper run in containers from this exact candidate image, independently limited to **2 vCPU/3 GiB**, on internal networks.

Run the independent sample/mixed comparison alone:

```sh
python3 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/compare_rule.py /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-00c0c224d637/stage-2
```

It exits **0** after executing all 350 company/epoch comparisons (24 sample-alone plus 326 mixed). Safe per-company keys, calls/selection metadata, costs and totals are written to:

- `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/r217-sample.json`
- `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/r217-second-reader.json`

No credentials or session exports are stored in these reports. All owned comparison containers/networks were removed.

## Retained notes

**N1 — Budgetedge completeness trade-off, non-blocking under R2-17.** On this revision, `budgetedge.test` returns fourteen supported CEO page/value candidates and omits the Dana Ruiz candidates at `https://budgetedge.test/a/3` and `/a/6`. The selected Lina Chen and contested status are correct. The build spends 13 searches + research 25 + fourteen renders × 3 = 80. The seven-query policy reads all sixteen returned pages at 7 + 25 + sixteen × 3 = 80 and preserves all fourteen actual keys. This remains the observed boundary, including its per-company feasible plan. Because that same rule loses build keys on other workload companies, it is a different trade-off rather than a blocking better rule under R2-17. Both epochs of the new comparison reproduce Budgetedge 14/16.

**N2 — Accepted Stage 1 export evidence residual.** R2-08/R2-09 still record that accepted Stage 1 did not export all served text needed for the original Stage 2 migration requirement. Every actually exported excerpt is re-evaluated; absent unexported text is a non-blocking earlier-stage residual for the final report. The accepted Stage 1 folder remains unchanged.

**N3 — Spending.** Full-cap spending remains a non-blocking Stage 2 note under R2-14. No Stage 4 efficiency or optimal-spend claim is made, and no rejected CEO-only saving proof is revived.

**N4 — Sample rule-only candidate.** On both sample epochs the seven-query policy additionally obtains Quillmate funding total **28,500,000** from `https://businessbeat.test/2025/06/quillmate-eyes-new-markets`, which the build omits. This is retained in the comparison report as another per-page completeness trade-off note under R2-17; the same policy's 29 lost build keys on each sample epoch prevent a blocking dominance claim.

## Full audit, ledger and kit

The one-required-argument runner now performs the workload comparison as well as the complete audit and applies R2-17 to raw completeness mismatches only after obtained-record integrity has passed:

```sh
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-00c0c224d637/stage-2
```

The observed component results are **181 passed, 0 failed, 1 note** after direct application of R2-17 to the existing exact-hash full audit. The comparison command and direct classification both completed successfully. The updated wrapper itself was not rerun merely to repeat the same product checks. The raw boundary failure and its 80-unit plan remain in the report. Safe classified snapshot: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/results-00c0c224d637-r17.json`; the earlier raw report remains archived separately. Reproduce the exact direct classification used for this reissue with:

```sh
cd /Users/[REDACTED]/dev/band-factory/work/second-reader
python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,'probes/stage-2'); import r217_classification; p=Path('probes/stage-2/results.json'); r=r217_classification.apply(json.loads(p.read_text()),'00c0c224d637ab25653e709f869ac209ac747c3e'); p.write_text(json.dumps(r,indent=2,ensure_ascii=False)); print(r['passed'],r['failed'],r['notes'])"
```

This exits **0**, printing `181 0 1` once the comparison reports and full-audit report above exist.

All **153 normative/ambiguous ledger units** have exact-revision evidence. Original completeness requirements and all R2-12..R2-17 decisions are retained; note evidence explicitly identifies its conditional R2-17 scope. Both commands exit **0**, with no open units:

```sh
ledger-check 2 --phase audit --revision 00c0c224d637ab25653e709f869ac209ac747c3e
ledger-check 2 --phase reading
```

The exact-hash isolated kit sample still exits **0**, printing **`claimed stage: 2`**, at `checks/second-reader-s2-00c0c224-01`. It was not repeated merely for this policy-classification change. Command:

```sh
cd /Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026
env BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/docker-buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-00c0c224d637 --stage 2 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s2-00c0c224-01
```

Clean exact-hash `fclone`/`fserve` and Stage 1 immutability were verified in the original audit; the comparison driver again asserts a clean clone and builds that exact source. Product-user's exact-revision PASS and the verifier's PASS were read after my own probes. No product code/tests were edited, no forbidden sources or later-stage material were opened, and all owned containers are removed. Probes remain private until final publication.
