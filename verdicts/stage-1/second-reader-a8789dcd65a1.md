VERDICT: PASS
REVISION: a8789dcd65a18ca385d968116c51d23590913c33

# Stage 1, round 4

**PASS: 183 independent probes passed, none failed.** F1–F5 are fixed. The isolated sample harness claims stage 1. All 293 normative and five ruled ambiguous ledger units have passing evidence for this exact revision, and `ledger-check 1 --phase audit --revision a8789dcd65a18ca385d968116c51d23590913c33` exits 0.

## Exact-revision verification

- `fclone a8789dcd65a18ca385d968116c51d23590913c33 /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-1-a8789dcd65a1` — exit 0; clean clone.
- `BUILDX_CONFIG=/Users/sunzeyu/dev/band-factory/work/second-reader/buildx fserve a8789dcd65a18ca385d968116c51d23590913c33 1 20010 --container-port 8097` — exit 0; health 200 on the nondefault port.
- First retest: `SECOND_READER_ONLY=bounded-supporting-span-reader-tail-span.test,bounded-supporting-span-reader-middle-span.test,bounded-supporting-span-reader-search-span.test /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clone>/stage-1` — **4 passed, 0 failed**, including the mandatory sample. All three F5 variants now return known Dana Ruiz with supported, served spans no longer than 500 characters.
- Complete suite: `SECOND_READER_FIRST=bounded-supporting-span-reader-tail-span.test,bounded-supporting-span-reader-middle-span.test,bounded-supporting-span-reader-search-span.test,late-founded-year-799-character-sentence /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-1-a8789dcd65a1/stage-1` — **183 passed, 0 failed**, exit 0. The fresh-process clock prerequisite precedes cases that reset the service.
- From the kit directory: `BUILDX_CONFIG=/Users/sunzeyu/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-1-a8789dcd65a1 --stage 1 --mode isolated --out /Users/sunzeyu/dev/band-factory/work/checks/second-reader-s1-a8789dcd-round4` — exit 0, **claimed stage: 1**. This sample result is further evidence, not the basis of this verdict.

The runner builds and starts the supplied stage folder itself; its root run.sh requires only that folder argument. No product module is imported on the host. Services run with 2 vCPU and 3 GiB, Nimble alone, and mock providers. Host HTTP probes use a local bridge; the dispatched harness separately exercises isolated operation.

## R1-7 and the new span algorithm

All earlier probes were retained. Added independent checks cover the requested algorithm boundaries:

- A searchable 799-character sentence with a late founding-year span returns 1952. This independently reconstructs the reported V3-1 shape; it does not read or copy the verifier's private corpus. The exact ironvale case is additionally reported passing by the verifier below.
- Short supporting prose is cited whole, including its punctuation. Short negated or competing-value sentences remain unknown even when a prefix alone could look supportive.
- Long-sentence spans retain complete words, grouped numbers, decimals, USD amounts/scales and Unicode capitalized-name/place runs. Cases include `$12 million`, `1,200`, `$12.5 million`, `12 million dollars`, San Luis Obispo and Élodie Maria Müller. A four-word name cannot become an eligible three-word CEO by clipping, and amount-contained 2014 cannot become a founding year.
- The no-eligible-span control correctly remains unknown when the only company name is over 500 characters from the field statement/value.
- A roughly 400 KB single sentence with its supported fact in the middle completes within the 10-second bound while 50 concurrent health requests meet their request bounds. The complete probe, including reset, concurrent requests and citation checks, took **0.477 seconds**. A dense negative sentence with 100 repeated company/phrase/value groups also passes, with a complete probe time of **0.260 seconds**. These are mock/local measurements, not live-provider latency claims.

The oracle's edge checks are independent of product code: they locate the returned span in served text and reject edges inside alphanumeric words, numeric groups, amounts or runs of capitalized words. The existing short-sentence expectations already used whole sentences, so no short-span acceptance was carried forward. These probes belong to the second-reader's unsealed private suite; no sealed verifier suite was edited.

The full run also covers authentication, error precedence and formats, domain/query boundaries, same-key and same-domain concurrency, original replay bodies, clocks, refresh success/failure, reset/import during builds, cross-process transfer, source stop/restart after export, imported tokens/password hashes/retries, budget pressure and transport/no-page/refusal costs, exact-domain search counting, citation provenance, research completeness, all listed legal suffixes and negators, field formats and Unicode.

## Further evidence from the verifier

Only after the independent full run completed, read `verdicts/stage-1/verifier-a8789dcd65a1.md`. It reports PASS, **186/186**, exact ironvale and F5 retests passing, R1-7 whole-sentence/edge assertions, a dense 30,874-character timing check, and the isolated sample claiming stage 1. Its reported results are attached as further evidence. No verifier test source was read, and the independent result was established before this read.

