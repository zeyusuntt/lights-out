VERDICT: BLOCK
REVISION: 7a5202cac9f9b10c173487164654f09ad96781da

# Independent second reading audit, fix round 5

## Earlier findings

SR1-05 was retested first. Its original checkpoint passes on a valid repeat; the full load probe additionally observed every build ready **7.130 seconds after the earliest initiating request**, with maximum provider HTTP reply 0.609 seconds and maximum complete research interval 0.787 seconds. All fifty builds had six known fields; total 2,400 units agreed with the provider log. An initial run whose complete research interval exceeded one second by 0.007 seconds was excluded as an unmet setup premise.

SR1-01..04 then passed all eight focused regression cases before the complete run: reset during a partial body returns 401 and leaves the replacement state empty; unchanged import retaining the token permits 202; both header controls, the near-deadline call, the two-page confirmation margin and both research-budget cases pass.

## SR1-06 — S1-121/R1-02 and S1-223: short supporting excerpt inside a long sentence is omitted

The mock serves a searchable page whose prose is one 1,100-character sentence. It contains this exact 39-character excerpt:

> Length Harbor is headquartered in Porto

The fragment is a single sentence under A.1, names the company, contains the headquarters statement phrase and exactly one city, and contains no negating phrase. It is copied from served prose, falls inside the 1..500-character excerpt limit and supports `hq_city: Porto`. The specification places no 500-character ceiling on the surrounding page sentence and does not require an excerpt to be an entire original sentence.

The service obtains that supporting text but returns headquarters unknown. Its short-sentence control returns Porto correctly. The long build is ready, spends 40 units (seven searches, eight extracts, one research) and has no provider failure. This violates the required known-if-supported behavior, even under a reading limited to actually gathered evidence.

Reproduce on this exact clean clone:

```sh
SECOND_READER_ONLY=long-sentence-with-short-supporting-excerpt /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/audit-1-7a5202cac9f9/stage-1
```

It builds/starts the service and unchanged official mock with independent added company data, verifies the short control and actual service of the quoted text, prints one failure and exits 1. A fresh clone may be made with `fclone 7a5202cac9f9b10c173487164654f09ad96781da <directory>`; pass its stage-1 folder instead. No private check data or product test is involved.

## SR1-07 — S1-224/S1-312: prompt provider refusals still take over ten seconds

The same ten-second requirement also applies when provider calls answer with errors. An independent timing proxy forwards the unchanged mock's HTTP 500 responses after about 0.8 seconds. Every call answers within one second, yet the build takes more than ten seconds to finish.

The full run observed **24 calls, maximum provider reply 0.836 seconds and build completion at 14.185 seconds**. The focused run independently gave 0.827 seconds and 14.368 seconds. Both correctly end failed with zero spent units. This is a completion-time failure; neither a provider timeout nor erroneous accounting causes it. The source's retry phases corroborate the independent observation, but the finding relies on measured HTTP behavior.

```sh
SECOND_READER_ONLY=subsecond-provider-refusals-finish-within-ten-seconds /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/audit-1-7a5202cac9f9/stage-1
```

This builds/starts everything, prints the provider/build timing summary and exits 1. The proxy preserves provider response bodies and records request receipt through response flush. A research start is itself refused, so there is no unanswered research lifecycle or result-poll delay hidden in the premise. All submission provider requests still go through WebRouter.

## Complete audit

The root run.sh completed **48 cases: 46 passed, two failed**, exit 1. SR1-06 and SR1-07 are the only blockers. Both epochs of all twelve supplied companies passed: 24 builds, 138 supported known fields, 668 research units and maximum build 39. All five earlier findings pass their focused retests and the complete rerun.

Other passing coverage includes auth/JSON/domain/query/clock rules, idempotency scope and precedence, duplicate/alias races, reset/import body races, reset during provider work, refresh failure/recovery, listings, active spending, source-stopped replacement transfer and charged-build snapshots. PORT=8089 and default-port services were healthy. The exact clone remained clean and all owned containers/networks were removed. No product source or product test was edited.

Only after the independent full run was the verifier's verdict for this revision read. Its 105-test PASS and isolated stage claim are supplementary evidence; the two additional counterexamples remain.

All 318 normative/ruled ledger units have refreshed exact-revision evidence. `ledger-check 1 --phase audit --revision 7a5202cac9f9b10c173487164654f09ad96781da` exits 1 with exactly **S1-121, S1-223, S1-224 and S1-312** open. Mechanism/isolation evidence is in `ledger/stage-1-audit-7a5202cac9f9.md`; complete case outcomes are in `ledger/stage-1-probe-results-7a5202cac9f9.md`. Private probes remain unpublished until all stages close.
