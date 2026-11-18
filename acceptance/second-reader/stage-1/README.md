# Independent Stage 1 probes

```sh
./run.sh /absolute/path/to/any-clean-copy/stage-1
```

One argument is required. The runner builds the supplied folder's Dockerfile and the kit mock, starts them with 2 vCPU and 3 GiB, exercises the required public sample corpus and independently generated corpora, prints per-case results and counts, removes its containers/networks, and exits nonzero if any probe fails. It does not import product modules or read product tests.

Prerequisites are Python 3, Docker, and `with-slot` on PATH. `DOSSIER_KIT` optionally overrides the dispatched kit directory. Build subprocesses have 30-minute timeouts; other Docker commands and HTTP waits are bounded. Run one invocation at a time: host HTTP ports are within 20040–20043. Host access uses a bridge network; the dispatched harness's separate isolated run is recorded in each verdict.

`last-results.json` is generated locally. Temporary corpora, build metadata and container logs go in the sibling `runs-stage-1` directory. Credential-bearing service exports stay in memory.

Optional selectors preserve the single-argument interface:

```sh
SECOND_READER_ONLY=encoded-path-domain-validation,fixture-id-length-boundary ./run.sh /path/stage-1
SECOND_READER_ONLY=research-header-shaped-prose-is-evidence,research-excerpt-length-limit ./run.sh /path/stage-1
```

The required sample corpus still runs with a selector. `SECOND_READER_FIRST` prioritizes selected cases during a complete run; the initial system-clock check runs before cases that reset the fresh process.

The research regression corpus distinguishes a real Facts header from a `Profile:` label occurring after the page's header/prose delimiter. It also serves a 1,056-character supporting research sentence to check the API's 500-character citation limit. These are ordinary mock page/research inputs, derived from the numbered specification, with no answer key or shipped check source used.
