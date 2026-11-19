#!/usr/bin/env python3
"""PreToolUse guard for Claude Code seats. Exit 2 refuses the call and tells the seat why.

Mechanical versions of the protocol's boundaries:
- nobody rewrites history, skips hooks, or touches Docker state other people use;
- nobody reads supplied check sources;
- the verifier cannot reach product code before its suite is sealed;
- the product-user cannot read source;
- only the builder writes stage folders;
- nobody reads a stage's specification before the previous stage is accepted.
"""
import json, os, pathlib, re, shlex, sys

HOME = pathlib.Path(__file__).resolve().parents[2]
WORK = pathlib.Path(os.environ.get("FACTORY_WORK", HOME / "work"))
SEAT = os.environ.get("FACTORY_SEAT", "")


def refuse(why):
    print(f"factory guard: {why}", file=sys.stderr)
    raise SystemExit(2)


def env():
    out = {}
    path = WORK / "run.env"
    if path.exists():
        for line in path.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep:
                out[key.strip()] = value.strip()
    return out


def without_allowed(text, kit):
    """The text with the kit's interpreter and specifications removed: what remains of the kit is off limits."""
    text = re.sub(re.escape(kit) + r"/\.venv/\S*", "", text)
    text = re.sub(re.escape(kit) + r"/(?:challenges/)?[^/\s]+/spec\S*", "", text)
    # The mock web a track documents for development: its README, source and sample corpus, never the checks' answer key.
    return re.sub(re.escape(kit) + r"/challenges/[^/\s]+/web(?![^\s\"']*key\.json)[^\s\"']*", "", text)


GIT_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def rewrites_history(command):
    """Whether any git invocation in a shell command rewrites history or skips hooks. Paths and messages don't count."""
    for part in re.split(r"&&|\|\||;|\||\n", command):
        try:
            words = shlex.split(part)
        except ValueError:
            words = part.split()
        for i, word in enumerate(words):
            if word != "git" and not word.endswith("/git"):
                continue
            j = i + 1
            while j < len(words) and words[j].startswith("-"):
                j += 2 if words[j] in GIT_OPTIONS_WITH_VALUE else 1
            if j >= len(words):
                continue
            sub, rest = words[j], words[j + 1:]
            if sub in ("push", "rebase", "filter-branch", "filter-repo"):
                return True
            if "--no-verify" in rest or (sub == "commit" and "--amend" in rest) \
                    or (sub == "reset" and "--hard" in rest) or (sub == "reflog" and "expire" in rest):
                return True
    return False


def kit_breach(command, kit):
    """Whether any part of a shell command reaches the kit other than through the allowed routes."""
    cd = r"\bcd\s+[\"']?" + re.escape(kit) + r"[\"']?"
    entered = re.search(cd, command)
    for part in re.split(r"&&|\|\||;|\n", command):
        if "-m harness" in part:
            continue
        if kit in without_allowed(re.sub(cd, "", part), kit):
            return True
        if entered and any(not w.startswith(("/", "$", "~")) and re.search(r"(^|/)tests?(/|$)|(^|/)test_\w+\.py$|conftest|key\.json", w)
                           for w in part.split()):
            return True
    return False


def spec_read_early(text, accepted_dir):
    """The later stages whose specification `text` reaches before the previous stage is accepted.

    A specification is a file `.../spec/stage-<k>.md`. A glob over the specification folder would
    read every stage at once, so it counts as reaching all of them.
    """
    if "spec" not in text:
        return []
    inside = re.search(r"\bcd\s+[\"']?\S*/spec/?[\"']?(\s|$|;|&)", text)
    stages = [int(k) for k in re.findall(r"spec/stage-(\d+)\.md", text)]
    if inside:
        stages += [int(k) for k in re.findall(r"(?<![\w/.-])stage-(\d+)\.md", text)]
    globbed = re.search(r"spec/(?:stage-)?[*?\[{]", text) or (inside and re.search(r"(?<![\w/$])\*|stage-[*?\[{]", text))
    if globbed:
        return ["every stage (a glob over the specifications)"]
    return sorted({k for k in stages if k > 1 and not (accepted_dir / f"stage-{k - 1}.txt").exists()})


def main():
    try:
        call = json.load(sys.stdin)
    except ValueError:
        return
    tool, data = call.get("tool_name", ""), call.get("tool_input") or {}
    run = env()
    kit = run.get("KIT", "\0")
    result = str(WORK / "result")
    if tool == "Bash":
        text = data.get("command", "")
        if rewrites_history(text):
            refuse("history is never rewritten and hooks are never skipped; fix forward")
        if re.search(r"\bdocker\s+(system|volume|image|container|network|builder)\s+prune\b", text) \
                or re.search(r"\bdocker\s+(stop|rm|kill)\b[^|;&]*\$\(", text) \
                or re.search(r"\bcolima\s+(stop|delete|restart|start)\b", text):
            refuse("this machine is shared; remove only containers you started, by name")
        if re.search(r"\bfind\s+[\"']?(/|~|\$HOME|/Users(/[^/\s\"']+)?|/Applications|/Library|/System|/opt|/usr|/private|/var|/Volumes)/?[\"']?(\s|$)", text):
            refuse("a search of the whole disk can run for many minutes; the factory's tools are on your PATH "
                   "(`fwho` lists the room); search inside the run's work folder")
        if kit_breach(text, kit):
            refuse("the kit is reachable only through its check command, its interpreter and its specifications")
    else:
        text = " ".join(str(data.get(k, "")) for k in ("file_path", "path", "pattern", "glob"))
        if kit in without_allowed(text, kit):
            refuse("only the specifications may be read from the kit")
    if tool in ("Grep", "Glob") and re.search(r"/spec/?$", str(data.get("path", ""))):
        refuse("search one stage's specification by its full name, stage-<n>.md")
    early = spec_read_early(text, WORK / "result" / "accepted")
    if early:
        refuse(f"the specification for stage {', '.join(map(str, early))} opens only after the previous stage is accepted "
               "(accepted/stage-<n-1>.txt); read the stages in order")
    # A seat's own long tool output is saved under its session's folder, and reading it back is ordinary work.
    readable = re.sub(r"\S*/\.claude/projects/[^/\s]+/[^/\s]+/tool-results/\S*", "", text)
    for private in ("/.ssh", "/.aws", "/.codex", "/.claude/", "/.jam/", "/Library/Keychains"):
        if private in readable and tool != "Bash":
            refuse("that path is outside this factory")
    stage_path = result + "/stage-"
    if SEAT == "builder" and any(p in text for p in (result + "/acceptance", str(WORK / "verifier"), str(WORK / "second-reader"))):
        refuse("another seat's tests are closed to you; a finding reaches you with its reproduction")
    if SEAT == "verifier" and stage_path in text:
        refuse("verify only clean clones made with fclone, never the shared checkout")
    if SEAT == "product-user" and (stage_path in text or "/clones/" in text or "/serve/" in text):
        refuse("you judge the running product; do not read its source")
    if SEAT == "foreman" and tool in ("Edit", "Write", "NotebookEdit") and stage_path in text:
        refuse("the foreman does not write product code")
    if tool == "AskUserQuestion":
        refuse("this is a dark run; decide from the requirements and the evidence")


if __name__ == "__main__":
    main()
