# Stage 4 cross-operation dangers

Independent reading sequences, not findings about an implementation. No Stage4 product code, product tests, supplied checks or other seats' tests were read. Earlier accepted folders stay final. The ambiguous ledger rows require foreman rulings before their audit oracles are fixed.

1. **Domain normalization across every lineage signal.** Give URL host, Registrant, First-Published-By and Canonical host case/www/trailing-dot variants of the same domain. They must collapse to one origin; a missing/invalid Registrant falls back to normalized URL host. Changing only presentation spelling must not create corroboration. (S4-012..016, S4-031.)

2. **Own host is not proof of own authority.** Compare explicit own on the company's host with a foreign registrant, explicit own on a foreign host with the company's registrant, and a foreign host with its own foreign registrant. Only company registrant permits own. The lookalike test separately compares registrant to URL host and requires an explicit own claim. Missing Kind still uses inherited fallback subject to the own restriction. (S4-018..027.)

3. **Origin precedence short-circuits a chain.** A page has valid First-Published-By, Canonical and lookalike signals. First publisher wins; there is no need to fetch an irrelevant original. Remove the first-publisher signal and Canonical must win before lookalike/registrant. (S4-024..028.)

4. **Depth belongs to the starting page.** In A→B→C→D→E, E has a first publisher different from its host. A reaches three edges and substitutes E's host at the fourth, while B can fetch E within its three edges and use E's first publisher. A cached origin for B must not erase A's remaining-depth limit; cached page text can still be reused. (S4-025, S4-029..030.)

5. **Cycles are still depth-bounded.** Use a self Canonical, a two-cycle and a three-cycle with different hosts/registrants. Do not hang or fetch indefinitely; a fourth edge uses its target host. An early cycle fallback is not automatically equivalent to the specified fourth-edge result, especially for a three-cycle. (S4-025, S4-029..030.)

6. **Originals unavailable versus expensive.** A copy points at a missing original, an original whose provider refuses, and a valid original requiring another paid request after the budget is exhausted. Missing-service fallback is explicit; budget exhaustion handling follows the S4-030 ruling and must not exceed80/shared caller budget or invent an independent publisher. (S4-028..030, S4-009, S4-098.)

7. **Canonical-only evidence scope.** A non-searchable original contains the only CEO/investor fact, and only a Canonical chain discovers it. The original must be fetched for lineage, but candidate inclusion depends on the S4-028 ruling. Do not accidentally use a lineage-only fetch as unsupported research evidence or omit it if the ruling expands evidence. (S4-028.)

8. **Copy count is not source count.** Ten URLs, mixed kinds and two providers all republish one first publisher. Their candidates may all remain and their selected-value citations may all be visible, but origins count once, scalar corroborated is false, and a news-only investor does not gain membership from the URL count. (S4-031, S4-035..037, S4-064.)

9. **Losing values cannot corroborate the winner.** Highest authority chooses A from one origin; several other origins support B. A remains uncorroborated, even though the field has many candidate origins overall. Add another A origin and only then qualify. Unknown fields always report empty origins. (S4-035..037.)

10. **Current and standing sources differ.** Ready buildT0 gathers A from originX, T1 gathers A only from originY, T2 gathers A only from X. Each current origins list has one item and corroborated is false, but standing origins reach two atT1, so corroborated_since remainsT1. A failed build cannot contribute, and metadata-only same-value builds do not reset the selection stint. (S4-038..040.)

11. **Same-time abandonment and return.** Without advancing the clock, build A with originX, switch to B, return to A with originY. Do not pool X from the old A stint by comparing learned_at timestamps alone. Build order defines the new stint; current Y alone has null corroborated_since. Later X can qualify it afresh. (S4-039..040, inherited equal-time build order.)

12. **Historical reads do not see future origins.** Capture as_of before the second source, then accumulate corroboration later. Earlier candidates/origins/booleans/since stay as known then. A /values answer that never won a current selection raises the separate new-key scope question in S4-033. (S4-033, S4-038..042, inherited snapshot isolation.)

