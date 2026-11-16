"""The README's install command is the one the pre-registration registered for P1, byte for byte.

Owner's ruling (2026-11-16): P1 ran the command as quoted in the pre-registration, so the README must state that same
string and must not drift from it. The two-command fallback (run once at P1, unregistered) is checked separately.
"""
from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTERED = "claude plugin install evidence-gates --marketplace FernandoSanabria/evidence-gates"
ONE_LINE = re.compile(r"claude plugin install [A-Za-z0-9._@/-]+ --marketplace [A-Za-z0-9._/-]+")


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def registered() -> str:
    """The backticked install command on the P1 Hypothesis line of the pre-registration."""
    m = re.search(r"^## P1 — Install\n\*\*Hypothesis\.\*\*[^\n]*?`(claude plugin install [^`]+)`",
                  read("docs/PREREGISTRATION.md"), re.M)
    assert m, "no install command on the P1 Hypothesis line"
    return m.group(1)


class Readme(unittest.TestCase):
    def test_registered_string_is_pinned(self):
        self.assertEqual(registered(), REGISTERED)

    def test_readme_one_line_install_is_the_registered_string(self):
        readme = read("README.md")
        self.assertIn("\n" + REGISTERED + "\n", readme, "the command must stand on its own line")
        found = ONE_LINE.findall(readme)
        self.assertTrue(found)
        self.assertEqual(set(found), {REGISTERED})

    def test_two_command_fallback_is_the_one_p1_ran(self):
        readme = read("README.md")
        self.assertIn("claude plugin marketplace add FernandoSanabria/evidence-gates", readme)
        self.assertIn("claude plugin install evidence-gates@evidence-gates", readme)


if __name__ == "__main__":
    unittest.main()
