# Stage 3 rulings

Ledger: ledger/stage-3.jsonl at 6777747b1a684cca8890d7ed968da7e3a89a60dc. Spec: stage-3.md. Stage-1 rulings R1-1..R1-7 and stage-2 rulings R2-1..R2-5 continue to apply.

## R3-1 — S3-070: `spent_units` of an `as_of` response

Readings: (a) every build whose time is at or before `as_of`, including what an in-flight build has incurred so far; (b) completed builds only.
Chosen: **(a)**. Basis: **EXPLICIT**.
Why: "`spent_units` is the total of the builds whose time is at or before `as_of`". That is not limited by outcome or completion, and it matches stage-1 §8, where current `spent_units` already includes in-flight spending. With `as_of` at or after the current time, the `as_of` total equals the current `spent_units`. The fields and `researched_at` still come only from the latest qualifying build that completed `ready`.

## R3-2 — S3-102: `learned_at` of a history entry whose value is null

Readings: (a) the time of the build that made the transition; (b) null.
Chosen: **(a)**. Basis: **EXPLICIT**.
Why: "An entry whose value is null has `"true_from": null` and `"citations": []`". The sentence names exactly those two as null, and names no null `learned_at`. For a selected value, `learned_at` is "the time of the build that made it the selected value", and that build exists. The history entry and its feed entry carry the same `learned_at`. The current field, while it is `unknown`, has `learned_at` null (Two times per value).

## R3-3 — S3-129 / S3-130 / S3-133: upgrading from the accepted stage-2 export

Foreman finding (from reading the accepted stage-2 export code, stage-2/app/state.py `export`): per dossier, the stage-2 export holds only the current view: state, `researched_at`, cumulative `spent_units`, and the six fields with their last-ready candidates (value, url, excerpt, provider, kind, published_at, retrieved_at, selected). It keeps no list of past builds, no `Effective` lines, and no gathered pages without candidates. Stage 2 is frozen, and import makes no provider call.
Chosen: **(b)**, the analogue of R2-5. Basis: **SILENT → assumption** (the specification assumes an export holds what this one does not).
- A dossier from a stage-2 export with non-null `researched_at` counts as **one** build that completed `ready` at `researched_at`. Its spending is the exported `spent_units`, all of it. Its candidates are the exported candidates. It gathered one page version per distinct candidate URL, with `true_from` equal to the UTC date of that page's `published_at`, or null (no Effective was kept). A dossier with `researched_at` null has no ready build: every `as_of`, and `/values`, is 404 until a build completes. Its spending still counts toward a later `as_of` total as a build at no time; tests do not assert that case.
- Imported candidates have `learned_at` equal to `retrieved_at`, and gain `true_from` as above.
- History: one `initial` entry per field that has a value. Its `learned_at` is `researched_at`, and its `true_from` is the selected candidate's `true_from` (the exported state records `published_at`, which gives the date). The feed starts empty. `executives` is `unknown`, with no history entry.
- S3-133 then needs no reconciliation: there is exactly one imported build, and the one `initial` row describes it.
- A stage-1 export imports as the spec says, with candidates per R2-5: one build at `researched_at`, and every `true_from` null.
- Earlier stage-2 builds, failed builds, Effective dates and candidate-free versions that the export did not keep cannot be recovered. This is a limitation of the accepted stage-2 folder, and the final report names it. Tests must not require them.
- A **stage-3** export must keep everything: every build with its time, outcome and spending, every page version including candidate-free ones, and the history, feed, seq counter and candidates' `learned_at`. A stage-3 → stage-3 import then answers `as_of`, `/values`, history and changes exactly as the exporter did.

## R3-4 — S3-142: abrupt stop while a build is running

Readings: (a) the interrupted build may be failed or resumed, with no partial state exposed; (b) only an idle stop is specified; (c) roll back to the pre-build snapshot.
Chosen: **(c)**, with (a)'s guarantees as the minimum. Basis: **IMPLIED** (the spec guarantees only an idle stop; R1-4 already defines how a running build is seen by a snapshot).
After a restart that interrupted a build:
- The dossier is as it was before that build: its fields, candidates, `researched_at`, history and feed. Its state is the outcome of its last completed build, or `failed` with every field unknown if it had none. No partial selected value, history entry or feed entry from the interrupted build is ever visible. It is not stuck in `building`, and a new refresh starts a new build normally.
- Every completed operation survives: accounts, tokens, other dossiers, the clock and completed idempotent responses. The 202 that started the interrupted build stays replayable as recorded.
- `spent_units` is at least the pre-build value. Spending durably recorded for the interrupted build may be kept (it was really incurred). Tests accept either the pre-build value or that value plus what the interrupted build recorded, at most 80.
- Writes must be crash-atomic: write a temporary file, fsync, then rename, or use an equivalent transactional store, so that a kill mid-write never leaves corrupt or half-written state. State lives in the container's filesystem, not on a mounted volume.

## R3-5 — S3-150 versus R1-1: a restart before any reset or clock call (second-reader DISPUTE)

Readings: (a) the restart freezes the clock at the last time it read; (b) the pre-reset system-time mode survives the restart.
Chosen: **(b)**. Basis: **SILENT → assumption**. The sentence is ruled not to reach this input.
Why: "The clock reads the time it read before the stop until reset or `POST /_test/clock` moves it" describes a standing clock, which is the clock after a reset or a valid clock call (R1-1). Before either, the clock "follows the system time" (stage-1 §3.4). The restart guarantee is that the service "answers after the restart exactly as it did before the stop", and a clock in system-time mode was answering with the system time. Freezing it at an arbitrary last read would also require a durable write on every read, which nothing else asks for. So after a restart that comes before any reset or clock call, the clock still follows system time. Once the clock is standing, a restart preserves its exact time (S3-150), and that case is required.
