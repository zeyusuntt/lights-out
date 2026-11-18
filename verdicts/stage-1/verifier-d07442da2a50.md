VERDICT: BLOCK
REVISION: d07442da2a5016e26e55e3f8b32a76e3d731c0dd

Seat: verifier. Round 3, after FIX 1 2 and R1-6. Worked from a clean clone (fclone) of the exact hash; fresh no-cache build per RUN.md under 2 vCPU / 3 GiB, internal network, kit mock web.

## Finding V3-1 — a supported field is left unknown when its supporting span sits late in a sentence of about 800 characters or more

Sentences: §8 "When a build completes ready, each field is known exactly when the evidence (§4) supports a value for it". RULING R1-2. RULING R1-6: "A field is only required to be known (R1-2) when some span of at most 500 characters supports it".
Case: suite corpus company ironvale-pottery.test, one searchable page. Its prose is one 799-character sentence that ends "... and Ironvale Pottery was founded in 1952 by two sisters." The span "Ironvale Pottery was founded in 1952 by two sisters." (52 chars) satisfies A.2 on its own. Observed: state ready, founded_year unknown. The build spent 34 of 80 units, and the page was served in full (lite snippet + 1 extract).
Cause (code read): support.citable stops after MAX_SPAN_CHECKS = 2000 span checks, scanning from the first word. When the supporting span starts late, the cap returns None first. Directly, citable() on the same shape gives a span at 456 chars and None at 796, 1136 and 1816 chars. My oracle finds a span in each.
No sentence sets a search cap. The span exists, and the budget was not exhausted.
Reproduce: `run.sh <clone>/stage-1 -k "ironvale"` (seal sha256:7b8b3d0f…). It fails test_post_seal_round3_edge_evidence[ironvale-pottery.test-founded_year-1952] and test_build_is_correct_cited_and_within_budget[ironvale-pottery.test].

## Reported problems retested first
- F3: fixed. copperleaf-studio.test has a non-searchable page whose prose is "Profile: Copperleaf Studio CEO: Ines Marlow.", served by research. ceo is known, "Ines Marlow", and the citation is that served excerpt.
- F4: fixed. saltmarsh-works.test has a research excerpt over 600 chars with "Saltmarsh Works was founded in 1961" at its start. founded_year is known, 1961, with a citation of at most 500 chars copied from the served text and supporting by A.2. No citation over 500 chars appears in any build (asserted on every build test).
- brackwater-kilns.test (a 600+ char sentence, R1-6): founded_year is known, 1952.

## Whole suite
- `run.sh stage-1`: 183/185 passed. The 2 failures are V3-1 above.
- Check command, isolated: `harness run ... --stage 1 --mode isolated --out work/checks/verifier-d074-r3` → "claimed stage: 1". This is a sample, not a verdict.

## Cost
560 units over 19 first builds, for 85 correct of 86 supportable fields: 6.59 units per correct field. On the 15 companies of round 2 the spend is unchanged in shape (27–33 per build). The extra units are the suite's four new edge companies, each 27–34 units. Max per build 34, well under 80.

## Suite amendments this round (code seen)
New corpus companies and the test above. The citation check now accepts research-served bare excerpts as prose, as F3 requires (my check had applied the page header rule to a bare excerpt). It now also explicitly rejects an excerpt found only in a page's rendered header line.

## Notes
- N1 scrypt still runs on the event loop (concurrency tests stay under 5 s).
