VERDICT: BLOCK
REVISION: 695a584c021cd5d61c09568504bedcbd3afae63a

**One finding: SR4-5 (S4-002/S4-108; S1-224–226; R4-9).** With the live hostname locally substituted to the mock proxy, every Nimble operation answers 500 immediately. The dossier is still building after **10.232 s**; expected failed within ten seconds. All 96 recorded responses are 500 and take at most **0.005314 s**. R4-9 applies the fast-call deadline on any host; the longer live protection concerns slow calls only. No public provider was contacted. The saved observation precedes reset cleanup; natural eventual completion was not awaited.

Reproduce:

```sh
SECOND_READER_ONLY=stage4-live-fast-failure /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/695a584c021c/stage-4
```

Focused result: one failed, 243 assertions, exit 1. Final whole-run confirmation: **building after 10.214 s**, 96 completed 500 responses, maximum provider response **0.006150 s**. The only failure is stage4-live-fast-failure.

Reported problem retested first: all four transient controls pass (235 assertions), including all 13 candidates after one extract refusal per URL and a 1.5-second native outage. Then total failure passes (three tests, 1248 assertions): both providers end in 6.125 s, eight concurrent builds including four batch jobs in 5.939–6.117 s, zero cost and no post-terminal calls. Corrected R4-8/R4-8a matrix passes (two tests, 78 assertions); SR4-3 remains withdrawn.

Full command:

```sh
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/695a584c021c/stage-4
```

**288 tests: 287 passed, one failed, 24802 assertions, exit 1**.

All 224 inherited probes pass, including the separate slow-live-call protection. All other Stage 4 probes pass. The eight-field cap case retains all 20 candidates at 80 units; prior boundaries remain complete. Required browser routes pass at 375/1280. Twenty-four DOM audits cover 660 visible text elements with no contrast/visible-label findings or horizontal overflow; current mobile investor/origin/date and desktop evidence screenshots were reviewed. Six original field test ids remain unchanged.

Prescribed isolated sample claims Stage 4 with 122+12+9+10 passing. Ledger audit: **exit 1 for S4-002/S4-108 only, failing exact-revision evidence for SR4-5, no missing rows**; no missing evidence among all 111 normative/ruled units. Details: `ledger/stage-4-audit-695a584c021c.md`; safe proof: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/artifacts/live-fast-failure.json`.

Only after the full independent probes were the other exact-revision reports read. Verifier reports 306 passing cases and one R4-9 failure (F3), independently corroborating SR4-5. It reports natural failure at 119.9 s; my probe independently establishes still building past ten seconds and does not claim that eventual duration. Product-user reports PASS after a complete 375/1440 re-walk with total/brief/optional-provider failure controls. No other-seat test sources were read.

No product code/tests edited, no supplied or other-seat test sources read. Narrow source-only checks follow independent full probes. Accepted folders unchanged; probes private; owned resources stopped.
