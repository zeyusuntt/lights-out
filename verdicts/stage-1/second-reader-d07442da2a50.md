VERDICT: BLOCK
REVISION: d07442da2a5016e26e55e3f8b32a76e3d731c0dd

# Stage 1, round 3

F1–F4 pass. One remaining completeness defect blocks this revision: a valid supporting span later in a long sentence is missed. The full suite has **166 passes and 3 failures**, all three instances of F5 below.

## F5 — Valid later supporting spans are omitted with budget unspent

Broken units: **S1-121 and S1-223**, under **R1-2 and R1-6**.

Each positive case contains a contiguous 32- or 33-character excerpt that independently satisfies Appendix A.2. Nevertheless, the service ends ready, returns CEO unknown, and has 46 or 47 units unspent. R1-6 makes completeness apply where such a span exists; the stated 2,000-check implementation cap does not provide an exception to the requirement.

| Company | Supplied page prose | Eligible excerpt | Actual result |
|---|---|---|---|
| `reader-tail-span.test` | `context ` repeated 150 times, then `Reader Tail Span CEO: Dana Ruiz.` | `Reader Tail Span CEO: Dana Ruiz.` (32 characters) | ready, 33 units, CEO unknown |
| `reader-middle-span.test` | `context ` repeated 100 times, then `Reader Middle Span CEO: Dana Ruiz`, then ` context` repeated 100 times, then `.` | `Reader Middle Span CEO: Dana Ruiz` (33 characters) | ready, 33 units, CEO unknown |
| `reader-search-span.test` | `Reader Search Span offers background `, then `context ` repeated 100 times, then `Reader Search Span CEO: Dana Ruiz`, then ` context` repeated 100 times, then `.` | `Reader Search Span CEO: Dana Ruiz` (33 characters) | ready, 34 units, CEO unknown |

The first two pages are non-searchable and their Nimble all-six-field research answers serve their whole prose as the citation for CEO Dana Ruiz. The third page is searchable, served by search/extract, and has no research claim. These are ordinary page/research inputs of roughly 1.2–1.7 KB, comparable in length to the accepted F4 fixture.

Each eligible excerpt names the company, contains CEO, contains no negator, and contains exactly the person's name Dana Ruiz after excluding the company name and CEO phrase. It is a contiguous span of a single sentence, below 500 characters. The middle/search excerpts need no terminal period under the explicit R1-6 ruling. The surrounding lowercase filler introduces no other person or negating phrase.

Reproduce the minimal case from a clean clone of this revision:

```sh
SECOND_READER_ONLY=bounded-supporting-span-reader-tail-span.test /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1
```

Run all three variants plus the control by setting SECOND_READER_ONLY to:

```text
bounded-supporting-span-reader-tail-span.test,bounded-supporting-span-reader-middle-span.test,bounded-supporting-span-reader-search-span.test,bounded-supporting-span-reader-distant-span.test
```

The runner builds/starts the supplied stage and its own kit mock, runs the public sample, and prints counts before exiting nonzero. A separate targeted run reproduced all three failures: **2 passed, 3 failed** including sample and the control. The control has the company name at one end and CEO/value over 500 characters away, without a second company-name occurrence; it correctly remains unknown because no eligible span exists.

The finding is established by independent HTTP/provider-fixture probes. The product's citation parser/support implementation was not read to establish it.

## Retests and exact-revision commands

- `fclone d07442da2a5016e26e55e3f8b32a76e3d731c0dd /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-d07442da2a50` — exit 0; clone clean.
- `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx fserve d07442da2a5016e26e55e3f8b32a76e3d731c0dd 1 20010 --container-port 8097` — exit 0; health 200 on nondefault port.
- Retested F3/F4 first with `SECOND_READER_ONLY=research-header-shaped-prose-is-evidence,research-header-citation-is-not-prose,research-excerpt-length-limit .../probes/stage-1/run.sh <clone>/stage-1` — **4 passed, 0 failed**, including the public sample. Genuine Profile-prefixed prose is known; an actual Facts header stays unknown; the former 1,056-character citation now yields a supported, served contiguous span of at most 500 characters, with CEO known.
- Complete suite: `SECOND_READER_FIRST=research-header-shaped-prose-is-evidence,research-header-citation-is-not-prose,research-excerpt-length-limit /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-d07442da2a50/stage-1` — **166 passed, 3 failed**, exit 1, F5 only. The initial-clock prerequisite runs before cases that reset the fresh process.
- Isolated check, from the kit directory: `BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-1-d07442da2a50 --stage 1 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s1-d07442da-round3` — exit 0, **claimed stage: 1**. The sample check is further evidence, not a stage verdict.

