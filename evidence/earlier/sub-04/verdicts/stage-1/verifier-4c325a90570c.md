VERDICT: PASS
REVISION: 4c325a90570c523622db2c485684608435818838

# Verifier: stage 1, fix round 2

Suite: the sealed stage-1 suite at seal sha256:ca3fb8be85137d97b6a3ece9a9926290ffd97edacd0720fe9e9a89756eee0b7e, 101 tests.
This round's amendment was made after I had read the code. It is a post-seal addition for SR1-02: a non-searchable page whose Facts header alone carries `Brisa Norte CEO Ana Lee`, cited by a Nimble research claim.

## Reported problems, retested first
- **SR1-02 / S1-128, S1-143** (header-only research claim): the new test passes on this revision, both with the cited page extracted and with extract refused. In both cases ceo stays unknown with `citations: []`. The same test fails on the previous revision 3e1560e9, so it tells the two apart.
  Command: `run.sh <clone>/stage-1 -k header_only`.
- **SR1-01 / S1-226** (live window): I drove the research call and the extract after it with a fake clock, in live mode, inside this image. A research run gets at least 30 s and can start no later than 220 s; it then ends by 255 s at worst. The extract of the cited page that follows always starts with at least 30 s, and everything ends by 290 s, inside 300 s.

  | Research starts | Research wait | Research done by | Extract wait | Extract ends |
  |---|---|---|---|---|
  | 0 s | 240 s | 245 s | 40 s | 290 s |
  | 100 s | 150 s | 255 s | 30 s | 290 s |
  | 200 s | 50 s | 255 s | 30 s | 290 s |
  | 220 s | 30 s | 255 s | 30 s | 290 s |
  | 221 s or later | not started | — | — | — |

## Whole stage
1. RUN.md, word for word (RUN.md, Dockerfile and requirements.txt are unchanged): the `--no-cache` build succeeded and `/health` returned 200 under 1 s after start.
2. Check command in isolated mode (`checks/verifier-s1-4c325a90`): stage 1 pass, `claimed stage: 1`.
3. Sealed suite: `COUNTS total=101 passed=101 failed=0`, at 2 vCPU / 3 GiB on an internal network.
4. Cost: 216 units over 8 builds for 29 confirmed supported known fields, **7.4 units per supported field (216 / 29)**. Every build stayed at or under 80 units, and spent_units equals the cost in the mock log.
5. Code diff (`providers.py`, `research.py`): a research excerpt is now asserted only when it is in the prose of a text a provider served for that page in this build. Provider traffic still goes only through WebRouter, and I found no fixture-keyed logic.
6. Upgrade path and restart: not applicable. Fault planting was done on 1c6dd772.

## Findings
None.
