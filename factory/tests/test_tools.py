"""Behaviour of the factory's tools, on a throwaway workspace."""
import json, os, pathlib, subprocess, sys, time
import pytest

BIN = pathlib.Path(__file__).resolve().parents[1] / "bin"
H = "a" * 40


@pytest.fixture
def work(tmp_path):
    w = tmp_path / "work"
    (w / "result").mkdir(parents=True)
    (w / "state").mkdir()
    (w / "verifier" / "sealed" / "stage-1").mkdir(parents=True)
    (w / "verifier" / "sealed" / "stage-1" / "test_x.py").write_text("x\n")
    (w / "verifier" / "sealed" / "stage-1" / "run.sh").write_text("#!/bin/sh\n")
    r = w / "result"
    git(r, "init", "-q", "-b", "main")
    git(r, "config", "user.name", "operator")
    git(r, "config", "user.email", "o@example.test")
    return w


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def tool(work, name, *args, seat="operator", timeout=30):
    env = {**os.environ, "FACTORY_WORK": str(work), "FACTORY_SEAT": seat}
    env.pop("FACTORY_SLOT_HELD", None)
    return subprocess.run([str(BIN / name), *map(str, args)], capture_output=True, text=True, env=env, timeout=timeout)


def stage_ready(work):
    """A stage folder sealed before any product commit, with passing verdict files and ledger."""
    r = work / "result"
    assert tool(work, "seal", 1, work / "verifier/sealed/stage-1").returncode == 0
    (r / "stage-1").mkdir()
    (r / "stage-1/Dockerfile").write_text("FROM scratch\n")
    (r / "stage-1/RUN.md").write_text("run\n")
    git(r, "add", "."); git(r, "commit", "-qm", "stage 1")
    rev = git(r, "rev-parse", "HEAD")
    (r / "ledger").mkdir()
    (r / "ledger/stage-1.units.tsv").write_text("S1-001\tA rule.\n")
    (r / "ledger/stage-1.jsonl").write_text(json.dumps({"unit": "S1-001", "class": "normative", "requires": "r", "observe": "o", "evidence": [{"kind": "probe", "ref": "p", "revision": rev, "result": "pass"}]}) + "\n")
    (r / "verdicts/stage-1").mkdir(parents=True)
    for seat in ("verifier", "second-reader", "product-user"):
        (r / f"verdicts/stage-1/{seat}-{rev[:12]}.md").write_text(f"VERDICT: PASS\nREVISION: {rev}\n")
    report = work / "report.json"
    report.write_text(json.dumps({"state": "completed", "mode": "isolated", "revision": rev, "claimed_stage": "1", "overshoot": None}))
    subprocess.run([str(BIN / "ledger-check"), "1", "--phase", "audit", "--revision", rev], env={**os.environ, "FACTORY_WORK": str(work)}, capture_output=True)
    git(r, "add", "."); git(r, "commit", "-qm", "evidence")
    return rev, report


def test_accept_check_passes_when_everything_holds(work):
    rev, report = stage_ready(work)
    out = tool(work, "accept-check", 1, rev, "--ui", "--report", report)
    assert out.returncode == 0, out.stdout + out.stderr


def test_accept_check_makes_the_interface_choice_explicit(work):
    rev, report = stage_ready(work)
    assert tool(work, "accept-check", 1, rev, "--report", report).returncode != 0


def test_accept_check_needs_product_user_when_there_is_an_interface(work):
    rev, report = stage_ready(work)
    r = work / "result"
    git(r, "rm", "-q", f"verdicts/stage-1/product-user-{rev[:12]}.md"); git(r, "commit", "-qm", "drop")
    assert tool(work, "accept-check", 1, rev, "--ui", "--report", report).returncode != 0
    assert tool(work, "accept-check", 1, rev, "--no-ui", "--report", report).returncode == 0


@pytest.mark.parametrize("change", [{"claimed_stage": None}, {"mode": "host"}, {"state": "error"}, {"revision": "b" * 40}, {"overshoot": "2"}])
def test_accept_check_reads_the_check_report(work, change):
    rev, report = stage_ready(work)
    body = json.loads(report.read_text()); body.update(change); report.write_text(json.dumps(body))
    assert tool(work, "accept-check", 1, rev, "--ui", "--report", report).returncode != 0


def test_accept_check_refuses_uncommitted_evidence(work):
    rev, report = stage_ready(work)
    path = work / f"result/verdicts/stage-1/verifier-{rev[:12]}.md"
    path.write_text(path.read_text() + "note\n")
    assert tool(work, "accept-check", 1, rev, "--ui", "--report", report).returncode != 0


def test_accept_check_refuses_a_changed_suite(work):
    rev, report = stage_ready(work)
    (work / "verifier/sealed/stage-1/test_x.py").write_text("changed\n")
    assert tool(work, "accept-check", 1, rev, "--ui", "--report", report).returncode != 0


