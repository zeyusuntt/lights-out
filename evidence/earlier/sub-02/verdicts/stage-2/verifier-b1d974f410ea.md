VERDICT: BLOCK
REVISION: b1d974f410eae3d2f9c1b1053cfca3bc82cc5e1e

# Verifier verdict: stage 2, round 1

Seal in force: SEAL AMENDED 2 sha256:39f4a0ca1c2498a41e9c165583be725282e8f65de3f3191615273776c4d6607f, 216 tests. `seal --verify` returned ok before the run. I had not seen stage-2 code when I sealed.

## What I ran (clean clone `fclone b1d974f… clone-b1d9`)

1. **Build and start:** the image built with no cache and started with only -e PORT plus provider variables, at 2 vCPU / 3 GiB. Healthy in 0 s; about 245 MiB of memory.
   - Note: RUN.md still tags the image `dossier-stage-1`. It works, so this is not a finding.
2. **Check command, isolated mode** (`checks/verifier-s2-b1d9-r1`): "claimed stage: 2", highest contiguous stage 2. This is a sample only and not evidence on its own.
3. **Sealed suite:** `sealed/stage-2/run.sh clone-b1d9/stage-2`. Result: **211 passed, 5 failed** (244 s).
   - All 5 failures share the one root cause in F1 below.
   - Every browser test passed: routes, testids, building cadence, latest-read-wins, lost-response retry with the same key, 375 px layout, labels, local assets, and signed-in across import.
4. **Upgrade path:** the real stage-1 image (`clone-b1d9/stage-1`) was populated through its API, exported, and imported into stage 2.
   - Passed: tokens and logins, dossier identity, imported candidates per R2-6 (null kind and published_at, retrieved_at = researched_at), replay of lost keys, and a failed refresh keeping imported candidates (R2-5).
   - Failed: the next successful build's candidates, because of F1.
5. **Cost:** from the mock's priced call log. I checked every citation and every candidate as served page text that supports its value; none were unsupported.
   - The kit's sample corpus, 12 companies: **634 units for 69 supported (known or contested) fields, 9.19 units per supported field.** Builds cost 44–63 units.
   - My corpus, 7 companies: **293 units for 24 supported fields, 12.21 units per supported field.**
   - No build exceeded 80 units.
6. **Code read:** no answers keyed to fixtures (no corpus names in app/). F1's root cause is in `planner.py` `field_query`.
7. **Fault planting:** not run. This revision did not pass, and I plant faults only on the first revision that passes.

## Findings

### F1: a supporting page of the evidence is never gathered, so a candidate is missing and the wrong value is selected

- **Sentences broken:**
  - stage-1 §4 Evidence: "The evidence for a company is every page that some search, through any provider and for any query naming the company … returns".
  - stage-1 §8: "When a build completes ready, each field is known exactly when the evidence (§4) supports a value for it".
  - stage-2 Candidates: "Every value that a page of the evidence (§4) supports for a field is a candidate of that field, once for each such page".
  - stage-2 operation 3, and The selection rule: "The rule runs over all of a field's candidates".
- **Scenario:**
  - A company has 11 searchable pages, more than the 10 results a search returns.
  - One of them is a news page with the latest publication time. Its prose sentence "<Name> has raised $25M so far." supports funding_total 25000000.
  - That page is not among the 10 results of the exact-domain search.
  - The build's other queries are the company's name plus each field's statement phrases (`planner.field_query`). They do not contain the domain, so they get no domain boost. They are filled by other companies' pages that repeat the statement phrases, and never return the page.
  - A query naming the company by its domain beside the phrases ranks the company's pages first ("A query containing a company's domain ranks that company's pages above every other page", web README) and does return it. The page is therefore evidence by §4.
- **Observed:**
  - funding_total candidates are only [10000000 (news, 2025-06-01), 99000000 (aggregator)], so the selected value is 10000000.
  - Expected: candidates [25000000 (news, 2026-01-15), 10000000, 99000000], with 25000000 selected.
  - In the call log, the 7 searches return the page 0 times and it is never extracted (spent 65 units).
- **Reproduce:**
  - Build the company above on the mock web, in a corpus that also holds a company with dozens of pages full of the statement phrases, then GET the dossier.
  - Or run `NOCACHE=0 sealed/stage-2/run.sh clone-b1d9/stage-2 -k "orbit"`.
  - The failing tests are `test_dossier_values_and_citations[orbit-forge.test]`, `test_weather_rate_limits[orbit-forge.test]`, `test_research_throttled_still_read`, `test_r2_1_throttle_everything` and `test_upgrade_next_build_replaces_candidates`: one cause, five symptoms.
- The accepted stage-1 build named the company by its domain in these queries and did not have this gap.

## Notes (do not block)

- **Spend.** Units per supported field on the sample corpus rose from 5.35 (stage 1) to 9.19, for the same 69 fields.
  - Every page the build reads is fetched with a rendered extract at 3 units per URL, against 1 for a plain extract.
  - The kit says the graded corpus has no disclosure controls. If plain and rendered text agree for such pages, rendering every page is avoidable spend: about 2 units per page read, around 20 units per build here.
  - This is a note with the numbers. Correctness of page text decides.
