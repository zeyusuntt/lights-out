VERDICT: PASS
REVISION: a34bf561b2bc5cdb5233e6cf26f4cae44098dd85

# Verifier verdict: stage 1, round 2

Seal in force: SEAL AMENDED 1 sha256:81f64c9c956db541bd385a495521aea2c82a149c4fb68156d4fa0c2527b5c0a1, 176 tests. `seal --verify` returned ok before the run.

## Reported problems, retested first

- **SR1-1 (S1-156), NaN / Infinity / -Infinity bodies:** 400 `malformed_request` on signup, login, reset, clock, POST /dossiers and import. The NaN create made no dossier. PASS.
- **R1-5, a display_name of only spaces:** 201, with display_name returned unchanged. PASS.
- Command: `NOCACHE=0 VPORT=19200 sealed/stage-1/run.sh clone-a34b/stage-1 -k "r1_5 or sr1_1"` → 6 passed.
- **RUN.md note from round 1:** fixed. I ran the command word for word in an empty environment (`env -i`). /health answered 200, and NIMBLE_BASE_URL is no longer set inside the container (checked with `docker exec … env`).

## Whole run (clean clone `fclone a34bf56… clone-a34b`)

1. **Product diff since c772508:**
   - app/api.py: strict JSON parsing with `parse_constant`, now also used by import.
   - app/service.py: the display_name check.
   - RUN.md: NIMBLE_BASE_URL is passed only when set.
   - No change to the gateway, planner, budget, builds or support code.
2. **Check command, isolated mode** (`checks/verifier-s1-a34b-r2`): "stage 1: pass", "claimed stage: 1". This is a sample only and not evidence on its own.
3. **Sealed suite:** `sealed/stage-1/run.sh clone-a34b/stage-1`, no-cache build, 2 vCPU / 3 GiB, -e PORT. Result: **176 passed, 0 failed** (171 s). Healthy in 0 s; about 248 MiB of memory.
4. **Upgrade path:** none; this is stage 1.
5. **Cost:** from the mock's priced call log. I checked every citation on every known field as served prose that supports its value; none were unsupported.
   - The kit's sample corpus, 12 companies: **369 units for 69 supported fields, 5.35 units per supported field.** Same as round 1.
   - My corpus, 6 companies, now including sprawl-hub.test: **293 units for 18 supported fields, 16.28 units per supported field.**
   - No build exceeded 80 units.
6. **Code read:** the diff only, since nothing else changed. Nothing found.
7. **Fault planting:** done on c772508, the first revision to pass (round 1 verdict). The parts this round touched are JSON parsing and display_name, and my new tests cover both.

## Findings

None.

## Notes (do not block)

- **Spend on companies with nothing to support.** With sprawl-hub.test in the corpus, searches for quiet-harbor.test and nothing-here.test also return sprawl-hub pages. Those pages name a different company, and the build extracts them anyway. Those two builds cost 77 and 80 units (48 and 45 extracts plus the 25-unit research run), up from 43 and 42. They support nothing, and the 80-unit cap holds.
  - The specification counts as evidence only pages that a search for a query naming the company returns, and support requires the excerpt to name the company. Skipping the extract of a page whose served text gives no sign of naming the company may lose nothing.
  - It is not strictly avoidable: an extract could show text that a search snippet left out. So this is a note with the numbers, not a finding.
