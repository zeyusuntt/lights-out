VERDICT: PASS
REVISION: b9d46b6fd9eabedd13ecc8fb09aa6247ad1fcf17

Seat: verifier. Round 2, after FIX 1 1. Worked from a clean clone (fclone) of the exact hash; fresh no-cache build per RUN.md under 2 vCPU / 3 GiB, internal network, kit mock web.

## Reported problems, retested first
- F1 (encoded-slash path domains): GET and refresh of `/dossiers/https%3A%2F%2Ftarnwick-labs.test`, `/dossiers/tarnwick-labs.test%2Fabout` and `/dossiers/tarnwick-labs.test%2F` now give 422 validation_failed. Fixed.
- F2 (fixture user id over 64 characters): a reset with a 65-char id gives 422 and the prior state (token) still works. A 64-char id gives 204, and login returns that id. Fixed.
Both are now covered by post-seal tests (test_post_seal_encoded_slash_path_domain_422, test_post_seal_fixture_user_id_over_64_rejected), which my seal had missed. They fail on 52f4f877 (4 of 4) and pass here. Reproduce: `run.sh <clone>/stage-1 -k "encoded_slash or user_id_over_64"`.

## Research citation change (research.py, pages.py)
Research excerpts are now cited as the research run served them, without re-extracting. Rechecked:
- Honesty: every citation on 15 companies' first builds, plus refreshes, appears character for character (modulo whitespace) in the text the named provider served for that URL according to the mock call log. Each is 1–500 chars and supports its value by my independent Appendix A oracle (check_citations, on every build test).
- Header excerpts are rejected (is_header_line). When a complete prose page for that URL was already gathered, the excerpt must appear in it.
- Unsupported research claims are not asserted: the nullmark-systems.test research claim "...is not led by a chief executive named Ola Berg." leaves ceo unknown.
- Research-only evidence still counts: the tarnwick-labs.test founded_year 1987 comes from a non-searchable page through research and is known, with no extract.
- Completeness: 81/81 supportable fields correct.

## Whole suite
- `run.sh stage-1`: 177/177 passed (seal sha256:1aebc59f…, which includes the 4 post-seal tests above).
- Check command, isolated: `harness run --track dossier --repo <clone> --stage 1 --mode isolated --out work/checks/verifier-b9d4-r2` → "claimed stage: 1". This is a sample, not a verdict.

## Cost
429 units for 81 correct of 81 supportable fields, 5.30 units per correct field (round 1: 438, 5.41). Per build 27–33 units. The re-extract noted in round 1 is gone: tarnwick-labs.test now spends 27 units, down from 28.

## Notes (no sentence broken)
- N1 `_from_prose` does not itself bound a research excerpt to 500 characters. All observed excerpts were within bounds.
- N2 scrypt still runs on the event loop. The concurrency tests stay under 5 s.
- N3 Fault planting was done on the first passing revision (52f4f877). This round adds only tests for findings the seal missed.
