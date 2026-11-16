"""Tests for hooks/hooks.json and hooks/pre-commit-guard.sh: the configuration, and the wrapper's behaviour on
non-commit commands, on dead citations, on edited pre-registrations, and when it must fail closed."""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from helpers import Repo, env, hook_payload  # noqa: E402

WRAPPER = os.path.join(ROOT, "hooks", "pre-commit-guard.sh")


def run_wrapper(stdin: str, path: str | None = None) -> subprocess.CompletedProcess:
    e = env(CLAUDE_PLUGIN_ROOT=ROOT)
    if path is not None:
        e["PATH"] = path
    return subprocess.run([WRAPPER], input=stdin, capture_output=True, text=True, env=e)


def path_without_python() -> str:
    """A PATH holding only `cat` and `dirname`: enough for the wrapper's shell part, and no python3."""
    d = tempfile.mkdtemp(prefix="eg-nopy-")
    for tool in ("cat", "dirname"):
        src = shutil.which(tool)
        os.symlink(src, os.path.join(d, tool))
    return d


class Config(unittest.TestCase):
    def test_one_pretooluse_entry_as_designed(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
        self.assertEqual(list(cfg["hooks"]), ["PreToolUse"])
        groups = cfg["hooks"]["PreToolUse"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["matcher"], "Bash")
        (h,) = groups[0]["hooks"]
        self.assertEqual(h["type"], "command")
        self.assertEqual(h["if"], "Bash(git *)")
        self.assertEqual(h["command"], "${CLAUDE_PLUGIN_ROOT}/hooks/pre-commit-guard.sh")
        self.assertEqual(h["args"], [])
        self.assertEqual(h["onFailure"], "block")

    def test_wrapper_is_executable(self):
        self.assertTrue(os.stat(WRAPPER).st_mode & stat.S_IXUSR)


class Wrapper(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Repo()
        self.r.write("README.md", "start\n")
        self.r.write("docs/prereg/calc_PREDICTION.md", "# calc\n**Falsified by:** not 42.\n")
        self.r.commit()
        self.r.tag("prereg/calc")

    def tearDown(self) -> None:
        self.r.close()

    def commit_payload(self, command: str = "git add -A && git commit -m x") -> str:
        return hook_payload(command, self.r.dir)

    def test_non_commit_exits_zero_without_python(self):
        nopy = path_without_python()
        p = run_wrapper(hook_payload("ls -la && git status", self.r.dir), path=nopy)
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_missing_python_on_commit_blocks(self):
        p = run_wrapper(self.commit_payload(), path=path_without_python())
        self.assertEqual(p.returncode, 2)
        self.assertIn("python3 was not found", p.stderr)

    def test_dead_hash_blocks_with_file_line(self):
        self.r.write("README.md", "start\ncites deadbeefcafe0123\n")
        p = run_wrapper(self.commit_payload())
        self.assertEqual(p.returncode, 2)
        self.assertIn("README.md:2: dead commit hash deadbeefcafe0123", p.stderr)

    def test_dead_link_blocks(self):
        self.r.write("README.md", "start\nSee [results](docs/results.md).\n")
        p = run_wrapper(self.commit_payload())
        self.assertEqual(p.returncode, 2)
        self.assertIn("README.md:2: dead relative link docs/results.md", p.stderr)

    def test_dead_tag_blocks(self):
        self.r.write("README.md", "start\nfrozen as `prereg/nope`\n")
        p = run_wrapper(self.commit_payload())
        self.assertEqual(p.returncode, 2)
        self.assertIn("dead tag citation prereg/nope", p.stderr)

    def test_new_prereg_citing_its_own_tag_commits(self):
        # The pilot finding: /prereg's template names the file's own tag, which is created right after the commit.
        self.r.write("docs/prereg/sq_PREDICTION.md", "# sq\nThis commit gets the annotated tag `prereg/sq`.\n")
        p = run_wrapper(self.commit_payload())
        self.assertEqual(p.returncode, 0, p.stderr)
        plain = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check_doc_citations.py"),
                                "--include-untracked"], cwd=self.r.dir, capture_output=True, text=True, env=env())
        self.assertEqual(plain.returncode, 1, plain.stdout)
        self.assertIn("docs/prereg/sq_PREDICTION.md:2: prereg/sq", plain.stdout)

    def test_prereg_citing_another_missing_tag_still_blocks(self):
        self.r.write("docs/prereg/sq_PREDICTION.md", "# sq\nSee `prereg/cube`; this one is `prereg/sq`.\n")
        p = run_wrapper(self.commit_payload())
        self.assertEqual(p.returncode, 2)
        self.assertIn("docs/prereg/sq_PREDICTION.md:2: dead tag citation prereg/cube", p.stderr)
        self.assertNotIn("dead tag citation prereg/sq ", p.stderr)

    def test_untracked_new_doc_in_add_all_commit_blocks(self):
        self.r.write("notes/new.md", "[x](missing.md)\n")
        p = run_wrapper(self.commit_payload())
        self.assertEqual(p.returncode, 2)
        self.assertIn("notes/new.md:1:", p.stderr)

    def test_edited_prereg_blocks(self):
        self.r.write("docs/prereg/calc_PREDICTION.md", "# calc\n**Falsified by:** not 41.\n")
        p = run_wrapper(self.commit_payload())
        self.assertEqual(p.returncode, 2)
        self.assertIn("docs/prereg/calc_PREDICTION.md", p.stderr)

    def test_clean_commit_allows(self):
        self.r.write("README.md", "start\nmore\n")
        self.assertEqual(run_wrapper(self.commit_payload()).returncode, 0)

    def test_unparseable_commit_input_blocks(self):
        self.assertEqual(run_wrapper("this is not json but says git commit").returncode, 2)


if __name__ == "__main__":
    unittest.main()
