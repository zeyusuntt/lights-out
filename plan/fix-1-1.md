FIX 1 1 — stage 1, round 1, on 52f4f877c4cf853d78515f431a8b58a950ee1da0

Verdicts: verifier PASS (verdicts/stage-1/verifier-52f4f877c4cf.md), second-reader BLOCK (verdicts/stage-1/second-reader-52f4f877c4cf.md). Fix both blocking findings in one new revision, then send CANDIDATE 1 <hash>.

## F1 — Invalid domain values containing an encoded slash bypass validation (second-reader)

Units S1-100, S1-153, S1-161, S1-162; ruling R1-5 (path domains are validated before lookup).
With a valid bearer token and, for refresh, a valid idempotency key, each of these returns 404 not_found. Required: 422 validation_failed, because the decoded path value is a URL or contains a path, not a valid normalised host name.

    GET /dossiers/https%3A%2F%2Fvalid.test
    POST /dossiers/https%3A%2F%2Fvalid.test/refresh
    GET /dossiers/valid.test%2Fpath
    POST /dossiers/valid.test%2Fpath/refresh

Root cause to look for: the router decodes %2F into path segments, or does not route encoded slashes to the dossier handler. The domain segment must be validated as a whole after decoding.
Reproduce: SECOND_READER_ONLY=encoded-path-domain-validation /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1 (exits nonzero on this revision)

## F2 — A fixture can create an account whose returned ID exceeds 64 characters (second-reader)

Units S1-090 (§3.5 "IDs are opaque strings of at most 64 characters"), S1-153, S1-161, S1-162.
A reset with a seeded user whose id is 64 characters succeeds. With a 65-character id, reset returns 204 and login returns a 65-character user_id. Required: such a fixture is rejected with 422 validation_failed and the prior state is left intact.
Reproduce: SECOND_READER_ONLY=fixture-id-length-boundary /Users/sunzeyu/dev/band-factory/work/second-reader/probes/stage-1/run.sh <clean-clone>/stage-1 (exits nonzero on this revision)

## Non-blocking notes from the verifier (address them if cheap, without regressing anything)

- A 1-unit extract re-fetches a research excerpt that the research run had already served. The dispatch says to reuse text a provider has already served within one build, so avoid this where the served research text is sufficient.
- scrypt hashing runs on the event loop. Move it off the loop so that 50 concurrent requests stay within 5 s.
