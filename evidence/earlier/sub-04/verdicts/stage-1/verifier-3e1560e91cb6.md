VERDICT: PASS
REVISION: 3e1560e91cb662d7595fed833008e3bd91904d61

# Verifier: stage 1, fix round 1

Suite: the sealed stage-1 suite, seal sha256:afe277ffd438ecd82b97bf113af480e4aab27d654df8cb59dc1229f070507944 (100 tests; `seal --verify` ok). No amendment this round.

## Reported problem retested first: SR1-01 / S1-226 (live-mode call near the build deadline)
- Fake-clock probe of `dossier.providers.Window` / `Gateway._call`, run inside this revision's image in live mode (NIMBLE_BASE_URL unset).

  | Call starts at | Allowed wait | Done by |
  |---|---|---|
  | 0 s | 240 s | 245 s |
  | 120 s | 165 s | 290 s |
  | 200 s | 85 s | 290 s |
  | 254 s | 31 s | 290 s |
  | 255 s | 30 s | 290 s |
  | 256, 270, 284 s | not started | — |

  The "done by" times include the 5 s cancel grace. So every call that starts gets at least 30 s, and none can run past 290 s, inside the 300 s bound.
- Code: the outer `wait_for` is gone; the per-build window is 285 s live and 110 s against the mock. The allowance is checked again after the semaphore is acquired; a call stopped at that point costs 0. A call cut off by `wait_for` is a lost answer and is charged in full (§9). Retries stop after 200 s live. Gathering is not limited by time within the first 120 s.
- End to end in live mode: the mock web was given the network alias `sdk.nimbleway.com`, and NIMBLE_BASE_URL was `http://sdk.nimbleway.com:8080/nimble`, so `is_live()` is true. With every Nimble method delayed 10 s, lumen-harbor.test ended ready in 51 s for 31 units, with the expected fields.
- Not a problem: a research excerpt from a page that was never read is accepted only when it is not a header line. The excerpt is text Nimble served for that URL (the research citation). It must still pass the Appendix A support check, and a header excerpt such as `Facts: {...}` is refused. The same rule existed in 1c6dd772. I read it as consistent with §4, so this is a note, not a finding.

## Whole stage
1. RUN.md, word for word, in a clean environment (RUN.md, Dockerfile and requirements.txt are unchanged since 1c6dd772): `docker build --no-cache -t dossier-stage-1 .` succeeded, and `/health` returned 200 1 s after `docker run`.
2. Check command in isolated mode (`--out checks/verifier-s1-3e1560e9`): stage 1 pass, `claimed stage: 1`.
3. Sealed suite: `run.sh <clone>/stage-1` gave `COUNTS total=100 passed=100 failed=0`, with 2 vCPU / 3 GiB and an internal network.
4. Upgrade path and restart: not applicable at stage 1.
5. Cost: 215 units over 8 builds for 29 confirmed supported known fields, **7.4 units per supported field (215 / 29)**. Every build stayed at or under 80 units, and spent_units equals the cost recorded in the mock log.
6. Code reading of the diff (`builds.py`, `providers.py`, `research.py`): provider traffic still goes only through WebRouter, and I found no fixture-keyed logic.
7. Fault planting: already done on the stage's first passing revision (1c6dd772: 6 of 8 caught; 1 hole closed by a post-seal test).

## Findings
None.
