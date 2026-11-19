# FACTORY

Lights Out is five model seats and one script sharing a Band Desktop room. One human message starts a run, and nobody types in the room after it. The verifier writes its acceptance tests from the specification and seals them before any product code exists; tests it adds later are labelled post-seal additions and re-sealed. A second model family numbers every sentence of the specification and has to show passing evidence for each one that states a requirement. A stage closes only when a program, `accept-check`, confirms that every verifying seat passed the same commit.

This repository holds run sub-05 (room `b62e27db-6fe2-4a98-98bb-41ddd09f422c`, dispatched 2026-11-18 16:00 UTC). The mandates in `mandates/` and the tooling in `factory/` are the versions that run was dispatched with, by the operator's record: `evidence/factory-revision.txt` names the commit of the factory's own (private) repository they come from, with its time against the dispatch, and `evidence/mandate-history.patch` times every mandate change to the second. In this run the foreman's mandate would have stopped the line at the fifth blocked round of a stage (no stage reached it; the most was three), and the builder, verifier and second-reader checked a stop in the middle of an operation wherever the specification required something to survive one. Changes made to the mandates after a run are described under [Catching bad work](#catching-bad-work-and-recovering), and `evidence/mandate-history.patch` holds every mandate change since kickoff.

## Seats

| Seat | Harness, model, effort | Owns | Never |
|---|---|---|---|
| foreman | Claude Code, claude-opus-5-5, medium | handoffs, rulings on ambiguous sentences, acceptance, the final report | writes product code or tests; asks the human anything |
| builder | Claude Code, claude-opus-5-5, medium | each stage folder: service, its own tests, Dockerfile, RUN.md | reads the kit's check sources or another seat's tests; accepts its own work |
| verifier | Claude Code, claude-opus-5-5, medium | an acceptance suite written from the specification and sealed before any code; verdicts on exact commits; planted faults against its own suite | sees product code before sealing; edits product code |
| second-reader | Codex, gpt-6.1-sol, high | a numbered ledger of every sentence and what it requires; its own black-box probes; evidence for every sentence on the exact commit | edits anything but the ledger, its probes and its verdicts |
| product-user | Claude Code, claude-sonnet-5-5, medium | a real-browser walk of every state the specification names, at 375 px and desktop width | reads source |
| timekeeper | none: a Python script, no model | wakes the foreman if the room has been silent longer than any command may run | decides anything; writes to the repository |

Every seat also follows `PROTOCOL.md`: message formats, who owns which path, how a commit names its revision. A commit hook in `factory/githooks/` enforces the ownership table for every seat. The Claude Code seats also run a read guard, `factory/hooks/guard.py`, that refuses what the protocol forbids, such as the kit's test sources or a later stage's specification. The Codex seat has no hook; it writes only under the run's workspace (its sandbox, `factory/settings/codex-config.toml`) and gets the same read rules as instructions.

## A stage

1. The foreman opens the stage to the second-reader and the verifier at the same time, pasting the complete specification into the handoff. In sub-05 the stage-1 opening was 36,918 characters as sent (36,951 in `room.json`, where the redaction lengthens each home path by three). The second-reader numbers every sentence (`funits`) and writes what each requires and how to observe it. The verifier writes its suite from the text alone and posts its digest (`seal`).
2. The foreman rules on every sentence the ledger marks ambiguous. It then opens the stage to the builder and the product-user with the specification, the ledger and the rulings. The verifier may extend its suite for anything the ledger found, before any code exists, and posts the new digest.
3. The builder starts the folder as an exact copy of the accepted previous stage (`stage-copy`) and offers one commit as `CANDIDATE`.
4. Each verifying seat makes its own clean clone of that commit and sends one verdict with every problem it found. The foreman merges the blocking findings, with their reproductions, into one `FIX` for the builder. It never forwards test sources.
5. The foreman runs the kit's check on a clean clone, then accepts only if `accept-check` exits 0. It refuses unless the seal predates the stage's first product commit and still matches the suite, every verdict on that hash is a committed PASS, the ledger shows passing evidence for every sentence on that hash, and the kit's isolated report claims the stage. An accepted folder never changes again; the commit hook refuses it.
6. If one finding returns twice, the foreman orders a change of approach. After a set number of blocked rounds it records `BLOCKED` and stops opening stages. Accepted stages stand.

## Stand it up

