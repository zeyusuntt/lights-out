# Lights Out

Team: Zeyu Sun. Track: Dossier, BAND Dark Factory Buildathon 2026.

Dossier is a company-research service with screens: given a company's web domain, it researches the company on the web and keeps a profile (legal name, headquarters, chief executive, founding year, headcount and funding, later its executives and investors) in which every value shows the sources behind it.

The name is the manufacturing term: a lights-out factory runs with nobody on the floor, which is what a dark factory is.

Lights Out is a software factory in one Band Desktop room: five model seats and a script. A foreman hands out the work, a builder writes the service, and three seats check it independently. The verifier seals its acceptance tests before any code exists, and labels any it adds later. The second-reader, on another model family, numbers every sentence of the specification and shows evidence for each requirement. The product-user walks every screen in a real browser. A stage closes only when a program confirms that every seat checking that stage passed the same commit (the product-user from stage 2, where the screens begin). One human message starts a run, and nobody types in the room after it.

## This run

Run sub-05 worked through all four stages from one human message in 419 minutes, and our own gate accepted every one: `stage-1/` to `stage-4/` hold the accepted revisions `a8789dc`, `bc19abf`, `cd24f51` and `a7228733`. The verifying seats blocked 6 of the 10 candidates sent to them, each time on a sentence of the specification, and every block was fixed in a new commit that the next round checked. On the kit's shipped checks, run in isolated mode on a fresh clone after the run, every folder claims its own stage: `stage-1/` 122/122, `stage-2/` adds 12/12, `stage-3/` adds 9/9, `stage-4/` adds 10/10. The second-reader's ledger shows passing evidence on the accepted commits for all 675 requirement units of the four specifications, 25 of them from reading the source alone. The verifier planted 31 faults in copies of the service to test its own suites: 23 were caught at once, and the 5 that exposed holes got new tests. `FACTORY.md` lists each block with its commits, and both tables.

## Read this first

- `FACTORY.md`: how the factory works, how to stand it up, what it cost, and how it caught bad work, with the commits.
- `room.json`: the room, downloaded from the Band console. One kind of edit: 3 occurrences of a private name from another of the operator's projects, 1,711 copies of the operator's home-directory path or user name, 164 copies of the operator's Band account name and 1 occurrence of the name of another person who uses the build machine now read `[REDACTED]`; nothing else in the file is changed (`evidence/room-redaction.txt` has the download's checksum from before the edit).
- `reports/final.md`: the foreman's final report for the run.
- `verdicts/`: every verdict, one file per seat and revision. A BLOCK names the sentence it breaks and how to reproduce it. The paths it quotes are the build machine's; `acceptance/second-reader/README.md` says how to run the published probes from this repository (with `factory/bin` on the PATH and `DOSSIER_KIT` set to the kit).

## How this repository is laid out

| Path | What it holds | Written by |
|---|---|---|
| `stage-1/` to `stage-4/` | one complete service per stage, each with its `Dockerfile` and `RUN.md` | builder seat |
| `ledger/` | every sentence of each stage's specification, numbered, with what it requires and the evidence on the accepted commit | second-reader seat |
| `acceptance/` | the verifier's sealed suites with their seal records; the second-reader's probes under `acceptance/second-reader/` | verifier and second-reader seats |
| `verdicts/` | one verdict per verifying seat and revision | verifier, second-reader, product-user seats |
| `journey/` | the product-user's screenshots and walk scripts, at 375 px and desktop width | product-user seat |
| `plan/`, `rulings/`, `accepted/`, `reports/` | handoff notes, fix requests, rulings on ambiguous sentences, acceptance records, the final report | foreman seat |
| `mandates/`, `PROTOCOL.md` | each seat's instructions as this run used them | operator |
| `factory/` | the tooling the seats and the operator use, with its tests | operator |
| `room.json` | the Band room, the console's full-session download (see above) | Band |
| `dossier-runway.com.json` | `GET /dossiers/runway.com` from `stage-4/`, built against the live web | the service, run by the operator |
| `checks/` | the kit's report from every check a seat ran during the run, in folders named after the seat and stage, then the revision or the round (each `report.json` records its revision); `checks/fresh-clone/` is the operator's isolated run of every stage folder on a fresh clone after the run | seats; operator |
| `evidence/` | measured facts of this run and earlier runs on this track (`run-stats`), the earlier runs' kit reports per candidate, and every mandate change since kickoff (`mandate-history.patch`) | operator |
| `rehearsals/` | results from rehearsal runs on other problems before the event | operator |

Everything under `stage-N/` came out of the room; the operator committed nothing there. The band's history is kept as the seats made it, and the operator's commits sit on top of it. The operator's home-directory paths and user name, e-mail addresses and Band account name read `[REDACTED]` in every file the operator added, and a second operator commit makes the same replacement in the band's files outside `stage-N/` and the verifier's sealed suites (`acceptance/stage-N/`, whose checksums in `SEAL.json` a change would break). Nothing was rewritten: the band's earlier commits and their author addresses, the stage folders and the sealed suites still hold the original text.

## Run a stage

Each `stage-N/RUN.md` says how to build and start that stage. To check a folder with the kit's shipped checks, run this from the kit's root, prepared as its participant guide says, with the absolute path of a clone of this repository:

```sh
.venv/bin/python -m harness run --track dossier --repo /path/to/clone --stage 4 --mode isolated
```

The `RUN.md` files start the kit's mock web from an image named `dossier-web`: build it first, from the kit's root, with `docker build -t dossier-web challenges/dossier/web`. Their API tests reach the mock at `http://localhost:8080`, so for those also add `-p 8080:8080` to the `docker run` that starts it.
