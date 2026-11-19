VERDICT: BLOCK
REVISION: 408ebd53d4cb62fbbb460c876c1d9e9d6f8566e6

# Independent second-reader audit — Stage 1

The candidate has three findings. The complete rerunnable audit finishes with **153 passed, 3 failed**: 149 passing and two failing black-box probes, plus four passing and one failing narrow source checks. All 319 normative or ambiguous ledger units have exact-revision evidence; five units retain failing evidence, corresponding to the three findings below.

## Reproduction and revision

```sh
fclone 408ebd53d4cb62fbbb460c876c1d9e9d6f8566e6 /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-408ebd53d4cb
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-408ebd53d4cb/stage-1
```

`fclone` returned the exact revision above. `git rev-parse HEAD` returned the same full hash, and `git status --short` was empty after the audit. The runner takes only the stage-folder argument, builds and starts its own service containers and the supplied mock web, runs every probe, prints counts, and exits 1 for these findings. It uses an internal Docker network, 2-vCPU/3-GiB service allocations and Nimble alone. The mock uses the supplied sample corpus plus independently authored prose cases; `key.json`, kit test/check sources and another seat's tests were not opened.

The probes remain private at `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/` until the final factory publication. Their repository destination after all stages close is `acceptance/second-reader/stage-1/`. No product code or product tests were edited.

## F1 — Discoverable evidence outside the opening snippet is missed

Units: **S1-121, S1-223**, ruled by R1-03.

An independently authored company has one searchable page with a generic registry title and URL. Its opening prose contains administrative notes; after the first 300 characters it contains the company's name and `CEO: Dana Ruiz.` The full page is available through the supplied mock's extract endpoint, and the exact-domain search returns it. The completed dossier reports `ceo.value: null` rather than `Dana Ruiz`.

This violates the requirement that a ready field is known exactly when the defined evidence supports a value. Citation correctness for fields already found does not satisfy completeness across the full searchable page text.

Reproduce with the complete runner above. Failure name: `prose/late-support-generic-page`; output: `('ceo', 'actual', None, 'expected', 'Dana Ruiz')`. The runner builds this corpus itself; no additional setup or secret fixture is needed.

After the independent probes ran, I read `verdicts/stage-1/verifier-408ebd53d4cb.md`. Its F1 describes the same behavior on another corpus. My result and finding were obtained independently and were not changed to agree with it.

## F2 — Encoded URL/path domain input returns 404 instead of validation failure

Units: **S1-100, S1-246** (with the every-domain rule in S1-098).

Authenticated `GET /dossiers/https%3A%2F%2Fx.test` returns **404 `not_found`**. The decoded domain argument is `https://x.test`; the domain rule explicitly excludes URLs with a scheme or path and requires **422 `validation_failed`** for invalid domains in a path as well as in a body. The probe also includes an encoded slash in a domain and the corresponding refresh path; the first failing assertion is the encoded scheme request.

Reproduce with the complete runner above. Failure name: `invalid-domain-paths`; output: `('status', 404, 422, 'not_found')`. The request is authenticated, so this is not an authentication-priority question.

## F3 — The configured connection timeout can abandon a live call before 30 seconds

Unit: **S1-226**.

`stage-1/dossier/gateway.py:15` constructs `httpx.Timeout(60.0, connect=15.0)`. Line 74 passes that timeout into the Nimble async client that WebRouter uses. No live-host override raises the connection timeout. Consequently a call still establishing its connection can time out after 15 seconds, although the live-provider rule says not to give up on a call that has waited less than 30 seconds. The 60-second read timeout does not change the separate connection timeout.

This is **source evidence**, not a claim that a real live-provider call was made. No live credentials or paid research were used. The supplied mock's bounded response-delay control cannot exercise a 30-second connection-establishment wait, so the narrow source review checks that otherwise unobserved branch.

```sh
python3 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/audit_source.py /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-408ebd53d4cb/stage-1
```

Failure name: `source/live-minimum-call-wait`; output reports `read_seconds: 60.0`, `connect_seconds: 15.0`, and the required minimum of 30. The complete runner invokes this check too.

## Evidence that passed and limits

Passing checks cover all listed statement phrases and legal suffixes, accented names/cities, employee-bucket and founding-year limits, dollar formats/scales and fractional-dollar rejection, negation, unsupported research claims, research-only evidence, header-only facts, copied prose citations, normalization, malformed/wrong-type input, signup/login rules, 50 simultaneous requests, keys and retries, field/timestamp preservation during failed refresh, reset/import cancellation, portable accounts/sessions/original idempotent responses, failed-key reuse after import, clock comparisons and destination-clock preservation, filtered pagination, in-flight cost visibility, and a workload reaching exactly 80 units without exceeding it.

Narrow source evidence covers the PyPI manifest/Docker installation, WebRouter routing, unused optional Tavily paths, scrypt hashing, unobservable timeout/no-page accounting branches, and live build/research upper bounds. Source review found no forbidden product material or direct provider bypass; development provenance beyond the submitted repository cannot be established by HTTP probes alone. No source read was used to excuse a failing black-box result.

The candidate was also started using `fserve` on port 20080; it answered HTTP. Docker buildx initially tried to write outside the sandbox, so the successful invocation put build metadata in the second-reader workspace. Probe bootstrap issues with Colima mounts/network access and a client path were corrected before the final run; they are not product findings.

The supplied check command was run only through the kit on this clean clone, with a new output directory each time. The successful command was:

```sh
cd /Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026
env BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/docker-buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-408ebd53d4cb --stage 1 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s1-408ebd53-02
```

It exited 0 and printed `claimed stage: 1 on the shipped checks`. This is sample evidence only and does not override the three independent findings. The earlier `...-01` attempt was a buildx sandbox failure and is not a product verdict. No later-stage specification or check log was opened.

`ledger-check 1 --phase audit --revision 408ebd53d4cb62fbbb460c876c1d9e9d6f8566e6` exits **1**, listing exactly S1-100, S1-121, S1-223, S1-226 and S1-246 as failing. There are no units lacking an evidence entry. A stage cannot pass until those findings are resolved or ruled otherwise.
