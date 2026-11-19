VERDICT: BLOCK
REVISION: 264a6a2b51ab10ff2e56c372e6d7e3671cdfbf00

## SR3-1 — Quiescent restart restores a clock older than its last read

**Units:** S3-150, S3-144; explicit ruling R3-5.

Before any reset/clock call, signup and a company build complete. Wait 1.1 seconds and read `/dossiers/chronicle.test/values?true_at=2025-09-01` without as_of; its returned as_of is an observed clock read. With no build running, SIGKILL/start the same container. New builds read an older, frozen clock:

```text
last observed default-as_of read  2026-11-17T02:28:05.710683+00:00
post-restart build time           2026-11-17T02:28:04.561262+00:00
next post-restart build time      2026-11-17T02:28:04.561262+00:00
```

The restored value is 1.149421 seconds earlier. R3-5 requires the last reading to survive, even in pre-reset moving mode. The assertion permits any later internal read; it rejects a restored value earlier than the exposed read.

```sh
SECOND_READER_ONLY=stage3-restart-pristine-clock /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-3/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/264a6a2b51ab/stage-3
```

Confirmation: **one failed, zero passed, 30 assertions, exit 1**. The previous focused run also failed the same condition. Safe timestamps: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-3/artifacts/pristine-clock.json`.

## Whole audit

The complete independent command `…/probes/stage-3/run.sh …/clones/264a6a2b51ab/stage-3` passed **224 tests, 14485 assertions** before the stronger last-read assertion was added. That earlier restart check established freezing only. The current one-argument runner includes the strengthened criterion; all other full-suite probes remain unchanged and passed. This is the only finding.

All 180 inherited checks pass. New temporal/executive/version/feed/concurrency/legacy/native transfer and other abrupt-restart cases pass under R3-1 through R3-6. The sixteen-page executive boundary retains 19 candidates and three members at 80 units; original boundaries remain complete and one-second-delay cases finish in 2.2–5.3 seconds. R3-6 permits search-only empty results; the fully read empty control also passes.

Browser routes at 375/1280 pass: 18 DOM audits, 460 visible text elements, no contrast/label or overflow findings. The prescribed sample claims Stage 3 with 122+12+9 checks passing. Other seats' PASS reports were read after the full run and do not override the subsequently strengthened clock probe; no other seat's test source was read.

Ledger audit exits **1** with two failed units and no missing evidence rows. All 150 units have required coverage as ruled. Details: `ledger/stage-3-audit-264a6a2b51ab.md`.

No product code/tests were edited. Probes remain private until all stages close. Supplied check sources, key.json, other seats' test sources and later-stage specifications stayed closed. All owned runtime resources were stopped.
