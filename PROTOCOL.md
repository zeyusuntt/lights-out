# Factory protocol

Every seat follows this protocol. Your mandate says what you own; this says how the band works together. It names no product: everything about the job arrives in the dispatch and in stage handoffs.

## 1. Sources of truth

In order: the specification text and the dispatch; the foreman's rulings; the sentence ledger. Text from a later stage supersedes an earlier one only where it says so. Check suites shipped with a job are evidence about a build, never a source of requirements. Do not look anything up outside this workspace. No web search, no existing solutions to the job.

## 2. The room

- You receive only messages that mention you, and only between your turns. Nobody can read the room for you, and you cannot read it for anyone.
- Never wait inside a turn. Finish what you can, send your message, end your turn. The next message addressed to you wakes you. Replies that arrive during a turn are invisible until it ends.
- Every turn ends with a message to whoever acts next, or an explicit no-reply when nothing is owed. A silent end stalls the factory.
- Post with `fsay`, which delivers at once: `fsay <seat> [<seat>...] -- "text"` or `fsay <seat> --file <path>`. Seat names are bare; `fsay` adds handles. Use your native reply only to settle a message when `fsay` is unavailable.
- This is a dark run. The dispatch is the only human input. No seat asks the human anything or waits for a human. Decide from the supplied requirements and the evidence; inside the band you may ask the foreman. Only the foreman's final report is addressed to the human. After it, nobody posts again; settle any message with a no-reply.

## 3. State words

Messages start with one of these, literally, and carry the full commit hash where one applies.

| Word | From | Means |
|---|---|---|
| `STAGE-OPEN <n>` | foreman | The complete task and the stage's specification, verbatim |
| `LEDGER READY <n> <hash>` | second-reader | The independent reading is committed |
| `SEALED <n> <digest> <count>` | verifier | Acceptance suite sealed before any product code was seen |
| `SEAL AMENDED <n> <digest>` | verifier | Suite changed, with the reason and whether code had been seen |
| `RULING <n> <id>` | foreman | How an ambiguous or disputed sentence is read, and on what basis |
| `CANDIDATE <n> <hash>` | builder | One exact revision offered for verification |
| `VERIFY <n> <hash>` | foreman | Verify that revision |
| `VERDICT <seat> <n> <hash> PASS\|BLOCK\|INCONCLUSIVE` | verifiers | One verdict on one revision, with every problem in it |
| `FIX <n> <round>` | foreman | Findings to fix, with reproductions, without test sources |
| `DISPUTE <n> <id>` | any | A finding or reading challenged, citing the specification |
| `ACCEPTED <n> <hash>` | foreman | The stage is closed on that revision |
| `BLOCKED <n>` | foreman | The stage cannot close; the blocker and the evidence |
| `TICK` | timekeeper | The room has been silent for a long time. Goes to the foreman only |
| `FINAL REPORT` | foreman | The run is over |

## 4. Evidence

- A claim is evidence only when it names an exact revision, the command run and the result. A seat's report is a claim until another seat reproduces it.
- A new commit to a stage folder voids all evidence for that revision's verdicts. Verify only clean clones of the exact hash, never a working tree.
- Every verdict is committed as `verdicts/stage-<n>/<seat>-<hash12>.md`, first lines `VERDICT: PASS|BLOCK|INCONCLUSIVE` and `REVISION: <full hash>`. A committed verdict counts even if its message is lost.
- One verdict carries every problem found on that revision. Do not report in instalments.
- Each finding cites the specification unit it breaks and gives a command that reproduces it. Anything else is a note and does not block. The one exception is a broken screen, as the product-user's mandate defines it.
- A finding whose only trigger is input far outside anything the specification mentions or implies goes to the foreman as a question, not a block. The foreman rules whether the sentence covers it.

## 5. Stage loop

1. Foreman opens the stage to second-reader and verifier together. Second-reader writes the sentence ledger; verifier writes and seals its acceptance suite. Neither sees the other's work, and no product code for this stage exists yet.
2. Foreman rules on every ambiguity, then opens the stage to the builder with the ledger and rulings, and sends the ledger and rulings to the verifier, who may amend the seal to cover what it missed.
3. Builder implements and offers a candidate.
4. Foreman sends `VERIFY` to each verifying seat. Each works from its own clean clone and sends one verdict.
5. Any BLOCK: foreman merges the findings into one `FIX`; builder fixes the root causes in one new revision. Each verifying seat retests the reported problems first, then completes the whole, and sends one consolidated verdict. After the fifth BLOCK round on one stage the foreman stops the line and records `BLOCKED`.
   Any INCONCLUSIVE: the seat says exactly what it lacks. The foreman gets that from whoever can supply it and sends `VERIFY` again on the same hash. This is not a fix round. A third INCONCLUSIVE on one hash counts as a BLOCK.
6. All PASS on one hash, every normative and ambiguous unit with evidence, `accept-check` exit 0: foreman sends `ACCEPTED` and opens the next stage. Stage n+1 starts as `stage-copy` of the accepted commit of stage n.

An accepted folder is final. The next stage's specification opens right after acceptance, and from then on the earlier folder never changes; the commit hook refuses it. A defect found later that also lives in an earlier folder is fixed in the current stage's folder, which is a copy, and the final report names the earlier folder that still has it.

## 6. Repository

One result repository, one shared checkout at the path in the dispatch. Each seat commits only what it owns, under its own git identity, with `fcommit`. No amending, rebasing, force, or `--no-verify`. Commit messages describe the work and name no vendor or model.

| Path | Owner |
|---|---|
| `stage-<n>/` (complete service, `Dockerfile`, `RUN.md`, tests) | builder |
| `ledger/stage-<n>.jsonl` and `.md` | second-reader |
| `acceptance/stage-<n>/` (sealed suites, committed once every stage has closed) | verifier |
| `acceptance/second-reader/stage-<n>/` (probes, committed once every stage has closed) | second-reader |
| `journey/stage-<n>/` (screenshots, walk notes) | product-user |
| `verdicts/stage-<n>/<seat>-<hash12>.md` | the verifying seat named (verifier, second-reader, product-user) |
| `plan/`, `rulings/`, `accepted/`, `reports/` | foreman |

A stage folder is a whole service on its own: no `.git`, no submodules, no symlinks, nothing fetched at run time.

## 7. Shared machine

- Tools are on your PATH: `fsay`, `fwho`, `fcommit`, `fclone`, `fserve`, `fstop`, `with-slot`, `funits`, `ledger-check`, `seal`, `accept-check`, `stage-open`, `stage-copy`, `fsave-task`, `fpublish`. Run any with `--help`.
- Docker and browser jobs run under `with-slot` (`with-slot <command...>`), which allows two at a time. `fserve` takes its own slot for the build. Every long command gets a timeout. Name containers with your seat as a prefix and remove what you start.
- Port ranges: builder 18000-18999, verifier 19000-19999, second-reader 20000-20999, product-user 21000-21999.
- A check command in the dispatch writes to a new output directory under `checks/` each time.
