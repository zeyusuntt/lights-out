"""Run state shared by the factory's tools. Stdlib only."""
import os, pathlib, subprocess, sys

HOME = pathlib.Path(__file__).resolve().parents[2]
WORK = pathlib.Path(os.environ.get("FACTORY_WORK", HOME / "work"))
SEAT = os.environ.get("FACTORY_SEAT", "")
BAND = "/Applications/Band.app/Contents/MacOS/jam"
if not os.path.exists(BAND):
    BAND = "band"


def service_limits() -> tuple[str, str]:
    """The CPU and memory a stage's service gets when a seat runs it: the job's stated limits, from run.env."""
    env = run_env()
    return env.get("SERVICE_CPUS", "2"), env.get("SERVICE_MEMORY", "2g")


def run_env() -> dict:
    env = {}
    path = WORK / "run.env"
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    return env


def result() -> pathlib.Path:
    return WORK / "result"


def git(*args, cwd=None, check=True):
    return subprocess.run(["git", *args], cwd=cwd or result(), capture_output=True, text=True, check=check)


def die(message: str, code: int = 1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def current_stage() -> str:
    path = WORK / "state" / "current-stage"
    return path.read_text().strip() if path.exists() else ""


def seal_path(stage: str) -> pathlib.Path:
    return WORK / "verifier" / "sealed" / f"stage-{stage}.seal"
