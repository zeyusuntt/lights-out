# Stage 3 cross-operation dangers

These are independent reading sequences, not product findings. Product code, product tests, other seats' tests and supplied checks were not read. Stages 1 and 2 remain inherited except where Stage 3 says otherwise. Rulings are needed for the ambiguous rows before final audit expectations are fixed.

1. **Three clocks, one delayed build.** Freeze service time T, start research, advance the clock to U while providers are delayed, and serve Effective E plus Published P with a nonzero offset. Candidate retrieved_at and new selected learned_at must use T; true_from uses E or the UTC date of P, not U or P's local date. All history/feed entries from the build use the same initiating time. (S3-012..023, S3-114.)

2. **Candidate return versus selection return.** Gather A from URL X, replace it with B, later regather A at X. Candidate A retains first acquisition time, while selecting A again gets the new transition time. Change only X's excerpt/kind/date in between: candidate identity is unchanged and retrieved_at advances. A at a different URL/provider/field/title is a different identity. (S3-016..020, S3-046.)

3. **Same winner, different effective date.** Keep selected A, but replace sources, effective date and contention. Current metadata/candidates update; history and feed gain no row. Query an earlier as_of: it must retain the older candidate set/effective metadata without later-history leakage. (S3-020, S3-023, S3-063, S3-068.)

4. **Initial failure is not first ready.** Let all provider calls fail twice, then obtain six values. The six first selections are initial history only, not feed events. If a field remains unknown in that first ready build and later gains a value, that first row is change from null. (S3-061..064.)

5. **Disappear and return.** A known value becomes unsupported, then comes back. Current unknown metadata must be null/null with no citations. The disappearance and reappearance each produce one change/feed row; old history/citations remain immutable. Null-row learned_at needs the S3-102 ruling. (S3-022, S3-060, S3-102..104.)

6. **Frozen-clock build order.** Run A, failed, B and C builds with the same clock time, including equivalent offsets. as_of at that instant selects C, never the first ready build; failed spending still counts under the ruled spending interpretation. Event seq remains ordered even when learned_at ties. (S3-070..073, S3-101, S3-110.)

7. **Current build versus earlier ready snapshot.** Begin a delayed refresh after a ready build, read as_of while provider cost accrues, then fail it. Fields/state come from the last ready snapshot; spend handling must follow the S3-070 ruling. No failed-build candidate/history/feed entry appears. (S3-064, S3-068..070.)

8. **Retroactive correction on one URL.** Gather URL X versions effective January, March, then February. At a late as_of, January holds before February, February replaces March thereafter; at an earlier as_of, March still exists. Insert a January-or-earlier correction and query every boundary again. Arrival/build order, not sorted effective dates alone, determines replacement. (S3-082..090.)

9. **An empty version erases support.** X has a valid fact effective January. A later gathered X has no candidates and effective April. January's fact must stop holding in April even though the new page supplies no replacement value. A different URL's still-active value may then win. (S3-088..094.)

10. **Undated version wipes but never holds.** Gather dated X versions, then an undated X. New as_of answers have no active X candidate for any true_at. Old as_of answers remain unchanged. Later dated X may supply new date-bounded support; the undated version must never be treated as beginning at minus infinity or retrieval time. (S3-087.)

11. **Not regathered is not an empty version.** X disappears from later search results while Y is gathered. Current dossier candidates reflect the latest build, but valid-time history may retain X's prior version until X is actually regathered/replaced. Distinguish an absent URL, a successful empty page and an extraction error. (S3-082..089, inherited gathering/cost rules.)

12. **Learned cutoff versus true date.** Learn a 2024-effective correction in April 2026. Query true_at in 2025 with as_of in March and April 2026. The correction changes only the later-knowledge answer; it must not rewrite the earlier snapshot, even if a version's true_from is far earlier. (S3-023, S3-068, S3-080..090.)

13. **Authority still wins at a date.** Multiple URLs hold at true_at. An older effective own/filing value beats a recent news/aggregator value; publication, URL and value ties still use Stage 2 ranking. true_from/learned_at are not new authority or tie-break criteria. Citations include every active winning-value candidate in rank order. (S3-024, S3-090, S3-094.)

14. **Independent executive titles.** One page supports CFO Ana, another supports COO Bo, and CTO has two conflicting names. Members remain cfo/coo/cto ordered; each title has exactly one selected candidate; overall status is contested because CTO disagrees. Two different uncontested people in two titles alone are known. (S3-031..048.)

15. **Executive correction uses differing titles only.** CFO changes with an earlier effective date; unchanged CTO's effective date becomes later. This is correction, despite the aggregate date moving later. Add/remove a title or include one later/null-dated rename and the whole executive event becomes change. One member-array transition yields one feed row, not one per title. (S3-050..053.)

