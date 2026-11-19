VERDICT: PASS
REVISION: 2d57d91816eebc89d258683e98eee368c7eadc65

# Verifier: stage 1, fix round 3

Suite: the sealed stage-1 suite at seal sha256:45147fc3a5f1e980e66610d20e32858163fdab2fb3e3ceac43ed604f6611401c, 102 tests.
This round's amendments were made after I had read the code. They are post-seal additions for SR1-03 / R1-02: a new corpus company, `sextant-labs.test`.
- Its six facts appear only on unsearchable pages, and each is cited by a Nimble research claim.
- 54 searchable pages name the company and support nothing (negated or no value). They come in six groups, one per field's query terms, so the field searches turn up many distinct pages to extract.

## Reported problems, retested first
- **SR1-03 / S1-223, S1-121 (R1-02):** on this revision sextant-labs.test ends ready with all six fields known and correctly cited, at exactly **80 units**. The same test fails on the previous revision 4c325a90: there the extracts used up the units needed to confirm the research claims, so fields stayed unknown.
  Command: `run.sh <clone>/stage-1 -k sextant`.
- **SR1-01:** `providers.py` is unchanged, and research still runs in the window shortened by 35 s. Fake-clock probe in live mode: research can start no later than 220 s and ends by 255 s at worst; the extract after it gets at least 30 s; everything ends by 290 s.
- **SR1-02:** the header-only research claim test passes, both with the cited page extracted and with extract refused.

## Whole stage
1. RUN.md, word for word (RUN.md, Dockerfile and requirements.txt are unchanged): the `--no-cache` build succeeded and `/health` returned 200 under 1 s after start.
2. Check command in isolated mode (`checks/verifier-s1-2d57d918`): stage 1 pass, `claimed stage: 1`.
3. Sealed suite: `COUNTS total=102 passed=102 failed=0`, at 2 vCPU / 3 GiB on an internal network.
4. Cost, with the stress corpus loaded:

   | Build | Units | Known fields |
   |---|---|---|
   | orrery-works | 29 | 6 |
   | kestrel-dynamics | 55 | 3 |
   | lumen-harbor | 55 | 4 |
   | vantor | 46 | 4 |
   | brisa-norte | 56 | 3 |
   | quarry-lane | 45 | 4 |
   | sextant-labs | 80 | 6 |
   | nobody-here | 74 | 0 |
   | vantor refresh | 36 | 5 |

   In total, **476 units for 35 confirmed supported known fields = 13.6 units per supported field**. No build went over 80 units, and spent_units equals the cost in the mock log.
5. Code diff (`research.py`): units are held back for research (25) and for confirming one cited page per field (6), and speculative page extracts get only what is left. A research claim is confirmed only when its excerpt supports the claimed value and is in the prose of a page served in this build. Provider traffic still goes only through WebRouter, and I found no fixture-keyed logic.
6. Upgrade path and restart: not applicable. Fault planting was done on 1c6dd772.

## Findings
None.

## Notes (non-blocking)
- Avoidable spend. Field searches that name the company also return the 54 noise pages, which never mention the other companies, and the service extracts them because their snippets are truncated. As a result the other companies' builds now cost 29 to 74 units, against 5 to 33 before the noise was added; orrery-works rose from 5 to 29 with the same 6 correct fields. A page can name the company further down its prose than the snippet shows, so this is a judgement about cost, not a correctness defect.
