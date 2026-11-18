# Stage 1 rulings

Ledger: ledger/stage-1.jsonl at 976ad55b8fc5504eb2071ec26279aa305d76fd36. Spec: stage-1.md.

## R1-1 — S1-080: clock before the first reset

Readings: (a) system time until the first reset or the first `POST /_test/clock`, either of which freezes it; (b) system time until the first reset even after a clock call; (c) frozen at startup.

Chosen: **(a)**. Basis: **EXPLICIT** for the no-call case, **SILENT → assumption** for a clock call before reset.

Why: §3.4 says "Before the first reset the clock follows the system time" — this specific sentence beats the general standing-clock bullet, so (c) is out: with no reset and no clock call, each read returns current system time. A clock call before any reset is not contemplated by the text. §3.4 also says only reset and `POST /_test/clock` move the clock, and a `now` earlier than "the clock's current time" is 422. Reading (b) would make a successful clock call have no effect, which a careful reader would not expect. Assumption: a valid clock call sets the clock to `now`, and from then on the clock stands still exactly as after a reset. Before that, the "current time" used for the backwards check is system time at the moment of the call.

## R1-2 — S1-121 and S1-223: what "the evidence" is, for completeness

Readings: (a) the whole provider universe as §4 defines it, whether gathered or not; (b) only what the build actually gathered.

Chosen: **(a)**. Basis: **EXPLICIT**.

Why: §4 defines evidence as "every page that some search, through any provider and for any query naming the company (as in Appendix A.2), returns, with its full text, and every claim that a `nimble` research run for the company asking for all six fields answers with". §8 says a ready build makes each field known "exactly when the evidence (§4) supports a value for it". That definition is not limited to gathered pages, and §4 uses the separate word "gathers" for gathered pages. So a ready build must find a supported value wherever one exists in that universe. The only relief is §9's 80-unit cap ("completes with the pages and research claims it has obtained"). That relief applies only when the budget is really exhausted. The dispatch also says that a saving which leaves out evidence a field needs is a defect. Builder: plan the searches and deep fetches so that full texts (not just snippets) of the pages that company-naming queries return are read, and use the all-six-field Nimble research claim, all within 80 units. Verifier and second-reader: a field left unknown while supporting evidence existed in the corpus and the build had unspent budget is a BLOCK under S1-223.

## R1-3 — S1-122: exactly one successful exact-domain search, versus total provider failure

Readings: (a) required whenever a provider answers it; a build in which every call errors ends `failed` with zero; (b) unconditional.

Chosen: **(a)**. Basis: **CONFLICT**, resolved by the specific sentence.

Why: §8 says "A build ends ... `failed` when none of its provider calls succeeded". That sentence is specific to total failure, and it cannot coexist with (b). Rules for the builder that follow from §4:
- Every build that ends `ready` has made exactly one search, answered without error, whose query is exactly the normalised domain. It is not zero, and it is not two, counting all providers together.
- A refused exact-domain search does not count and costs nothing (§9). Retry it on refusal within the time bounds of §8.
- Once one exact-domain search has succeeded, no other search in that build uses that query text.
- A timed-out or lost exact-domain search costs units (§9), and it is unknown whether it "answered without an error". Treat it as not answered and retry, within budget.
Assumption: if, within the time bound, the exact-domain search never succeeds while some other call does, the build ends per §8 (`ready` with what it obtained). Nothing in the specification contemplates this case.

## R1-4 — S1-309: spent_units of a dossier exported mid-build

Readings: (a) restore the whole pre-build snapshot including its pre-build `spent_units`; (b) keep spending incurred through export.

Chosen: **(a)**. Basis: **EXPLICIT** (the specific sentence wins).

Why: §10 says "An export taken while a build is running holds the dossier as it was before that build". This sentence is about this particular operation, so it beats the general cumulative rule of §8. The exported dossier carries the `spent_units`, fields, `researched_at` and state it had before the running build started. For a first build, that is `failed`, every field unknown, `researched_at` null, and `spent_units` 0. Exception: if the running build is a first build, `spent_units` is whatever the dossier had before that build started, which is 0. On the source, the running build continues and its spending counts as usual. Completed idempotent responses (for example the 202 `building` that started the build) are preserved verbatim in the export. Import starts no build.
