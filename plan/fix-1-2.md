FIX 1 2 — stage 1, round 2, on b9d46b6fd9eabedd13ecc8fb09aa6247ad1fcf17

Verdicts: verifier PASS (verdicts/stage-1/verifier-b9d46b6fd9ea.md), second-reader BLOCK (verdicts/stage-1/second-reader-b9d46b6fd9ea.md). F1 and F2 are confirmed fixed by both seats. Fix the two new findings at their root in one revision, then send CANDIDATE 1 <hash>. Both come from the round-2 research-citation change, so treat them as one design question: how a research-served excerpt is turned into a citation.

## F3 — Valid research prose beginning with `Profile:` is left unknown (second-reader)

Units S1-121, S1-223 under ruling R1-2; S1-139 (everything after the header's first empty line is prose); Appendix A.
The mock company `reader-research-prose.test` has one non-searchable page, https://reader-research-prose.test/page-0. Its whole prose, after the ordinary header and an empty line, is:

    Profile: Reader Research Prose CEO: Dana Ruiz.

The all-six-field Nimble research answer serves that same sentence for that URL and claims ceo "Dana Ruiz". It is a single sentence, it names the company, it contains `CEO`, it has no negating phrase, and it has exactly one person's name. Observed: ready, 33 units, ceo unknown, with 47 units unspent.
Root cause to address: whether a served excerpt is header or prose cannot be decided from the excerpt's shape alone. When it is in doubt, obtain the page's full text (an extract, budget permitting) and decide by §4's header rule: header lines run only from the first line to the first empty line.
Reproduce: SECOND_READER_ONLY=research-header-shaped-prose-is-evidence /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1 (exits 1 on this revision)

## F4 — A research citation exceeds the 500-character limit (second-reader; the verifier also noted it)

Unit S1-127 (§4 "It is 1 to 500 characters long").
For `reader-research-long.test`, a non-searchable page has one prose sentence: `Reader Research Long CEO: Dana Ruiz` followed by ` with published company background` 30 times, then a period. Research serves that sentence as the CEO citation, and the service asserts CEO Dana Ruiz with the whole 1,056-character excerpt.
Required: no citation is over 500 characters, from any source. A contiguous, character-for-character span of served prose is still a citation and is still a single sentence. Where a supporting sentence is longer than 500 characters, cite a span of at most 500 characters that on its own still satisfies Appendix A.2 for that value. If no such span exists, that sentence cannot be cited.
Reproduce: SECOND_READER_ONLY=research-excerpt-length-limit /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1 (exits 1 on this revision; prints "research citation length 1056")

## Non-blocking

- The verifier still reports scrypt on the event loop. You measured 50 concurrent logins at a worst case of 1.05 s, and that stands as a note.