16. **Executive date null contaminates aggregate.** One selected title has no date, other members have dates. Aggregate true_from is null. Remove the undated member: aggregate becomes the latest remaining member date, while event typing sees a removed title and uses change. (S3-047..053.)

17. **Research schema and executive support.** Keep research's six-field output schema. A research-cited page can still supply title-supporting browser text, but an unsupported research claim is never itself an executive candidate. CEO/CFO/COO/CTO phrases and longer capitalized runs must not cross-contaminate one another. (S3-028, S3-034..039.)

18. **Six-field UI contract survives a seventh API field.** Make only executives contested. The inherited contested screen still shows its empty state and no executive item with an inherited test ID. Dossier/evidence tests still have exactly the six named field containers; optional executive markup uses separate identifiers. (S3-054..056.)

19. **Feed order across two concurrent dossiers.** Start builds for two companies, coalesce many refreshes for one, and let completions interleave. Each commit contributes its changed fields in table order then executives. Global seq is unique/increasing; pagination since is exclusive; no initial rows enter the feed. Delayed reads see a serially valid state, not a partial field/event commit. (S3-065, S3-109..119, S3-137..138.)

20. **Replay after further history.** Save a create/refresh idempotent response, change the dossier several times and replay it. Original response and 200 must return; no history/feed/build/cost changes. Reuse with changed known body still conflicts. Export/import or restart between the original and replay must preserve this behavior. (Inherited §7/§10, S3-124, S3-149.)

21. **Legacy Stage 1 upgrade without refetch.** Export a known dossier, existing tokens and completed keys. Stage 3 reconstructs candidates under R2-5, one ready build at researched_at, and one initial history row per known field; executives remains unknown even if surviving text names a title. Earlier as_of is404; a first later executive selection is change. A never-ready imported dossier instead has no historical ready snapshot. (S3-121..128, S3-135.)

22. **Legacy Stage 2 history capability risk.** Build A, failed, B with distinct times, different Effective/Published values and an empty-page version. Export from the accepted frozen Stage 2 service and import unchanged into Stage 3. Stage 3 asks for all past builds/outcomes/spend/candidates/header-derived versions even though Stage 2 did not require exports to keep these. No source inspection was done for this reading; establish actual recoverable data and rule S3-129/S3-130 before deciding audit expectations. (S3-129..133.)

23. **Upgrade through two generations.** Import Stage 1 into Stage 2, refresh there, export into Stage 3. Treat the imported base as one synthetic ready build and preserve later recoverable Stage 2 builds. No old executive candidate or retroactive executive initial may be invented. Preserve the same browser bearer token and pending key/body retry through the transfers. (S3-124, S3-131..135, inherited browser continuity.)

24. **Native transfer preserves corrected timelines.** On Stage 3 build retroactive/undated/empty versions and failed builds, capture a matrix of as_of and true_at queries, export, then import twice into a distinct process already holding unrelated data. All answers, history and feed remain identical; previous destination credentials disappear; import makes no provider call. Reset afterwards clears every native/imported historical artifact and seq state. (S3-124..125 and inherited replacement/reset rules.)

25. **Idle abrupt restart preserves all surfaces.** With no build running, record users/sessions, list/current/snapshot/values/history/feed, clock and completed keyed responses; kill and start that exact container without replacing its filesystem. Every result survives. A new change gets a greater seq, and a replay gets its original response without spending. (S3-141..150.)

26. **Crash around a durable control/write.** Complete clock, signup, reset or import, then kill before another ordinary request. After restart, completed operations must not disappear or restore pre-reset credentials/history. An interruption during a build must follow the foreman's S3-142 recovery ruling and never be assumed harmless merely because idle restart passes. (S3-142..150, inherited atomic reset/import/idempotency.)

27. **Date/time and pagination boundaries stay read-only.** Probe invalid/empty as_of, impossible true_at, missing true_at, naive RFC3339, since negatives/exponents and limit 0/201. Correct validation errors make no provider calls or state changes; auth precedence and normalized domains still apply on every new endpoint. A ready dossier with no active valid-time candidate is200 null fields, distinct from no ready build's404. (S3-074..077, S3-095..096, S3-105, S3-115..119.)

28. **Durability and resource bounds together.** Large histories must not make ordinary concurrent reads miss the inherited five-second timeout or startup health miss60 seconds. The image remains one self-contained service within2vCPU/3GiB; persistence belongs to its writable filesystem, not runtime network assets, another container or a host path. Test a meaningful multi-build corpus and stop/start the same owned container. (S3-002, S3-141..150.)
