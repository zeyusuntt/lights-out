VERDICT: BLOCK
REVISION: b9d46b6fd9eabedd13ecc8fb09aa6247ad1fcf17

# Stage 1, round 2

Both previously reported failures are fixed. Two new research-citation failures block this revision: a valid supporting excerpt is omitted when genuine prose begins with a header-shaped label, and a research citation can exceed the 500-character limit.

## F3 — Valid research prose beginning with `Profile:` is left unknown

Broken units: **S1-121 and S1-223**, under ruling **R1-2**. Relevant definitions: S1-139 (everything after the page header's first blank line is prose), and Appendix A.

The independently authored mock company `reader-research-prose.test` has one non-searchable page at `https://reader-research-prose.test/page-0`. Its entire prose, after the mock's ordinary header and blank line, is:

```text
Profile: Reader Research Prose CEO: Dana Ruiz.
```

The all-six-field Nimble research answer serves the same sentence for that URL and claims `ceo: "Dana Ruiz"`. The sentence is a single sentence, names this company, contains `CEO`, has no negating phrase, and has exactly one eligible person's name, `Dana Ruiz`. `Profile:` is part of the page's prose; it is not one of the page's initial header lines. Thus this research claim is supporting evidence under §4 and Appendix A.

Observed: the service ends **ready**, spends **33 units**, and returns **ceo unknown**, with value null and no citations. It therefore omits supported evidence with 47 units unspent. This violates the foreman's explicit completeness ruling. The failure reproduces in both the full suite and a separate targeted run.

Reproduce on a clean clone of this exact revision:

```sh
SECOND_READER_ONLY=research-header-shaped-prose-is-evidence /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1
```

The command builds and starts its own service and mock, runs the sample corpus, then runs the named case. It exits 1 and prints the ready state, spending, unknown CEO, and the provider-served sentence. No product source was read to establish this failure.

Paired regression probes pass: an actual `Facts:` header citation is rejected, and six ordinary research-only supporting citations retain their exact served excerpts and complete at 27 units with no redundant extract.

## F4 — A research citation exceeds the 500-character limit

Broken unit: **S1-127**.

An ordinary non-searchable page for `reader-research-long.test` has one prose sentence: `Reader Research Long CEO: Dana Ruiz`, followed by ` with published company background` repeated 30 times, followed by a period. Nimble research serves that same complete sentence as the CEO citation. The service ends ready and asserts CEO Dana Ruiz with that entire **1,056-character excerpt** as its citation. The contract allows 1–500 characters, without an exception for research citations.

Reproduce:

```sh
SECOND_READER_ONLY=research-excerpt-length-limit /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1
```

This independently observed follow-up was motivated by the verifier's post-probe length note. The targeted command exits 1 and prints `research citation length 1056`, the URL, field CEO, and state ready. It uses normal provider-served page prose and does not inspect product code. A final full-suite run also includes this case.

## Retests and verification

- `fclone b9d46b6fd9eabedd13ecc8fb09aa6247ad1fcf17 /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-b9d46b6fd9ea` — exit 0; clean clone.
- `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx fserve b9d46b6fd9eabedd13ecc8fb09aa6247ad1fcf17 1 20010 --container-port 8097` — exit 0; health 200.
- First, `SECOND_READER_ONLY=encoded-path-domain-validation,fixture-id-length-boundary .../probes/stage-1/run.sh <clone>/stage-1` — **3 passed, 0 failed**, including the mandatory sample run. F1 now returns 422 on all four encoded-slash GET/refresh requests. F2 accepts a 64-character ID, rejects 65 characters with 422, and preserves the prior user identity.
- Then, `SECOND_READER_FIRST=encoded-path-domain-validation,fixture-id-length-boundary /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-b9d46b6fd9ea/stage-1` — initial complete run **163 passed, 1 failed**, exit 1 (F3); final complete run with F4 added **163 passed, 2 failed**, exit 1 (F3 and F4 only). The fresh-process clock prerequisite precedes cases that reset the service.
- Separate research retest with `SECOND_READER_ONLY=research-citations-verbatim-prose-and-reuse,research-header-citation-is-not-prose,research-header-shaped-prose-is-evidence` and the same runner/clone — **3 passed, 1 failed**, exit 1. F3 again ends ready at 33 units; diagnostics show the exact research-served sentence quoted above.
- From the kit directory, `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-b9d46b6fd9ea --stage 1 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s1-b9d46b6f-round2` — exit 0, **claimed stage: 1**. This sample is further evidence, not a stage verdict.

All the first-round probes were rerun, including concurrency, reset during a build, import during a build, unchanged cross-process transfer after stopping/restarting the source, idempotent retries, provider errors, budget pressure, no-page extraction and connection-loss costs, all legal suffixes and negators, Unicode names, conflicting values, headcount boundaries, and amount formats. The runner builds the supplied stage folder itself and requires no second argument.

## Further evidence from the verifier

Only after the independent full suite completed, read `verdicts/stage-1/verifier-b9d46b6fd9ea.md`. The verifier reports PASS, 177/177, both earlier findings fixed, 81/81 supported fields on its corpus, and no research re-extraction. Those results are attached as further evidence where relevant. Its corpus result does not exercise the counterexample above and does not change this independent finding. No verifier test source was read.

## Source review after probes

Source was used only for implementation properties that HTTP/mock observations cannot establish. Fresh byte comparisons against the first audited clean clone confirm unchanged Dockerfile, RUN.md, dependency manifests, providers.py, budget.py, passwords.py, and service.py. Changed parser behavior was evaluated through the black-box cases above.

### Process provenance

Only the opened specification, dispatch, rulings, allowed mock README/sample corpus, independent probes, and exact-revision delivery/narrow source review were used. No shipped check source, mock answer key, later-stage specification, or other seat's test source was opened. No product code or product test was edited. Exports stayed in process memory; no credential-bearing artifact was committed or posted. The suite uses a local bridge for host HTTP; the dispatched harness separately verifies isolated operation.

### Delivery and dependencies

Dockerfile SHA-256: `7d4711867f99cc0549b2abfe119d9c564b961ed11140a9c105f979e32f3e35a9`. Requirements SHA-256: `6e94dab8b2f77a2a420f3e3a77f92faeacee84bdbd9973e93d83bd37b9bc3de4`. Both are byte-identical to the reviewed first candidate. The manifest lists webrouter>=0.12.0 and its search/extract/research extras; the image installs its pinned dependencies at build time and starts the HTTP process inside the single container. Clean builds, nondefault-port startup, 2-vCPU/3-GiB runs and isolated checks were rerun.

### Provider boundary

`app/providers.py` SHA-256: `875591682dac33a8a0a70a88b2ab9fb9b060d667fd0385fec88b4c902e4f251e`, unchanged. Fresh `rg -n 'AsyncWebRouter|httpx|requests|urllib' <clone>/stage-1/app -g '*.py'` finds the same WebRouter boundary, URL parsing/unquoting, and HTTP-server request imports. Provider search/extract/research operations route through AsyncWebRouter, select Nimble, use environment configuration, and do not set render on extract. Research schema/query names all six fields and the company domain. Provider logs corroborate each active operation.

### Unused provider paths

The unchanged boundary uses Nimble lite search, extract, and research only; fast/deep and Tavily call paths remain absent. Their conditional call-cost requirements therefore have no runtime trigger. Actual active costs are reconciled independently against the mock log.

### Password storage

`app/passwords.py` SHA-256: `7ae7952a14c1eaa3e8c654eee14c51173ac8b8ed672c5005f7bb28f690e0904b`, unchanged. Salted scrypt parameters and comparison behavior remain as reviewed in round 1. Fresh `rg -n 'hash_password|password_hash|User\('` plus the relevant reset/signup sections of routes.py confirms candidate reset users are hashed before state publication and signup hashes before storing its User. Hashing uses asyncio.to_thread. Seeded/new login and unchanged-export hash usability were rerun.

### Budget reservations

`app/budget.py` SHA-256: `1c25aef93a8f35c96836e3c2d1e43544dc40df1efb6dfbfab0d519f8e0ec67e0`, unchanged. Reservation includes outstanding reservations and occurs before each provider await. The unchanged Gateway settles refusals versus uncertain transport delivery. Budget-pressure, missing-page, refusal and connection-loss accounting probes all pass again.

### Live provider bounds

providers.py and service.py are byte-identical to the previously reviewed candidate. Fresh research.py gate inspection confirms gathering/extraction still checks may_gather around the same bounded phases. Live configuration retains the 45-second ordinary call timeout, 200-second research/gather windows, and 180-second retry window; a final bounded phase stays below 300 seconds and gathering is not cut off before 120 seconds. This is source evidence; no real provider call was made.

## Ledger status

Revision-specific evidence is refreshed for all 293 normative and five ruled ambiguous units, while preserving prior-revision evidence. S1-121, S1-127 and S1-223 retain failing evidence for this revision. Audit ledger-check must remain nonzero; this is a BLOCK, not a PASS.

The exact-revision clone remains clean. The fserve container and all probe containers/networks have been removed. Probes remain private pending the foreman's all-stages-closed instruction.

Private TaskCreate was again rejected by the runtime's approval-policy setting. No private-lane or shared-board workaround was used.
