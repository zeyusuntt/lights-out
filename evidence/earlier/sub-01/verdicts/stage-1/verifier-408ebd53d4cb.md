VERDICT: BLOCK
REVISION: 408ebd53d4cb62fbbb460c876c1d9e9d6f8566e6

# Verifier verdict — stage 1, candidate 408ebd53d4cb

Seal: SEAL AMENDED 1 sha256:164853f03d60c1760bd851685e6001b843123f269b6a589b6562f396a5723cdc (101 tests).
The last pre-code seal was sha256:89588eeb… (100 tests). After seeing the code I made two changes: I fixed one test helper bug, and I added one test.

## Steps

1. Clean clone via `fclone`. Built with `docker build --no-cache` and started word for word from RUN.md, against the mock web. It was healthy after about 2 s, and a build of acme-robotics.test returned all six correct fields at 36 units. No finding on RUN.md. The manifest lists `webrouter[search,extract,research]>=0.12.0`.
2. Check command, isolated mode, output in `checks/verifier-s1-408e-1`: "claimed stage: 1", and stage 1 passed. As the task says, this is a sample only.
3. Sealed suite, `run.sh <clone>/stage-1`. The suite builds with no cache and runs on an internal network at 2 vCPU / 3 GiB, with a Nimble-only container and a container that is never reset. Result: **100 passed, 1 failed** (185 s). The first run also failed `test_missing_or_empty_key_400`. That was a bug in my test helper, which turned an empty key into a random one. I fixed the helper and recorded the fix as an amendment; on re-run the product passes that test.
4. Upgrade path: none (stage 1).
5. Cost: 33 to 36 units per build on the verifier corpus, always under 80. The README reports 44 to 51 units on the sample corpus. No finding.
6. Code read: every provider call goes through `web_router`'s AsyncWebRouter with the nimble provider, and no other HTTP client calls a provider. I found no fixture-keyed answers or special cases. Live-mode limits: per-call timeout 60 s, research wait 240 s, build deadline 285 s. These are consistent with §8.
7. Fault planting: not run. It applies only to the first revision that passes everything.

## Finding F1 — a field the evidence supports is left unknown (BLOCK)

Sentences broken:
- §8 Builds: "When a build completes `ready`, each field is `known` exactly when the evidence (§4) supports a value for it."
- §4 Evidence: "every page that some search … for any query naming the company … returns, with its full text."
- Ruling R1-03: a field the evidence universe supports but the build left `unknown` is a defect.

Trigger: a page about the company that the domain search returns, whose title, URL and first 300 characters of prose do not name the company. Later in its prose is a supporting sentence: "Lumen Grid was founded in 2011." This is an ordinary news or digest page.

Observed: the search for the exact domain `lumen-grid.test` returned the page. The build never extracted it, so `founded_year` came back `unknown`. The build spent 33 of its 80 units. Cause, from reading the code: `dossier/gathering.py`, `Gatherer._about_company`. Pages are read only when the lite title or snippet names the company, or the URL contains its slug.

Reproduce: `bash $FACTORY_WORK/verifier/probes/probe.sh <image built from stage-1> $FACTORY_WORK/verifier/probes/corpus-a lumen-grid.test`. Expected founded_year 2011, got null. The sealed suite has the same case as a post-seal test: `run.sh <stage-1> -k postseal`.

## Notes (non-blocking)

- Every build runs six additional field-keyword lite searches (6 units) and a research run (25 units). That is within budget, and the research run is needed for evidence only research reaches (R1-11).
