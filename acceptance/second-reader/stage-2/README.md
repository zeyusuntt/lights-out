# Independent Stage 2 probes

```sh
./run.sh /absolute/path/to/clean-copy/stage-2
```

One argument is required. The runner builds the supplied stage, the required kit mock and the accepted Stage 1 service, then runs inherited API regressions, candidate/ranking/rate-limit/upgrade probes and Chromium browser journeys at 1280 and 375 CSS pixels. The legacy image uses the sibling stage-1 folder; if absent, the runner clones accepted revision a8789dcd65a18ca385d968116c51d23590913c33 through fclone. It never imports product modules or reads product/peer test sources.

Prerequisites: Python 3, Docker, factory with-slot/fclone tools, and the kit browser image df-harness-runner. DOSSIER_KIT optionally overrides the dispatched kit directory. Builds use with-slot and bounded subprocess timeouts. Browser jobs also use with-slot. Service containers have 2 vCPU and 3 GiB. Run one invocation at a time; host ports are within 20040–20044. Host HTTP probes use a bridge network; isolated harness results are recorded separately in the verdict.

The provider proxy only forwards to the actual kit mock and records request/answer times and argument identity, without recording auth headers. It enables a direct check that retries begin at least one second after a 429 response. Every product provider request still originates through WebRouter.

Outputs: last-results.json beside the runner; corpora, sanitized browser results, screenshots, container logs and build metadata in sibling runs-stage-2. No exported credential-bearing service state is written there; upgrade exports stay in memory. Temporary browser configuration is removed after use. Containers and networks started by the runner are removed on completion.

Optional selectors retain the one-argument interface:

```sh
SECOND_READER_ONLY=stage2-slow-research-then-throttled-extract SECOND_READER_NO_BROWSER=1 ./run.sh /copy/stage-2
SECOND_READER_ONLY=stage2-html-shell-content-negotiation SECOND_READER_BROWSER_ONLY=latest-manual-read-wins ./run.sh /copy/stage-2
```

The public sample corpus still runs with selectors. With no selectors, every probe runs, counts are printed, and any failure yields a nonzero exit. SECOND_READER_NO_BROWSER is only for focused API reproductions, not the complete audit.

Rulings R2-1 through R2-5 govern cooldowns, HTML shells, dual-format timestamps, token continuity and legacy migration from surviving citation excerpts. Legacy reconstruction tests excerpts against every field and checks deduplication and metadata nulls. Browser retries compare the original key/body and test a committed lost response across a Stage 1 export/Stage 2 import without reading localStorage implementation details.
