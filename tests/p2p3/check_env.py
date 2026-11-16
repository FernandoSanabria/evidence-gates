#!/usr/bin/env python3
"""Assert that the hook-proof environment dumps match the runner's allow-list byte for byte.

  check_env.py <run-id> <hookproof.jsonl> <hookproof.env>

Every line `run_arm.sh envlist <run-id>` prints must appear verbatim in both dumps: the hook's (`hookproof.env`,
written by the hook on each call) and the Bash call's (`env | sort` in the transcript). Every other variable in the
dumps must be one that Claude Code or the shell adds on its own (listed below, and reported); a variable outside both
sets fails the check. Values are never printed, only names. Exit 0 on a match, 1 otherwise.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Added by the subject's own Claude Code process or by its shell, not by the runner.
ADDED_BY_CLAUDE_OR_SHELL = {
    "AI_AGENT", "CLAUDECODE", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_EXECPATH",
    "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_CODE_SESSION_ATTENDED",
    "CLAUDE_CODE_SESSION_ID", "CLAUDE_EFFORT", "CLAUDE_PID", "CLAUDE_PROJECT_DIR", "COREPACK_ENABLE_AUTO_PIN",
    "GIT_EDITOR", "NoDefaultCurrentDirectoryInExePath", "OLDPWD", "PWD", "SHLVL", "_",
}


def bash_dump(transcript: str) -> list[str]:
    for line in open(transcript, encoding="utf-8"):
        d = json.loads(line)
        if d.get("type") != "user" or not isinstance(d["message"]["content"], list):
            continue
        for c in d["message"]["content"]:
            if c.get("type") == "tool_result" and not c.get("is_error"):
                text = c["content"] if isinstance(c["content"], str) else "".join(x.get("text", "") for x in c["content"])
                return [l for l in text.splitlines() if "=" in l]
    return []


def hook_dump(path: str) -> list[str]:
    calls, cur = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("--- hook call"):
            cur = []
            calls.append(cur)
        elif cur is not None and "=" in line:
            cur.append(line)
    return calls[0] if calls else []


def main(run_id: str, transcript: str, hookenv: str) -> int:
    allow = subprocess.run(["bash", os.path.join(HERE, "run_arm.sh"), "envlist", run_id],
                           capture_output=True, text=True, check=True).stdout.splitlines()
    bad = 0
    for name, dump in (("hook", hook_dump(hookenv)), ("bash", bash_dump(transcript))):
        lines = set(dump)
        missing = [a.split("=", 1)[0] for a in allow if a not in lines]
        names = {l.split("=", 1)[0] for l in dump}
        allowed_names = {a.split("=", 1)[0] for a in allow}
        unknown = sorted(names - allowed_names - ADDED_BY_CLAUDE_OR_SHELL)
        added = sorted(names & ADDED_BY_CLAUDE_OR_SHELL)
        ok = not missing and not unknown
        bad += not ok
        print("%s dump: %d variables; allow-list lines present byte for byte: %d/%d%s; unknown: %s; added by Claude Code or the shell: %s"
              % (name, len(names), len(allow) - len(missing), len(allow),
                 (" (missing: %s)" % ", ".join(missing)) if missing else "", unknown or "none", " ".join(added)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
