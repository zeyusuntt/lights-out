VERDICT: PASS
REVISION: a8789dcd65a18ca385d968116c51d23590913c33

Seat: verifier. Round 4, after FIX 1 3 and R1-7. Worked from a clean clone (fclone) of the exact hash; fresh no-cache build per RUN.md under 2 vCPU / 3 GiB, internal network, kit mock web.

## Reported problems, retested first
- V3-1: fixed. ironvale-pottery.test (one 799-char sentence, supporting span at its end) gives founded_year known, 1952, and the citation is a supporting span of at most 500 chars. `run.sh <clone>/stage-1 -k ironvale` passes.
- F5: fixed. The second reader's reproductions pass for each case:
  `SECOND_READER_ONLY=bounded-supporting-span-<c>.test .../second-reader/probes/stage-1/run.sh <clone>/stage-1`
  For c = reader-tail-span, reader-middle-span and reader-search-span, the result is rc=0, "2 passed 0 failed".

## New span algorithm (support.citable): checks asked for
- Short sentences are cited whole. Every citation in every build (19 companies, first builds and refreshes) equals a whole served sentence of at most 500 chars, or is an edge-intact span of a served sentence over 500 chars (R1-7 shape check in check_citations, seal sha256:0f942c22…).
- Edge integrity. I compared it in-process with my oracle on adversarial shapes:
  - a late span in a 1392-char sentence: found;
  - a negator far outside the span (783 chars): found, with the negator excluded;
  - a 4-word name, where a span would cut the capitalised run: nothing, matching the oracle;
  - a name more than 500 chars from the amount: nothing, matching the oracle.
  The spans returned do not cut a word, an amount or a capitalised run.
- Response time: a 30,874-char sentence dense with names, years, amounts and counts takes at most 0.093 s per field, with no cap. Every build in the suite ended within 10 s.
- Code read: values are anchored on occurrences, each paired with the nearest name and phrase on each side plus any overlapping occurrence, widened to safe edges, and re-checked by supported_value on the span alone. Short sentences go straight to whole-sentence support.

## Whole suite
- `run.sh stage-1`: 186/186 passed (seal sha256:0f942c22…).
- Check command, isolated: `harness run ... --stage 1 --mode isolated --out work/checks/verifier-a878-r4` → "claimed stage: 1". This is a sample, not a verdict.

## Cost
559 units over 19 first builds, for 86 correct of 86 supportable fields: 6.50 units per correct field. Per build 27–34 units, max 34 of 80.

## Notes
- N1 scrypt still runs on the event loop. The concurrency tests stay under 5 s.
- N2 A `$0M` amount normalises to funding_total 0. No sentence excludes 0; I mention it only for awareness.
