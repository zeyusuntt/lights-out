VERDICT: BLOCK
REVISION: d5b3d5b94d938f30847c7db818f6582785fb2b39

# Second-reader, stage 1, round 3

The accounting and live-deadline findings are fixed. One confirmed product failure remains: **S1-224—fast-provider builds exceed ten seconds under the supported concurrency.** R1-8 has resolved the excerpt-boundary reading, with passing evidence.

With 50 distinct companies researched concurrently, every provider response is at most **0.555 seconds**, but **36 builds take over 10.3 seconds**, the slowest **16.737 seconds**. Every company has six supported facts on a single ordinary page, and all 50 finish with six known fields. The reproduction uses a normal mock-host URL, 2 CPU/3 GiB, and an internal network. A separate SDK-host run and the full suite reproduce it too.

```sh
fclone d5b3d5b94d938f30847c7db818f6582785fb2b39 /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-d5b3d5b94d93-fast
SECOND_READER_FAST_NONLIVE=1 SECOND_READER_CASE=fifty-distinct-builds-fast-providers /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-d5b3d5b94d93-fast/stage-1
```

The runner builds and starts the folder, measures provider and build durations, and exits 1 in about 20 seconds with `fast providers complete every build within ten seconds`. The default runner also includes the SDK-host form. The shared 32-operation provider semaphore queues planned work past the ten-second bound; provider responses themselves remain subsecond.

Validation in the requested order:

- Reported queued-accounting case first: **336/336 pass**, ready at 286.044 seconds, reported cost **37 = actual 37**, no extracts or older follow-up requests dispatched.
- Live deadline next: **637/637 pass**, ready at 285.041 seconds, cost 39 including two interrupted dispatched calls; minimum wait/gathering behavior retained.
- Whole suite afterward: **8,644 checks, 8,643 pass, one performance failure**. The full run again passes the 300-second bound and queued refund.
- Focused ordinary-mock repetition: **689 checks, 688 pass, same performance failure**; 1,150 provider requests measured, all below 0.56 seconds.
- Clean fclone/fserve and health pass. No product code/tests edited. Verifier PASS was read afterward; the independent failure remains.

**S1-321/S1-324 resolved by R1-8:** A citation is a complete original A.1 prose sentence, copied except whitespace collapsing, and 1..500 characters. Clipped substrings are invalid; longer sentences do not make a field known. The candidate's unknown for `Reading28 was founded in 2014 and 2015.` is correct. Both ledger rows retain their alternative readings and now carry the chosen ruling. An updated focused sample/Appendix A/boundary run passed 5,446/5,446 checks on this exact revision.

The `citation-sentence-boundary-reading` case now enforces the ruling: the prefix is structurally rejected and the conflicting complete sentence keeps the field unknown. The initial 24-check neutral observation remains historical evidence of the question, not the chosen rule.

Full commands, source-review scope, report paths and evidence are in `ledger/stage-1-audit-d5b3d5b94d93.md`. Probes remain private until all stages close.

Reading validation exits 0 (379 units, 290 normative, 7 ambiguous). Audit validation exits 1 with only S1-224 failing. All other normative and ruled ambiguous rows have passing exact-revision evidence.