You need Band Desktop and its `band` CLI, signed in; Claude Code and Codex, signed in; Docker; `timeout` on the PATH; and the event's kit (`band-ai/sf-buildathon-2026`; this run used commit `704324580f8a`), prepared as its participant guide (`docs/participant-guide.md`) says (a Python 3.12 virtual environment with `harness/requirements.txt` and Playwright's Chromium). The first isolated check builds the kit's runner image, so time it once before a real run.

```sh
factory/bin/make-seats            # create or update the seats; each seat's instructions are its mandate plus PROTOCOL.md
factory/bin/new-run <run-id> <track> --kit <kit dir> --submission --cpus 2 --memory 3g
factory/bin/dispatch --print      # read the one human message before it goes
factory/bin/dispatch              # send it; refuses a second send in the same run
```

Those four commands start a run without its helpers. For a real run use `factory/bin/launch <run-id> <track> --kit <kit dir> --submission --cpus 2 --memory 3g` (the kit directory's path must not contain spaces: `launch` passes its options on unquoted), which runs the same steps and then starts the watchdog, the timekeeper and a meter guard that pauses the seats near the plan's usage limit (`factory/bin/launch`, last lines). `new-run` only warns when a seat has no running worker, and `launch` goes on to the one dispatch anyway, so read that output, or run the four commands by hand, before the message goes out. Every tool answers `--help` without acting. After the run, from the run's workspace, `factory/bin/score-run` scores it with the untouched kit on a fresh clone, and `factory/bin/run-stats` prints the measured facts this document quotes. `score-run` prints the chain and then exits 1 until the run is packaged, because the kit's offline check also wants the mandates and `room.json`, which `factory/bin/package-run` adds; its `chain:` line is the score. Neither works on a clone of this repository, which has no run workspace; to score the clone, use the kit's own command (Run a stage, in README.md).

For another problem in the kit's format (a track folder whose `spec/` holds up to four `stage-N.md` files; `dispatch` reads them from there and `score-run` scores stages 1 to 4) you change two files and no mandate: `factory/templates/dispatch.md` (the task message) and `factory/templates/track-rules/<track>.md` (the event's rules for that track, sent inside the dispatch). The machine-specific parts are few and named: the seat launchers `factory/bin/seat-claude` and `factory/bin/seat-codex` (the Codex binary's path, per-seat settings), the seats' commit identity in `factory/settings/operator.env`, the operator identity `factory/bin/new-run` sets on the result repository, and the Claude CLI path in `factory/bin/plan-meter`. Change those for your machine. `factory/tests/` holds the tooling's tests: `python -m pytest factory/tests`.

## Generic

The mandates say how a seat works: what it owns, how it takes work, when it rejects. Nothing in them names this track, and three checks enforce that:

- a tooling test fails if a mandate contains any of the track's provider or product words (`factory/tests/test_tools.py`, `test_the_dispatch_carries_the_tracks_event_rules_and_mandates_do_not`);
- the kit's own vocabulary scan (`harness check`, gate 4) passes on `mandates/` (its output on this repository is in `evidence/harness-check.txt`);
- every rule specific to the track sits in `factory/templates/track-rules/dossier.md`, which reaches the seats only through the dispatch.

Before the event the same mandates, in earlier versions, ran three other problems: a shared counter (six runs), a payments service (two runs) and a booking service the factory had never seen (one run, four of four stages). Records are in `rehearsals/RESULTS.md`.

## Effective: how far it got

Runs on this track, all dispatched with one human message into a fresh room and a fresh, empty repository. "Shipped checks" is the kit's isolated run on a fresh clone with the untouched kit, after the run ended.

| Run | Dispatched (UTC) | Accepted by our gate | Rounds per stage | Shipped checks, fresh clone | Wall clock |
|---|---|---|---|---|---|
| sub-01 | 2026-11-13 18:11 | stage 1 (`e391dd0`). Stage 2's `00c0c22` passed all three verifying seats but our own tooling refused it (below); stages 3 and 4 never opened | 2, 5 | `stage-1/` 122/122; `stage-2/` 122/122, 12/12: chain stage 2 | 272 min |
| sub-02 | 2026-11-16 21:27 | stages 1 to 3 (`a34bf56`, `e7ed787`, `09e5770`). Stage 4 blocked after five rounds on a real defect (below) | 2, 4, 2, 5 | `stage-1/` 122/122; `stage-2/` adds 12/12; `stage-3/` adds 9/9; `stage-4/` adds 10/10: chain stage 4 | 553 min |
| sub-03 | 2026-11-18 04:19 | none. Stage 1 blocked after seven rounds, all of them the second-reader's | 7 | `stage-1/` 122/122: chain stage 1 | 315 min |
| sub-04 | 2026-11-18 09:54 | none. Stage 1 blocked after seven rounds, all of them the second-reader's | 7 | `stage-1/` 122/122: chain stage 1 | 361 min |
| sub-05, this repository | 2026-11-18 16:00 | stages 1 to 4 (`a8789dc`, `bc19abf`, `cd24f51`, `a7228733`) | 4, 2, 1, 3 | `stage-1/` 122/122; `stage-2/` adds 12/12; `stage-3/` adds 9/9; `stage-4/` adds 10/10: chain stage 4 | 419 min |

The shipped checks are a sample: 57%, 6%, 4% and 8% of the stage 1 to 4 suites (the kit's participant guide, "Do not write to the tests"). They could not tell our candidates apart. All 10 candidates the foreman sent for verification in sub-05 passed every shipped check of their stage, in isolated mode, on a clean clone, and so did all 20 in sub-01 and sub-02. The foreman ran those checks itself on each candidate. The reports are in `checks/foreman-*/report.json` for the run in this repository and in `evidence/earlier/<run>/checks/` for earlier runs. In sub-05 the verifying seats blocked 6 of the 10. Each block named a sentence of the specification, and each fix came back through the room as a new commit:

| Stage | Blocked revision | Blocked by | What the shipped checks never asked | Fixed in |
|---|---|---|---|---|
| 1 | `52f4f87` | second-reader (the verifier had passed it) | a domain written with an encoded slash got past validation; a fixture could create an account whose returned ID was longer than 64 characters | `b9d46b6`, offered 4 min after the fix request |
| 1 | `b9d46b6` | second-reader (the verifier had passed it) | valid research prose that begins `Profile:` was left unknown; a research citation was longer than the 500-character limit | `d07442d`, offered 4 min after the fix request |
| 1 | `d07442d` | verifier, and the second-reader from its own probes before it read the verifier's verdict | a supported field stayed unknown when its supporting span sat late in a sentence of about 800 characters. The long-sentence handling had now failed twice, so the foreman ordered a change of approach | `a8789dc`, offered 5 min after the fix request, accepted |
| 2 | `3cf3cef` | second-reader (the verifier and the product-user had passed it) | after a slow research response, an extract that a provider had refused with a 429 was given up instead of retried | `bc19abf`, offered 4 min after the fix request, accepted |
| 4 | `b928822` | verifier; the second-reader reproduced it with a company of its own after reading the verifier's verdict, and found three more, one of them only after a restart (see below) | a batch skipped research it could still afford and left a field unknown | `010b35a`, offered 4 min after the fix request |
| 4 | `010b35a` | second-reader; the verifier confirmed it after the ruling the second-reader's question led to | a batch that could not afford its whole plan spent its budget on research before rendering pages it could afford, and lost a field | `a7228733`, accepted |

"Offered" is the builder's `CANDIDATE` message in the room; its commit is a minute or two earlier. Every BLOCK verdict, with links, is listed under [Measured](#measured-the-submitted-run). Earlier runs' verdicts are in `evidence/earlier/<run>/verdicts/`.

The sealed suites reach far past the shipped sample. The verifier's suite for `stage-4/` ran 306 tests covering stages 1 to 4, where the kit ships 153 checks for the same folder (122, 12, 9 and 10). Each stage's suite carries the previous one forward; 35 of the 306 were added at stage 4, against the 10 shipped checks for stage 4.

### Evidence on the accepted commits

The second-reader numbers every sentence, heading, code block and table row of each specification (`ledger/stage-N.jsonl`) and records the evidence for each on exact commits. `accept-check` refuses a stage while any normative or ambiguous unit lacks passing evidence on the commit being accepted.

| Stage | Units | Normative or ambiguous | With passing evidence on the accepted commit | Of those, from reading the source alone |
|---|---|---|---|---|
| 1 (`a8789dc`) | 379 | 298 | 298 | 11 |
| 2 (`bc19abf`) | 188 | 144 | 144 | 14 |
| 3 (`cd24f51`) | 150 | 127 | 127 | 0 |
| 4 (`a7228733`) | 125 | 106 | 106 | 0 |
| All | 842 | 675 | 675 | 25 |

Most of that evidence is the second-reader's own black-box probes; the rest is the verifier's suite, the kit's check, the product-user's walks, and, for 25 units that no request can observe from outside, a reading of the source.

The verifier also tests its own suite. On the first revision of each stage that passes it, it plants faults one per throwaway copy of the service and runs the frozen suite against each. A fault the specification forbids that survives is a hole, closed with a test labelled post-seal (`verdicts/stage-N/verifier-<hash>.md`, "Fault planting"):

| Stage | Faults planted | Caught at once | Holes, closed with a new test | Equivalent (no observable difference) | Outside the specification |
|---|---|---|---|---|---|
| 1 | 8 | 5 | 2 | 1 | 0 |
| 2 | 9 | 6 | 2 | 0 | 1 |
| 3 | 7 | 6 | 0 | 1 | 0 |
| 4 | 7 | 6 | 1 | 0 | 0 |
| All | 31 | 23 | 5 | 2 | 1 |

Stage 2 used nine copies, one more than the mandate's eight.

### Stage 4

Stage 4 was accepted on `a7228733` after three rounds and 162 minutes. The product-user passed every round. The verifier and the second-reader blocked the first two:

1. `b928822`: the verifier found that a batch skipped a research run it could still afford and left a field unknown (V4-1). After reading the verifier's verdict, the second-reader reproduced the finding with a company of its own (a 49-unit batch skipped research that a 38-unit build completes, S4-F4); from its own probes it found three more: a corroboration time carried over when a scalar value changed (S4-F1), unused headroom for lineage hid two evidence pages the build could afford (S4-F2), and refused calls that had completed came back as 35 charged units after a restart (S4-F3). The second-reader found S4-F3 with a probe that stops the service in the middle of an operation and starts it again, which its mandate asks for wherever the specification requires something to survive a restart. While that audit was still running, the foreman ruled on refused attempts across a restart (ruling R4-8), and the builder committed the fix early (`79b12c0`).
2. `010b35a`, built on `79b12c0`: the fixed reserves are gone, and every call is decided by need; research, for example, runs whenever its 25 units fit what is left of the batch's budget. All five earlier findings passed their retests first. The second-reader then found a new case: a batch that could not afford its whole plan spent its budget on research before rendering pages it could still afford, and lost a field (S4-F5). It asked the foreman how the specification reads there; the foreman ruled (R4-9), and the verifier added a test under that ruling and confirmed the defect (V4-2).
3. `a7228733` renders the pages it has already found before it spends on research when the remainder cannot cover the plan. The verifier passed 306 of 306 tests, the second-reader 305 of 305 probes with its ledger audit exiting 0, and the product-user passed it. `accept-check --ui` exited 0.

The verifier's restart checks passed on every stage-4 revision: it killed the service with `docker kill` while it was idle and while a refresh and a batch were running, then started it again. Interrupted builds ended within 10 seconds of the service reporting healthy, a failed end left every field unchanged, and the units already billed were still counted in the dossier and the batch. The second-reader's restart probe failed once: on `b928822`, calls the provider had refused came back after a restart as 35 charged units (S4-F3 in its verdict). It passed on `a7228733`, with all 11 refused calls still at zero after the restart.

Those checks exist because of sub-02, an earlier run on this track. Its stage 4 stopped after five blocked rounds, the last on a real defect: a graceful `docker stop` during a build lost the units of the provider calls in flight, so one build recorded 52 units against 84 billed, over the 80-unit cap (`evidence/earlier/sub-02/verdicts/stage-4/verifier-8dcb475512da.md`, finding F4). After that run the builder, verifier and second-reader were told to check a stop in the middle of an operation wherever a specification requires something to survive one. In this run that check found S4-F3 and passed on the accepted revision.

## Catching bad work, and recovering

What stops a bad stage, in the order it acts:

- Tests before code. The verifier seals its suite before the stage's first product commit, and `accept-check` refuses a stage whose seal is later or no longer matches. The builder never sees a test it is judged by.
- Two independent readings. The second-reader runs another vendor's model in its own sandbox and writes its own probes. It reads the verifier's verdict only after its probes have run, and may not change a finding to agree.
- Exact commits. Every verdict names a full hash, and each seat builds its own clean clone of it; no seat takes a working tree as evidence.
- One fix list per round. The foreman waits for every verdict and sends one `FIX`, so the builder fixes everything at once instead of one finding per round.
- Change of approach. When a finding returns twice, the foreman tells the builder to change the approach. In sub-05 stage 1 the long-sentence handling failed twice; the foreman told the builder to replace it rather than tune it (`plan/fix-1-3.md`), and the next candidate was accepted. In sub-02 stage 2 the same order ended a finding that had survived two fixes.
- Stop the line. After a set number of blocked rounds the foreman records `BLOCKED` and stops opening stages, without asking the human for a decision.
- Acceptance is checked by a program. `accept-check` reads the committed verdicts, the seal, the ledger audit and the kit report for one hash, and the foreman accepts only when it exits 0. It checks the records; the judgement is in the verdicts.

The factory also caught its own defects. Each fix was made after the run, in the factory's own repository, with a regression test in `factory/tests/`:

- In sub-01 the builder created `stage-2/` as a copy of accepted stage 1 before the stage-2 seal. `seal` counted that copy as product code, so `accept-check` refused stage 2 although all three verifying seats had passed it (`00c0c22`). The foreman recorded `BLOCKED` as its mandate says and stopped; stages 3 and 4 never opened. `seal` now treats a commit that only copies the frozen previous stage as no product code (`factory/bin/seal`; test `test_a_copy_of_the_previous_stage_made_before_the_seal_is_not_product_code`). In sub-05 the builder again committed each stage copy before the seal, at all three openings, and each seal recorded no product commits.
- Archiving a run stopped the seat workers, which cost sub-01 two minutes at the start and broke sub-02's first setup. `new-run` now restarts every worker, the timekeeper first, before opening the room (`factory/bin/new-run`).
- A probe file in sub-01 held a test placeholder that the kit's credential scan flags. `fpublish` now leaves such a file out (`factory/bin/fpublish`; test `test_fpublish_leaves_out_files_the_kit_would_read_as_credentials`).
- The timekeeper missed two final reports, one that began with mentions and one written as a markdown heading; in sub-03 the operator marked the run finished by hand. It now reads the foreman's text without mentions or heading marks (`factory/bin/timekeeper`; test `test_final_report_is_the_foremans_message_that_opens_with_it`). In sub-05 it found the final report itself.
- For sub-03 and sub-04 the foreman's mandate stopped the line at the seventh blocked round while `PROTOCOL.md`, which every seat reads, still said the fifth. A tooling test now fails when the two disagree (`test_the_protocol_and_the_foreman_state_the_same_round_cap`).

Mandate changes between runs, each made after a run and never during one (the diffs are in `evidence/mandate-history.patch`):

- After sub-01: change approach when a finding returns twice instead of three times; the builder treats a saving that leaves out evidence as a defect; the verifier reports units spent per supported result in every verdict where calls are priced; the product-user walks responses that arrive out of order or never arrive, at 375 px.
- After sub-02, whose stage 4 stopped on a graceful `docker stop` that lost the units of the provider calls in flight: the foreman stops the line at the seventh blocked round instead of the fifth; where a specification requires something to survive a stop or restart, the builder makes it durable before the action that depends on it, and the verifier and second-reader stop the service in the middle of such an operation. The rule is conditional on the specification, so no stage is built around a later one.
- After sub-04: the stop went back to the fifth blocked round, and the durability rule stayed. Under the seventh-round stop, sub-03 and sub-04 each stopped at stage 1 after seven blocked rounds, every block the second-reader's and each a real defect; sub-02 had accepted the same stage in two rounds. Only one run has used the restored stop, the one in this repository, which is too few to say the stop made the difference.

## Measured: the submitted run

Dispatch 2026-11-18 16:00 UTC; final report 22:59 UTC; 419 min from dispatch to final report. Human messages in the room: 1.

| Stage | Ledger ready | Tests sealed | First candidate | Candidates | BLOCK verdicts | Time | Accepted revision | Shipped checks, fresh clone |
|---|---|---|---|---|---|---|---|---|
| 1 | +7 min | +12 min | +31 min | 4 | 4 | 107 min | `a8789dcd65a1` | 122/122 (claims its stage) |
| 2 | +11 min | +13 min | +27 min | 2 | 1 | 92 min | `bc19abf8cbde` | 122/122, 12/12 (claims its stage) |
| 3 | +6 min | +9 min | +28 min | 1 | 0 | 53 min | `cd24f51fb21b` | 122/122, 12/12, 9/9 (claims its stage) |
| 4 | +15 min | +10 min | +30 min | 4 | 4 | 162 min | `a7228733bd42` | 122/122, 12/12, 9/9, 10/10 (claims its stage) |

Times are from the stage's opening message. Shipped checks: the kit's isolated run on a fresh clone of the final repository.

| Seat | Commits | Room messages | Tool calls shown in the room |
|---|---|---|---|
| builder | 24 | 17 | 304 |
| foreman | 80 | 46 | 205 |
| product-user | 6 | 6 | 69 |
| second-reader | 16 | 18 | 492 |
| verifier | 11 | 23 | 233 |

BLOCK verdicts:

- stage 1, second-reader, on `52f4f877c4cf` at 16:54 UTC: [`verdicts/stage-1/second-reader-52f4f877c4cf.md`](verdicts/stage-1/second-reader-52f4f877c4cf.md); room message `0353d0b7-fd91-48b7-ad0e-131dff85834a`
- stage 1, second-reader, on `b9d46b6fd9ea` at 17:18 UTC: [`verdicts/stage-1/second-reader-b9d46b6fd9ea.md`](verdicts/stage-1/second-reader-b9d46b6fd9ea.md); room message `479b7355-04a5-4971-9d67-2d1775f39fdf`
- stage 1, verifier, on `d07442da2a50` at 17:29 UTC: [`verdicts/stage-1/verifier-d07442da2a50.md`](verdicts/stage-1/verifier-d07442da2a50.md); room message `348ac083-cb96-4e50-be85-e1d6ecb10f88`
- stage 1, second-reader, on `d07442da2a50` at 17:30 UTC: [`verdicts/stage-1/second-reader-d07442da2a50.md`](verdicts/stage-1/second-reader-d07442da2a50.md); room message `55f76e33-f55e-4d9b-84d9-839d286c97a0`
- stage 2, second-reader, on `3cf3cef0862c` at 19:03 UTC: [`verdicts/stage-2/second-reader-3cf3cef0862c.md`](verdicts/stage-2/second-reader-3cf3cef0862c.md); room message `e7b75471-7dee-4204-a9dd-3151ddc0227f`
- stage 4, verifier, on `b928822534e8` at 20:53 UTC: [`verdicts/stage-4/verifier-b928822534e8.md`](verdicts/stage-4/verifier-b928822534e8.md); room message `357fae33-024f-4dd6-baea-f807850ad12e`
- stage 4, second-reader, on `b928822534e8` at 21:56 UTC: [`verdicts/stage-4/second-reader-b928822534e8.md`](verdicts/stage-4/second-reader-b928822534e8.md); room message `66289f87-63c2-4ada-91af-c6bd9a89fb36`
- stage 4, second-reader, on `010b35ad7282` at 22:12 UTC: [`verdicts/stage-4/second-reader-010b35ad7282.md`](verdicts/stage-4/second-reader-010b35ad7282.md); room message `e77ee23c-6169-4386-aa2d-3a7d076fc804`
- stage 4, verifier, on `010b35ad7282` at 22:14 UTC: [`verdicts/stage-4/verifier-010b35ad7282.md`](verdicts/stage-4/verifier-010b35ad7282.md); room message `2a8089f6-d9e2-4fae-a1b2-83bd4dc0669e`

Spend at list prices, estimated: Claude seats about $72.72 from `band usage rooms` (builder $32.96, verifier $26.67, product-user $2.21, foreman $10.88); Codex seat about $104 from its session logs (69,125,552 input tokens, 68,211,712 cached, 525,855 output).

"Candidates" counts every `CANDIDATE` message. Ten of them went to the checking seats; the eleventh, stage 4's `79b12c0`, was superseded by the next revision before verification.

The Claude figure above, $72.72, is Band's list-price estimate for the four Claude seats in this room (`band usage rooms`): builder $32.96, verifier $26.67, foreman $10.88, product-user $2.21. It was read on 2026-11-19 at 04:04 UTC (`evidence/usage-20261119T0404Z.txt`), once Band had recorded each seat's session to the final report. The Codex figure, about $104, covers the second-reader seat at the assumed rate given under What the design costs. Over the run the Claude plan meter moved from 20% to 24% of the week.

## What the design costs

| Run | Wall clock, dispatch to final report | Claude seats, list-price estimate | Codex seat, estimate | Claude plan meter |
|---|---|---|---|---|
| sub-01 | 272 min (2 stages opened) | $44.24 | about $67 | 82% to 87% |
| sub-02 | 553 min (4 stages opened) | $84.36 | about $150 | 3% to 8% |
| sub-03 | 315 min (1 stage opened) | $26.63 | about $82 | 12% to 17% |
| sub-04 | 361 min (1 stage opened) | $34.13 | about $75 | 17% to 20% |
| sub-05, this repository | 419 min (4 stages opened) | $72.72 | about $104 | 20% to 24% |

Claude figures are Band's per-room estimates at list prices (`band usage rooms`) for the four Claude seats (foreman, builder, verifier, product-user), read hours after each run because Band records usage late. sub-05's read is `evidence/usage-20261119T0404Z.txt` (2026-11-19 04:04 UTC), taken once Band had recorded every seat's session to the end of the run: their last recorded activity is 22:56 to 22:59 UTC, and the final report 22:59:31. The plan meter, as the meter guard logged it during the run, is in `evidence/plan-meter.log`. Codex figures cover the second-reader seat: tokens from its session logs at an assumed rate (USD 10 per million input, 1 per million cached input, 50 per million output). We have not found a published rate for this model, so treat them as rough. In sub-05 the Codex seat read 69.1 million input tokens, 68.2 million of them cached, and wrote 0.53 million.

Where the time and money go:

- Reading before building. In sub-05 the builder received each stage 9 to 16 minutes after it opened, once the ledger, the seal and the rulings existed.
- Fixes are fast and audits are slow. In sub-05 the builder offered a fix 3 to 5 minutes after the fix request (its commit came a minute or two before that); in the last round it had the fix ready before the request. From a candidate to the fix request that answered it took 9 to 74 minutes, because the foreman waits for every verdict. The second-reader finished last in 4 of the 6 rounds that ended in a fix request, 1 to 63 minutes after the verifier.
- The second-reader is the most expensive seat (about $104 of about $177 for sub-05; the builder, the dearest Claude seat, came to $32.96) and it found the most. It issued 6 of the 9 blocking verdicts, and in three blocked rounds it was the only seat that blocked: stage 1 rounds 1 and 2, and stage 2. Without it, stages 1 and 2 would have been accepted with the defects in the table above.
- The two verifying seats overlap. Where both blocked the same round, they reported the same defect: once from separate probes, and twice where one seat confirmed the other's finding with its own reproduction. That costs a second audit, and one seat's miss does not pass a stage.

## Agent Teamwork

- Handoffs carry the whole task. Every stage opening pastes the complete specification. The builder's opening also quotes the rulings and names the commit of the ledger. Fix requests name each finding and point to the verdict file and the committed fix plan (`plan/fix-<stage>-<round>.md`), which holds the reproductions.
- The work is spread across seats. Commits and room messages per seat for the submitted run are in the table under Measured. The foreman commits most because it records every verdict and ruling; the builder is the only seat that commits under `stage-N/`.
- Review changed the work. Every block produced a new commit that fixed the named sentence, and the next round checked that commit. Each stage's last commit is its accepted revision.
- Seats address each other by `@handle`. In sub-05's room the foreman and each of the four other model seats exchanged messages in both directions, four reciprocal pairs counted from the room log. For the run in this repository, `harness check` confirms gate 2 on `room.json` (`evidence/harness-check.txt`).
- No human input after the dispatch. Each run's room has exactly one human message, the dispatch. A tooling test checks that only `dispatch` can post as the human; the watchdog and meter guard only stop or restart seats, and the timekeeper posts only as itself.

## Research economy

The kit's participant guide (Rubric, Research economy) judges spend "per correct field on a fixed stage-4 workload, compared with a fixed strategy benchmark". It publishes neither the workload nor the benchmark, so we cannot compare our figure with it. What we measured instead, through the verifier, is units spent per supported field on each accepted revision, with both counts. A supported field is one the verifier's own checks confirm as known or contested with a correct citation. Each run's verifier chooses its own workload, so figures from different runs are not comparable.

| Revision | Units for correct fields, verifier's workload | Builds |
|---|---|---|
| stage 1, `a8789dc` | 559 units for 86 of 86 supportable fields: 6.50 per field | 19 first builds, 27 to 34 units each |
| stage 2, `bc19abf` | 1,038 units for 92 of 92: 11.3 per field | 21 first builds, 36 to 63 units |
| stage 3, `cd24f51` | 1,132 units for 96 of 96: 11.8 per field | 22 first builds, 37 to 70 units |
| stage 4, `a7228733` | 1,302 units for 103 of 103: 12.6 per field | 24 first builds, 38 to 74 units |

Each row comes from the verifier's verdict on that revision (`verdicts/stage-N/verifier-<hash>.md`, the Cost section). In this run the verifier's workload was the mock web's sample corpus of 12 companies together with the companies its own suite adds, which grew from 7 at stage 1 to 12 at stage 4 (19 to 24 first builds), so the per-field figures move with the workload as well as with the service. Every supportable field was correct in every row, and no build reached the 80-unit cap. Spend per field rose from 6.50 to 11.3 at stage 2, when the specification made the service read a page as a browser shows it, and rose by under a unit per field at each later stage as the specification added fields and lineage.

sub-02's verifier reported the sample corpus on its own, 9.01 units per field at stage 4. That figure and this run's 12.6 come from different workloads, so they cannot be compared, and neither is the judged workload.

How the service spends: it plans its searches once per build, reuses within one build any text a provider has already served, and reserves units before every call, so no build on these corpora passed the 80-unit cap. From stage 2 on, a page read as a browser shows it costs 3 units, against 1 for a plain extract. In stage 4 the verifying seats blocked three ways a batch saved units by leaving out evidence it could afford; the accepted design drops fixed reserves and, when the remaining budget cannot cover the whole plan, renders the pages it has already found before it spends on research (ruling R4-9, `a7228733`). Correctness came first in every ruling, and a cheaper build that left out a supported field counted as a defect.

## Before the event

The factory was rehearsed on other problems before kickoff. These numbers come from those rehearsals, not from this track; records and planted-fault patches are in `rehearsals/`.

- One agent, no room. The builder's model alone, given the same payments job, finished in 23 minutes for $6.04 and passed every shipped check. The verifier's sealed suite then failed it on 22 tests that a separate triage classed as product defects, written up as 20 reproductions (`rehearsals/solo-run-triage.md`), including money destroyed at the balance limit. The factory's service passed that suite. Two suites written from the specification outside the room, one by Codex and one by Amp running Claude, scored the two services about the same. The result shows how far the sealed suite reaches and says nothing about the hidden tests.
- Planted faults. On the unseen booking service, 24 faults planted one per copy by two model families: the shipped checks caught 3, the verifier's sealed suite 23, the second-reader's probes 22.

## What we tried that failed

- Band appends its own `--settings` flag, which replaced ours, so the first rehearsal seats ran without our guard. Settings now live in each seat's working directory, and every run is checked for signs of the leak.
- A watchdog that trusted Band's activity timestamp restarted busy seats 221 times in one rehearsal. It now judges silence from room events, waits 45 minutes, cools down, and gives up after six restarts.
- `fstop --all` matched containers by name prefix and removed another job's containers. It now reads the run's own record.
- The first guard refused a seat's own saved tool output, and the kit's interpreter.

## Limits

- The judges' full suites are not ours to see. Every number here comes from the shipped checks, our own seats' suites and probes, and outside suites written from the same text.
- Run-to-run variance is real. The same verifier wrote suites of 210, 321 and 376 test functions in one rehearsal and 241, 522 and 681 in another. On this track, stage 1 was accepted in two rounds in sub-02 and four in sub-05, and blocked after seven in sub-03 and sub-04.
- Units per supported field are measured on each verifier's own workload (the mock web's sample corpus, plus in sub-05 the suite's own companies), not on the judged workload.
- The Codex dollar figures rest on an assumed rate.
- The live web is harder than the mock web. `dossier-runway.com.json`, built from `stage-4/` against the live web with Nimble alone on 2026-11-19 at 03:34 UTC, is ready but knows 2 of the 6 base fields: the CEO and the founding year, both cited from one page. The other four, and the executives and investors, are unknown. The build spent its whole 80-unit budget. The kit's check warns that live providers answer far more slowly than the mock web (a search can take over ten seconds, a research run about a minute) and that a service which stops waiting sooner leaves fields unknown; we have not separated how much of the gap is the budget and how much is waiting. On the mock web's corpora every supportable field was found within the cap.
