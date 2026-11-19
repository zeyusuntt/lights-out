"""The watchdog must leave a working seat alone, and must not restart in a loop."""
import importlib.machinery, importlib.util, pathlib

path = pathlib.Path(__file__).resolve().parents[1] / "bin" / "watchdog"
loader = importlib.machinery.SourceFileLoader("watchdog_mod", str(path))
spec = importlib.util.spec_from_loader("watchdog_mod", loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
decide = mod.decide
M = 60


def state(**kw):
    base = dict(queued=True, has_process=True, last_event_age=5 * M, since_restart=None, restarts=0, gone_for=0)
    base.update(kw)
    return base


def test_busy_seat_with_a_queued_message_is_left_alone():
    # A seat in a long turn has a queued message and stale Band bookkeeping, but it keeps producing events.
    assert decide(**state(last_event_age=30)) is None


def test_long_foreground_command_is_not_a_stall():
    assert decide(**state(last_event_age=40 * M)) is None


def test_stalled_seat_is_restarted():
    assert decide(**state(last_event_age=46 * M)) == "stalled"


def test_no_restart_inside_the_cooldown():
    assert decide(**state(last_event_age=46 * M, since_restart=10 * M)) is None


def test_restart_allowed_after_the_cooldown():
    assert decide(**state(last_event_age=50 * M, since_restart=46 * M)) == "stalled"


def test_cap_stops_a_restart_loop():
    assert decide(**state(last_event_age=99 * M, restarts=6)) is None


def test_nothing_queued_means_nothing_to_do():
    assert decide(**state(queued=False, last_event_age=99 * M)) is None


def test_missing_runtime_waits_out_the_spawn():
    assert decide(**state(has_process=False, gone_for=30)) is None
    assert decide(**state(has_process=False, gone_for=200)) == "no-process"


def test_grace_counts_only_while_a_message_waits():
    # A seat with no runtime and nothing queued is just idle; the grace starts when work arrives.
    clock = {"t": 0}
    tracker = mod.GoneTracker(lambda: clock["t"])
    assert tracker.gone_for(queued=False, has_process=False) == 0
    clock["t"] = 20 * M
    assert tracker.gone_for(queued=True, has_process=False) == 0
    clock["t"] = 20 * M + 200
    assert tracker.gone_for(queued=True, has_process=False) == 200
    assert tracker.gone_for(queued=True, has_process=True) == 0


def test_it_stops_once_the_final_report_is_seen(tmp_path):
    import shutil, subprocess
    (tmp_path / "factory/bin").mkdir(parents=True)
    shutil.copy(path, tmp_path / "factory/bin/watchdog")
    (tmp_path / "work/state").mkdir(parents=True)
    (tmp_path / "work/run.env").write_text("ROOM=00000000-room\n")
    (tmp_path / "work/state/final-seen").write_text("FINAL REPORT\n")
    out = subprocess.run(["python3", str(tmp_path / "factory/bin/watchdog"), "--interval", "1"], capture_output=True, text=True, timeout=20)
    assert out.returncode == 0, out.stderr
    assert "final report seen, stopping" in (tmp_path / "work/state/watchdog.log").read_text()
