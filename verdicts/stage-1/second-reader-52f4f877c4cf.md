VERDICT: BLOCK
REVISION: 52f4f877c4cf853d78515f431a8b58a950ee1da0

# Independent Stage 1 audit

Two reproducible contract failures block this revision. The supplied isolated sample harness claims stage 1; that result does not override either independent finding.

## F1 — Invalid domain values containing an encoded slash bypass validation

Units: **S1-100, S1-153, S1-161, S1-162**. Ruling R1-5 explicitly applies domain validation to GET and refresh paths before resource lookup.

With a valid bearer token and, for refresh, a valid idempotency key, each request below returns **404 `not_found`**. The required response is **422 `validation_failed`**, because the path value is a URL or contains a path rather than a valid normalized hostname.

```http
GET /dossiers/https%3A%2F%2Fvalid.test
POST /dossiers/https%3A%2F%2Fvalid.test/refresh
GET /dossiers/valid.test%2Fpath
POST /dossiers/valid.test%2Fpath/refresh
```

Reproduction, from a clean clone of the stated revision:

```sh
SECOND_READER_ONLY=encoded-path-domain-validation /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1
```

The command builds and starts its own service and local mock, runs the required sample corpus, then reproduces all four requests. It exits nonzero. No product source was read to establish this finding.

## F2 — A fixture can create an account whose returned ID exceeds 64 characters

Units: **S1-090, S1-153, S1-161, S1-162**.

Reset with a seeded user whose `id` is 64 characters succeeds and the user logs in normally. Change that same ID to 65 characters: reset again returns **204**, and login returns a **65-character `user_id`**. S1-090 limits IDs to 64 characters. A correctly typed value that exceeds the stated limit must be rejected with **422 `validation_failed`**, leaving the prior fixture intact.

Reproduction:

```sh
SECOND_READER_ONLY=fixture-id-length-boundary /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1
```

The probe reports the accepted reset status and the returned ID length without disclosing credentials. It exits nonzero.

## Commands and scope

- Clean clone: `fclone 52f4f877c4cf853d78515f431a8b58a950ee1da0 /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-1-52f4f877c4cf` — exit 0; clone initially clean.
- Required start: `BUILDX_CONFIG=/Users/sunzeyu/dev/band-factory/work/second-reader/buildx fserve 52f4f877c4cf853d78515f431a8b58a950ee1da0 1 20010 --container-port 8097` — exit 0; health 200 on the nondefault container port.
- Independent suite: `SECOND_READER_FIRST=encoded-path-domain-validation,fixture-id-length-boundary /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-1-52f4f877c4cf/stage-1` — exit 1; **159 passed, 2 failed**, namely F1 and F2. The fresh-process clock prerequisite runs before tests that reset the service.
- Isolated sample check: `BUILDX_CONFIG=/Users/sunzeyu/dev/band-factory/work/second-reader/buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/sunzeyu/dev/band-factory/work/second-reader/clones/stage-1-52f4f877c4cf --stage 1 --mode isolated --out /Users/sunzeyu/dev/band-factory/work/checks/second-reader-s1-52f4f877-round1b`, from `/Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026` — exit 0, `claimed stage: 1`. No shipped check source was opened.

Independent probes cover the public sample, authentication, error taxonomy, domain and query boundaries, idempotency precedence and concurrency, logical clock behavior, refresh success/failure, supported/unsupported research citations, evidence beyond snippets and beyond ten initial results, pagination, reset during active work, repeated cross-process import, old tokens and replay records after transfer, source stop/restart after export, mid-build export snapshots, budget pressure, refusal/connection-loss/no-page costs, all listed legal suffixes and negators, statement phrases, Unicode words, conflicting values, headcount boundaries, and USD amount formats. Services run with 2 vCPU and 3 GiB and no Tavily configuration.

The independent runner uses a local bridge for host HTTP access: this Docker version does not publish host ports on an internal network. The dispatched harness separately verifies isolated runtime operation. Docker's default buildx metadata directory was sandbox-inaccessible; pointing BUILDX_CONFIG at a writable task directory fixed setup. These setup failures are not product findings.

## Source review after probes

Only implementation properties that could not be established through HTTP/mock observations were reviewed. No supplied checks, other-seat test source, or later-stage specification was read. No product file or product test was edited.

### Process provenance

