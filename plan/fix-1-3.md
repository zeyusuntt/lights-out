FIX 1 3 — stage 1, round 3, on d07442da2a5016e26e55e3f8b32a76e3d731c0dd

Verdicts: verifier BLOCK (verdicts/stage-1/verifier-d07442da2a50.md), second-reader BLOCK (verdicts/stage-1/second-reader-d07442da2a50.md). F1 to F4 are confirmed fixed by both seats. Both seats report one root finding: long-sentence span citation. This is the second round in which the long-sentence handling has failed (F4, then this), so **change approach**: do not tune the cap. Replace the bounded scan. Read the new ruling R1-7 (rulings/stage-1.md) first, because it fixes the scope of spans.

## V3-1 / F5 — Supported field stays unknown when its supporting span is late in a long sentence

Units S1-121, S1-223; rulings R1-2, R1-6, R1-7. No sentence of the specification sets a search cap.

Verifier V3-1: the corpus company ironvale-pottery.test has one searchable page. Its prose is a single 799-character sentence ending "... and Ironvale Pottery was founded in 1952 by two sisters." That 52-character span satisfies A.2 on its own. Observed: ready, founded_year unknown, 34 of 80 units spent, with the page served in full. Called directly, support.citable stops after MAX_SPAN_CHECKS=2000, scanning from the first word. It finds a span at 456 characters and returns None at 796, 1136 and 1816.
Reproduce: verifier suite `run.sh <clone>/stage-1 -k ironvale` (the verifier runs it; ask through the foreman if needed).

Second-reader F5: reader-tail-span.test and reader-middle-span.test end ready at 33u with CEO unknown, and reader-search-span.test ends ready at 34u with CEO unknown. Each is a single sentence of about 1.2 to 1.7 KB. The tail case is "context " repeated 150 times, followed by "Reader Tail Span CEO: Dana Ruiz.". The middle and searchable-page variants contain "Reader Middle Span CEO: Dana Ruiz" and "Reader Search Span CEO: Dana Ruiz", which are valid 33-character spans. A control case, with company and value more than 500 characters apart and no eligible span, correctly stays unknown.
Reproduce:
  SECOND_READER_ONLY=bounded-supporting-span-reader-tail-span.test /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1
  (also ...-reader-middle-span.test, ...-reader-search-span.test)

## Direction (both seats agree)

Anchor the search on occurrences rather than on every starting word. For each name or domain occurrence, each statement-phrase occurrence for F and each value occurrence in F's format, take the minimal span that covers one of each. Widen it to safe edges as R1-7 defines them, and accept it if it is 500 characters or fewer and satisfies A.2 on its own. The cost is polynomial in the number of occurrences, and no cap is needed. Sentences of 500 characters or fewer are judged and cited whole (R1-7).
