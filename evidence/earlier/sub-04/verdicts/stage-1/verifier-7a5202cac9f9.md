VERDICT: PASS
REVISION: 7a5202cac9f9b10c173487164654f09ad96781da

# Verifier: stage 1, fix round 5

Suite: the sealed stage-1 suite at seal sha256:695dba98ec8e745cd5ae11760eca21bade4e40872fad1390d98188c3d0dab3c1, 105 tests.
This round's amendment was made after I had read the code. It is a post-seal addition for SR1-05: 50 simultaneous creates for 50 distinct companies, with every Nimble method delayed 0.5 s.

## Reported problems, retested first
- **SR1-05 / S1-224, S1-312:** all 50 builds end `ready` within 10 s of their own POST on this revision. On the previous revision 3b729f1a the builds took about 28 s.
  Command: `run.sh <clone>/stage-1 -k fifty`.
- **SR1-01:** fake-clock probe in live mode, unchanged: research can start no later than 220 s and ends by 255 s at worst; the extract after it gets at least 30 s; everything ends by 290 s.
- **SR1-02, SR1-03 and SR1-04:** the header-only claim test, the sextant-labs test (80 units) and the two request-body tests pass.
- `data_apis=False`: the mock log still records each search as a Nimble `lite` search at 1 unit, and spent_units matches the log exactly.

## Whole stage
1. RUN.md, word for word (RUN.md, Dockerfile and requirements.txt are unchanged): the `--no-cache` build succeeded and `/health` returned 200 under 1 s after start.
2. Check command in isolated mode (`checks/verifier-s1-7a5202ca`): stage 1 pass, `claimed stage: 1`.
3. Sealed suite: `COUNTS total=105 passed=105 failed=0`, at 2 vCPU / 3 GiB on an internal network.
4. Cost: 476 units over 9 builds for 35 confirmed supported known fields, **13.6 units per supported field**. The most any build spent was 80.
5. Code diff (`providers.py`, `research.py`): 16 routers in rotation and an in-flight cap of 256. Units are still reserved before every call, and I found no fixture-keyed logic.
6. Upgrade path and restart: not applicable. Fault planting was done on 1c6dd772.

## Findings
None.

## Notes: the page pattern behind the avoidable spend, as the foreman asked
The extra extracts come from search results that do not name the company being researched. Each such page:
- names only another company;
- has prose of about 360 characters, so its lite snippet is cut off at 300 and the service treats the page as unread;
- has a title and text built from one field's statement-phrase words (for example "legal name registered company entity"), and a title that also contains another company's `.test` domain.

So when a build searches `"<Company> <that field's phrases>"`, BM25 ranks these pages among the top 10 on the phrase words alone. The domain search for a small company also returns them to fill its 10 results, matching the `test` token in their titles.

The service extracts every returned page whose snippet is not its whole prose, so it pays 1 unit per such page, up to the room left after research and confirmation are reserved. Yet neither the title nor the snippet of these pages names the company or its domain.

Effect in my corpus: orrery-works.test, whose own four pages hold all six facts, went from 5 units to 29 for the same six correct fields once such pages existed for another company.

A pattern like this is plausible in the graded corpus: any news page about some other company that uses the same field vocabulary. One possible economy is to rank or defer the extraction of results whose title and snippet name neither the company nor its domain. But such a page can name the company further down its prose, beyond the snippet, so this is a judgement about cost, not a correctness defect.
