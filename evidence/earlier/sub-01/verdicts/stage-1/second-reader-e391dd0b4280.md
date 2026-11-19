VERDICT: PASS
REVISION: e391dd0b4280ee518d358387614110bebf90c116

# Independent second-reader audit — Stage 1, round 2

All **156 checks passed**: 151 black-box probes and five narrow source checks. The three findings from revision `408ebd53d4cb62fbbb460c876c1d9e9d6f8566e6` are resolved. There are no new findings or ledger gaps on this revision.

## Exact revision and command

```sh
fclone e391dd0b4280ee518d358387614110bebf90c116 /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-e391dd0b4280
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-e391dd0b4280/stage-1
```

The clone is this exact hash and `git status --short` is empty. The runner builds and starts the supplied stage folder itself, starts the supplied mock web with its sample corpus and independently authored cases, and uses an isolated network, Nimble alone and 2-vCPU/3-GiB service limits. It printed `COUNTS 151 passed 0 failed` and `TOTAL COUNTS 156 passed 0 failed`, exiting **0**. The candidate also started successfully using `fserve` on port 20080.

The complete probe directory is private at `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/` pending publication after all stages close. No product code or product tests were edited. No check/test sources, `key.json` or later-stage specification were opened.

## Retest of reported findings

- **F1, S1-121/S1-223:** `prose/late-support-generic-page` now returns the supported CEO value `Dana Ruiz`, with a citation copied from the searchable generic registry page whose support is beyond the opening snippet. This regression runs before the remainder of the black-box suite.
- **F2, S1-100/S1-246:** `invalid-domain-paths` now returns **422 `validation_failed`** for the encoded URL-shaped domain, encoded slash domain and matching refresh path. This regression runs first in the black-box suite.
- **F3, S1-226:** narrow source review and `source/live-minimum-call-wait` confirm both read and connection timeouts are **60 seconds**. This source check was rerun before the full suite. The probe now recognizes HTTPX's default timeout applying to an omitted phase keyword; its 30-second threshold is unchanged, and it still fails the original revision's 15-second connection timeout. No live provider request was made.

## Full audit and cost

The entire existing suite then passed: statement phrases and legal suffixes, Unicode names/cities, number/amount/bucket boundaries, negation, supported and unsupported research claims, citation provenance, normalization and errors, authentication, idempotency and original-response replays, 50-request races, resets and imports during builds, atomic portable snapshots, sessions and hashed-password login after transfer, failed-key reuse after transfer, clocks and list pagination.

`accounting` independently sums the provider call log and matches `spent_units`; `building-spending` checks charged calls are visible while a build is still running; refresh checks preserve cumulative spending. `prose/budget-boundary` reaches **exactly 80 units** and passes without overflow. All these passed on the changed gathering behavior. Failed/refused refreshes preserve prior fields/timestamps and add no refused-call cost.

All 319 normative/ambiguous ledger units have refreshed evidence for this exact revision. The audit command:

```sh
ledger-check 1 --phase audit --revision e391dd0b4280ee518d358387614110bebf90c116
```

exits **0**: `ok: 379 units, 310 normative, 9 ambiguous, phase audit`.

Source evidence is limited to otherwise unobservable properties: provider routing/dependencies, password hashing, timeout/no-page cost classification and live timing configuration. Live build/research upper bounds remain 285/240 seconds. This is configuration evidence, not a paid live-provider experiment. No verifier verdict for this revision was present when checked after my probes finished; this PASS does not depend on another seat's claim.

The kit sample check also exited **0** and printed `claimed stage: 1 on the shipped checks`, using the required kit entry point and a fresh output directory:

```sh
cd /Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026
env BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/docker-buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-e391dd0b4280 --stage 1 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s1-e391dd0b-01
```

This sample check is supplementary and is not the basis of the PASS. No later-stage check log was opened. All owned service/probe containers were removed.