13. **Two-member union is insufficient.** CFO A has only originX; CTO B onlyY. Executive origins is[X,Y] but corroborated is false. Add a second independent origin to one title and keep false until both qualify individually. Rival names and ineligible investors never enter the member origin union. (S4-045..050.)

14. **Member continuity differs from whole-field history.** CFO A stays while CTO B changes or an investor is added. A retains its standing sources even though the whole selected array and field learned_at change. A removed/rejoining member starts a new stint; an old candidate learned_at does not preserve that former membership's sources. (S4-049..050.)

15. **Removing the weak member.** AtT0 A has two origins, B one; atT1 B leaves and A remains. Whether aggregate corroborated_since becomesT0 orT1 is S4-049's ruling question. Test it explicitly, including reintroduction of B and a retained member whose current sources later shrink. (S4-048..050.)

16. **Investor name parsing is not CEO parsing.** Use two names in one sentence, a four-word suffix name, every allowed terminal word, a standalone Capital, an uppercase-word break, an invalid longer run ending in another word, and a company name that itself ends Capital. Remove company/phrases first and retain every valid investor name, not only one agreeing value. (S4-055..062.)

17. **Amount-sensitive non-suffix names.** Compare “raised$40M … led by General Atlantic” with “is led by Dana Ruiz”, EUR-only amounts, one-word names, different phrases and negated/rumoured statements. Only the specified USD-amount led/backed exception widens names; semantic guesses must not replace AppendixA. (S4-058..061.)

18. **Unknown investor field can have candidates.** One news source supports Bluebird Capital: keep its candidate, selected false, value null, status unknown, citations/origins empty. A genuine own/filing candidate or a second independent origin makes the name a member. Do not reuse inherited unknown⇔no-candidates logic unchanged for investors. (S4-064..070.)

19. **All member candidates selected, all names ordered.** Rank multiple investor candidates so different names interleave. The value sorts member names by Unicode, the candidate list remains global Stage2 rank, and citations group by sorted member then rank. Every candidate of every member is selected, including duplicates across distinct pages; a nonmember may rank before them. (S4-065, S4-068..070.)

20. **Investor date and correction boundaries.** One member's oldest nonnull candidate date wins even at lower authority; nulls are ignored unless all dates are null. Field date is the latest member date. Adding an earlier/equal-dated name can be correction relative to the old field date, but any removal or mixed nonqualifying addition makes change. Same arrays with new dates add no event. (S4-071..076.)

21. **Membership at a date uses active versions.** A news investor has one origin before a second URL's Effective date and two afterwards; a candidate-free or undated replacement later removes active support. /values recomputes membership, dates and citations from active candidates, not the current member array or standing historical origins. (S4-073, inherited page-version rules.)

22. **Old six-field UI contracts remain six.** Make executives contested and investors known while all six old fields are uncontested. /contested is empty; investor/executive rows, if shown, use separate markup and cannot collide with required field/evidence test IDs. No batch browser screen is required by the listed routes. (S4-077 and inherited screens.)

23. **Batch validation is atomic and retryable.** Submit an unsorted list with an invalid final domain, a normalized duplicate, or an out-of-range budget. No earlier domains may be created and the failed key remains unused. Auth precedes missing key; wrong budget types are422 rather than400; the integral-decimal question follows S4-089. Unknown body fields do not change replay identity. (S4-083..091.)

24. **Overlapping writers share dossiers, not budgets.** Race two batches and standalone POST creation for the same normalized domain. Exactly one creates/starts its first build; every other operation sees an existing dossier, makes no research call for it and charges no batch units. Existing failed/building dossiers are not batch refresh requests. (S4-093..097.)

25. **All-existing batch and dynamic item states.** Submit a batch containing only existing dossiers, including one another client is currently building. It has no own running build and is done at zero spend, although an item can say building. A later independent refresh may change an item's current state without reopening the batch. Keep input order, not list-domain sorting. (S4-092..101.)

