VERDICT: BLOCK
REVISION: 1713b99d57253edaf51ec4259ba30b7d29aad18f

# Independent second reading audit, fix round 6

## Retests first

The first six-case run passes the original SR1-06 long-sentence reproduction and the R1-06/06a negation, conflict, no-fitting-part and short-research-quotation controls. SR1-07 still fails. A further focused case establishes the exact-limit citation failure below, with its positive control. SR1-01..05 then pass all nine selected earlier regression cases, including the strict fifty-company completion check, before the complete run.

## SR1-07 remains — S1-224/S1-312: live-host prompt refusals exceed ten seconds

The original reproduction uses `NIMBLE_BASE_URL=http://sdk.nimbleway.com:18080/nimble` on an internal network, forwarding the unchanged official mock's answers. All 24 provider calls receive HTTP 500 refusals within one second. The complete run finishes only at **14.087 seconds**, with maximum provider reply **0.832 seconds**. The independent focused retest gives 14.333 seconds and 0.834 seconds. State correctly becomes failed and spending remains zero.

S1-224 promises ten seconds when every provider call answers within one second. Its slower-provider exception does not apply to these prompt answers. A research start is itself refused, so no long research lifecycle or unmeasured poll hides outside that premise. The mock-only retry cutoff change leaves this original live-host case unchanged; the source corroborates the timing observation but is not the finding's basis.

```sh
SECOND_READER_ONLY=subsecond-provider-refusals-finish-within-ten-seconds /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/audit-1-1713b99d5725/stage-1
```

The command builds/starts the exact clean clone and mock, prints the timing summary and exits 1. It was also the reproduction on the preceding revision.

## SR1-08 — S1-121/R1-02/R1-06/R1-06a and S1-223: a fitting 500-character citation ending before a comma is missed

A 523-character page sentence, taken whole, supports headquarters Porto. Its first **500 characters** are a contiguous single-sentence excerpt that independently supports the same value, names the company and contains no conflict or negation. The final 23 characters begin `,with regional offices.`. All words are short.

The service obtains this exact supporting text, ends ready and returns headquarters unknown. In the positive page version, only the character immediately after the identical 500-character excerpt changes from comma to space. That version correctly returns Porto. The focused control spends 43 units; the failing version spends 44 (seven searches, twelve extracts and one research), well inside budget.

R1-06 permits a contiguous part, including one ending immediately before punctuation; it imposes no requirement that the excerpt end at whitespace. R1-06a excludes sentences with no fitting part, while this one has a fitting part of exactly the permitted limit. Space-delimited token enumeration in the implementation misses that eligible excerpt. The one-character control and actual served-text check reproduce the externally visible completeness failure.

```sh
SECOND_READER_ONLY=r1-06-punctuation-boundary /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/audit-1-1713b99d5725/stage-1
```

This builds/starts everything, checks the whitespace control first, verifies the excerpt is exactly 500 characters and was served, prints one failure and exits 1. A fresh exact clone can be made with `fclone 1713b99d57253edaf51ec4259ba30b7d29aad18f <directory>` and its stage-1 folder supplied instead.

## Complete audit

The complete root run.sh reports **53 cases: 51 passed, two failed**, exit 1. These are the only blockers. The original SR1-06 example and all four ruling controls pass; SR1-01..05 pass their focused retests and the complete rerun. Every one of fifty distinct-company builds is observed ready within 7.106 seconds of the earliest initiating request, with maximum provider HTTP reply 0.609 seconds and complete research interval 0.798 seconds.

Both sample epochs pass: 24 builds, 138 supported known fields, 670 units, maximum sample build 40. Other passing checks include authentication/JSON/domain/query/clock rules, idempotency scope and precedence, duplicate/alias races, reset/import body races, refresh failure/recovery, listings, active spending, source-stopped replacement transfer and charged-build snapshots. PORT=8089 and default-port services are healthy. The clone is clean and owned containers/networks were removed; no product file or product test was edited.

The verifier's 108-test PASS and isolated stage claim were read only after our complete independent run. Those supplementary reports do not resolve the two measured counterexamples: the original live-host prompt-refusal case and the exact-limit punctuation boundary.

All 318 normative/ruled units have exact-revision evidence. `ledger-check 1 --phase audit --revision 1713b99d57253edaf51ec4259ba30b7d29aad18f` exits 1 with exactly **S1-121, S1-223, S1-224 and S1-312** open. Detailed mechanism/isolation evidence is in `ledger/stage-1-audit-1713b99d5725.md`; complete case results are in `ledger/stage-1-probe-results-1713b99d5725.md`. Private probes remain unpublished until all stages close.
