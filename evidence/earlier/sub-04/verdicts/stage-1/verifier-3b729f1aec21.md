VERDICT: PASS
REVISION: 3b729f1aec21154fa42fc5ca79d95e86f90f8768

# Verifier: stage 1, fix round 4

Suite: the sealed stage-1 suite at seal sha256:be61bce2b1e6a82bd165edf5e7f352b313fd1ede6d0cde60f1720f347ab08b7b, 104 tests.
This round's amendment was made after I had read the code. It is a post-seal addition for SR1-04: a POST /dossiers whose body arrives in two parts, with a reset, or an unchanged import, sent between the parts.

## Reported problems, retested first
- **SR1-04 / S1-071, S1-311, S1-312:**
  - Reset while the body is still arriving: the old POST leaves nothing behind. After the reset the dossier list is empty and GET returns 404, also 3 s later.
  - Unchanged import while the body is still arriving: the POST still answers 202, and its build completes on the same dossier_id.
  - The reset test fails on the previous revision 2d57d918, and both pass here. Command: `run.sh <clone>/stage-1 -k during_request_body`.
  - Code: `create` now reads the body before it touches any state; authentication, the replay check and the write all run in one synchronous step against one store. `login` checks the password again if the state was replaced while the password was being verified.
- **SR1-01:** the provider and research code is unchanged. The fake-clock probe in live mode still holds: research starts no later than 220 s, each call gets at least 30 s, everything ends by 290 s.
- **SR1-02 and SR1-03:** the header-only claim test and the sextant-labs test pass (the latter at 80 units).

## Whole stage
1. RUN.md, word for word (RUN.md, Dockerfile and requirements.txt are unchanged): the `--no-cache` build succeeded and `/health` returned 200 under 1 s after start.
2. Check command in isolated mode (`checks/verifier-s1-3b729f1a`): stage 1 pass, `claimed stage: 1`.
3. Sealed suite: `COUNTS total=104 passed=104 failed=0`, at 2 vCPU / 3 GiB on an internal network.
4. Cost: 476 units over 9 builds for 35 confirmed supported known fields, **13.6 units per supported field**. The most any build spent was 80, and spent_units equals the cost in the mock log. The figures are the same as on 2d57d918, and the avoidable-spend note from that verdict still applies.
5. Code diff (`auth.py`, `dossiers.py`, `http.py`): I found no fixture-keyed logic, and provider traffic is unchanged.
6. Upgrade path and restart: not applicable. Fault planting was done on 1c6dd772.

## Findings
None.
