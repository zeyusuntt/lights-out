VERDICT: PASS
REVISION: cd24f51fb21b312aac2398adff8813a1b6276b57

Seat: verifier. Stage 3, round 1. Worked from a clean clone (fclone) of the exact hash.
- stage-3/ was built fresh with no cache per RUN.md.
- The clone's accepted stage-1/ and stage-2/ were built as previous-stage images for both upgrade paths.
- All ran under --cpus 2 --memory 3g on an internal network with the kit mock web.

## Evidence
- Sealed suite `run.sh <clone>/stage-3`: 269/270 in the full run. The one failure was my test's misreading (below), fixed; the fixed test and the rest of its file then passed (37/37). A post-seal latency test passed (2/2 with the 50-in-flight test). Seal sha256:c64bd8a7…, 271 tests.
- Restarts, with real abrupt stops (`docker kill` + `docker start`):
  - Phase B, idle stop: answers to /dossiers, ?as_of=, /values, /history and /changes are identical; tokens, logins and replays survive; the clock is kept; a new feed seq is larger than every earlier one (4/4).
  - Phase C, kill mid-build (R3-4): rolled back to the pre-build dossier, history and feed; not stuck in building; the 202 replays; a new refresh ends ready (2/2).
- Check command, isolated: `harness run ... --stage 3 --mode isolated --out work/checks/verifier-s3-cd24-r1` → "claimed stage: 3". This is a sample, not a verdict.

Covered:
- All stage-1 and stage-2 tests still in force, with 7 fields.
- Executives oracle: per-title selection, citations, status and true_from.
- true_from from Effective, else the UTC Published date (23:30 -02:00 gives the next day), else null.
- learned_at of candidates and of selected values.
- History and feed against a model over 3 epochs: initial, change, correction, a value disappearing, a first value after unknown, executives typed by title, null-value learned_at (R3-2).
- Feed paging and validation.
- ?as_of= snapshots, including same-time ties, equivalent offsets, spent totals and in-flight spending (R3-1).
- /values page versions at 11 dates under 2 as_of settings, including a candidate-free gathered version ending an earlier one (C2).
- Same value adds nothing; a failed build adds nothing; 20 concurrent refreshes add each entry once.
- Stage-3 export/import round trip.
- Upgrades from the real stage-1 and stage-2 images (R3-3).

## Suite amendment after seeing code (test misreading, not a finding)
test_stage3_export_import_round_trip called reset before the import, and reset moves the clock to the fixture's now. /values without as_of defaults to the clock, so it compared different moments. The test now sets the clock back to the exporter's time; the service was right.

## Durability (code read, as asked)
- A write's response is not sent before it is durable: routes.persist_writes awaits service.persist() for every non-GET request before returning the response.
- store.Store writes the whole snapshot to a temp file, fsyncs it, os.replace()s it into place and fsyncs the directory.
- Concurrent saves are grouped. The snapshot is taken under the lock after the covering requests' mutations, so a grouped save never acknowledges a write it did not include.
- Latency: 50 concurrent signups, then 50 concurrent POST /dossiers on an existing dossier, each under the 5 s bound, with no 5xx. The 200-request mixed load at 50 in flight also passes.

## Cost
1132 units over 22 first builds, for 96 correct of 96 supportable fields: 11.8 units per correct field. Per build 37–70 units (max 70 of 80).

## Fault planting (first passing revision of stage 3), 7 copies
- Caught: correction test using < for <=; as_of spent summing every build; feed order reversed; first value after unknown typed initial; persistence middleware removed (phase B); version end inclusive.
- Survived, equivalent: a later version replacing only earlier versions with strictly later true_from. The kept equal-dated version gets end = its own start, so it holds on no date; no observable difference.
No suite holes found this round.

## Notes (no sentence broken)
- N1 The whole state is rewritten on every write. That is fine at test scale, but write cost grows with state size.
- N2 The heaviest build spends 70 of its 80 units, which leaves little headroom on larger companies.
- N3 scrypt runs on the event loop. The 50-signup burst stayed within 5 s.
