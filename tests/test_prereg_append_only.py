"""Tests for scripts/check_prereg_append_only.py: append-only against the tag and HEAD, deletion, rename and
replacement, verdict evidence, the /prereg collision check, and the hook mode."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import Repo, hook_payload  # noqa: E402

FILE = "docs/prereg/calc_PREDICTION.md"
FROZEN = "# calc: pre-registration\n\n## P1\n**Hypothesis.** prints 42.\n\n**Falsified by:** any other output.\n"


class AppendOnly(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Repo()
        self.r.write(FILE, FROZEN)
        self.r.commit("prereg")
        self.r.tag("prereg/calc")

    def tearDown(self) -> None:
        self.r.close()

    def check(self, *args: str):
        return self.r.run("check_prereg_append_only.py", *args)

    def test_untouched_passes(self):
        self.assertEqual(self.check(FILE).returncode, 0)

    def test_pure_append_passes(self):
        self.r.write(FILE, FROZEN + "\n## Outcome (recorded 2026-11-16)\n### P1 — FALSIFIED\n```\n41\n```\n")
        self.assertEqual(self.check(FILE).returncode, 0)

    def test_insertion_above_heading_fails(self):
        self.r.write(FILE, FROZEN.replace("## P1\n", "## P1\nNote: inserted.\n"))
        p = self.check(FILE)
        self.assertEqual(p.returncode, 1)
        self.assertIn(FILE + ":4:", p.stdout)

    def test_deletion_above_heading_fails(self):
        self.r.write(FILE, FROZEN.replace("**Falsified by:** any other output.\n", ""))
        self.assertEqual(self.check(FILE).returncode, 1)

    def test_edit_above_heading_fails(self):
        self.r.write(FILE, FROZEN.replace("prints 42", "prints 41"))
        p = self.check(FILE)
        self.assertEqual(p.returncode, 1)
        self.assertIn("prereg/calc", p.stdout)

    def test_deleted_file_fails_working_tree_and_staged(self):
        os.remove(os.path.join(self.r.dir, FILE))
        self.assertEqual(self.check(FILE).returncode, 1)
        self.r.git("rm", "-q", "--cached", FILE)
        p = self.check("--staged")
        self.assertEqual(p.returncode, 1)
        self.assertIn("deleted", p.stdout)

    def test_renamed_file_fails_staged_and_hook(self):
        self.r.git("mv", FILE, "docs/prereg/other_PREDICTION.md")
        p = self.check("--staged")
        self.assertEqual(p.returncode, 1)
        self.assertIn("renamed to docs/prereg/other_PREDICTION.md", p.stdout)
        h = self.r.run("check_prereg_append_only.py", "--hook", stdin=hook_payload("git commit -m x", self.r.dir))
        self.assertEqual(h.returncode, 2)
        self.assertIn("renamed to", h.stderr)

    def test_replaced_by_non_superset_fails_staged(self):
        self.r.write(FILE, "# something else entirely\n")
        self.r.git("add", FILE)
        self.assertEqual(self.check("--staged").returncode, 1)

    def test_edit_of_committed_outcome_fails_against_head(self):
        self.r.write(FILE, FROZEN + "\n## Outcome (recorded 2026-11-16)\n### P1 — FALSIFIED\n```\n41\n```\n")
        self.r.commit("outcome")
        self.r.write(FILE, FROZEN + "\n## Outcome (recorded 2026-11-16)\n### P1 — HOLDS\n```\n42\n```\n")
        p = self.check(FILE)
        self.assertEqual(p.returncode, 1)
        self.assertIn("HEAD", p.stdout)

    def test_unfrozen_file_passes(self):
        self.r.write("docs/prereg/new_PREDICTION.md", "draft\n")
        self.assertEqual(self.check("docs/prereg/new_PREDICTION.md").returncode, 0)

    def test_reference_tag_newest_holding_tag_for_preregistration_md(self):
        self.r.write("docs/PREREGISTRATION.md", "v1 text\n")
        self.r.commit("v1")
        self.r.tag("prereg/v0.1")
        self.r.write("docs/PREREGISTRATION.md", "v2 text\n")
        self.r.commit("v2")
        self.r.tag("prereg/v0.2")
        self.r.write("docs/PREREGISTRATION.md", "v2 text\nappended\n")
        self.assertEqual(self.check("docs/PREREGISTRATION.md").returncode, 0)

    def test_check_verdicts(self):
        self.r.write(FILE, FROZEN + "\n## Outcome (recorded 2026-11-16)\n### P1 — FALSIFIED\nIt printed 41.\n")
        p = self.check("--check-verdicts", FILE)
        self.assertEqual(p.returncode, 1)
        self.assertIn("without pasted output", p.stdout)
        self.r.write(FILE, FROZEN + "\n## Outcome (recorded 2026-11-16)\n### P1 — NOT TESTED\nNo time.\n")
        self.assertIn("Reason:", self.check("--check-verdicts", FILE).stdout)
        self.r.write(FILE, FROZEN + "\n## Outcome (recorded 2026-11-16)\n### P1 — FALSIFIED\n```\n41\n```\n")
        self.assertEqual(self.check("--check-verdicts", FILE).returncode, 0)


class NewCollision(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Repo()
        self.r.write("README.md", "x\n")
        self.r.commit()

    def tearDown(self) -> None:
        self.r.close()

    def test_free_slug_passes(self):
        p = self.r.run("check_prereg_append_only.py", "--new", "docs/prereg/calc_PREDICTION.md")
        self.assertEqual(p.returncode, 0)

    def test_existing_file_stops(self):
        self.r.write("docs/prereg/calc_PREDICTION.md", "x\n")
        p = self.r.run("check_prereg_append_only.py", "--new", "docs/prereg/calc_PREDICTION.md")
        self.assertEqual(p.returncode, 1)
        self.assertIn("STOP", p.stdout)
        self.assertIn("no other slug is picked", p.stdout)

    def test_existing_tag_stops(self):
        self.r.tag("prereg/calc")
        p = self.r.run("check_prereg_append_only.py", "--new", "docs/prereg/calc_PREDICTION.md")
        self.assertEqual(p.returncode, 1)
        self.assertIn("prereg/calc already exists", p.stdout)


class HookMode(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Repo()
        self.r.write(FILE, FROZEN)
        self.r.commit()
        self.r.tag("prereg/calc")

    def tearDown(self) -> None:
        self.r.close()

    def hook(self, command: str):
        return self.r.run("check_prereg_append_only.py", "--hook", stdin=hook_payload(command, self.r.dir))

    def test_non_commit_allows(self):
        self.r.write(FILE, "tampered\n")
        self.assertEqual(self.hook("git status").returncode, 0)

    def test_commit_with_edit_blocks(self):
        self.r.write(FILE, FROZEN.replace("42", "41"))
        p = self.hook("git add -A && git commit -m 'fix the record'")
        self.assertEqual(p.returncode, 2)
        self.assertIn(FILE, p.stderr)

    def test_commit_with_append_allows(self):
        self.r.write(FILE, FROZEN + "\n## Outcome (recorded 2026-11-16)\n")
        self.assertEqual(self.hook("git commit -am outcome").returncode, 0)

    def test_deleted_file_blocks(self):
        os.remove(os.path.join(self.r.dir, FILE))
        self.assertEqual(self.hook("git commit -am gone").returncode, 2)

    def test_unparseable_input_blocks(self):
        p = self.r.run("check_prereg_append_only.py", "--hook", stdin="not json, but mentions commit")
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
