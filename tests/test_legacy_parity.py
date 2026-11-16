"""Differential tests: the new guard against the verbatim legacy script (tests/legacy_check_doc_citations.py, copied
from rag-pipeline at the G8 merge). Both run as subprocesses on the same fixture repositories. Green case: the two
`OK:` lines are byte-identical and both exit 0. Red case: the same `file:line: target` lines and both exit 1."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from helpers import Repo, env  # noqa: E402

LEGACY = os.path.join(HERE, "legacy_check_doc_citations.py")
NEW = os.path.join(os.path.dirname(HERE), "scripts", "check_doc_citations.py")
LEGACY_SHA256 = "e50b3c4ed1bcc8afeefc6c8eba8d7efc41faa1bcc2704262a5fb0aa076e324fc"


def run(script: str, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", script], cwd=cwd, capture_output=True, text=True, env=env())


class LegacyCopy(unittest.TestCase):
    def test_verbatim_sha256(self):
        with open(LEGACY, "rb") as fh:
            self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), LEGACY_SHA256)


class Parity(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Repo()
        self.r.write("README.md", "# fixture\n")
        c1 = self.r.commit("one")
        self.r.write("src/config.py", "x = 1\n")
        self.r.write("render.yaml", "a: b\n")
        c2 = self.r.commit("two")
        self.r.write("README.md", "# fixture\n\nBuilt at %s and %s; see [c](src/config.py), [r](render.yaml),\n"
                     "[blog](blog/post.md#part), [same](#here), [web](https://example.com/x), [m](mailto:a@b.c).\n"
                     "Also %s twice: %s.\n\n```bash\necho [fake](not-here.md) %s\n```\n"
                     % (c1[:7], c2, c1[:10], c1[:10], c2[:9]))
        self.r.write("blog/post.md", "Back to [readme](../README.md) and [eval](../eval/M.md#x). Commit %s.\n" % c2[:12])
        self.r.write("eval/M.md", "metrics, fp_c881474fd1 is not a hash, nor is a64 %s.\n" % ("a" * 64))
        self.r.commit("docs")

    def tearDown(self) -> None:
        self.r.close()

    def test_green_ok_lines_identical(self):
        old, new = run(LEGACY, self.r.dir), run(NEW, self.r.dir)
        self.assertEqual(old.returncode, 0, old.stdout)
        self.assertEqual(new.returncode, 0, new.stdout)
        self.assertEqual(old.stdout.splitlines()[:2], new.stdout.splitlines()[:2])

    def test_red_same_dead_lines(self):
        self.r.write("blog/post.md", self.r.read("blog/post.md") + "Dead deadbeefcafe0123 and [gone](../gone.md).\n")
        self.r.commit("break")
        old, new = run(LEGACY, self.r.dir), run(NEW, self.r.dir)
        self.assertEqual((old.returncode, new.returncode), (1, 1))
        pick = lambda out: [l for l in out.splitlines() if l.startswith("  ")]  # noqa: E731
        self.assertEqual(pick(old.stdout), pick(new.stdout))
        self.assertIn("  blog/post.md:2: deadbeefcafe0123", pick(new.stdout))


if __name__ == "__main__":
    unittest.main()