26. **Exactly one original response, ownership private.** Fifty concurrent identical POST/batches requests yield one202 and the others200 with the same original JSON response, even as GET batch spending/states move. B cannot read A's batch, but B sees its dossiers and may use the same key independently. The same user's key also works on create/refresh paths. Preserve replies through import/restart. (S4-007, S4-081..085, S4-111.)

27. **Reserve both ceilings before calls.** With several new companies and a tiny shared budget, delay all provider replies so reservations overlap. No combination may exceed either80 for a build or the shared budget. Rejected/refused reservations do not leak units. Originals, retries and in-flight uncertain calls must all be priced, not just initial searches. (S4-009, S4-095..098, S4-109.)

28. **One expensive next call versus cheaper remaining work.** Leave2 units and place a3-unit render/25-unit research before a1-unit search. Global-latch versus skip-and-continue behavior follows S4-098's ruling. In either reading, finish all builds with permitted partial results and keep current contested/investor semantics rather than forcing every supported field's status to known. (S4-098.)

29. **Batch time is request time.** Submit many new domains at one frozen time, advance the clock while workers/providers run, and read them when complete. Each build's timestamps use the request that started it, not worker dequeue/completion time. With up to50 entries, background scheduling still must respect inherited fast-provider build bounds and ordinary API timeouts. (S4-002, S4-079..080, inherited §8.)

30. **Failure is per reachable operation.** Make optional providers unavailable but Nimble answer; separately fail every research run while Nimble search/rendered extract works. Gather all reachable scalar, executive and investor support, including conflicts and origins. With all used providers failing, end failed within bounds and preserve prior ready values/history/feed. 429/5xx refusals cost zero, waits respect cooldown, and prior Stage2 late-throttle protection still applies. (S4-105..109.)

31. **Crash after billing, before result commit.** Delay research/extract after some searches have billed, kill the exact container, then restart with fast providers. Every interrupted standalone/batch build becomes terminal within10s of first health200, and every billed pre/post-stop unit remains counted. Stage3's optional pre-build spending rollback is no longer acceptable. Conservative unbilled in-flight charges are allowed, but caps still hold. (S4-113..118.)

32. **Repeat a crash near both caps.** Kill/restart a batch member multiple times after different successful calls. Recovery is still one build under its original80 and shared caller budget, not a new80 allowance on every process start. An explicit fresh-key refresh after terminal recovery is a new build; replaying the original batch/create/refresh key is not. (S4-116..119.)

33. **Idle durable batch and mid-build native export.** Capture owner visibility, batch IDs/budgets/spending/items, completed replies and all earlier durable state; idle kill/start must reproduce them. Export/import native batches into a distinct process as covered by the S4-111 ruling, especially a batch with one completed and one running member. No imported build may silently research again or stay stuck because dossier snapshots excluded it. (S4-111.)

34. **Upgrade origin fallback versus reinterpreting old lineage.** Export each accepted legacy stage with same/different URL hosts, executive history and existing tokens/keys. Missing origins use URL hosts, without refetch or invented Registrant/Canonical headers. Stage3 snapshots/builds remain intact with new keys; investors is unknown in every old build even if old excerpts incidentally name an investor. Its first later membership is change unless there had never been a ready build. (S4-041..043, S4-121..125.)

35. **Stage3 accumulated sources survive the upgrade.** In Stage3, select A from X, later A from Y, then B and A again. Import its full build list into Stage4: reconstruct standing origins at each old build time, distinguish same-time selection stints, and do not pool both abandoned A stints or collapse acquisition to the last researched_at. Native Stage4 transfer must preserve already recorded origins and corroboration history. (S4-039..043, S4-122.)

36. **Reset/replacement is wider than the visible list.** After batches, origins, investor transitions and interrupted recovery, reset must remove all dossiers/batches/history/feed/completed keys and old tokens, and persist that replacement across restart. Invalid reset/import changes nothing. Import into a destination with its own batches is replacement, not a merge; original successful keys remain scoped to the imported users. (S4-002, S4-111, S4-121 and inherited controls.)