def test_accept_check_refuses_a_seal_made_after_product_commits(tmp_path):
    w = tmp_path / "work"; (w / "result").mkdir(parents=True); (w / "verifier/sealed/stage-1").mkdir(parents=True)
    (w / "verifier/sealed/stage-1/t.py").write_text("x\n")
    (w / "verifier/sealed/stage-1/run.sh").write_text("#!/bin/sh\n")
    r = w / "result"
    git(r, "init", "-q", "-b", "main"); git(r, "config", "user.name", "o"); git(r, "config", "user.email", "o@e.test")
    (r / "stage-1").mkdir(); (r / "stage-1/a").write_text("a\n"); git(r, "add", "."); git(r, "commit", "-qm", "code")
    tool(w, "seal", 1, w / "verifier/sealed/stage-1")
    out = tool(w, "accept-check", 1, git(r, "rev-parse", "HEAD"), "--no-ui", "--report", w / "none.json")
    assert out.returncode != 0 and "sealed after" in out.stdout


def test_with_slot_nested_call_does_not_wait(work):
    # A seat that wraps a tool which itself takes a slot must not deadlock.
    out = tool(work, "with-slot", BIN / "with-slot", "true", timeout=20)
    assert out.returncode == 0


def test_with_slot_two_holders_and_a_nested_call(work):
    env = {**os.environ, "FACTORY_WORK": str(work), "FACTORY_SEAT": "a"}
    env.pop("FACTORY_SLOT_HELD", None)
    holders = [subprocess.Popen([str(BIN / "with-slot"), str(BIN / "with-slot"), "sleep", "3"], env=env) for _ in range(2)]
    start = time.time()
    assert [p.wait(timeout=30) for p in holders] == [0, 0]
    assert time.time() - start < 15


def test_with_slot_passes_on_the_exit_code(work):
    assert tool(work, "with-slot", "sh", "-c", "exit 7").returncode == 7


def test_with_slot_recovers_from_a_killed_holder(work):
    env = {**os.environ, "FACTORY_WORK": str(work), "FACTORY_SEAT": "a"}
    env.pop("FACTORY_SLOT_HELD", None)
    procs = [subprocess.Popen([str(BIN / "with-slot"), "sleep", "60"], env=env) for _ in range(2)]
    time.sleep(1.5)
    for p in procs:
        p.kill(); p.wait()
    assert tool(work, "with-slot", "true", timeout=15).returncode == 0


def test_fcommit_prints_its_own_commit(work):
    r = work / "result"; (r / "a.txt").write_text("a\n")
    out = tool(work, "fcommit", "-m", "add a", "a.txt")
    assert out.returncode == 0 and out.stdout.strip() == git(r, "rev-parse", "HEAD")


def test_seal_verify_detects_a_change(work):
    d = work / "verifier/sealed/stage-1"
    assert tool(work, "seal", 1, d).returncode == 0
    assert tool(work, "seal", "--verify", 1, d).returncode == 0
    (d / "test_x.py").write_text("changed\n")
    assert tool(work, "seal", "--verify", 1, d).returncode != 0


def load_script(name):
    import importlib.machinery, importlib.util
    loader = importlib.machinery.SourceFileLoader(name.replace("-", "_"), str(BIN / name))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def test_timekeeper_rings_only_after_long_silence_and_backs_off():
    due = load_script("timekeeper").due
    T = 35 * 60
    assert not due(T - 1, T, 0, 0)
    assert due(T + 1, T, 0, 10 ** 9)
    assert not due(3 * T, T, 1, T)          # second tick waits twice as long
    assert due(3 * T, T, 1, 2 * T)
    assert not due(10 ** 6, T, 6, 10 ** 9)  # a capped clock stays quiet


def test_fstop_all_touches_only_what_this_run_recorded(work, tmp_path):
    fake = tmp_path / "bin"; fake.mkdir()
    log = tmp_path / "docker.log"
    (fake / "docker").write_text(f'#!/bin/sh\necho "$@" >> {log}\nexit 0\n')
    (fake / "docker").chmod(0o755)
    (work / "verifier/serve").mkdir(parents=True)
    (work / "verifier/serve/started").write_text("verifier-mine-1\n")
    env = {**os.environ, "FACTORY_WORK": str(work), "FACTORY_SEAT": "verifier", "PATH": f"{fake}:{os.environ['PATH']}"}
    out = subprocess.run([str(BIN / "fstop"), "--all"], capture_output=True, text=True, env=env)
    assert out.returncode == 0 and "removed verifier-mine-1" in out.stdout
    calls = log.read_text()
    assert "verifier-mine-1" in calls and " ps" not in calls