All previous probes were rerun, including F1/F2, concurrency, retry precedence, reset/import while builds run, cross-process transfer and source stop/restart after export, clocks, exact-domain search counting, budgeting/transport faults, all legal suffixes/negators, field formats, Unicode, and amount/headcount boundaries. No new failure outside F5 was observed.

## Further evidence from the verifier

After the independent full suite and separate span retest, read `verdicts/stage-1/verifier-d07442da2a50.md`. It reports BLOCK, 183/185, with both failures caused by a supported founding-year span late in a 799-character sentence, spending 34 units. Its V3-1 independently corroborates this completeness finding on a different company and field. It also reports F3/F4 fixed and citation lengths valid. Those results are attached as further evidence; no verifier test source was read, and the independent finding was not changed to match the peer's report.

## Source review after probes

Only externally unobservable implementation obligations were inspected. Fresh byte comparisons against the previous audited clean clone show unchanged Dockerfile, requirements, constraints, providers.py, budget.py, passwords.py, service.py, and routes.py. RUN.md changed; its single-container build/start command remains the same. A fresh search of WebRouter/network imports and hashing call sites, and inspection of live gather gates, confirm the prior boundary review on this exact revision.

### Process provenance

Used only opened-stage requirements, dispatch, rulings, permitted mock README/sample data, independent probes, and exact-revision delivery/narrow source evidence. No supplied check source, mock key.json, other-seat test source, or later-stage specification was opened. No product file/test was edited. Exports stayed in memory. Probes use a local bridge for host HTTP access; the dispatched harness separately verifies isolated operation.

### Delivery and dependencies

Dockerfile SHA-256 `7d4711867f99cc0549b2abfe119d9c564b961ed11140a9c105f979e32f3e35a9`; requirements SHA-256 `6e94dab8b2f77a2a420f3e3a77f92faeacee84bdbd9973e93d83bd37b9bc3de4`, both unchanged. The manifest includes webrouter>=0.12.0 and its required extras, dependency installation happens in the image build, and the image runs without Compose/host imports. Fresh build/start, nondefault PORT, CPU/memory limits and isolated checks were rerun. RUN.md SHA-256 is `5ee55e8ac0f7f44c15e0654ec4e9de95e027020c2d981a5077064aa40b39e74f`; its updated research description was read, with no product test referenced there opened.

### Provider boundary

providers.py SHA-256 `875591682dac33a8a0a70a88b2ab9fb9b060d667fd0385fec88b4c902e4f251e`, unchanged. Fresh `rg -n 'AsyncWebRouter|httpx|requests|urllib' <clone>/stage-1/app -g '*.py'` shows the same WebRouter-only provider boundary and URL parsing/server request imports. Search/extract/research select Nimble; extract does not set render; all-six-field research names the domain and schema fields. Provider traces corroborate active operations and costs.

### Unused provider paths

The unchanged boundary has only Nimble lite search, extract and research paths. Fast/deep and Tavily calls remain unused, so their conditional costs have no runtime trigger. Active-operation costs are independently reconciled against the mock.

### Password storage

passwords.py SHA-256 `7ae7952a14c1eaa3e8c654eee14c51173ac8b8ed672c5005f7bb28f690e0904b`; routes.py SHA-256 `145fff40af2bedea8398adabf9da0816e09a16629508353440a734f87a45182a`, unchanged. The reviewed salted scrypt storage and off-loop hashing/verification calls remain intact. Fresh hashing-call search, signup/seeded login and unchanged-export transfer corroborate this.

### Budget reservations

budget.py SHA-256 `1c25aef93a8f35c96836e3c2d1e43544dc40df1efb6dfbfab0d519f8e0ec67e0`, unchanged. Reservation includes outstanding reservations and precedes provider awaits; unchanged Gateway settlement distinguishes refusals from uncertain delivery. Budget pressure, no-page extract, provider error and dropped-connection accounting probes pass.

### Live provider bounds

The provider timing and service completion files are unchanged. Fresh `rg -n 'may_gather|async def run|await self._searches|await self._extract' <clone>/stage-1/app/research.py` confirms the same gather-phase time gates, now also covering header-shaped claim-page extracts. Live configuration retains the 45-second ordinary-call timeout, 200-second research/gather windows and 180-second retry window. These bounded phases preserve the earlier source argument for completing below 300 seconds without a first-120-second gathering cutoff. No real provider call was made.

## Ledger and cleanup

Evidence is refreshed for all 293 normative and five ruled ambiguous units, retaining earlier revision records. R1-6 is explicitly attached to the affected citation/completeness rows. Current failures are limited to S1-121 and S1-223; the audit check must remain nonzero. This is not a PASS.

The exact clone remains unmodified. All probe containers/networks and the fserve container have been removed. Probes remain private until all stages close. Private task creation was attempted through the advertised tools and rejected by approval policy; no shared-board fallback was used.
