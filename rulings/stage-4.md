# Stage 4 rulings

Ledger: ledger/stage-4.jsonl at bbd39040608627394ff3b60e24d958e7cd9a6214. Spec: stage-4.md. All earlier rulings continue to apply, except that R3-4 is superseded by stage-4 Restarts (below).

## R4-0 — stage-4 Restarts supersedes R3-4 for builds running at a kill

Basis: **SUPERSEDED** (stage-4 Restarts says so explicitly).
After a restart, a build that was running does not stay `building`. It ends `ready` or `failed` within 10 s of `/health` first answering 200, when its calls answer within 1 s. It may resume or fail. A failed end leaves fields, history and feed as they were.
Every unit a provider billed, before and after the stop, counts in the dossier's `spent_units`, and also in the batch's `spent_units` for a batch build. Calls in flight at the stop may also be counted. So units must be reserved and durably recorded **before** each call is sent, and the reservation is settled after the call. Per-build totals across the restart stay at or below 80, and a batch's at or below `budget_units`.

## R4-1 — S4-028: is a Canonical original candidate evidence?

Chosen: **(a)**. Basis: **EXPLICIT** (§4 and stage 2 define the evidence, and stage 4 does not widen it).
An original fetched only to resolve an origin is lineage only. It yields candidates only when it is itself evidence: returned by a company-naming search, or cited by a research claim (R1-2 universe). Its served text may be reused within the build if it later turns out to be evidence.

## R4-2 — S4-030: the budget prevents fetching a needed original

Chosen: plan first, then **(a)** as the fallback. Basis: **SILENT → assumption**.
A build that gathers a page with a `Canonical` URL other than its own should reserve the fetch of the original (and of any further hop needed, up to the limit) before spending on lower-value calls. If the per-build cap or the batch budget still makes a needed original unaffordable, the copy's origin is the normalised host of the URL that could not be fetched, exactly as for an original that no provider serves. Its candidates are kept. This treats "cannot be obtained" alike whether the cause is the budget or the provider.

## R4-3 — S4-033: do `/values` fields carry origins/corroborated/corroborated_since?

Chosen: **(a)**. Basis: **IMPLIED**.
The three keys are defined from selected-value history and standing origins of the dossier's builds. They are required on the field objects of `GET /dossiers/{domain}`, with and without `as_of` (an `as_of` response computes them from history and builds at or before `as_of`). `/values` field objects keep `value`, `true_from` and `citations`, with the investor membership rules. Tests must not require the three keys on `/values`. Including them there is not a defect.

## R4-4 — S4-049: member `corroborated_since` after a weak member leaves

Chosen: **(b)**. Basis: **EXPLICIT**.
"the time of the earliest ready build after which every member has had two or more standing origins". This is evaluated after each ready build, against the members of the field **as they stood after that build**. If at T0 A has 2 origins and B has 1, the condition fails after T0. If B leaves at T1 while A still has 2, the condition first holds after T1, so `corroborated_since` = T1. It never backdates before the build at which the condition first held for the current run. When the condition later fails, it becomes null, and when it holds again it is that build's time.

## R4-5 — S4-089: is `budget_units` 1.0 or 1e0 an integer?

Chosen: **(a)**. Basis: **IMPLIED** (stage-1 §5 already treats `4.0` and `1e9` as non-integers for integer-valued parameters, and the row says "whatever its JSON type").
Only a JSON number written without a fraction or exponent, and not a boolean, is an integer. `1.0`, `1e0`, `1.5`, `true`, `"1"` and `null` are each 422 `validation_failed` (this row takes precedence over 400). An integer from 1 to 100000 is valid.

## R4-6 — S4-098: one unaffordable call in a batch

Chosen: **(a)**. Basis: **EXPLICIT**.
"When the budget would be exceeded by a further call, the batch makes no more provider calls." The first call whose units cannot be reserved within the remaining batch budget latches the batch: no build in it makes any further provider call, even a cheaper one. Its builds then complete from what they hold, with each field known exactly when that supports a value. Builder: order each build's plan so the highest-value calls come first. Concurrent builds of one batch reserve against the shared remainder atomically, and the latch is decided at reservation time.

## R4-7 — S4-111: batches in a native stage-4 export and import

Chosen: **(a)**. Basis: **IMPLIED** (stage-1 §10 says import "atomically replaces the service's state", R1-4 covers running builds, and stage-4 Restarts makes batches part of the state).
- A stage-4 export holds every batch: id, owner, domains, `budget_units`, its builds and `spent_units`. A running build in it is settled as in R1-4: the dossier as before that build. In the exported batch that build counts as not having run, so the batch's `spent_units` is the spending of its completed builds, and its state is `done` once none of its builds is still to run after import.
- Import makes no provider call and resumes nothing. After import every imported batch is `done`, and `GET /batches/{id}` answers for its owner (404 for others). The original `POST /batches` replays its original 202 body (D7).
- Stage-1, 2 and 3 exports hold no batches.

## R4-8 — S4-109 / S4-118: refused attempts whose refund was not yet durable at a kill (second-reader DISPUTE)

Readings: (a) a call already answered with an error before the stop is not in flight, so its units must not be counted after the restart; (b) its durable reservation may be counted until a settlement is recorded.
Chosen: **(a)**. Basis: **EXPLICIT**.
Why: stage-4 Restarts allows counting only calls "that were in flight at the stop and that no provider billed". A call the provider has already answered with an error status is complete, and it "costs nothing" (§9, stage-4 Provider failure). The restart rules also require everything else to be "answered as before the stop": a dossier showing `spent_units` 0 before the kill must not show 35 after it, merely because a refund lived only in memory. Builder: record a call's settlement (refund on refusal, or final cost) durably no later than the moment it becomes visible in any response. Equivalently, do not expose a refund in memory before it is persisted. Only reservations for calls that had no answer at the stop may be counted after a restart.

## R4-9 — S4-002 / S4-098: planning a build under a tight caller budget (second-reader DISPUTE, round 2)

Case: batch-reader-aa.test, budget 30. One searchable page, rendered for 3u, supplies all eight fields. The build starts a 25u research run, spends the remaining 5u on lite searches, latches, and ends ready at 30u with every field unknown. At budgets 14 and 20 it gets all eight.
Readings: (a) genuine exhaustion of the caller budget excuses the loss, since the batch rule only says builds complete with what they obtained; (b) the build must plan so that affordable evidence is not displaced by calls that cannot yield it.
Chosen: **(b)**. Basis: **IMPLIED** (the dispatch event rules: "correctness comes first: a saving that leaves out evidence a field needs is a defect" and "plan the searches once per build"; R4-6 already requires the highest-value calls first). The batch rule's completion clause says how a build ends once the budget is spent. It does not license spending the budget in an order that throws away evidence the same budget could have obtained.
Required ordering when the remaining budget (batch remainder or per-build cap) cannot cover the whole plan:
1. First, the company-naming searches and the rendering of the pages they return, highest value first.
2. Then a research run, only while some field is still unsupported, and only if the remainder after its 25u can still pay to render at least one page it cites (3u). A claim's citation must be read from browser text to become a candidate (stage 2), so research without that is not evidence.
3. The R4-6 latch stays at reservation time.
This is need-based, not a fixed reserve (FIX 4 1 stands). V4-1 and F4 must still pass: there the evidence needs research, and after the page work the budget covers research plus a cited page. When the whole plan fits the budget, as in an unbatched build under 80, the order is free.
Tests: the budget-30 case above must end with all supported fields known. Its oracle is the evidence reachable within the budget by this ordering.
