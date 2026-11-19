VERDICT: BLOCK
REVISION: b1d974f410eae3d2f9c1b1053cfca3bc82cc5e1e

Three confirmed findings. The first was found independently before other-seat verdicts were read. The other two subsequently reproduce product-user's reported UI problems.

For each reproduction below, append this stage-folder argument:

```text
/Users/[REDACTED]/dev/band-factory/work/second-reader/clones/b1d974f410ea/stage-2
```

The private runner builds/starts the supplied stage and documented mock itself; it also obtains the accepted Stage 1 revision for upgrade checks. It requires no other argument and changes no product code.

## SR2-1 — Supported candidates after a generic search snippet are lost

**Units:** S2-054, with S2-002/S2-005/S2-008/S2-080 and inherited evidence completeness.

Two companies each have one returned evidence page. The first 300 prose characters are a generic market introduction; later a separate visible sentence says `Latername CEO: Dana Ruiz.` or `Latersource CEO: Dana Ruiz.`. That sentence supports the CEO under Appendix A. One page is on the company host, the other on a journal host. Both have Kind news and a valid publication timestamp.

**Actual:** ready dossier, 32 spent units, CEO null/unknown with no candidates. Every provider call succeeded. The page occurs in the successful search log, but no extract was made: seven searches plus one research run were charged. An additional three-unit rendered extract fits well within the 80-unit cap.

**Expected:** retain the supported Dana Ruiz candidate, select Dana Ruiz, and report known. A search snippet omitting the company/fact cannot exclude a returned evidence page's full-text support.

```sh
SECOND_READER_ONLY=candidates-later /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/b1d974f410ea/stage-2
```

Result: **2 failed, exit 1**. Diagnostics: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/artifacts/candidate-latername.test.json` and `candidate-latersource.test.json` beside it. This differs from verifier F1: the page already was returned in this build, and each company has only one page.

## SR2-2 — A committed write with delivery withheld remains Sending without uncertainty/retry

**Units:** S2-117/S2-173/S2-174; also confirms the product-user's stalled-screen finding.

The actual `POST /dossiers` returns 202 to the interceptor, but its response is withheld from the browser. The dossier completes ready on the service. After **45 seconds** the browser still shows Sending, no `research-uncertain`, and no usable same-key retry path on the form. Ordinary immediate response-abort handling does pass; the pending-delivery case does not recover.

```sh
SECOND_READER_ONLY=corroborate /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/clones/b1d974f410ea/stage-2
```

The `corroborate-hanging-response` probe fails. Screenshot: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/artifacts/corroborated-pending-response-45s.png`. Provide uncertainty/retry recovery preserving the original key/body; this finding does not mandate a specific timeout value or implementation.

## SR2-3 — Visible null text in the signed-out header

**Unit:** S2-106; also confirms product-user's unfinished-screen finding.

A fresh anonymous browser renders `Dossier.`, `null`, `Sign in`, `Create account` in its header. The raw null is visible UI output, unrelated to user data or an intentional status. The same corroborate command above fails `corroborate-anonymous-header`.

Screenshot: `/Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-2/artifacts/corroborated-anonymous-header.png`.

## Audit evidence

The expanded full independent run has **173 cases: 169 passed, four failed** (6964 assertions); the two returned-page cases share SR2-1. Targeted follow-ups confirm the pending response at 45 seconds, the anonymous header, the rendered UI audit, and the successful post-import replacement path. All 154 inherited checks pass on their original corpus; these added cases expose behavior outside that passing set.

Candidate ranking/ties/metadata, research-cited pages, 429s, normal browser routes and exact attributes at 375/1280, signup/login/logout/errors, empty/unknown/not-found/building states, latest-read-wins, immediate lost-response retry, and real Stage 1 upgrade/session/retry preservation pass. The full sample harness claims Stage 2 with **122 Stage 1 + 12 Stage 2** checks passed; it remains supplementary evidence.

Ledger audit exits **1** for nine units with failing evidence and no missing rows. Every normative/ruled unit has evidence for this revision. The verifier's distinct query-coverage BLOCK was read only after independent probes, as was product-user's report; their private test sources were not read. No product code/tests were changed. All private probes remain unpublished until every stage closes.

Complete commands, coverage, source-review limits, ruling applications, and results: `ledger/stage-2-audit-b1d974f410ea.md`.
