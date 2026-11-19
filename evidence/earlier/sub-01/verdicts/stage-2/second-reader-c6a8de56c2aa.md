VERDICT: BLOCK
REVISION: c6a8de56c2aac958122e5d30806f7dbf6858dd09

# Independent second-reader audit — Stage 2, round 2

The complete audit finishes with **178 passed, 2 failed**: 173 passing and two failing black-box probes plus five passing narrow source checks. Four of the five previously reported scenarios pass. The Deepwell missing-candidate scenario remains, and an additional case confirms the remaining non-domain-result filter can select the wrong value.

## Reproduction

```sh
fclone c6a8de56c2aac958122e5d30806f7dbf6858dd09 /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-c6a8de56c2aa
/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-c6a8de56c2aa/stage-2
```

The runner builds/starts the supplied stage, immutable sibling Stage 1 upgrade source and supplied mock, using the sample corpus plus independently authored cases. It takes one required argument, runs every probe and exits **1**. Services run at 2 vCPU/3 GiB on an internal network with Nimble alone. The five previous failures run before the remainder of the suite. Probes/results remain private in `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/` until final publication.

The clone has the exact revision above and clean status. `fserve` also started it successfully. `git diff --exit-code e391dd0b4280ee518d358387614110bebf90c116 HEAD -- stage-1` exits 0, so the legacy source is the immutable accepted Stage 1 tree. No product code/tests were edited; supplied tests/check sources, `key.json` and later-stage specifications/logs were not read. Source-only checks are limited to properties unavailable through HTTP, such as routing, timing configuration and optional-provider/null-kind branches.

## F1 — Deepwell still lacks a supported candidate with budget remaining

Units: **S2-005, S2-054**, R1-03/R2-06. This is a retained finding.

`candidates/beyond-ten-results` still returns **13 of 14** supported CEO candidates for `deepwell.test`. Missing: `Sam Ortiz` from `https://reports.test/news-c`, whose prose is `Deepwell chief executive officer: Sam Ortiz.` The selected `Lina Chen` value is correct in this fixture, but the candidate set is incomplete.

The witness now records **74 units**, comprising ten successful lite searches, one research run and thirteen rendered extracts. There is no extract attempt for the missing URL. Six units remain, enough for a further targeted search and rendered fetch. Fourteen rendered pages plus the ten existing searches and research would total **77**, under 80; this is not an impossible evidence set or a request to exceed the budget.

Reproduce with the complete runner above. Failure name: `candidates/beyond-ten-results`. Safe `results.json` includes the field counts, selected value and provider query/URL/cost/status witnesses. This is the same authored case used on the preceding revision; its expected fourteen candidates were not changed.

## F2 — A returned generic non-domain result is skipped, changing the winner

Units: **S2-005, S2-008, S2-054, S2-080**, R1-03/R2-06. This checks the builder's remaining stated assumption directly.

`shadowbrook.test` has ten own pages dated 2025 supporting CEO `Dana Ruiz`, and a filing dated 2026 supporting `Lina Chen`. The filing's title and URL are generic (`Administrative registry record`, `https://registry.test/record-late`), and its first 300 prose characters are ordinary administrative notes. Its later prose contains `Shadowbrook chief executive officer: Lina Chen.` No clicks are required, and static and browser text agree.

The provider returns that filing to the service for the non-domain query **`shadowbrook CEO chief executive`**. The probe explicitly verifies this in the provider log before checking candidates. The exact-domain search does not return it. The service makes no extract attempt for the returned filing and finishes with ten Dana Ruiz candidates, selecting **Dana Ruiz**. Expected: eleven candidates, including the newer filing, selecting **Lina Chen**; the complete field is contested.

The build spends **65 units**: ten searches, one research run and ten rendered extracts. Reading the already-discovered filing would cost another three units, bringing the total to **68**. The missing candidate is not caused by a full budget. The absence of a company name in a title/snippet/URL cannot establish that the full evidence page has no support.

Reproduce with the complete runner above. Failure name: `candidates/generic-nondomain-result`. Its witness records the returned URL in `served_urls` for that query, no extraction of the URL, selected Dana Ruiz, and ten candidates. The fixture is constructed by the runner; no separate file or secret is required.

## Retests and passing checks

- Fixed: browser-only short/static text, browser-only long/static text, the inherited whitespace-normalized headquarters phrase, and the late generic registry support case. They were retested first with Deepwell, before the rest of the suite.
- Full API regression and candidate checks passed apart from the two cases above: authority/recency/instant/URL/value ordering, null/default metadata, per-page/value deduplication, citation provenance/order, statuses, refresh replacement, auth/idempotency/concurrency, resets/imports and clock behavior.
- Fourth-attempt 429 recovery, refused-call zero cost, rendered-extract costs, in-flight and cumulative spent_units passed. No cap overflow was found. Current cost witnesses are 74 and 65 for the two failing companies, so both have room to finish gathering their required evidence. I do not claim that a respected cap or the kit sample establishes optimal research spend on the unopened Stage 4 workload.
- Browser flows pass at 375/1280: signup/login/logout, invalid research and confirmed auth/refresh refusals, normalized/existing domains, unknown outcomes with the same key/body, polling, reload and latest-read-wins, evidence/contested/not-found/empty states, zero-dollar values, and contested data after 201 earlier-sorting completed dossiers.
- Both lost create and lost refresh responses survive real Stage 1 export/import with the same open browser and old token. Replays recover the original response without new provider work; legacy null metadata is preserved; failed refresh keeps imported candidates and the next ready refresh replaces them.

The pagination setup now creates completed dossiers in bounded batches. An initial exploratory version left 201 provider jobs unfinished and then applied an arbitrary 15-second deadline to the aggregate contested screen; it timed out and delayed a subsequent control call. The final probe isolates pagination from that background-job load and does not invent an overall UI deadline. This verdict neither claims that exploratory load passed nor treats it as a separately reproduced blocking finding. The existing per-request timeout checks remain in effect.

The product-user verdict is PASS for this exact hash, and its revised header/building copy/signup navigation notes were read after my own probes. Its visual authority remains R2-11. My own narrow/desktop walks reproduce the required flows and no-overflow checks. No verifier verdict for this hash was present when checked; this BLOCK relies on my own reproductions.

## Ledger, legacy residual and sample check

All **153 normative/ambiguous units** have evidence for this revision. `ledger-check 2 --phase audit --revision c6a8de56c2aac958122e5d30806f7dbf6858dd09` exits **1**, listing exactly S2-005, S2-008, S2-054 and S2-080 as failing. No unit lacks evidence.

The R2-08/R2-09 exception remains: unexported served text missing from the accepted Stage 1 export is a **non-blocking residual of Stage 1** for the final report, not a Stage 2 finding. The original obligation and residual remain recorded; the upgrade probe re-evaluates only available exported excerpts as ruled.

The required sample command, on the clean clone and a fresh output directory, exited **0** and printed `claimed stage: 2 on the shipped checks`:

```sh
cd /Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026
env BUILDX_CONFIG=/Users/[REDACTED]/dev/band-factory/work/second-reader/docker-buildx with-slot .venv/bin/python -m harness run --track dossier --repo /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/stage-2-c6a8de56c2aa --stage 2 --mode isolated --out /Users/[REDACTED]/dev/band-factory/work/checks/second-reader-s2-c6a8de56-01
```

That sample does not override the two independent findings. All owned service/probe containers were removed. Probes will be published only when the foreman closes every stage.
