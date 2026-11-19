VERDICT: BLOCK
REVISION: 7eac8a66d4239f624bac647bfebd084257121341

Two findings:

1. **S1-224:** quick provider errors exceed the ten-second build bound. With the documented mock 500 fault and no added latency, a fresh service using the local SDK hostname ends failed at **24.212 seconds**, every provider response at most **0.005 seconds**, spent 0. Seven backoff sleeps total 23.9375 seconds. The 200-second retry window permits all eight attempts; the 285-second absolute bound does not meet the separate ten-second requirement. The earlier combined and later full run reproduce it. Failure state and cost are correct.

Reproduce: `SECOND_READER_CASE=fast-refusals-build-deadline timeout 1000 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-7eac8a66d423/stage-1`. Focused **952 checks, 951 passed, one failure**. The runner builds and starts itself on an internal network with 2 CPU / 3 GiB.

2. **S1-014/S1-245/S1-277/S1-284:** a free status-poll error refunds an accepted 25-unit research start. Refuse only two status polls with 500, then answer normally: three actual starts cost 75, plus 14 other units = **89 actual units**, while the dossier reports **39**. This violates the 80-unit build cap and cumulative reporting. Reproduce: `SECOND_READER_CASE=research-poll-refusal-preserves-start-cost timeout 1000 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-7eac8a66d423/stage-1`. **178 checks, 176 passed**, two assertions from one cause. A one-poll diagnostic likewise reports 39 versus 64 actual units. Citation and year recovery work; this is accounting across the research lifecycle.

Reported reset/lost-response findings first: **11,638/11,638 passed**. R1-9 answer counting, needed-extract recovery and reset/import cancellation pass. Whole suite afterward: **20,932 checks, 20,930 passed**. One additional failed assertion records the fifty-build latency premise (provider maximum 2.676 seconds), a setup qualification rather than a product defect; all fifty builds still complete by 4.758 seconds with six known fields. The fifty-build service peaks at 96.8 MiB under its 2 CPU / 3 GiB cgroup, with no OOM. Live deadline and dispatch accounting pass. Full details: `ledger/stage-1-audit-7eac8a66d423.md`.

Reading check exits 0; audit exits 1 with S1-014/224/245/277/284 open. The other 292 normative/ruled obligations have passing evidence for this revision. Peer verdict read only after own probes. No product code or tests edited; probes remain private.
