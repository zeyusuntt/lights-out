#!/usr/bin/env bash
# Stage-4 acceptance suite runner (includes the stage-1..3 tests still in force).
#   run.sh <stage-folder> [extra pytest args, e.g. -k idempotency]
# Builds the stage folder fresh (no cache), starts it twice under the stage's resource limits
# (2 vCPU, 3 GiB) on an internal network beside the kit's mock web (sample corpus + this suite's
# corpus), runs the whole suite from a runner container on that network, prints counts, exits
# non-zero on any failure.
set -u
[ $# -ge 1 ] || { echo "usage: run.sh <stage-folder> [pytest args]"; exit 2; }
STAGE=$(cd "$1" && pwd) || exit 2
shift
HERE=$(cd "$(dirname "$0")" && pwd)
KIT=${KIT:-/Users/sunzeyu/dev/band-factory/vendor/sf-buildathon-2026}
ID=verifier-s4-$$
IMG=$ID-svc
TMPBASE=${VERIFIER_TMP:-/Users/sunzeyu/dev/band-factory/work/tmp}
mkdir -p "$TMPBASE"
WORK=$(mktemp -d "$TMPBASE/verifier-s4.XXXXXX")  # under a Docker-shared path
mkdir -p "$WORK/corpus" "$WORK/out"
cleanup() {
  docker rm -f "$ID-web" "$ID-svc" "$ID-svc2" "$ID-svc1" "$ID-svcp" "$ID-svc3" >/dev/null 2>&1
  docker rmi "$ID-prev" "$ID-prev2" "$ID-prev3" >/dev/null 2>&1
  docker network rm "$ID-net" >/dev/null 2>&1
  [ -n "${KEEP_IMAGE:-}" ] || docker rmi "$IMG" >/dev/null 2>&1
}
trap cleanup EXIT

# corpus: the kit's sample companies and traits (never key.json) plus the suite's own companies
cp "$KIT"/challenges/dossier/web/corpus/sample/*.test.json "$WORK/corpus/"
cp "$KIT"/challenges/dossier/web/corpus/sample/traits.json "$WORK/corpus/" 2>/dev/null
cp "$HERE"/corpus_custom/*.json "$WORK/corpus/"

echo "== build $STAGE (no cache)"
if [ -n "${NO_REBUILD:-}" ] && docker image inspect "$NO_REBUILD" >/dev/null 2>&1; then
  IMG=$NO_REBUILD; KEEP_IMAGE=1
else
  docker build --no-cache -q -t "$IMG" "$STAGE" >"$WORK/build.log" 2>&1 || { cat "$WORK/build.log"; echo "BUILD FAILED"; exit 1; }
fi
# the previous stage, for the upgrade path: the stage-1 folder beside the given stage folder
PREV=$(cd "$STAGE/../stage-1" 2>/dev/null && pwd)
[ -n "$PREV" ] || { echo "no stage-1 folder beside $STAGE"; exit 1; }
docker build -q -t "$ID-prev" "$PREV" >"$WORK/build-prev.log" 2>&1 || { cat "$WORK/build-prev.log"; echo "PREV BUILD FAILED"; exit 1; }
PREV2=$(cd "$STAGE/../stage-2" 2>/dev/null && pwd)
[ -n "$PREV2" ] || { echo "no stage-2 folder beside $STAGE"; exit 1; }
docker build -q -t "$ID-prev2" "$PREV2" >"$WORK/build-prev2.log" 2>&1 || { cat "$WORK/build-prev2.log"; echo "PREV2 BUILD FAILED"; exit 1; }
PREV3=$(cd "$STAGE/../stage-3" 2>/dev/null && pwd)
[ -n "$PREV3" ] || { echo "no stage-3 folder beside $STAGE"; exit 1; }
docker build -q -t "$ID-prev3" "$PREV3" >"$WORK/build-prev3.log" 2>&1 || { cat "$WORK/build-prev3.log"; echo "PREV3 BUILD FAILED"; exit 1; }
docker build -q -t verifier-dossier-web "$KIT/challenges/dossier/web" >/dev/null || { echo "mock build failed"; exit 1; }

docker network create --internal "$ID-net" >/dev/null
docker run -d --name "$ID-web" --network "$ID-net" --network-alias web \
  -e MOCK_ADMIN_TOKEN=verifier-admin -v "$WORK/corpus:/data/corpus:ro" verifier-dossier-web >/dev/null
for i in $(seq 1 60); do
  docker run --rm --network "$ID-net" df-harness-runner python -c \
    "import httpx;httpx.get('http://web:8080/_mock/health',timeout=2).raise_for_status()" >/dev/null 2>&1 && break
  sleep 1
done

docker run -d --name "$ID-svc" --network "$ID-net" --network-alias svc --cpus 2 --memory 3g \
  -e PORT=8000 -e NIMBLE_API_KEY=local -e NIMBLE_BASE_URL=http://web:8080/nimble \
  -e TAVILY_API_KEY=local -e TAVILY_BASE_URL=http://web:8080/tavily \
  -e KERNEL_API_KEY=local -e KERNEL_BASE_URL=http://web:8080/kernel \
  -e BROWSERBASE_API_KEY=local -e BROWSERBASE_BASE_URL=http://web:8080/browserbase "$IMG" >/dev/null
docker run -d --name "$ID-svc1" --network "$ID-net" --network-alias svc1 --cpus 2 --memory 3g \
  -e PORT=8002 -e NIMBLE_API_KEY=local -e NIMBLE_BASE_URL=http://web:8080/nimble \
  -e TAVILY_API_KEY=local -e TAVILY_BASE_URL=http://web:8080/tavily "$ID-prev" >/dev/null
docker run -d --name "$ID-svcp" --network "$ID-net" --network-alias svcp --cpus 2 --memory 3g \
  -e PORT=8003 -e NIMBLE_API_KEY=local -e NIMBLE_BASE_URL=http://web:8080/nimble "$ID-prev2" >/dev/null
docker run -d --name "$ID-svc3" --network "$ID-net" --network-alias svc3 --cpus 2 --memory 3g \
  -e PORT=8004 -e NIMBLE_API_KEY=local -e NIMBLE_BASE_URL=http://web:8080/nimble "$ID-prev3" >/dev/null
docker run -d --name "$ID-svc2" --network "$ID-net" --network-alias svc2 --cpus 2 --memory 3g \
  -e PORT=8001 -e NIMBLE_API_KEY=local -e NIMBLE_BASE_URL=http://web:8080/nimble "$IMG" >/dev/null
started() { docker inspect -f '{{.State.StartedAt}}' "$1" | python3 -c "import sys,datetime;print(datetime.datetime.fromisoformat(sys.stdin.read().strip()[:26]+'+00:00').timestamp())"; }
S1=$(started "$ID-svc"); S2=$(started "$ID-svc2")

echo "== run suite"
docker run --rm --network "$ID-net" -e PYTHONDONTWRITEBYTECODE=1 \
  -e SVC=http://svc:8000 -e SVC2=http://svc2:8001 -e SVC1=http://svc1:8002 -e SVCP=http://svcp:8003 -e SVC3=http://svc3:8004 -e MOCK=http://web:8080 -e MOCK_ADMIN_TOKEN=verifier-admin \
  -e CORPUS=/corpus -e OUT=/out -e SVC_STARTED="$S1" -e SVC2_STARTED="$S2" \
  -v "$HERE:/suite:ro" -v "$WORK/corpus:/corpus:ro" -v "$WORK/out:/out" -w /suite \
  df-harness-runner python -m pytest tests -p no:cacheprovider -q -rfE --tb=short \
  --junitxml=/out/junit.xml --ignore=tests/test_98_restart_b.py --ignore=tests/test_99_restart_c.py "$@" 2>&1 | tee "$WORK/out/pytest.txt"
RC=${PIPESTATUS[0]}
if [ -f "$WORK/out/restart_snapshot.json" ]; then
  echo "== abrupt stop (docker kill) and start of the service"
  docker kill "$ID-svc" >/dev/null; docker start "$ID-svc" >/dev/null
  for i in $(seq 1 60); do docker run --rm --network "$ID-net" df-harness-runner python -c "import httpx;httpx.get('http://svc:8000/health',timeout=2).raise_for_status()" >/dev/null 2>&1 && break; sleep 1; done
echo "== run suite, phase B (after restart)"
docker run --rm --network "$ID-net" -e PYTHONDONTWRITEBYTECODE=1 \
  -e SVC=http://svc:8000 -e SVC2=http://svc2:8001 -e SVC1=http://svc1:8002 -e SVCP=http://svcp:8003 -e SVC3=http://svc3:8004 -e MOCK=http://web:8080 -e MOCK_ADMIN_TOKEN=verifier-admin \
  -e CORPUS=/corpus -e OUT=/out -e SVC_STARTED="$S1" -e SVC2_STARTED="$S2" \
  -v "$HERE:/suite:ro" -v "$WORK/corpus:/corpus:ro" -v "$WORK/out:/out" -w /suite \
  df-harness-runner python -m pytest -p no:cacheprovider -q -rfE --tb=short \
  --junitxml=/out/junit-b.xml tests/test_98_restart_b.py 2>&1 | tee "$WORK/out/pytest-b.txt"
  RCB=${PIPESTATUS[0]}; [ $RCB -ne 0 ] && RC=$RCB
  if [ -f "$WORK/out/midbuild_snapshot.json" ]; then
    echo "== abrupt stop (docker kill) while builds run, then start"
    docker kill "$ID-svc" >/dev/null
    # after the restart each provider call must answer within one second (stage 4 Restarts): lift the delay
    docker run --rm --network "$ID-net" df-harness-runner python -c "import httpx;httpx.post('http://web:8080/_mock/faults',json={'provider':'nimble','methods':['search','extract','research'],'mode':'none'},headers={'X-Mock-Admin':'verifier-admin'},timeout=5)" >/dev/null
    docker start "$ID-svc" >/dev/null
    HEALTH_AT=$(docker run --rm --network "$ID-net" df-harness-runner python -c "
import time, httpx
while True:
    try:
        if httpx.get('http://svc:8000/health', timeout=1).status_code == 200:
            print(time.time()); break
    except Exception:
        pass
    time.sleep(0.1)")
echo "== run suite, phase C (after a kill mid-build)"
docker run --rm --network "$ID-net" -e PYTHONDONTWRITEBYTECODE=1 -e HEALTH_AT="$HEALTH_AT" \
  -e SVC=http://svc:8000 -e SVC2=http://svc2:8001 -e SVC1=http://svc1:8002 -e SVCP=http://svcp:8003 -e SVC3=http://svc3:8004 -e MOCK=http://web:8080 -e MOCK_ADMIN_TOKEN=verifier-admin \
  -e CORPUS=/corpus -e OUT=/out -e SVC_STARTED="$S1" -e SVC2_STARTED="$S2" \
  -v "$HERE:/suite:ro" -v "$WORK/corpus:/corpus:ro" -v "$WORK/out:/out" -w /suite \
  df-harness-runner python -m pytest -p no:cacheprovider -q -rfE --tb=short \
  --junitxml=/out/junit-c.xml tests/test_99_restart_c.py 2>&1 | tee "$WORK/out/pytest-c.txt"
    RCC=${PIPESTATUS[0]}; [ $RCC -ne 0 ] && RC=$RCC
  fi
fi

docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' "$ID-svc" "$ID-svc2" 2>/dev/null
docker logs "$ID-svc" >"$WORK/out/svc.log" 2>&1
python3 - "$WORK/out/junit.xml" "$WORK/out/junit-b.xml" "$WORK/out/junit-c.xml" <<'EOF'
import os, sys, xml.etree.ElementTree as ET
try:
    t = f = e = sk = 0
    for path in sys.argv[1:]:
        if not os.path.exists(path):
            continue
        r = ET.parse(path).getroot(); s = r if r.tag == "testsuite" else r[0]
        a, b, c, d = (int(s.get(k, 0)) for k in ("tests", "failures", "errors", "skipped"))
        t += a; f += b; e += c; sk += d
    print(f"COUNTS total={t} passed={t-f-e-sk} failed={f} errors={e} skipped={sk}")
except Exception as x:
    print("COUNTS unavailable", x)
EOF
[ -f "$WORK/out/units_summary.json" ] && echo "UNITS $(cat "$WORK/out/units_summary.json" | tr -d '\n ')"
echo "artifacts: $WORK/out"
exit $RC