def test_ledger_check_refuses_duplicate_units(work):
    r = work / "result"; (r / "ledger").mkdir()
    (r / "ledger/stage-1.units.tsv").write_text("S1-001\tA rule.\n")
    rows = [{"unit": "S1-001", "class": "normative", "requires": "r", "observe": "o"},
            {"unit": "S1-001", "class": "informative", "requires": "", "observe": ""}]
    (r / "ledger/stage-1.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows))
    out = tool(work, "ledger-check", 1, "--phase", "reading")
    assert out.returncode != 0 and "more than once" in out.stdout


def test_seal_refuses_a_missing_or_empty_suite(work):
    assert tool(work, "seal", 1, work / "verifier/nowhere").returncode != 0
    (work / "verifier/empty").mkdir()
    assert tool(work, "seal", 1, work / "verifier/empty").returncode != 0


def test_accept_check_refuses_a_dirty_stage_folder(work):
    rev, report = stage_ready(work)
    (work / "result/stage-1/scratch.txt").write_text("uncommitted\n")
    out = tool(work, "accept-check", 1, rev, "--ui", "--report", report)
    assert out.returncode != 0 and "uncommitted" in out.stdout


def test_stage_copy_takes_the_accepted_commit_not_the_working_tree(work):
    rev, report = stage_ready(work)
    (work / "result/stage-1/RUN.md").write_text("edited after acceptance\n")
    out = tool(work, "stage-copy", 1, 2, rev)
    assert out.returncode == 0, out.stderr
    assert (work / "result/stage-2/RUN.md").read_text() == "run\n"
    assert not (work / "result/stage-2/.git").exists()


def test_run_stats_markdown_from_an_archive(tmp_path):
    """The FACTORY.md tables come from the archive: room file, git history and score, not typed by hand."""
    run = tmp_path / "runs" / "x-01"
    r = run / "result"
    r.mkdir(parents=True)
    git(r, "init", "-q", "-b", "main")
    for seat in ("builder", "verifier", "builder"):
        git(r, "-c", f"user.name={seat}", "-c", "user.email=s@example.test", "commit", "-q", "--allow-empty", "-m", seat)
    (r / "verdicts/stage-1").mkdir(parents=True)
    (r / "verdicts/stage-1" / f"verifier-{'b' * 12}.md").write_text("VERDICT: BLOCK\n")
    (run / "run.env").write_text("RUN_ID=x-01\nROOM=00000000-room\nTRACK=toy\n")
    (run / "score").mkdir()
    (run / "score/summary-1.json").write_text(json.dumps({"1": {"claimed": "1", "overshoot": None, "suites": {"1": [8, 8]}}}))
    at = lambda m: f"2026-11-07T10:{m:02d}:00Z"
    say = lambda i, who, kind, text, m: {"id": f"m{i}", "senderName": who, "senderType": "User" if who == "human" else "Agent",
                                         "messageType": kind, "content": text, "insertedAt": at(m)}
    msgs = [say(0, "human", "text", "build it", 0), say(1, "foreman", "text", "STAGE-OPEN 1", 1),
            say(2, "second-reader", "text", "LEDGER READY 1", 3), say(3, "verifier", "text", "SEALED 1 sha256:x", 5),
            say(4, "builder", "tool_call", "{}", 6), say(5, "builder", "text", "CANDIDATE 1 " + "b" * 40, 10),
            say(6, "verifier", "text", "@[[id]] VERDICT verifier 1 " + "b" * 40 + " BLOCK", 15),
            say(7, "builder", "text", "CANDIDATE 1 " + "c" * 40, 20),
            say(8, "verifier", "text", "VERDICT verifier 1 " + "c" * 40 + " PASS", 25),
            say(9, "foreman", "text", "ACCEPTED 1 " + "c" * 40, 26), say(12, "foreman", "text", "STAGE-OPEN 2", 26),
            say(13, "foreman", "text", "ACCEPTED 1 " + "d" * 40 + " (BACKPORT re-accepted). ACCEPTED 2 " + "e" * 40 + " closed", 29),
            say(10, "foreman", "text", "FINAL REPORT\nall done", 30),
            say(11, "verifier", "text", "late note", 50)]
    (run / "room-export.json").write_text(json.dumps({"scope": "full", "messages": msgs}))
    out = subprocess.run([str(BIN / "run-stats"), "--run", str(run), "--markdown"], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert "30 min from dispatch to final report" in out.stdout and "Human messages in the room: 1" in out.stdout
    assert f"| 1 | +2 min | +4 min | +9 min | 2 | 1 | 28 min | `{'d' * 12}` | 8/8 (claims its stage) |" in out.stdout
    assert f"| 2 | — | — | — | 0 | 0 | 3 min | `{'e' * 12}` |" in out.stdout
    assert "| builder | 2 | 2 | 1 |" in out.stdout and "| verifier | 1 | 4 | 0 |" in out.stdout
    assert f"verdicts/stage-1/verifier-{'b' * 12}.md" in out.stdout and "room message `m6`" in out.stdout


def test_package_run_fills_run_facts_into_the_documents(tmp_path):
    """--docs copies README, FACTORY and evidence, with <!-- run-facts --> replaced by the generated tables."""
    run = tmp_path / "runs" / "x-02"
    r = run / "result"
    r.mkdir(parents=True)
    git(r, "init", "-q", "-b", "main")
    git(r, "-c", "user.name=builder", "-c", "user.email=s@example.test", "commit", "-q", "--allow-empty", "-m", "x")
    (run / "run.env").write_text("RUN_ID=x-02\nROOM=00000000-room\nTRACK=toy\n")
    msg = lambda i, who, text, m: {"id": f"m{i}", "senderName": who, "senderType": "User" if who == "human" else "Agent",
                                   "messageType": "text", "content": text, "insertedAt": f"2026-11-07T10:{m:02d}:00Z"}
    (run / "room-export.json").write_text(json.dumps({"messages": [msg(0, "human", "go", 0), msg(1, "foreman", "FINAL REPORT", 12)]}))
    docs = tmp_path / "docs"
    (docs / "evidence").mkdir(parents=True)
    (docs / "evidence/shot.png").write_bytes(b"png")
    (docs / "README.md").write_text("# R\n\n<!-- run-facts -->\n")
    (docs / "FACTORY.md").write_text("# F\n")
    (run / "checks/foreman-s1-r1").mkdir(parents=True)
    (run / "checks/foreman-s1-r1/report.json").write_text("{}")
    (run / "score/all-7").mkdir(parents=True)
    (run / "score/all-7/summary.json").write_text("{}")
    (run / "score/summary-7.json").write_text("{}")
    dest = tmp_path / "pkg"
    live = tmp_path / "live" / "dossier-runway.com.json"
    live.parent.mkdir()
    live.write_bytes(b'{"domain": "runway.com", "status": "ready"}\n')
    subprocess.run([str(BIN / "package-run"), str(dest), "--run", str(run), "--docs", str(docs), "--artifact", str(live)],
                   capture_output=True, text=True, timeout=120)
    assert (dest / "dossier-runway.com.json").read_bytes() == live.read_bytes()
    assert (dest / "checks/foreman-s1-r1/report.json").exists() and (dest / "checks/fresh-clone/per-folder.json").exists()
    assert "12 min" in (dest / "evidence/run-stats.txt").read_text()
    readme = (dest / "README.md").read_text()
    assert "12 min from dispatch to final report" in readme and "<!-- run-facts -->" not in readme
    assert (dest / "evidence/shot.png").read_bytes() == b"png" and (dest / "room.json").exists() and (dest / "mandates").is_dir()
    assert "Add factory documents" in git(dest, "log", "--format=%s")


def test_check_links_finds_missing_files_and_anchors(tmp_path):
    (tmp_path / "rec").mkdir()
    (tmp_path / "rec/a.md").write_text("x\n")
    (tmp_path / "FACTORY.md").write_text("# F\n\n## The run in this repository\n\n```\n[x](inside-code-ignored)\n```\n")
    (tmp_path / "README.md").write_text("[a](rec/a.md) [f](FACTORY.md#the-run-in-this-repository) [w](https://example.test)\n")
    ok = subprocess.run([str(BIN / "check-links"), str(tmp_path)], capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout
    (tmp_path / "README.md").write_text('[a](rec/b.md) [f](FACTORY.md#no-such) <img src="evidence/x.png">\n')
    bad = subprocess.run([str(BIN / "check-links"), str(tmp_path)], capture_output=True, text=True)
    assert bad.returncode == 1 and "rec/b.md" in bad.stdout and "#no-such" in bad.stdout and "evidence/x.png" in bad.stdout
    (tmp_path / "README.md").write_text("[a](rec/a.md)\n<!-- RUN: the story -->\n")
    left = subprocess.run([str(BIN / "check-links"), str(tmp_path)], capture_output=True, text=True)
    assert left.returncode == 1 and "unfilled template marker" in left.stdout


HOOKS = pathlib.Path(__file__).resolve().parents[1] / "githooks"


def commit_as(repo, seat, path):
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    import uuid
    (repo / path).write_text(f"{seat} {uuid.uuid4()}\n")   # always a real change, so only the hook can refuse it
    subprocess.run(["git", "add", path], cwd=repo, check=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": seat, "GIT_AUTHOR_EMAIL": "s@example.test", "GIT_COMMITTER_NAME": seat, "GIT_COMMITTER_EMAIL": "s@example.test"}
    done = subprocess.run(["git", "commit", "-q", "-m", f"{seat} commits {path}", "--", path], cwd=repo, env=env, capture_output=True, text=True)
    if done.returncode:
        subprocess.run(["git", "reset", "-q", "--", path], cwd=repo)
    return done.returncode


def test_each_seat_commits_only_its_own_folders(tmp_path):
    repo = tmp_path / "result"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "core.hooksPath", str(HOOKS))
    assert commit_as(repo, "verifier", "acceptance/stage-1/run.sh") == 0
    assert commit_as(repo, "verifier", "acceptance/stage-1.seal") == 0
    assert commit_as(repo, "second-reader", "acceptance/second-reader/stage-1/run.sh") == 0
    assert commit_as(repo, "second-reader", "ledger/stage-1.jsonl") == 0
    assert commit_as(repo, "verifier", "acceptance/second-reader/stage-1/x.py") != 0
    assert commit_as(repo, "second-reader", "acceptance/stage-1/test_x.py") != 0
    assert commit_as(repo, "builder", "acceptance/second-reader/y.py") != 0
    assert commit_as(repo, "builder", "stage-1/app.py") == 0


def test_the_commit_hook_enforces_the_protocol_ownership_table(tmp_path):
    """PROTOCOL.md section 6 and the hook define ownership twice; a sample path from every row must agree."""
    import re as _re
    table = (pathlib.Path(__file__).resolve().parents[2] / "PROTOCOL.md").read_text().split("## 6. Repository", 1)[1].split("## 7.", 1)[0]
    rows = _re.findall(r"^\| (.+?) \| (.+?) \|$", table, flags=_re.M)[2:]
    seats = ["builder", "verifier", "second-reader", "product-user", "foreman"]
    repo = tmp_path / "result"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "core.hooksPath", str(HOOKS))
    checked = 0
    for paths, owner in rows:
        for spec in _re.findall(r"`([^`]+)`", paths):
            if spec in ("Dockerfile", "RUN.md", ".md"):
                continue
            for seat in (["verifier", "second-reader", "product-user"] if owner.startswith("the verifying seat named") else [owner]):
                sample = spec.replace("<n>", "1").replace("<seat>", seat).replace("<hash12>", "a" * 12)
                sample = sample + "f.txt" if sample.endswith("/") else sample
                assert commit_as(repo, seat, sample) == 0, (seat, sample)
                others = [s for s in seats if s != seat]
                assert all(commit_as(repo, other, sample) != 0 for other in others), (sample, "taken by another seat")
                checked += 1
    assert checked >= 10


def test_final_report_is_the_foremans_message_that_opens_with_it():
    final = load_script("timekeeper").is_final_report
    mentions = "@[REDACTED]/[REDACTED] " + " ".join(f"@[[{'a' * 8}-{'b' * 4}-{'c' * 4}-{'d' * 4}-{'e' * 12}]]" for _ in range(4))
    assert final({"message_type": "text", "sender_name": "foreman", "content": mentions + " FINAL REPORT\n\n# Final report"})
    assert final({"message_type": "text", "sender_name": "foreman", "content": "FINAL REPORT"})
    # sub-03, 11-18: the foreman wrote its report as a markdown heading.
    assert final({"message_type": "text", "sender_name": "foreman", "content": "@[[x]] # FINAL REPORT\n\nAll stages"})
    assert final({"message_type": "text", "sender_name": "foreman", "content": "**FINAL REPORT** for the run"})
    assert not final({"message_type": "text", "sender_name": "verifier", "content": "FINAL REPORT received"})
    assert not final({"message_type": "text", "sender_name": "foreman", "content": "ACCEPTED 4 abc. The FINAL REPORT follows the commits."})
    assert not final({"message_type": "thought", "sender_name": "foreman", "content": "FINAL REPORT"})


def test_fsay_refuses_a_name_that_is_not_a_seat(work):
    (work / "run.env").write_text("OWNER=owner1\nROOM=room-1\n")
    out = tool(work, "fsay", "nobody", "--", "hello", seat="foreman")
    assert out.returncode == 1 and "no seat named nobody" in out.stderr


def test_fpublish_puts_suites_and_seal_records_under_fixed_names(work):
    assert tool(work, "seal", 1, work / "verifier/sealed/stage-1").returncode == 0
    (work / "verifier/sealed/stage-1/__pycache__").mkdir()
    (work / "verifier/sealed/stage-1/__pycache__/x.pyc").write_text("x")
    out = tool(work, "fpublish", 1, seat="verifier")
    assert out.returncode == 0, out.stderr
    files = git(work / "result", "ls-files").split()
    assert {"acceptance/stage-1/SEAL.json", "acceptance/stage-1/run.sh", "acceptance/stage-1/test_x.py"} <= set(files)
    assert not any("__pycache__" in f for f in files)
    (work / "second-reader/probes/stage-1").mkdir(parents=True)
    (work / "second-reader/probes/stage-1/run.sh").write_text("#!/bin/sh\n")
    out = tool(work, "fpublish", 1, seat="second-reader")
    assert out.returncode == 0, out.stderr
    assert "acceptance/second-reader/stage-1/run.sh" in git(work / "result", "ls-files")
    assert tool(work, "fpublish", 1, seat="builder").returncode == 1


def test_fpublish_refuses_a_suite_changed_after_its_seal(work):
    assert tool(work, "seal", 1, work / "verifier/sealed/stage-1").returncode == 0
    (work / "verifier/sealed/stage-1/test_x.py").write_text("changed\n")
    out = tool(work, "fpublish", 1, seat="verifier")
    assert out.returncode == 1 and "no longer matches its seal" in out.stderr


ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_every_mandate_starts_with_its_harness_model_and_effort():
    """Gate 1: each mandate starts with its actual Harness:, Model: and Effort: (none for the script-driven timekeeper)."""
    for mandate in sorted((ROOT / "mandates").glob("*.md")):
        head = mandate.read_text().splitlines()[:3]
        assert head[0].startswith("Harness: ") and head[1].startswith("Model: "), mandate.name
        assert head[2].startswith("Effort: "), mandate.name
        if head[0] in ("Harness: Claude Code", "Harness: Codex"):
            assert head[2].split(": ")[1] in ("low", "medium", "high", "xhigh", "max"), mandate.name
        else:
            assert head[2] == "Effort: none", mandate.name


def test_launchers_carry_the_mandates_effort(tmp_path):
    import shutil
    (tmp_path / "bin").mkdir()
    shutil.copy(BIN / "make-launchers", tmp_path / "bin/make-launchers")
    subprocess.run([str(tmp_path / "bin/make-launchers"), "builder:claude:medium", "second-reader:codex:high", "old:claude"], check=True)
    assert "FACTORY_SEAT_EFFORT=medium" in (tmp_path / "bin/seats/builder").read_text()
    assert "FACTORY_SEAT_EFFORT=high" in (tmp_path / "bin/seats/second-reader").read_text()
    assert 'seat-claude" "$@"' in (tmp_path / "bin/seats/old").read_text()
    assert '--effort "$FACTORY_SEAT_EFFORT"' in (BIN / "seat-claude").read_text()
    assert '"{EFFORT}"' in (ROOT / "factory/settings/codex-config.toml").read_text()


def test_stage_open_waits_for_the_previous_acceptance(work):
    (work / "run.env").write_text("OWNER=owner1\nROOM=room-1\n")
    spec = work / "spec"
    spec.mkdir()
    for n in (1, 2):
        (spec / f"stage-{n}.md").write_text(f"stage {n}\n")
    early = tool(work, "stage-open", 2, spec / "stage-2.md", "verifier", seat="foreman")
    assert early.returncode == 1 and "stage 1 is not accepted yet" in early.stderr
    wrong = tool(work, "stage-open", 1, spec / "stage-2.md", "verifier", seat="foreman")
    assert wrong.returncode == 1 and "is not the specification for stage 1" in wrong.stderr
    r = work / "result"
    (r / "accepted").mkdir()
    (r / "accepted/stage-1.txt").write_text("ACCEPTED 1\n")
    uncommitted = tool(work, "stage-open", 2, spec / "stage-2.md", "verifier", seat="foreman")
    assert uncommitted.returncode == 1 and "is not committed" in uncommitted.stderr
    git(r, "add", "accepted/stage-1.txt")
    git(r, "commit", "-q", "-m", "accept stage 1")
    # Past the gate, fsay refuses the unknown seat before any message is sent.
    opened = tool(work, "stage-open", 2, spec / "stage-2.md", "nobody", seat="foreman")
    assert "no seat named nobody" in opened.stderr and "not accepted yet" not in opened.stderr


def test_an_accepted_stage_folder_never_changes_again(tmp_path):
    repo = tmp_path / "result"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "core.hooksPath", str(HOOKS))
    assert commit_as(repo, "builder", "stage-1/app.py") == 0
    assert commit_as(repo, "foreman", "accepted/stage-1.txt") == 0
    assert commit_as(repo, "builder", "stage-1/app.py") != 0
    assert commit_as(repo, "builder", "stage-2/app.py") == 0


def test_the_dispatch_carries_the_tracks_event_rules_and_mandates_do_not(tmp_path):
    import shutil
    (tmp_path / "factory/bin").mkdir(parents=True)
    shutil.copy(BIN / "dispatch", tmp_path / "factory/bin/dispatch")
    shutil.copytree(ROOT / "factory/templates", tmp_path / "factory/templates")
    for track in ("dossier", "toy"):
        kit = tmp_path / "kit"
        (kit / track / "spec").mkdir(parents=True, exist_ok=True)
        for n in range(1, 5):
            (kit / track / "spec" / f"stage-{n}.md").write_text("spec\n")
        (tmp_path / "work").mkdir(exist_ok=True)
        (tmp_path / "work/run.env").write_text(f"KIT={kit}\nTRACK={track}\nOWNER=o\nROOM=r\n")
        out = subprocess.run(["python3", str(tmp_path / "factory/bin/dispatch"), "--print"], capture_output=True, text=True, timeout=30)
        assert out.returncode == 0, out.stderr
        assert "{" not in out.stdout.replace("{n}", ""), "a placeholder was left"
        assert ("webrouter>=0.12.0" in out.stdout) == (track == "dossier")
        assert "stage-4.md" in out.stdout
    for mandate in (ROOT / "mandates").glob("*.md"):
        text = mandate.read_text().lower()
        assert not any(term in text for term in ("webrouter", "nimble", "dossier", "runway")), mandate.name


def test_services_run_with_the_jobs_stated_limits(work):
    import importlib.util
    spec = importlib.util.spec_from_file_location("fenv_t", BIN.parent / "lib" / "fenv.py")
    (work / "run.env").write_text("ROOM=r\nSERVICE_CPUS=2\nSERVICE_MEMORY=3g\n")
    os.environ["FACTORY_WORK"] = str(work)
    try:
        fenv_t = importlib.util.module_from_spec(spec); spec.loader.exec_module(fenv_t)
        assert fenv_t.service_limits() == ("2", "3g")
        (work / "run.env").write_text("ROOM=r\n")
        assert fenv_t.service_limits() == ("2", "2g")
    finally:
        os.environ.pop("FACTORY_WORK", None)
    assert '"--memory", "2g"' not in (BIN / "fserve").read_text()


def test_only_the_dispatch_speaks_as_the_human():
    """Autonomy: the dispatch is the one human message. Helpers that pause, restart or wake seats never post as the human."""
    import re as _re
    senders = {}
    for path in sorted(BIN.iterdir()):
        if path.is_file() and path.parent.name != "seats":
            text = path.read_text(errors="replace")
            if _re.search(r'"send"|\bsend\b', text) and _re.search(r"band|jam|BAND", text):
                senders[path.name] = text
    assert set(senders) == {"dispatch", "fsay", "timekeeper"}, sorted(senders)
    assert '"--session", "df-timekeeper", "send"' in senders["timekeeper"]   # the timekeeper speaks as itself
    assert '"--as", f"{owner}/{fenv.SEAT}", "send"' in senders["fsay"]        # a seat speaks as itself
    assert "FACTORY_SEAT is unset" in senders["fsay"]                         # and never without a seat
    for helper in ("watchdog", "meter-guard"):
        text = (BIN / helper).read_text()
        assert not _re.search(r'\bsend\b|"send"', text), helper
        assert "restart" in text or "stop" in text


def test_package_run_without_documents_or_artifacts_still_commits(tmp_path):
    run = tmp_path / "runs" / "x-03"
    r = run / "result"
    r.mkdir(parents=True)
    git(r, "init", "-q", "-b", "main")
    git(r, "-c", "user.name=builder", "-c", "user.email=s@example.test", "commit", "-q", "--allow-empty", "-m", "x")
    (run / "run.env").write_text("RUN_ID=x-03\nROOM=00000000-room\nTRACK=toy\n")
    msg = lambda i, who, text: {"id": f"m{i}", "senderName": who, "senderType": "User" if who == "human" else "Agent",
                                "messageType": "text", "content": text, "insertedAt": f"2026-11-07T10:0{i}:00Z"}
    (run / "room-export.json").write_text(json.dumps({"messages": [msg(0, "human", "go"), msg(1, "foreman", "FINAL REPORT")]}))
    dest = tmp_path / "pkg"
    subprocess.run([str(BIN / "package-run"), str(dest), "--run", str(run)], capture_output=True, text=True, timeout=120)
    assert "Add factory documents" in git(dest, "log", "--format=%s")


def test_dispatch_sends_nothing_on_help_unknown_arguments_or_a_second_time(tmp_path):
    import shutil
    (tmp_path / "factory/bin").mkdir(parents=True)
    shutil.copy(BIN / "dispatch", tmp_path / "factory/bin/dispatch")
    (tmp_path / "factory/templates").mkdir()
    (tmp_path / "factory/templates/dispatch.md").write_text("task {TRACK} {SPECS}\n")
    (tmp_path / "kit/toy/spec").mkdir(parents=True)
    (tmp_path / "kit/toy/spec/stage-1.md").write_text("spec\n")
    (tmp_path / "work/state").mkdir(parents=True)
    (tmp_path / "work/run.env").write_text(f"KIT={tmp_path / 'kit'}\nTRACK=toy\nOWNER=o\nROOM=r\n")
    run = lambda *a: subprocess.run([str(tmp_path / "factory/bin/dispatch"), *a], capture_output=True, text=True, timeout=30,
                                    env={**os.environ, "PATH": "/usr/bin:/bin"})
    help_ = run("--help")
    assert help_.returncode == 0 and "Send the one human message" in help_.stdout
    bad = run("--bogus")
    assert bad.returncode != 0 and "nothing was sent" in bad.stderr
    shown = run("--print")
    assert shown.returncode == 0 and "task toy" in shown.stdout and not (tmp_path / "work/state/dispatch.md").exists()
    (tmp_path / "work/state/dispatched-at").write_text("1\n")
    again = run()
    assert again.returncode != 0 and "already dispatched" in again.stderr


def test_every_tool_answers_help_without_acting(tmp_path):
    """`<tool> --help` prints usage and changes nothing: no workspace, no room, no message. 11-13: dispatch sent on --help."""
    import shutil, stat
    shutil.copytree(BIN.parent, tmp_path / "factory", ignore=shutil.ignore_patterns("__pycache__", "build"))
    tools = sorted(p for p in (tmp_path / "factory/bin").iterdir() if p.is_file() and p.stat().st_mode & stat.S_IXUSR)
    assert len(tools) > 30
    for tool_path in tools:
        out = subprocess.run([str(tool_path), "--help"], capture_output=True, text=True, timeout=30, cwd=tmp_path,
                             env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)})
        assert out.returncode == 0, (tool_path.name, out.stdout[-300:], out.stderr[-300:])
        assert out.stdout.strip(), (tool_path.name, "printed no usage")
        assert not (tmp_path / "work").exists(), (tool_path.name, "created a workspace")


