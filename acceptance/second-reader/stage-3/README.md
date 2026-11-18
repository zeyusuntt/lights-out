# Independent Stage 3 audit

Run `./run.sh <stage-folder>`. It builds the supplied service, the documented mock web, and the team's accepted Stage 1/2 services for upgrade tests; starts its own uniquely named containers; runs the public sample corpus, inherited API/browser regressions and independent Stage 3 probes; prints counts; removes its containers; and exits nonzero on a failure. No product module or supplied/peer check source is imported.

The only required argument is the complete stage folder. If accepted earlier-stage siblings are absent, the runner clean-clones their fixed accepted commits. Host Docker, factory `with-slot`/`fclone` tools, Python 3 and the supplied df-harness-runner browser image are used. Service containers run at 2 vCPU and 3 GiB. Provider calls go to the actual kit mock through a timestamp-only forwarding proxy; mock faults and corpus epochs are controlled through its documented admin API. No real provider is contacted.

`temporal.py` supplies authored corpora and independent HTTP oracles for candidate/selected learning dates, UTC Effective fallback, page-version replacement and empty/undated versions, as_of ties and spending, title-specific executive support/selection/correction typing, immutable history/feed, global cursors, legacy reconstruction under R3-3, native temporal transfer, idle abrupt restart, interrupted-build rollback, response durability and 50 concurrent writes. `browser.py` repeats inherited route/retry/read-order journeys at desktop/mobile sizes and checks executive markup plus the six-field contested contract.

Optional selectors: `SECOND_READER_ONLY=case1,case2`, `SECOND_READER_FIRST=case1,case2`, `SECOND_READER_NO_BROWSER=1`, or `SECOND_READER_BROWSER_ONLY=browser-case-without-browser-prefix`. The required sample still runs. Default invocation runs everything. Each run prints a private PROBE_WORK directory and writes last-results.json; that file and transient artifacts are excluded from eventual probe publication. Exports and tokens stay in memory. Browser temporary configuration is removed.

The probes are private until all stages close; only then does the second-reader publish them with fpublish.
