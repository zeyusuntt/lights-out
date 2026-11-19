# Independent review 2, 2026-11-07

Same reviewer, setup and prompt as review 1 (Codex gpt-6.1-sol, high, read-only), on the code after pf-02. Raw output: `scratch/review-2.out`. 16 findings, all real. Tests: 49 pass; 6 of the new ones failed before the fixes (`scratch/r2-red.log`).

| # | Finding | What changed |
|---|---|---|
| 1 | A quota pause could outlive the guard's 48-hour timeout | Guard has no fixed timeout; it exits once the final report is out and nothing is paused |
| 2 | Starting a new run deleted the previous room, which the submission needs | `--submission` runs: a new run refuses to archive until the download is marked done, and never deletes that room |
| 3 | Seats from another checkout could commit elsewhere | `make-seats` refuses a seat that runs from another checkout |
| 4 | A failed room deletion let old seats write into the new run | Abort before moving anything |
| 5 | The next stage copied unverified edits from the working tree | `stage-copy` copies the accepted commit; acceptance refuses a dirty stage folder |
| 6 | Backported stages kept a stale acceptance | Protocol: reopen, re-verify, re-accept, replace the record |
| 7 | Tools reported success after failures | Exit codes propagate |
| 8 | Killing `with-slot` left its Docker job running | The child dies with its slot; `fserve` cleans up on timeout |
| 9 | `fstop` hid failed removals | Reported, kept in the record, non-zero exit |
| 10 | Every handoff told every seat to read every stage | Only the foreman reads ahead |
| 11 | Mandate, protocol and checker disagreed on which units need evidence | Normative and ambiguous do; informative don't |
| 12 | The first seal had no time bound | About 45 minutes, then pre-code amendments; representative orderings |
| 13 | The guard refused `git diff -- stage-2/rebase/...` | Parses the git subcommand |
| 14 | The guard refused a seat's own suite run from the kit directory | Refuses only relative paths into the kit's tests |
| 15 | Duplicate ledger rows could hide a failing unit | Refused |
| 16 | Sealing a missing or empty folder succeeded | Needs test files and a `run.sh` |
