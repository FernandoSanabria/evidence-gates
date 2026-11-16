"""Shared fixtures for the unit tests: throwaway git repositories with a neutral identity. Standard library only."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t"}


def env(**extra: str) -> dict:
    e = dict(os.environ)
    e.update(GIT_ENV)
    e.update(extra)
    return e


class Repo:
    """A temporary git repository on branch main."""

    def __init__(self) -> None:
        self.dir = tempfile.mkdtemp(prefix="eg-test-")
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str, check: bool = True) -> str:
        p = subprocess.run(["git", "-C", self.dir, *args], capture_output=True, text=True, env=env())
        if check and p.returncode != 0:
            raise RuntimeError("git %s: %s" % (" ".join(args), p.stderr))
        return p.stdout.strip()

    def write(self, path: str, text: str) -> None:
        full = os.path.join(self.dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(text)

    def read(self, path: str) -> str:
        return open(os.path.join(self.dir, path), encoding="utf-8").read()

    def commit(self, message: str = "c") -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def tag(self, name: str, ref: str = "HEAD") -> None:
        self.git("tag", "-a", name, "-m", name, ref)

    def run(self, script: str, *args: str, stdin: str | None = None, cwd: str | None = None,
            extra_env: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, script), *args], cwd=cwd or self.dir,
                              input=stdin, capture_output=True, text=True, env=env(**(extra_env or {})))

    def close(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)


def hook_payload(command: str, cwd: str) -> str:
    import json
    return json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": cwd,
                       "tool_input": {"command": command}})
