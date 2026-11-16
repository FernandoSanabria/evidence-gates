"""Tests for scripts/gitcmd.py: which shell commands count as a `git commit`, and where."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from gitcmd import commit_dirs  # noqa: E402


class CommitDirs(unittest.TestCase):
    def test_plain_commit(self):
        self.assertEqual(commit_dirs("git commit -m x", "/r"), ["/r"])

    def test_compound_and_flags(self):
        self.assertEqual(commit_dirs("git add -A && git -c user.name=x commit -qm 'a b'", "/r"), ["/r"])
        self.assertEqual(commit_dirs("FOO=1 git --no-pager commit --amend", "/r"), ["/r"])

    def test_dash_c_directory(self):
        self.assertEqual(commit_dirs("git -C sub commit -m x", "/r"), ["/r/sub"])

    def test_not_a_commit(self):
        for c in ("git status", "git log --grep=commit", "echo commit", "git commit-tree abc", "git show HEAD"):
            self.assertEqual(commit_dirs(c, "/r"), [], c)

    def test_multiline_and_subshell(self):
        self.assertEqual(commit_dirs("printf x >> a\ngit add a && git commit -qm \"m\nCo-Authored-By: y\"", "/r"), ["/r"])

    def test_unparseable_segment_fails_toward_commit(self):
        self.assertEqual(commit_dirs("git commit -m 'unterminated", "/r"), ["/r"])


if __name__ == "__main__":
    unittest.main()