The audit used only the opened Stage 1 specification, dispatch, committed rulings, allowed mock README/sample data, independently authored probes, and the exact candidate's delivery and narrowly scoped source files. Research results came from the local mock. Exports remained in process memory; no credential-bearing export was committed or posted. Product process-history compliance cannot be proven by HTTP alone; this review found no forbidden external product reference and introduced none.

### Delivery and dependencies

Reviewed `stage-1/Dockerfile`, `requirements.txt`, `constraints.txt`, and `RUN.md` at the stated revision using `sed -n`. Dockerfile installs dependencies during build, copies the application into the image, and starts Python inside that image. Requirements explicitly list both `webrouter>=0.12.0` and `webrouter[search,extract,research]>=0.12.0`; constraints pin WebRouter 0.12.0 and the provider SDK packages. Clean builds and the isolated harness substantiate bundled runtime dependencies. RUN.md's single-container command requires no Compose or host source import.

### Provider boundary

Reviewed `stage-1/app/providers.py` using `sed -n '1,260p'` and searched application call sites with `rg -n 'AsyncWebRouter|httpx|requests|urllib'`. Provider operations call only `AsyncWebRouter.search`, `.extract`, and `.research`; Nimble is the sole selected provider. The only urllib use is URL parsing. The SDK import is used for exception classification. Search explicitly passes `search_depth="lite"`; extract passes the URL and provider without setting render. Research supplies the company domain query and schema properties for all six fields. Nimble key/base environment configuration is left to WebRouter's provider. Optional Tavily base configuration is inapplicable because no Tavily call path is used.

### Unused provider paths

`providers.py` exposes only Nimble lite search, Nimble extract, and Nimble research. It has no fast/deep or Tavily call site. Thus the conditional pricing obligations for those unused calls have no runtime trigger in this implementation. `app/budget.py` also lists the correct Nimble fast/deep constants; active-call pricing is independently reconciled with the mock log.

### Password storage

Reviewed `app/passwords.py`, `app/state.py` lines 20–25, and the hashing sections of `app/routes.py` lines 50–68 and 78–94 after probes. Passwords are salted with 16 random bytes and hashed with scrypt (N=16384, r=8, p=1, 32-byte output); stored records hold a password_hash. Reset hashes its local candidate users before publishing state; signup hashes before creating a stored User. Verification recomputes scrypt and uses constant-time digest comparison. Login and unchanged-export transfer independently confirm hash usability.

### Budget reservations

Reviewed `app/budget.py` and `Gateway._call` in `app/providers.py`. Reservation checks include already-spent and outstanding reserved units, and happen before each awaited provider call. Settlement charges successes and uncertain transport delivery, refunds actual refusals, and is reflected in dossier spending. The event-loop-local reservation has no await between checking and incrementing. Independent budget-pressure, refusal, missing-page, and dropped-connection probes corroborate observable accounting.

### Live provider bounds

Reviewed `Timing.for_environment` in `app/providers.py`, the gather-time gates in `app/research.py` lines 81–104 and 150–154, and build completion in `app/service.py` lines 49–71. Live detection is an unset base URL or sdk.nimbleway.com hostname. Live call timeout is 45 seconds, research timeout 200 seconds, retry window 180 seconds, and gather window 200 seconds. Gathering therefore is not cut off during its first 120 seconds. Calls run in bounded concurrent phases; no new extract phase begins after the 200-second gather window, and a last ordinary call can extend to 245 seconds, below 300. This is source evidence, not a claim that real provider calls were made. Local mock timing and terminal state behavior were probed separately.

## Evidence status

All normative and ruled ambiguous rows receive revision-specific evidence references. Failing evidence remains attached to S1-090, S1-100, S1-153, S1-161, and S1-162; audit ledger-check must remain nonzero until those failures are fixed and reverified. No PASS is claimed for the stage.

`ledger-check 1 --phase audit --revision 52f4f877c4cf853d78515f431a8b58a950ee1da0` reports exactly those five failing units, with no missing evidence rows. Evidence covers 293 normative and five ruled ambiguous units. The readable ledger is regenerated. No verifier verdict existed at the time of the final post-probe check, so none was used as further evidence. The clean candidate clone remains unmodified. The fserve container and every probe-owned container/network were removed.

Private task-list creation was attempted through the advertised tools and rejected because approval policy is never. No shared-board or daemon fallback was used.
