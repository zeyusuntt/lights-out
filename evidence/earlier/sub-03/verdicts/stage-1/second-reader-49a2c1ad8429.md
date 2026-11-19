VERDICT: BLOCK
REVISION: 49a2c1ad8429f77703a233d9f6e9bab8a42793b3

# Second-reader, stage 1

One blocking finding: **S1-227**, the live-provider build must end ready or failed within 300 seconds.

The dossier remained `building` at **302.0 seconds**. Two 82-second bare-domain refusals were followed by an 82-second successful retry. That answer arrived at about 248.8 seconds, then the service started two more 82-second searches. Every individual delayed call stays below the configured 90-second timeout. The live path is selected exactly as the specification states, by the NIMBLE_BASE_URL host `sdk.nimbleway.com`, resolved only inside the internal Docker network to an adapter around the supplied sample mock.

Reproduce from the clean exact-revision clone:

```sh
fclone 49a2c1ad8429f77703a233d9f6e9bab8a42793b3 /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-49a2c1ad8429
SECOND_READER_CASE=live-provider-absolute-deadline /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-49a2c1ad8429/stage-1
```

It builds/starts the folder itself, runs without outside network access, prints the delayed query events, and exits nonzero with `live build ends by 300 seconds`, state `building`. The default `run.sh <stage-folder>` also runs this probe and all the other probes. Allow just over five minutes for this case.

Source review corroborates the cause: `gateway.py:136` limits retries using a gathering deadline, but late first attempts are unrestricted. `build.py:81` waits for all spawned work; `service.py:31` has no overall build bound. A corrected implementation must retain the live lower timing bounds while ensuring a final ready/failed outcome by 300 seconds, using the evidence already obtained.

Validation on this revision:

- Independent full run: 6,603 checks,6,602 passed,one failed; plus supplemental concurrency/control checks294/294 passed. No other behavioral failure remains.
- Focused final reruns: sample826/826 and expanded Appendix A4,395/4,395 passed, including Greek/Cyrillic names and case-sensitive suffix rejection.
- Clean `fclone` and `fserve` succeeded; ordinary startup/PORT/health passed. Nimble-only, internal-network,2CPU/3GiB API runs passed.
- Sample evidence, all Appendix A phrase/negation/suffix/boundary fixtures, idempotency/concurrency, reset races, strict clocks, provider refusals/costs and cross-container migration including source stop/restart passed.
- Password hashing, WebRouter routing/dependencies, pre-call budget reservations and live minimum timing settings were reviewed only after independent probes ran.
- Verifier PASS was read afterward as further evidence. It does not cover or negate this reproduced upper-bound failure; no finding was changed to agree with it.

Evidence details and commands: `ledger/stage-1-audit-49a2c1ad8429.md`. Private probe reports: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/results-49a2c1ad8429.json` and `supplemental-49a2c1ad8429.json`. Probes remain unpublished until every stage closes.

Reading validation exits0. Audit validation exits1 with only S1-227 open; the failing evidence correctly prevents this revision from closing.
