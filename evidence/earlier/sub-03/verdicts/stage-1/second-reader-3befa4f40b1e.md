VERDICT: BLOCK
REVISION: 3befa4f40b1e66f6f38ed325043183970bc770fa

One finding: **S1-134/S1-223/S1-321/S1-324, R1-8.** Research supplies `Clipped Claim was founded in 2014`, clipped from `Clipped Claim was founded in 2014 and 2015.` The complete conflicting sentence is served through search in this same build, yet the API returns 2014 known with the incomplete prefix as its citation. The whole original sentence supports neither year, so the field must be unknown.

Reproduce: `SECOND_READER_CASE=research-clipped-sentence-r1-8 timeout 1000 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-3befa4f40b1e/stage-1`. **42 checks, 40 passed**, two assertions from one cause. The corrected oracle self-check and actual-served-full-sentence checks pass. This supplemental probe was added while the full run continued; full-run counts below exclude it.

Reported failures first: **425/425 passed**. Quick 500 answers finish the build in 7.883 seconds. Two failed free status polls retain one research start, 39 actual / 39 reported units and supported year 2014. Both previous findings are fixed.

Every earlier finding next: **12,739/12,739 passed**. Whole stage afterward: **20,375/20,375 passed**. Live deadline/minimum waits, cancellation/queued cost, fifty builds, reset overlap, accepted lost answers, child stopping, API/error/idempotency/clock/migration and the existing evidence/Appendix A cases pass. The full fifty-build maximum is 5.381 seconds, all six fields known; provider maximum 1.697 seconds is recorded with the fast-premise qualification. Service cgroup 2 CPU / 3 GiB, peak 95.0 MiB, no OOM.

Commands/results and source review: `ledger/stage-1-audit-3befa4f40b1e.md`. Re-run every probe with `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-3befa4f40b1e/stage-1`. It builds and starts itself, requires no other argument, prints counts and exits nonzero on failure.

Reading check exits 0; audit exits 1 with S1-012/013/121/133/134/223/321/324 open. These eight rows reflect one citation/support defect; the other 289 obligations pass on this exact revision. Peer verdict read only after own probes. No product code or tests edited; probes remain private until all stages close.
