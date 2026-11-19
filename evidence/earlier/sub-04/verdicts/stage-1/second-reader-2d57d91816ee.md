VERDICT: BLOCK
REVISION: 2d57d91816eebc89d258683e98eee368c7eadc65

# Independent second reading audit, fix round 3

## Earlier findings retested first: resolved

SR1-03's control and archive-heavy six-citation cases both pass, with all six fields known for 46 and 80 units respectively. SR1-01 and SR1-02 then passed their three-case retest before the full stage run. The full verification-margin case returned research at second 249, obtained two cited pages after 35 seconds, rejected the header quote, retained a valid prose quote and finished at 284.12 seconds, inside 300 seconds. No call was abandoned before its permitted minimum wait.

## Blocking finding SR1-04 — S1-311/S1-312 and S1-071: a pre-reset write repopulates the replacement state under an invalidated token

A valid authenticated POST can begin reading its JSON body before reset, finish receiving it after reset, and create a dossier visible in the replacement state even though its bearer token has already been invalidated. This cannot be serialized with reset as §11 requires.

The independent HTTP probe performs this sequence, using the same valid fixture for both resets:

1. Log in to get T0; begin `POST /dossiers` with valid bearer/key/content-type/content-length headers, but send only the first body byte, `{`.
2. After 0.15 seconds, reset successfully returns 204 and login obtains replacement token T1.
3. Confirm T0 receives 401 and T1 sees an empty dossier list.
4. Send the rest of the valid body `{"domain":"brightwater-labs.test"}` on the original connection.
5. The old POST returns **202**; a subsequent T1 read of the domain returns **200** with the new dossier. No other dossier write occurred after reset.

The request completes comfortably inside the five-second limit. This is ordinary valid HTTP/JSON arriving in more than one packet, with only two overlapping requests.

Neither allowed sequential order explains the result:

| Order | Required result |
|---|---|
| POST before reset | Reset removes that dossier; the subsequent read is 404 |
| Reset before POST | T0 is unknown; the POST is 401 and creates no dossier |

The actual combination is POST 202 plus a post-reset dossier read of 200, despite T0 already being confirmed invalid. S1-311's sequential-order requirement fails, S1-312 requires the invariants at every read, and S1-071's replacement fixture is contaminated by the earlier request.

Reproduce on a fresh exact clone:

```sh
fclone 2d57d91816eebc89d258683e98eee368c7eadc65 /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-04
SECOND_READER_ONLY=reset-during-request-body /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-04/stage-1
```

The command builds and starts everything itself using the unchanged official mock and supplied sample, on an internal network with 2-vCPU/3-GiB service limits. It prints a failure containing `write_status: 202`, `post_reset_read_status: 200`, `old_token_is_invalid: True`, then `COUNTS total=1 passed=0 failed=1`, exit 1. It was reproduced standalone and in the full run. Probe sources remain private until all stages close.

The companion `SECOND_READER_ONLY=import-during-request-body` passes. It replaces state with an unchanged export that retains T0; the same overlapping write returns 202 and T0 remains valid, as §10 requires. Authorization and state effects must therefore remain consistent across the control operation while preserving valid imported sessions.

## Complete audit evidence

The full run completed **44 cases: 43 passed and 1 failed**. The separately run import/body companion adds one passing unique case: **45 unique cases, 44 passing and one failing**. SR1-04 is the only blocking finding. The cloned working tree remained clean; no product file or product test was edited.

Both sample epochs pass again: 24 builds, 138 supported known fields, 669 research units, maximum sample build 40. Other passing coverage includes JSON/auth/error conventions, clock behavior, domain/query validation, idempotency scope/precedence, 50-writer races, reset during provider work, refresh failure/recovery, listings, active spending, source-stopped replacement import, destination-only data/credential/key removal, and exports taken after charges settle during first/later builds. Default-port instances and explicit PORT=8089 both serve health.

The verifier's committed PASS on 102 sealed tests and its isolated check claiming stage 1 were read after independent execution. The reset/body case supplies additional concrete evidence and does not change to agree with that report.

All 318 normative/ruled units have refreshed exact-revision evidence. `ledger-check 1 --phase audit --revision 2d57d91816eebc89d258683e98eee368c7eadc65` exits 1 with exactly **S1-071, S1-311 and S1-312** open. Full command/source evidence and results are in `ledger/stage-1-audit-2d57d91816ee.md` and `ledger/stage-1-probe-results-2d57d91816ee.md`. Owned resources were removed.
