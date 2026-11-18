# Independent second-reader probes

Published after all four stages were accepted. Each stage's `run.sh` takes one argument: a complete service folder. It builds and starts that folder, runs the documented mock sample and independent probes, prints counts, and exits nonzero on failure. Stage READMEs describe optional selectors.

From the repository root, run any stage:

```sh
acceptance/second-reader/stage-1/run.sh "$PWD/stage-1"
acceptance/second-reader/stage-2/run.sh "$PWD/stage-2"
acceptance/second-reader/stage-3/run.sh "$PWD/stage-3"
acceptance/second-reader/stage-4/run.sh "$PWD/stage-4"
```

Use the job's Docker environment, `with-slot` and `df-harness-runner` image. Set `DOSSIER_KIT` if the supplied kit is outside its original factory path. Generated results and temporary run directories are ignored; real credentials are not required. Mock keys and seeded users are local test fixtures. No supplied check source, product test source or peer test source is used by these probes.

Ledger evidence now links to these repository-relative runners. Each relocated reference preserves its original execution path in `original_ref`; the tested revision and result are unchanged. Publication verified every copied file against its private original. The recorded final independent counts were 183, 205, 246 and 305 passing probes for stages 1 through 4, respectively. Refer to the exact accepted-revision verdict for its commands and limitations.
