VERDICT: BLOCK
REVISION: 1c6dd77224ce853f5a4b646ec071b1ae609e7fe1

# Independent second reading audit, Stage 1

## Blocking finding SR1-01 — S1-226: outer build deadline abandons a new live call after 5.95 seconds

The specification requires that against live Nimble (including any NIMBLE_BASE_URL whose host is `sdk.nimbleway.com`) a build must not give up on a provider call that has waited less than 30 seconds. The implementation has a 290-second outer build deadline but starts further calls without reserving their minimum permitted time. The outer timeout cancels a late call well before that minimum.

An independent HTTP probe uses only the supplied sample mock as its answer source. A transparent delay proxy is named `sdk.nimbleway.com` on the isolated container network, so the documented live-mode condition holds. It passes provider bodies/answers through unchanged. Two domain searches are refused by the mock after 40 seconds each, then the same query succeeds after 40 seconds. Other search and initial extract rounds take 25 seconds. The mock's Nimble research answer is delivered at second 284; the service then starts extracting its previously unseen cited page, with that answer delayed 40 seconds.

Observed exact-revision trace:

- Domain search attempts began at 0.17, 41.32, and 82.45 seconds; the first two were provider refusals and the third succeeded.
- Field searches began at 122.51 seconds; initial extracts began at 147.58 seconds.
- Research started at 172.62 seconds, with status/result collected at 284.02 and 284.08 seconds.
- A new `POST /nimble/v2/extract` began at **284.09 seconds** and had not answered when the dossier left `building` at **290.04 seconds**.
- The provider call had waited only **5.95 seconds**. The probe exits 1.

All requests and responses are normal sample-mock operations. The delay durations are within the slower-provider behavior covered by §8; the call is not refused or answered when the build terminates. This is a deadline-composition defect, not a claim that a 45-second per-call timeout alone is too short.

Reproduce from a clean exact clone:

```sh
fclone 1c6dd77224ce853f5a4b646ec071b1ae609e7fe1 /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-01
SECOND_READER_ONLY=live-call-started-near-build-deadline /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-01/stage-1
```

The command builds/starts the folder and sample mock itself, uses an internal network and 2-vCPU/3-GiB service containers, prints counts, and removes its resources. It takes about five minutes. The full root `run.sh <stage-folder>` also includes this reproduction, with every ordinary probe, and exits nonzero on failure. Probe sources remain private until all stages close, as required.

Source corroboration, read only after independent probes: `stage-1/dossier/builds.py` wraps the entire researcher in `asyncio.wait_for(..., 290.0)` for live mode. `stage-1/dossier/research.py` starts `_fetch(unseen)` after collecting research claims without checking that 30 seconds remain. `stage-1/dossier/providers.py`'s 45-second extract timeout cannot prevent the outer cancellation.

## Other audit evidence

There are **37 passing ordinary cases**. These cover health/auth/JSON errors, clock before/after initialization, validation, idempotency identity and validation precedence, two 50-request create races, reset with an in-flight build, failure/recovery refresh, listing, running-build spending, and export/import. Transfer actually stops the source container before proving the destination's independent accounts, password-hash login, existing tokens, dossier contents, and original idempotent responses; the source is then started again.

Both sample epochs for all 12 companies passed an independent Appendix A and actual-served-citation oracle: **24 builds, 138 supported known fields, 669 research units, maximum 40 units in one build**. The source was inspected only for mechanisms and grammar variants not established by the finite black-box sample, including WebRouter-only routing, dependency packaging, password hashing, budget reservation, and literal support rules. The image also answered health with PORT=8089 in a separate fserve run.

The verifier's `verdicts/stage-1/verifier-1c6dd77224ce.md` was read only after independent execution. It reports a 100/100 suite and a shipped isolated check claiming stage 1 on this revision. Its PASS does not change the independently reproduced finding above.

Per-unit evidence and ruled readings are in `ledger/stage-1.jsonl`; the complete result summary and timing trace are in `ledger/stage-1-probe-results.md`; commands and source evidence are in `ledger/stage-1-audit.md`. `ledger-check 1 --phase audit --revision 1c6dd77224ce853f5a4b646ec071b1ae609e7fe1` must remain nonzero because S1-226 has failing evidence. No unit is silently omitted.
