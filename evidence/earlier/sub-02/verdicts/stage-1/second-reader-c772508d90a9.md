VERDICT: BLOCK
REVISION: c772508d90a96c5214a26528c59a93ba38336cd3

One confirmed finding covers all three failing probes. No other confirmed problems were found in this audit.

## SR1-1 — Invalid JSON numeric literals are accepted and start dossier builds

**Specification unit:** S1-156. An unparseable JSON body must return `400 malformed_request`. `NaN`, `Infinity`, and `-Infinity` are not JSON values, including when they appear in a field that would be ignored after successful parsing. Unknown-field ignoring in S1-088 does not permit invalid JSON to bypass parsing.

**Observed on the exact revision:** after a reset and login, each of these request bodies to `POST /dossiers` with valid bearer authentication, a fresh `Idempotency-Key`, and `Content-Type: application/json` returns **202** with a newly created building dossier:

```text
{"domain":"witness.test","unknown":NaN}
{"domain":"witness.test","unknown":Infinity}
{"domain":"witness.test","unknown":-Infinity}
```

**Required:** reject each body with `400` and `error.code` equal to `malformed_request`, before creating a dossier, claiming a key, or starting research.

**Reproduce without product imports or product test sources:**

```sh
fclone c772508d90a96c5214a26528c59a93ba38336cd3 /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-c772508d90a9
SECOND_READER_ONLY=strict-json /Users/[REDACTED]/dev/band-factory/work/second-reader/probes/stage-1/run.sh /Users/[REDACTED]/dev/band-factory/work/second-reader/repro-c772508d90a9/stage-1
```

The runner builds and starts that stage-folder and the documented mock itself. Result: **3 failed, 0 passed; exit 1**. Probe names: `strict-json-NaN`, `strict-json-Infinity`, `strict-json--Infinity`.

## Passing evidence and limits

The preceding complete independent suite passed **150/150 probes, 5817 assertions** on this revision, including support grammar, every legal suffix/statement phrase/negation and headcount boundary, 50 concurrent create/signup requests, idempotency and key validation precedence, failed refreshes, reset races, cross-process import with existing tokens and original responses, interrupted-build snapshots, live-host 31-second call handling, and cost accounting after lost connections. All current probes have run: the 150-case suite plus the three subsequently added strict JSON probes.

The prescribed isolated sample harness claims **Stage 1**, with **122/122** Stage 1 checks passed. That sample result does not close the independent finding. Narrow post-probe source review confirms WebRouter provider routing and scrypt password storage. Product code and product tests were not edited; private probes remain outside the result repository until the factory closes every stage.

See `ledger/stage-1-audit.md` and the per-unit ledger for exact commands, evidence references, rulings, and the audit-check result.
