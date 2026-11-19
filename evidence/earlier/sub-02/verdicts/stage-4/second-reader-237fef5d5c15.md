VERDICT: BLOCK
REVISION: 237fef5d5c152b310842a64be097aeaba0c99809

**One new finding, SR4-6: S4-002/S4-109/S4-118; S1-245/S1-280; R4-0.** A restart during the wait after completed 429 refusals converts free attempts into charged units. Eight initial calls (seven lite searches, one research creation) have all completed 429, cost zero, and response counts stay quiescent before the stop. After SIGKILL/start, the build becomes ready with **70 spent_units**, while the complete provider bill is **38**. The excess **32** equals the eight completed reservations (7+25); no pre-stop request was still awaiting a provider response. The uncertainty permission for in-flight calls does not cover these known refusals.

Reproduce:

```sh
SECOND_READER_ONLY=stage4-refused-restart /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/237fef5d5c15/stage-4
```

Focused official confirmation: one failed, 82 assertions, exit 1; a separate investigation also fails with the same 70 versus 38 (110 assertions). Final whole-run confirmation: **70 reported versus 38 billed**, with all eight pre-stop replies complete and free; measured pre-pause quiescence **0.155 s**, followed by 0.1 s drain while paused, counts still eight. Maximum pre-stop provider-response duration **0.002161 s**. No other full-run probe fails.

SR4-5 was retested first: one passed, 155 assertions, failed within 5.937 s. All twelve targeted regressions then pass (2901 assertions), including 0.8-second errors finishing in 7.651 s, 1.2-second errors recovering full evidence after an eight-second outage in 16.145 s, and the 31-second slow-call protection. All earlier findings are resolved or withdrawn.

The original full run passed all 290 probes (25409 assertions). The durability review then added this completed-refusal case to the default runner and reran the whole:

```sh
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/237fef5d5c15/stage-4
```

**291 tests: 290 passed, one failed, 25272 assertions, exit 1**. Only stage4-refused-restart fails.

All 224 inherited cases and all other Stage 4 cases pass. Eight-field boundary retains all 20 candidates at 80 units; prior boundaries complete. Required browser routes pass at 375/1280. Twenty-four DOM audits cover 660 visible text elements, with no contrast/visible-label findings or horizontal overflow. Current mobile investor/origin/date and desktop evidence screenshots were reviewed; exactly six original field hooks remain.

The prescribed isolated sample claims Stage 4, 122+12+9+10 passing. Ledger audit: **exit 1 for S4-002/S4-109/S4-118 only, failing exact-revision evidence for SR4-6, with no missing rows**, with exact-revision evidence for all 111 normative/ruled units and no missing rows. Detail/source corroboration: `ledger/stage-4-audit-237fef5d5c15.md`; safe proof: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-4/artifacts/refused-restart.json`.

Verifier reports 307/307 PASS and product-user PASS. The product-user report was read after the original independent 290-probe whole run; no verifier verdict existed at that check. Both exact-revision reports were read after the final 291-probe run. Neither report describes the completed-refusal stop window, and their passing results do not override this additional reproduced case. No other-seat test sources were opened.

No product code/tests edited, no supplied or other-seat test sources read. Accepted folders unchanged; probes private; owned resources stopped.
