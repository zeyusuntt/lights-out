FIX 2 1 — stage 2, round 1, on 3cf3cef0862c212f6f572712876ad700e9e0e381

Verdicts: verifier PASS (verdicts/stage-2/verifier-3cf3cef0862c.md), product-user PASS (verdicts/stage-2/product-user-3cf3cef0862c.md), second-reader BLOCK (verdicts/stage-2/second-reader-3cf3cef0862c.md). Fix the blocking finding at its root in one new revision, then send CANDIDATE 2 <hash>.

## S2-F1 — A throttled extract after slow research is never retried; the build ends ready with every candidate empty (second-reader)

Units S2-002, S2-005, S2-054 ("Time a build spends waiting to make a call again after a 429 does not count toward the 10 seconds"); stage-1 §8 known-exactly rule, R1-2; R2-1.
Setup: mock research delay 7 s, with extract throttled so that the first identical extract gets 429 and the next one succeeds. reader-full.test ends ready at 33 units with every field's candidates empty, and its extract statuses are exactly [429], with no retry. The page supports all six fields. Another rendered extract costs only 3u, and a 1 s wait plus a retry fits the time and the budget.
Root cause reported: a global 6.5 s non-live retry_window cuts off the first extract retry once earlier research latency has used up the window. Time spent waiting after a 429 must not count toward any internal deadline derived from the 10 s bound. The 10 s bound itself holds only when every call answers within 1 s, so it is not a reason to stop gathering. Make the deadline account for provider latency and 429 waits as the spec does, or drop the time-based retry cut-off for 429s, which are guaranteed to clear after at most three in a row (R2-1).
Reproduce: SECOND_READER_ONLY=stage2-slow-research-then-throttled-extract SECOND_READER_NO_BROWSER=1 /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh <clean-clone>/stage-2 (prints ready/33/unknown/empty candidates/[429] and exits 1 on this revision)

## Non-blocking — fix these in the same revision; they are cheap, and product quality is judged

From the product-user:
1. A wrong-password login shows the raw text "a valid bearer token is required". Show a people-first message such as "Email or password is incorrect."
2. During a first build, fields read "Not found in sources" / Unknown. While building with no completed build, say the field is not researched yet, or that research is in progress. Keep data-status as the API status.
3. On the desktop home screen, the Research button sits below the input's baseline. Align them.
4. Citation links and "Compare sources" are only 16-20 px tall at 375 px. Give them a tap target of at least 44 px.
5. The contested list shows the raw key `hq_city` next to the friendly label. Show the label only. The data attributes stay as they are.
6. The login screen shows the Dossier/Contested nav to a signed-out visitor. Hide or adapt it when signed out.
From the verifier:
7. RUN.md tags the image dossier-stage-1. Tag it for stage 2.
