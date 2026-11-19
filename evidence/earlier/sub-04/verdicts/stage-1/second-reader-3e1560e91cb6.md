VERDICT: BLOCK
REVISION: 3e1560e91cb662d7595fed833008e3bd91904d61

# Independent second reading audit, fix round 1

## SR1-01 retested first: resolved

The original live-call deadline reproduction passed before the whole stage rerun. Research status/result arrived at 284.02/284.07 seconds, the service started no late extract, and the build completed at 284.14 seconds with the valid late research claim retained. The full rerun repeated this case successfully, including independent checks of its actual served citation text, page prose, support, and cost. Source inspection confirms that the outer build cancellation is removed and the remaining allowance is checked both before reservation and after acquiring a provider slot.

## Blocking finding SR1-02 — S1-128 and S1-143: a header fragment becomes a citation when its page remains unread

When a research answer arrives too late to extract its cited page, `_in_prose` accepts a quotation if the quotation itself does not look like a complete header line. A fragment quoted from inside a header value passes that test. The delivered API then uses header text as a citation, violating S1-128 (an excerpt is taken from page prose, not its header) and S1-143 (Facts is informative only; citations come from prose).

The independent fixture uses the official mock unchanged, retaining every supplied sample company and traits and adding one fictional company. Its unsearchable page has the valid header:

```text
Facts: {"hq_city":"Proof Harbor is headquartered in Porto."}

The public record concerns Proof Harbor. The record supplies no company profile in its prose.
```

The quoted sentence occurs only in that header. The Facts keys and arbitrary-format values are permitted by S1-141–142; S1-143 explicitly prohibits using them as citation prose. Nimble research claims hq_city Porto with citation excerpt `Proof Harbor is headquartered in Porto.` for that page's real URL. That fragment is character-for-character provider-served text and passes Appendix A's grammar; it remains a header quotation.

Two operations against the same fixture demonstrate the defect:

1. **Fast control:** ordinary research and extract obtain the full page. The API correctly returns the field unknown; the independently computed support/citation oracle passes.
2. **Delayed research:** the ordinary live-mode timing sequence delivers research at second 284, leaving insufficient time for a new extract. At **284.17 seconds**, with no late extract started, the API returns:

```json
{"value":"Porto","status":"known","citations":[{"url":"https://proof-harbor.test/register","excerpt":"Proof Harbor is headquartered in Porto.","provider":"nimble"}]}
```

Its sole citation came from the Facts header. The fast/slow difference is caused by skipping page verification; the provider's page and research claim are identical. The claim must not be accepted with that citation.

Reproduction on a fresh exact clone:

```sh
fclone 3e1560e91cb662d7595fed833008e3bd91904d61 /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-02
SECOND_READER_ONLY=research-header-citation-fast-control,research-header-citation-late /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-sr1-02/stage-1
```

It builds/starts the stage and official mock itself on an internal network with 2-vCPU/3-GiB service limits. It uses the supplied sample corpus plus the one private adversarial fixture; it does not open/copy the answer key or any kit tests. The control passes and the delayed case fails: `COUNTS total=2 passed=1 failed=1`, exit 1, in about five minutes. The root `run.sh <stage-folder>` runs both alongside every other probe by default. Probe sources remain private until every stage closes.

Source corroboration, read after independent execution: `stage-1/dossier/research.py` collects the claimed value and snippet, calls `_fetch(unseen)`, then `_in_prose`; when neither full page nor prose exists, `_in_prose` returns `not is_header_line(excerpt)`. The new time window can legitimately prevent the fetch, exposing that insufficient provenance check. No product code or product test was edited.

## Complete audit evidence

The original 38-case whole-stage rerun passed on this exact revision, including both sample epochs, the deadline reproduction, and its late prose citation. The two added provenance cases gave one pass and one failure. Across all **40 independent cases: 39 pass, 1 fails**. There is one blocking finding, SR1-02, covering S1-128 and S1-143.

The ordinary probes cover auth/error conventions, fixed/system clock behavior, validation, idempotency identity and precedence, 50-writer races, reset with a build in flight, failure/recovery refresh, listing, running-build spending, and replacement export/import. The transfer probe stops the source before importing and proving session/hash-login/dossier/original-response independence, then starts the source again. Default PORT and an explicit PORT=8089 both served health from the built image. The exact clone remained clean.

Both epochs of all 12 supplied sample companies passed: 24 sample builds, 138 supported known fields, 669 research units, largest sample build 40 units. Citation characters, actual provider serving, page-prose origin, Appendix A support, value types, schema fields, literal-domain query counts, and costs are independently checked. The adversarial company's fast build is accounted separately and stays under 80 units.

The verifier's committed PASS on this exact revision, including its 100/100 suite and isolated check claiming stage 1, was read after independent execution. The header-fragment provenance case supplies additional concrete evidence; that PASS does not change this finding.

The refreshed ledger covers all 379 units with current-revision evidence for all 318 normative/ruled units. `ledger-check 1 --phase audit --revision 3e1560e91cb662d7595fed833008e3bd91904d61` remains nonzero for S1-128 and S1-143. Details are in `ledger/stage-1-audit-3e1560e91cb6.md` and `ledger/stage-1-probe-results-3e1560e91cb6.md`. Owned containers, networks, and temporary corpus copies were removed.
