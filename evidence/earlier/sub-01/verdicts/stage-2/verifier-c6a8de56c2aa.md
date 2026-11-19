VERDICT: BLOCK
REVISION: c6a8de56c2aac958122e5d30806f7dbf6858dd09

# Verifier verdict — stage 2, candidate c6a8de56c2aa (round 2)

Seal: SEAL AMENDED 2 sha256:f7ddd0342e025798c5008487ea949e49d6c8b47b80bf680b0dd3c01fbf2e2a03 (134 tests). Code had been seen. After seeing it I fixed one test and added one post-seal test.

## Reported problem first

- F1 from round 1 (vega-motors.test candidates missing): **fixed**. hq_city is now Milan, cited to registry.test/vega, at 77 units. `vega_selection`, `throttle_every`, `nimble_only_service` and `contested_screen` now pass.

## Steps

1. Clean clone, built with `docker build --no-cache`. RUN.md start works.
2. Check command, isolated mode, output in `checks/verifier-s2-c6a8-1`: "claimed stage: 2". This is a sample only.
3. Sealed suite: **132 passed, 1 failed, 1 xfailed**. The failure is the new post-seal test, F2. The xfail is the R2-09 note (N1 in round 1).
   - The first run's only failure was a fault in my test. A /contested link of the form `/dossiers/twin-forge.test/evidence#evidence-hq_city` is a link to the evidence screen, but my test compared the whole href. I fixed the test, and it passes.
4. Upgrade from the real stage-1 image: passes, as in round 1.
5. Cost: 77 units for vega-motors.test and 65 for orbit-labs.test, both within 80. See note N2.
6. Code read: still every provider call goes through web_router, with no external assets and no fixture keys.
7. Fault planting: not run. It applies only to the first revision that passes everything.

## Finding F2 — evidence returned only by a non-domain search is not read (BLOCK)

Sentences broken:
- §8 "When a build completes ready, each field is known exactly when the evidence (§4) supports a value for it."
- §4 evidence is "every page that some search … for any query naming the company … returns, with its full text".
- stage 2 Candidates. Rulings R1-03 and R2-06.

Trigger, from the builder's stated remaining assumption:
- orbit-labs.test has ten own pages, which fill the domain search.
- A news digest page, https://digest.test/issue-12, is returned **first** by the build's own query "orbit labs founded established incorporated".
- Its title, URL and first 300 characters do not name the company. Its prose ends "Orbit Labs was founded in 2016."

Result: the page is never extracted, so founded_year is `unknown`, with 15 of 80 units left. Expected: `known` 2016.

Reproduce:
- `bash $FACTORY_WORK/verifier/probes/probe-served.sh <stage-2 image> $FACTORY_WORK/verifier/probes/corpus-b orbit-labs.test`.
- Or `run.sh <stage-2> -k postseal_2`.

This is the same reading that blocked stage-1 candidate 408ebd53 (F1 there), now through a non-domain search.

## Notes (non-blocking)

- N1: R2-09 xfail, as before.
- N2: spend. Every read page is a rendered extract at 3 units; the vega build ran at 77 of 80. Rendered and plain text are identical for every page of the mock corpus. Plain extracts would cost a third, which leaves budget to read every returned page. That would also make F2 affordable.
