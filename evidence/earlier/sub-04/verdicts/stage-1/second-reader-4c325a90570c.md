VERDICT: BLOCK
REVISION: 4c325a90570c523622db2c485684608435818838

# Independent second reading audit, fix round 2

## Previously reported findings: resolved

SR1-02 (S1-128/S1-143) was retested first with the fast header control and the original delayed-header case. Both passed. The original SR1-01/S1-226 deadline case passed next, before the whole-stage run. In the delayed cases the research request timed out after about 77.6 seconds, the build completed around second 250, no unverified quotation was asserted, and the unanswered request's full 25-unit cost was retained. No actual research result had been collected in that scenario.

The full run also exercised the new verification margin: research returned at second 249, then two cited pages took 35 seconds to extract. One quotation occurred only in a Facts header and was rejected; one occurred in prose and was preserved as a known CEO field. The build finished at **284.07 seconds**, with both extracts answered and cost correctly reported as 42 units. This independently confirms the positive and negative citation paths within the live deadline.

## Blocking finding SR1-03 — S1-223 and S1-121 as ruled by R1-02: early extracts leave insufficient budget to verify all six supported research claims

A ready build leaves three fields unknown even though its Nimble research answer provides supported claims for all six fields. The build uses 45 units extracting administrative archive pages before research, reserves only three units for the pages research cites, and exhausts the 80-unit budget after verifying only three of six different cited pages.

The independent fixture is a normal six-field company profile. It contains 60 searchable administrative archive pages with long prose and no supported field values, plus six unsearchable filing pages, one for each field. Nimble research returns all six values, with valid single-sentence citations actually present in those filing pages' prose. Each provider call answers normally; there are no refusals, delays, lost replies, unsupported claims, or header quotations in this case.

The API completes `ready` with only three known fields. These supported fields remain unknown:

| Field | Supported value | API result |
|---|---|---|
| legal_name | `Budget Harbor Inc.` | unknown |
| hq_city | `Porto` | unknown |
| headcount_range | `51-200` | unknown |

The exact-revision provider log and `spent_units` agree:

| Work | Units |
|---|---:|
| 7 lite searches | 7 |
| 45 archive-page extracts | 45 |
| 1 research run asking for all six fields | 25 |
| 3 research-cited-page extracts | 3 |
| Total | **80** |

The cost limit itself is respected. Field completeness is not. A plan leaving room for all six cited pages fits inside the same cap: 7 searches + 42 early extracts + 25 research + 6 cited-page extracts = 80. The dispatch also explicitly prioritizes correctness and calls a saving that omits needed evidence a defect.

A control keeps the exact same six research claims and cited-page prose but omits the administrative archive pages. It produces all **six known fields for 46 units**, confirming that the claims, values, page contents, provider shapes, and citation parser are valid. The large-result case consistently produces only three known fields for 80 units. This is an allocation/planning failure, not an unavailable-provider or malformed-input case.

Reproduction from a fresh exact clone:

```sh
fclone 4c325a90570c523622db2c485684608435818838 /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-03
SECOND_READER_ONLY=research-citation-budget-control,six-research-citation-budget /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-03/stage-1
```

The command builds/starts the folder and unchanged official mock itself, preserves all supplied sample companies/traits, adds one independent company in a separate mock/source pair, uses an internal network and 2-vCPU/3-GiB service limits, and prints `COUNTS total=2 passed=1 failed=1`, exit 1. Both builds finish in under one second after setup. No answer key, kit tests, product tests, or shipped check sources are read. The same case fails in the full root `run.sh <stage-folder>`; probe sources remain private until every stage closes.

Source corroboration: `stage-1/dossier/research.py` uses `VERIFY_RESERVE = 3`, subtracting that constant and the 25-unit research cost before spending the remaining extraction room. `_research` subsequently obtains six claims and attempts six different cited-page URLs. The Budget admits only three. The new verified-prose requirement correctly rejects unread quotes, so those three values stay unknown. The plan must preserve enough budget to satisfy field completeness with valid citations.

## Complete audit evidence

The whole-stage run gave **42 cases: 41 passed, 1 failed**. A separate budget-control run added the passing control above, and stronger replacement-import and charged-snapshot probes were rerun successfully. Across **43 unique independent cases: 42 pass, 1 fails**. There is one blocking finding, SR1-03, covering S1-223 and S1-121/R1-02.

Both epochs of all 12 supplied sample companies passed again: 24 sample builds, 138 supported known fields, 669 research units, largest sample build 40 units. Other passing coverage includes JSON/auth conventions, clock behavior, validation, idempotency scope/precedence, 50-writer races, reset during a build, failure/recovery refresh, listings, and cumulative spending during builds.

The strengthened transfer probe stops the source before import, preserves its tokens/hash login/dossier IDs/fields/original replay responses, removes a destination-only account/dossier/token/idempotency key, and makes no provider call during import/replay. The strengthened snapshot probe exports after a provider charge has actually settled while the build is running; import restores the pre-build state/cost, for both first and later builds. PORT=8089 and the default-port service both answered health. The cloned candidate stayed clean, and no product file/test was edited.

The verifier's `verdicts/stage-1/verifier-4c325a90570c.md` was read only after independent execution. It reports PASS, 101/101 sealed tests, and an isolated check claiming stage 1. The budget-completeness case supplies additional concrete evidence and does not change to agree with that report.

All 379 ledger units remain covered, with current-revision evidence for all 318 normative/ruled units. `ledger-check 1 --phase audit --revision 4c325a90570c523622db2c485684608435818838` exits 1 with exactly **S1-121 and S1-223** open. Full results and source/command evidence are in `ledger/stage-1-probe-results-4c325a90570c.md` and `ledger/stage-1-audit-4c325a90570c.md`. Owned containers, networks, and temporary corpus copies were removed.
