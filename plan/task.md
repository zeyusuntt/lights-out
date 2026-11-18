You are the lead seat of this factory. Build the job below, stage by stage, with the band, to the end, without asking me anything. This message is the only human input of the run.

Result repository (absolute path, empty, the band commits here): /Users/sunzeyu/dev/band-factory/work/result
Stage folders: /Users/sunzeyu/dev/band-factory/work/result/stage-1/ to stage-4/. Each is a complete service with its own Dockerfile and RUN.md, and holds that stage's solution, nothing from a later stage. Stage n+1 starts as a copy of the accepted commit of stage n. An accepted folder never changes again.

Specifications, in order: /Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026/challenges/dossier/spec/stage-1.md /Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026/challenges/dossier/spec/stage-2.md /Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026/challenges/dossier/spec/stage-3.md /Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026/challenges/dossier/spec/stage-4.md
No seat, the foreman included, reads a stage's specification before the previous stage is accepted; each stage reaches the seats when the foreman opens it. Earlier stages' requirements continue to apply unless a later stage says otherwise.

Check command, run through the job's kit and only that way, new output directory each time:
cd /Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026 && with-slot .venv/bin/python -m harness run --track dossier --repo <clean clone of the result repository> --stage <n> --mode isolated --out /Users/sunzeyu/dev/band-factory/work/checks/<new-name>
It prints "claimed stage: <n>" when a stage folder claims its stage. It runs a sample only, and a green run is not evidence of a stage. Its check sources are not to be opened by any seat.

Tools for tests: /Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026/.venv/bin/python has pytest, httpx and playwright with chromium. Where a sandbox stops a browser launching, the Docker image df-harness-runner has python, playwright and chromium; attach it to the service's container network.

Event rules for this track, published 11-11, binding on every stage alongside the specifications:
- Deliver each stage as one self-contained container with its own Dockerfile and RUN.md. stage-1 must build and serve from a clean container by following its RUN.md.
- Route every provider request through the Python `webrouter` package, in-process or through a Python helper inside the same container. The dependency manifest must list `webrouter>=0.12.0`. No direct provider API calls outside WebRouter. WebRouter's own documentation may be used; source code, API documentation or schemas from existing products in this domain may not.
- Research must work through Nimble alone. Tavily, Kernel and Browserbase are optional, and their absence must not prevent research while Nimble answers.
- Put every runtime dependency and asset in the image. Docker builds may fetch dependencies; the graded runtime reaches only the specified provider endpoints, supplied by the local mock web.
- Operate within 2 vCPU and 3 GiB of memory. Compose is optional and the harness does not use it.
- Support asserted facts with excerpts actually served by a provider to the service. Never invent or rewrite a citation, or attach an excerpt that does not support the value.
- No single dossier build may exceed 80 research units. Research spend per correct field is judged, so spend no more than correct answers need, and correctness comes first: a saving that leaves out evidence a field needs is a defect. Plan the searches once per build, reuse within one build the text a provider has already served (a refresh calls again), and reserve units before each call.
- For development and your own checks, a local mock web stands in for every provider. Read /Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026/challenges/dossier/web/README.md and run the mock web the way it says, with its sample corpus. Its `key.json` and the kit's `test/` folders stay closed to every seat: they hold the checks' answers, and code built to them disqualifies the entry.
- The graded checks run in isolated mode: an internal network with no outbound access, 2 vCPU and 3 GiB.
- No credential goes into the repository, its history or the room.

Seats: foreman, builder, verifier, second-reader, product-user

Done for each stage means: the check command claims the stage; the ledger shows evidence for every sentence on the accepted revision; every verifying seat has passed that exact revision. When all stages are closed or the line has stopped, report to me once.