def test_dispatch_finds_specifications_under_challenges(tmp_path):
    import shutil
    (tmp_path / "factory/bin").mkdir(parents=True)
    shutil.copy(BIN / "dispatch", tmp_path / "factory/bin/dispatch")
    (tmp_path / "factory/templates/track-rules").mkdir(parents=True)
    (tmp_path / "factory/templates/dispatch.md").write_text("{TRACK_RULES}specs {SPECS}\n")
    (tmp_path / "factory/templates/track-rules/dossier.md").write_text("mock web at {TRACK_DIR}/web/README.md\n")
    for n in (1, 2):
        (tmp_path / "kit/challenges/dossier/spec").mkdir(parents=True, exist_ok=True)
        (tmp_path / f"kit/challenges/dossier/spec/stage-{n}.md").write_text("spec\n")
    (tmp_path / "work").mkdir()
    (tmp_path / "work/run.env").write_text(f"KIT={tmp_path / 'kit'}\nTRACK=dossier\nOWNER=o\nROOM=r\n")
    out = subprocess.run([str(tmp_path / "factory/bin/dispatch"), "--print"], capture_output=True, text=True, timeout=30)
    assert out.returncode == 0, out.stderr
    assert f"{tmp_path}/kit/challenges/dossier/spec/stage-1.md {tmp_path}/kit/challenges/dossier/spec/stage-2.md" in out.stdout
    assert f"mock web at {tmp_path}/kit/challenges/dossier/web/README.md" in out.stdout