## Source review after probes

Source was used for properties that cannot be established fully from HTTP observations. Fresh byte comparisons against the previous audited clean clone confirm unchanged Dockerfile, requirements, constraints, providers.py, budget.py, passwords.py, service.py and routes.py. RUN.md changed and was read; its single-container build/start command remains intact. Citation correctness and edge behavior were established through the black-box probes; the internal absence of a search cap was separately checked below.

### Process provenance

Used only opened-stage requirements, dispatch, committed rulings, permitted mock README/sample data, independent probes and narrowly scoped exact-revision source/delivery evidence. No supplied check source, mock key.json, other-seat test source or later-stage specification was opened. No product file or product test was edited. Exports remained in memory; no credential-bearing artifact was committed or posted.

### Delivery and dependencies

Dockerfile SHA-256 `7d4711867f99cc0549b2abfe119d9c564b961ed11140a9c105f979e32f3e35a9`; requirements SHA-256 `6e94dab8b2f77a2a420f3e3a77f92faeacee84bdbd9973e93d83bd37b9bc3de4`, unchanged. The manifest includes webrouter>=0.12.0 and the search/extract/research extras. Dependency installation occurs at Docker build time; the image starts the HTTP process without Compose or host imports. Fresh builds, nondefault PORT, resource-limited runs and isolated checks pass. RUN.md SHA-256 is `64527a502bda62c1668187117bfa3b5c53bdedac322328bad535e88dde82a18e`; its cited product tests were not opened.

### Provider boundary

providers.py SHA-256 `875591682dac33a8a0a70a88b2ab9fb9b060d667fd0385fec88b4c902e4f251e`, unchanged. Fresh `rg -n 'AsyncWebRouter|httpx|requests|urllib' <clone>/stage-1/app -g '*.py'` shows the same WebRouter-only provider call boundary and URL/server request utilities. Search/extract/research select Nimble; extract does not set render; all-six-field research names the normalized domain/schema fields. Logs corroborate active call types, provenance and pricing.

### Unused provider paths

The unchanged boundary uses Nimble lite search, extract and research only. Fast/deep and Tavily operation paths remain absent, so their conditional pricing rules have no runtime trigger. Active costs are independently reconciled against mock logs.

### Password storage

passwords.py SHA-256 `7ae7952a14c1eaa3e8c654eee14c51173ac8b8ed672c5005f7bb28f690e0904b`; routes.py SHA-256 `145fff40af2bedea8398adabf9da0816e09a16629508353440a734f87a45182a`, unchanged. Salted scrypt storage remains intact. Fresh hashing-call search shows asyncio.to_thread at reset/signup/verification call sites. Login and unchanged-export transfer confirm seeded/new/imported hash usability.

### Budget reservations

budget.py SHA-256 `1c25aef93a8f35c96836e3c2d1e43544dc40df1efb6dfbfab0d519f8e0ec67e0`, unchanged. Reservations account for spent and outstanding units before each provider await. Gateway settlement/refusal classification is unchanged. Budget-pressure, no-page extract, provider error and connection-loss probes all pass.

### Live provider bounds

Provider timing and service completion files are unchanged. Fresh `rg -n 'may_gather|async def run|await self._searches|await self._extract' <clone>/stage-1/app/research.py` confirms the same bounded gather phases, including header-shaped claim-page extraction. Live configuration retains the 45-second ordinary-call timeout, 200-second research/gather windows and 180-second retry window. The previously reviewed bounded-phase argument remains below 300 seconds without an initial-120-second gathering cutoff. This is source evidence; no real provider was called.

### Span search

After the probes, inspected `app/support.py` lines 352–430 solely to verify the internal no-cap requirement. `citable` sends sentences at most MAX_CITATION directly to whole-sentence support. Longer sentences iterate value occurrences and neighboring company/phrase occurrences, widen edges, and recheck support. There is no fixed iteration/check counter or early exhaustion limit. Fresh `rg -n 'def citable|MAX_SPAN|2000|cap'` also finds no former scan cap. Functional correctness and safe-edge effects are covered by the independent probes above.

## Ledger and cleanup

All 379 units are accounted for: 293 normative, five ruled ambiguous, 81 informative. Every normative/ambiguous row has passing evidence for this exact hash, with R1-6/R1-7 attached where relevant. Earlier-revision failures remain historical evidence and do not apply to this verdict. Audit ledger-check exits 0 with no gap.

The candidate clone remains clean. All probe containers/networks and the fserve container were removed. Probes remain private until the foreman says every stage has closed; no publication was performed.

Private TaskCreate was attempted through the advertised tools and rejected by approval policy. No shared-board fallback was used.
