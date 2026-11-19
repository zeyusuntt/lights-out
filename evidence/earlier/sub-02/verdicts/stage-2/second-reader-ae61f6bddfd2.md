VERDICT: BLOCK
REVISION: ae61f6bddfd23c08039c3b2ef17a91acf19f9270

**SR2-4 remains partially unresolved.** Plain capstone passes; generic-prefix capedge still fails. No new finding is added.

## SR2-4 — One returned supporting page omitted with exactly enough budget left

**Units:** S2-054/S2-080 (complete candidate set), S2-078 (selected-value citations), S2-005/S2-008/S2-077/S2-084 (missing alternative changes value and status).

The capedge build returns all 16 supporting page URLs. It then makes seven lite searches (7), one research run (25), and 15 rendered extracts (45), and finishes ready at **77 units**. All calls succeed. Its sole unread returned page is `https://capedge.test/funding_total-1`.

That own page is dated February 1 and supports **25000000** after a generic 300-character opening snippet. The retained own page is dated January 1 and supports **12000000**. Actual result: **12000000, known**, only the old candidate. Required: **25000000 selected, contested**, both candidates.

**Three units remain, and the missing page's rendered extract costs three units.** One additional call completes the candidate set at exactly 80. The cap therefore does not require the omission. The plain 16-page case now correctly spends 80 and retains all candidates; only this previously reported prefix variant remains.

```sh
SECOND_READER_ONLY=candidates-cap /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/ae61f6bddfd2/stage-2
```

Result: **one passed, one failed; exit 1**. The runner builds/starts the supplied stage and documented mock itself. Diagnostics: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/artifacts/candidate-capedge.test.json`, with `candidate-capstone.test.json` and `budget-summary.json` beside it.

## Complete audit

SR2-4 was retested first, then the earlier generic-prefix, header, and hung research/refresh regressions (all five pass), then the complete independent suite.

Full result: **180 tests, 178 passed, two failed, 8849 assertions**. Both failures are capedge completeness: normal and one-second-delayed providers. Complete latency cases finish in **2.2–4.2 seconds**. The delayed capedge build also ends in 2.2 seconds, but with the same missing page; there is no separate timing finding.

All 154 inherited checks, normal candidate ranking/metadata, 429, UI, concurrency and real Stage 1 upgrade checks pass. The isolated sample claims Stage 2 with **122 Stage 1 + 12 Stage 2** checks passed. The other seats' PASS reports were read after independent probes and do not override this additional failing variant.

Ledger audit exits **1** for seven failed units, with no missing evidence rows. No product code/tests were edited. Probes remain private until all stages close.

Details and exact execution record: `ledger/stage-2-audit-ae61f6bddfd2.md`.
