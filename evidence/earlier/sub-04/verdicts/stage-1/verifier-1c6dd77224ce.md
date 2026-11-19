VERDICT: PASS
REVISION: 1c6dd77224ce853f5a4b646ec071b1ae609e7fe1

# Verifier: stage 1

Suite: sealed stage-1 suite, current seal sha256:afe277ffd438ecd82b97bf113af480e4aab27d654df8cb59dc1229f070507944 (100 tests).
Seal history: the first seal (91 tests) and the first amendment (99 tests, after the ledger and rulings) were both made before any code existed. The amendments made on this revision are below.

## Evidence
1. Clean clone: `fclone 1c6dd772… cand`. RUN.md followed word for word: `docker build --no-cache -t dossier-stage-1 .` built. `docker run … -e PORT=8080 -e NIMBLE_API_KEY=… -e NIMBLE_BASE_URL=http://web:8080/nimble` gave a healthy service in about 1 s. Against the kit's sample corpus: reset 204, login, and a POST /dossiers for quillmate.test ended ready, costing 39 units, with 5 fields known. No step was missing.
2. Check command (isolated): `harness run --track dossier --repo <clone> --stage 1 --mode isolated --out checks/verifier-s1-1c6dd772` reports `stage 1: pass` and `claimed stage: 1`. Its stage 2 failure is expected.
3. Sealed suite: `sealed/stage-1/run.sh <clone>/stage-1` (no-cache build, 3 instances at 2 vCPU / 3 GiB, internal network) gave `COUNTS total=100 passed=100 failed=0`.
   The first run, at the pre-candidate seal, gave 96/99. All 3 failures were my own test errors, fixed in the amendment:
   - the client library itself refuses the header `Bearer ` with a trailing space;
   - the "253-character" domain was actually 254 characters long;
   - one test read a www.-prefixed dossier through a path that normalises away its www.
4. Upgrade path: none. This is the first stage.
5. Restart: §2 "state need not survive a container restart". Nothing is required to survive.
6. Cost, measured from the mock call log on the suite's corpus. There are 8 builds: 7 first builds and 1 refresh.

   | Build | Units |
   |---|---|
   | orrery-works | 5 |
   | kestrel-dynamics | 30 |
   | lumen-harbor | 31 |
   | vantor | 29 |
   | brisa-norte | 30 |
   | quarry-lane | 29 |
   | nobody-here | 33 |
   | vantor refresh | 28 |

   In total, 215 units bought 29 known fields that the checks confirm as supported: **7.4 units per supported field (215 / 29)**. All 48 fields were correct, including the unknown ones. No build exceeded 80 units, and in every build spent_units equals the cost in the log.
7. Code reading:
   - All provider traffic goes through `web_router.AsyncWebRouter`, Nimble only, and `requirements.txt` lists `webrouter>=0.12.0`. There are no direct HTTP calls to providers and no credentials in the tree.
   - Units are reserved before each call (`Budget.reserve`). Refused calls cost 0; lost answers cost their full price.
   - Live bounds:
     - 45 s per call, which is at least 30 s;
     - retries allowed for up to 200 s;
     - a build deadline of 290 s, which is within 300 s.
   - A stale build is dropped by a check on the store's identity.
   - spent_units includes the running build's spend at every read.
   - I found no answers keyed to fixtures.
8. Fault planting: 8 faults, each in its own throwaway copy, each run against the relevant part of the frozen suite.
   - Caught (6): per-user key scope, refresh overwriting spent_units, `www.` not stripped, researched_at taken at completion, a case-sensitive `q`, and citations mixed across values.
   - Survived (2):
     - Removing `not` from the negating phrases: a hole in the suite. Post-seal addition: a corpus sentence whose only negation is `not`. That copy is now caught, and the real revision passes it (18/18 on the evidence and amendment subset).
     - Dropping the store-identity check on a stale build: an equivalent change. After a reset the stale build writes only to the old dossier object, which nothing can reach. No test is possible.

## Findings
None.

## Notes (non-blocking)
- Tavily is not used. That is allowed: §2 makes Tavily optional.
- Pages are extracted only while units remain after reserving the research run and 3 spare units. On a company with very many search results, some might go unread. I did not observe this with ≤10 pages per company.
- On the sample corpus, both search and plain extract serve the about page's static text ("head office in Brno"), so `hq_city=Brno` is the value the evidence supports. This is correct.