def test_a_copy_of_the_previous_stage_made_before_the_seal_is_not_product_code(work):
    """sub-01, 11-13: the builder's stage-copy of accepted stage 1 landed before the stage-2 seal, seal counted it as a
    product commit, and accept-check refused a stage all three seats had passed."""
    r = work / "result"
    (r / "stage-1").mkdir()
    (r / "stage-1/app.py").write_text("print('stage 1')\n")
    git(r, "add", "-A"); git(r, "commit", "-q", "-m", "stage 1")
    import shutil
    shutil.copytree(r / "stage-1", r / "stage-2")
    git(r, "add", "-A"); git(r, "commit", "-q", "-m", "Stage 2: start as a copy of accepted stage 1")
    suite = work / "verifier" / "sealed" / "stage-2"
    suite.mkdir(parents=True)
    (suite / "test_x.py").write_text("x\n"); (suite / "run.sh").write_text("#!/bin/sh\n")
    assert tool(work, "seal", 2, suite).returncode == 0
    log = json.loads((work / "verifier/sealed/stage-2.seal").read_text())
    assert log[0]["product_commits"] == "0"
    (r / "stage-2/app.py").write_text("print('stage 2')\n")
    git(r, "add", "-A"); git(r, "commit", "-q", "-m", "stage 2 code")
    (suite / "test_y.py").write_text("y\n")
    assert tool(work, "seal", "--amend", "after code", 2, suite).returncode == 0
    log = json.loads((work / "verifier/sealed/stage-2.seal").read_text())
    assert log[1]["product_commits"] == "1"


