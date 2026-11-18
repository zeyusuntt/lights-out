# Dossier service, stage 1

An HTTP service that researches companies by web domain and keeps a dossier of six
cited fields. Every provider call goes through WebRouter's `nimble` provider.

## Build and start

```sh
docker build -t dossier-stage-1 .
docker run --rm -p 8080:8080 -e PORT=8080 \
  -e NIMBLE_API_KEY=<key> -e NIMBLE_BASE_URL=<nimble base url> \
  dossier-stage-1
```

`PORT` defaults to 8080. Leave `NIMBLE_BASE_URL` unset to use the live Nimble endpoint;
never pass it empty. `TAVILY_API_KEY` and `TAVILY_BASE_URL` are accepted and not needed:
research runs on Nimble alone. No other setup is required; `GET /health` answers 200 within
a few seconds of start.

## Against the local mock web

```sh
docker network create dossier
docker run --rm -d --name web --network dossier -e MOCK_ADMIN_TOKEN=local-admin \
  -v "<kit>/challenges/dossier/web/corpus/sample:/data/corpus:ro" dossier-web
docker run --rm --network dossier -p 8000:8000 -e PORT=8000 \
  -e NIMBLE_API_KEY=local -e NIMBLE_BASE_URL=http://web:8080/nimble \
  dossier-stage-1
```

## Tests

Unit tests need only the Python dependencies; the API tests run against a started
service and the mock web:

```sh
python -m pytest tests/unit
DOSSIER_URL=http://localhost:8000 MOCK_URL=http://localhost:8080 MOCK_ADMIN_TOKEN=local-admin \
  python -m pytest tests/api
```

`tests/api/test_edge_corpus.py` runs too when a second mock web serves `tests/corpus`
(`EDGE_MOCK_URL`) to a second service (`EDGE_DOSSIER_URL`). That corpus has research excerpts
shaped like header lines and sentences longer than 500 characters.

## How a build spends

A build makes, at most, in this order:

1. together: one `lite` search for exactly the normalised domain, one `lite` search for the
   company's name, and one Nimble research run asking for the six fields (27 units);
2. extracts (1 unit each) of a research-cited page only when the excerpt has the shape of a
   header line and the field is still unsupported, since only the page's own text places it in
   header or prose, and, while some field still has no supported value, of truncated
   search results that name the company;
3. only for fields still unsupported: one `lite` search per field with the company's name
   and that field's statement phrases, then extracts of new truncated results naming it.

A supporting sentence longer than 500 characters is cited by the longest run of its whole
words, at most 500 characters, that supports the value on its own.

Units are reserved before every call and a build never exceeds 80. Refused calls (429,
5xx) cost nothing and are retried after a pause; calls that time out are charged.
