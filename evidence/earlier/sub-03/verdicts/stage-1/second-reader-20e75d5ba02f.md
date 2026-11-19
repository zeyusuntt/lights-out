VERDICT: BLOCK
REVISION: 20e75d5ba02fceddfb7ef9f0ea23c3278e6efc34

One finding: **S1-133/S1-321/S1-324, R1-10**. The API asserts funding of $1 with `Fetchable Funding raised $1.`, clipped at the decimal point from `Fetchable Funding raised $1.5 million.` The build does not hold the full page, but an independent WebRouter extract obtains it immediately for one unit. The build spent 49 units and has budget room. R1-10 permits the fallback only when full text cannot be obtained; that condition is false. The claim and citation are unsupported.

Reproduce: `SECOND_READER_CASE=research-fetchable-source-r1-10 timeout 1000 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-20e75d5ba02f/stage-1`. **44 checks, 42 passed**, two assertions from one cause. Both independent-extract verification assertions pass. The helper runs after the dossier completes; its one unit is excluded from build spending. The probe permits any outcome that rejects the unsupported $1 claim and uses a valid citation. It does not prescribe an exact replacement value.

Reported held-text prefix first: **37/37 passed**. Truly unavailable terminated/unterminated research cases pass. Full suite afterward: **20,605 checks, 20,603 passed**, only the same two fetchable-source assertions fail. All prior timing, cost, reset, lost-answer, concurrency and API/evidence regressions pass. Fifty builds finish by 5.105 seconds with six known fields; provider maximum 1.812 seconds is qualified. Cgroup 2 CPU / 3 GiB, peak 95.8 MiB, no OOM.

Diff limited to evidence.py/text.py plus a builder test filename; gateway/ledger/pace/build plan unchanged. Full commands/source explanation: `ledger/stage-1-audit-20e75d5ba02f.md`.

Reading check exits 0; audit exits 1 with S1-012/013/121/133/321/324 open from this one finding. The other 291 obligations pass on this exact hash. Peer verdict read only after all own probes. No product code or tests edited; probes remain private.