def test_fpublish_leaves_out_files_the_kit_would_read_as_credentials(work):
    """sub-01, 11-13: a probe's results JSON held `token=TOKEN` from a test description; the kit's check flags that."""
    (work / "second-reader/probes/stage-1").mkdir(parents=True)
    (work / "second-reader/probes/stage-1/run.sh").write_text("#!/bin/sh\n")
    (work / "second-reader/probes/stage-1/results-abc.json").write_text('{"case": "auth(token=TOKEN, key=1)"}\n')
    (work / "second-reader/probes/stage-1/notes.json").write_text('{"ok": true}\n')
    out = tool(work, "fpublish", 1, seat="second-reader")
    assert out.returncode == 0, out.stderr
    files = git(work / "result", "ls-files").split()
    assert "acceptance/second-reader/stage-1/run.sh" in files and "acceptance/second-reader/stage-1/notes.json" in files
    assert "acceptance/second-reader/stage-1/results-abc.json" not in files and "results-abc.json" in out.stdout


def test_the_protocol_and_the_foreman_state_the_same_round_cap():
    """11-18: the foreman's mandate said seventh while PROTOCOL.md still said fifth, through sub-03 and sub-04."""
    import re as _re
    words = {"third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10}
    foreman = (ROOT / "mandates/foreman.md").read_text()
    protocol = (ROOT / "PROTOCOL.md").read_text()
    a = _re.search(r"On a (\w+) BLOCK, record `BLOCKED`", foreman)
    b = _re.search(r"After the (\w+) BLOCK round on one stage the foreman stops the line", protocol)
    assert a and b, "the round cap sentence moved; update this test with it"
    assert words[a.group(1)] == words[b.group(1)], (a.group(1), b.group(1))
