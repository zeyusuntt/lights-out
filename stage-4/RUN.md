# Dossier service, stage 3

An HTTP service and browser screens for researching companies by web domain. Each dossier keeps
six fields plus `executives` (CFO, COO, CTO): every value the sources support, as ranked
candidates, the selected value, and its citations. It keeps every build, the page versions each
ready build gathered, each field's history and a change feed, so it answers `?as_of=`,
`/values?true_at=`, `/history` and `/changes`. Every provider call goes through WebRouter's
`nimble` provider.

## State on disk

All state is written to `/srv/data/state.json` inside the container: after every write request,
and when a build completes. It is written crash-atomically (temporary file, fsync, rename), and
loaded at start, so a stopped and started container answers as before. A build running at the
stop is rolled back to the dossier as it was before that build. Set `DOSSIER_STATE_PATH` to
keep the file elsewhere, for example when running the app outside the image.

The screens are served from the same port: `/`, `/dossiers/{domain}` (with `Accept: text/html`),
`/dossiers/{domain}/evidence`, `/contested`, `/signup` and `/login`. Their script and stylesheet
come from the image (`/assets/`). DESIGN.md records the design.

## Build and start

```sh
docker build -t dossier-stage-3 .
docker run --rm -p 8080:8080 -e PORT=8080 \
  -e NIMBLE_API_KEY=<key> -e NIMBLE_BASE_URL=<nimble base url> \
  dossier-stage-3
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
  dossier-stage-3
```

## Tests

Unit tests need only the Python dependencies; the API tests run against a started
service and the mock web:

```sh
python -m pytest tests/unit
DOSSIER_URL=http://localhost:8000 MOCK_URL=http://localhost:8080 MOCK_ADMIN_TOKEN=local-admin \
  python -m pytest tests/api
```

`tests/ui` holds the browser tests (Playwright with Chromium, same variables).
`tests/api/test_upgrade.py` runs when `STAGE1_URL` and `STAGE2_URL` point at the accepted
stage-1 and stage-2 services on the same mock web. `tests/api/test_restart.py` runs when
`RESTART_CONTAINER` names the service's container, which it kills and starts again. `tests/api/test_edge_corpus.py` runs too when a second mock web serves `tests/corpus`
(`EDGE_MOCK_URL`) to a second service (`EDGE_DOSSIER_URL`). That corpus has research excerpts
shaped like header lines and sentences longer than 500 characters.

## How a build spends

A build plans its calls once:

1. together: a `lite` search for exactly the normalised domain, a `lite` search for the
   company's name, one `lite` search per field with the name and that field's statement phrases,
   and one with the name and the executive titles' phrases (9 units), and one Nimble research run asking for the six fields (25 units);
2. a rendered Nimble extract (`render: True`, 3 units each) of every page a research claim
   cites, then of every search result that names the company, company-site pages first. A result
   is skipped only when the search already served the page's whole prose and it contains no
   statement phrase for any field.

Candidates come only from the rendered text, so from what a browser shows. Each page gives one
candidate per field and value. Page kind and publication time come from its `Kind` and
`Published` header lines.

A sentence of at most 500 characters is judged and cited whole. A longer one is cited by the
shortest span of at most 500 characters that covers a value with the nearest company name and
statement phrase on either side of it, cuts no word, amount or run of capitalised words, and
supports that value on its own. There is no search cap.

Units are reserved before every call and a build never exceeds 80. Refused calls (429,
5xx) cost nothing and are retried after at least 1.1 s, up to five attempts. Time spent waiting
after a 429 does not count toward the build's time. Calls that time out are charged.

A stage-1 or stage-2 export imports as one ready build at `researched_at` holding all its
spending, with one `initial` history entry per valued field (R3-3). An export from a stage-1 service is accepted by import: each exported citation excerpt is tested
against every field, and gives candidates with `kind` and `published_at` null.
