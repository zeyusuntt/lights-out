"""The guard must stop what the protocol forbids and leave ordinary work alone."""
import json, os, pathlib, subprocess, tempfile

GUARD = pathlib.Path(__file__).resolve().parents[1] / "hooks" / "guard.py"
KIT = "/tmp/kit"


def run(seat, tool, data, sealed=False):
    with tempfile.TemporaryDirectory() as work:
        pathlib.Path(work, "run.env").write_text(f"KIT={KIT}\n")
        env = {**os.environ, "FACTORY_SEAT": seat, "FACTORY_WORK": work}
        call = json.dumps({"tool_name": tool, "tool_input": {k: (v.replace("WORK", work) if isinstance(v, str) else v) for k, v in data.items()}})
        return subprocess.run(["python3", str(GUARD)], input=call, text=True, env=env, capture_output=True).returncode


def bash(seat, command):
    return run(seat, "Bash", {"command": command})


def read(seat, path):
    return run(seat, "Read", {"file_path": path})


# Ordinary work the guard got wrong.
def test_a_seat_can_read_its_own_saved_tool_output():
    assert read("builder", "/Users/x/.claude/projects/-a-b/uuid/tool-results/abc.txt") == 0


def test_the_kit_interpreter_is_usable():
    assert bash("builder", f"{KIT}/.venv/bin/python -m pytest tests -q") == 0


def test_the_check_command_is_usable():
    assert bash("verifier", f"cd {KIT} && with-slot .venv/bin/python -m harness run --track t --repo /r --stage 1 --mode isolated --out /o") == 0


def test_specifications_can_be_read():
    assert read("builder", f"{KIT}/track/spec/stage-1.md") == 0
    assert bash("builder", f"cat {KIT}/track/spec/stage-1.md") == 0


# What it must keep stopping.
def test_check_sources_stay_closed():
    assert read("builder", f"{KIT}/track/test/stage_1/test_sample.py") == 2
    assert bash("builder", f"cat {KIT}/track/test/stage_1/test_sample.py") == 2
    assert bash("verifier", f"grep -r amount {KIT}") == 2


def test_personal_paths_stay_closed():
    assert read("builder", "/Users/x/.claude/CLAUDE.md") == 2
    assert read("builder", "/Users/x/.codex/AGENTS.md") == 2
    assert read("builder", "/Users/x/.ssh/id_rsa") == 2


def test_history_is_not_rewritten():
    assert bash("builder", "git commit --amend -m x") == 2
    assert bash("builder", "git push origin main") == 2
    assert bash("builder", "git rebase main") == 2


def test_verifier_cannot_reach_the_shared_stage_folder():
    assert read("verifier", "WORK/result/stage-1/app.py") == 2


def test_product_user_cannot_read_source():
    assert read("product-user", "WORK/result/stage-2/app.py") == 2


def test_foreman_does_not_write_product_code():
    assert run("foreman", "Write", {"file_path": "WORK/result/stage-1/x.py", "content": "x"}) == 2


def test_shared_docker_state_is_left_alone():
    assert bash("builder", "docker system prune -af") == 2
    assert bash("builder", "colima stop") == 2


def test_a_commit_message_may_say_anything():
    assert bash("builder", 'git commit -m "Fix push notifications and the rebase form" -- stage-2/') == 0


def test_cd_into_the_kit_does_not_open_its_checks():
    assert bash("builder", f"cd {KIT} && cat track/test/stage_1/test_sample.py") == 2
    assert bash("builder", f"cd {KIT} && with-slot .venv/bin/python -m harness run --track t --repo /r --stage 1 --out /o; cat track/test/conftest.py") == 2


def test_builder_cannot_read_other_seats_suites():
    assert read("builder", "WORK/result/acceptance/stage-1/test_x.py") == 2
    assert read("builder", "WORK/verifier/sealed/stage-1/test_x.py") == 2
    assert bash("builder", "cat WORK/second-reader/probes/stage-1/api.py") == 2


def test_git_paths_and_messages_naming_push_or_rebase_are_ordinary():
    assert bash("builder", "git diff -- stage-2/rebase/index.html") == 0
    assert bash("builder", "git show HEAD:stage-2/push/client.js") == 0
    assert bash("builder", "git -C /r log --oneline -- stage-1/push") == 0


def test_history_rewrites_are_still_refused_with_options():
    assert bash("builder", "git -C /r push origin main") == 2
    assert bash("builder", "git -c user.name=x commit --amend --no-edit") == 2
    assert bash("builder", "git -C /r reset --hard HEAD~1") == 2


def test_a_seat_may_run_its_own_suite_from_the_kit_directory():
    assert bash("verifier", f"cd {KIT} && .venv/bin/python -m pytest /work/verifier/sealed/stage-1/tests -q") == 0


