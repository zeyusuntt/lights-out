# Independent review 1, 2026-11-06

Reviewer: Codex (gpt-6.1-sol, high), read-only, given the code and the precedent's rules, no conclusions from me. Raw output: `scratch/review-1.out`. 21 findings.

| # | Finding | Call | What changed |
|---|---|---|---|
| 1 | Second-reader can't write its outputs | Overstated: pf-01 ran, because the writable roots were in a config outside the repo. Real as a reproducibility gap | Config template committed, installed by `make-seats` |
| 2 | An idle stall has no trigger; INCONCLUSIVE undefined | Real, the most dangerous | Timekeeper seat rings the foreman; INCONCLUSIVE has a defined path |
| 3 | `with-slot fserve` deadlocks | Real, reproduced by a failing test | Slots nest |
| 4 | Package replaces the official room file | Real | `--room-json`; the CLI export is labelled rehearsal only |
| 5 | Product-user never gets requirements | Real; the foreman improvised in pf-01 | Stages open to product-user |
| 6 | `accept-check` skips the product-user unless asked | Real | `--ui` or `--no-ui` required |
| 7 | Acceptance doesn't read the check's claim | Real | `--report` validated: claim, revision, isolated mode, no overshoot |
| 8 | Slot allocator can delete a live lock | Real | OS-held locks |
| 9 | Guard misses `cd` and broad searches; builder could read committed suites | Real | Per-segment check; builder refused other seats' tests; suites committed only after the last stage |
| 10 | Acceptance can consume uncommitted evidence | Real | Refused |
| 11 | Seal not compared with the suite in use | Real | `seal --verify` in acceptance; additions require an amendment |
| 12 | `fserve` leaves resources on failure | Real | Cleaned up |
| 13 | `make-seats` doesn't update the runtime | Real | Model updated with instructions |
| 14 | Guard path is absolute | Real | Placeholders filled at install |
| 15 | Dispatch and scoring hide failures | Real | Exit codes propagate |
| 16 | Retest rule contradicts one verdict | Real | One consolidated verdict |
| 17 | Product-user may block on taste | Real | Broken screens block; taste is a note |
| 18 | Guard rejects commit messages saying "push" | Real | Quoted text ignored |
| 19 | `fcommit` can print another seat's hash | Real | Lock covers commit and hash |
| 20 | Fault audit credits a failing baseline | Real | Baseline must pass; otherwise marked invalid |
| 21 | Relative package path | Real | Made absolute |

Tests: `factory/tests/`, 40 pass. 13 of them failed before the fixes (`scratch/tools-red.log`), including the deadlock.

Timekeeper wake tested end to end in a throwaway room: its TICK woke the foreman, which replied. Not verified yet: all of this in a live run. tk-01 is the first run on the fixed tooling.