def test_whole_disk_searches_are_refused():
    for command in ("find / -maxdepth 4 -name jam -type f 2>/dev/null | head", "find ~ -name x", "find $HOME -name x",
                    "find /Users/someone -name x", "find /Applications -name jam", "ls; find '/' -name x"):
        assert bash("foreman", command) == 2, command


def test_searches_inside_the_work_folder_are_allowed():
    for command in ("find /Users/someone/dev/band-factory/work/result -name '*.md'", "find . -name x", "find stage-1 -type f",
                    "find $FACTORY_WORK/builder -name '*.py'"):
        assert bash("builder", command) == 0, command


def run_with(seat, tool, data, accepted=()):
    """Like run, with accepted/stage-<n>.txt records present in the result repository."""
    with tempfile.TemporaryDirectory() as work:
        pathlib.Path(work, "run.env").write_text(f"KIT={KIT}\n")
        for n in accepted:
            pathlib.Path(work, "result/accepted").mkdir(parents=True, exist_ok=True)
            pathlib.Path(work, f"result/accepted/stage-{n}.txt").write_text("ACCEPTED\n")
        env = {**os.environ, "FACTORY_SEAT": seat, "FACTORY_WORK": work}
        call = json.dumps({"tool_name": tool, "tool_input": data})
        return subprocess.run(["python3", str(GUARD)], input=call, text=True, env=env, capture_output=True).returncode


def test_a_later_specification_stays_closed_until_the_previous_stage_is_accepted():
    spec = f"{KIT}/track/spec"
    assert run_with("foreman", "Read", {"file_path": f"{spec}/stage-1.md"}) == 0
    assert run_with("foreman", "Read", {"file_path": f"{spec}/stage-2.md"}) == 2
    assert run_with("foreman", "Read", {"file_path": f"{spec}/stage-2.md"}, accepted=[1]) == 0
    assert run_with("foreman", "Bash", {"command": f"cat {spec}/stage-3.md"}, accepted=[1]) == 2
    assert run_with("foreman", "Bash", {"command": f"stage-open 2 {spec}/stage-2.md second-reader verifier"}) == 2
    assert run_with("foreman", "Bash", {"command": f"stage-open 2 {spec}/stage-2.md second-reader verifier"}, accepted=[1]) == 0
    assert run_with("foreman", "Bash", {"command": f"cd {spec} && wc -l stage-4.md"}, accepted=[1, 2]) == 2
    assert run_with("foreman", "Bash", {"command": f"cd {spec} && cat stage-1.md && echo ${{HOME}}"}) == 0


def test_no_glob_reads_every_specification_at_once():
    spec = f"{KIT}/track/spec"
    for command in (f"cat {spec}/stage-*.md", f"cat {spec}/*", f"cd {spec} && cat *", f"cat {spec}/stage-{{1,2}}.md"):
        assert run_with("foreman", "Bash", {"command": command}, accepted=[1, 2, 3]) == 2, command
    assert run_with("foreman", "Glob", {"pattern": "stage-*.md", "path": spec}) == 2
    assert run_with("foreman", "Grep", {"pattern": "error", "path": spec}) == 2


def test_files_named_like_stages_elsewhere_are_not_specifications():
    for path in ("WORK/result/ledger/stage-2.md", "WORK/result/rulings/stage-3.md", "WORK/result/stage-2/RUN.md"):
        assert run("foreman", "Read", {"file_path": path}) == 0, path


# The kickoff kit of 11-13 keeps tracks under challenges/<track>/, with a mock web for development.
def test_specifications_under_challenges_can_be_read():
    assert read("builder", f"{KIT}/challenges/dossier/spec/stage-1.md") == 0
    assert bash("verifier", f"cat {KIT}/challenges/dossier/spec/stage-1.md") == 0


def test_the_mock_web_can_be_read_built_and_run():
    assert read("builder", f"{KIT}/challenges/dossier/web/README.md") == 0
    assert bash("builder", f"docker build -t dossier-web {KIT}/challenges/dossier/web") == 0
    assert bash("verifier", f"cd {KIT} && docker build -t dossier-web challenges/dossier/web") == 0
    assert bash("verifier", f'docker run -d -v "{KIT}/challenges/dossier/web/corpus/sample:/data/corpus:ro" dossier-web') == 0


def test_the_answer_key_and_the_checks_stay_closed():
    assert read("builder", f"{KIT}/challenges/dossier/web/corpus/sample/key.json") == 2
    assert bash("builder", f"cat {KIT}/challenges/dossier/web/corpus/sample/key.json") == 2
    assert bash("builder", f"cd {KIT} && cat challenges/dossier/web/corpus/sample/key.json") == 2
    assert read("verifier", f"{KIT}/challenges/dossier/test/stage_1/test_sample.py") == 2
    assert bash("builder", f"cd {KIT} && cat challenges/dossier/test/stage_1/test_sample.py") == 2
