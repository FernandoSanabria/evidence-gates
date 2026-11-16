"""Tests for the four skills: frontmatter, the identical standing-rules block, the /prereg collision rule, the /gate
STOP, and the absence of fence lines that would confuse the doc guard's fence detection."""
from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMANDS = ("prereg", "gate", "outcome")


def read(name: str) -> str:
    with open(os.path.join(ROOT, "skills", name, "SKILL.md"), encoding="utf-8") as fh:
        return fh.read()


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "no frontmatter"
    return dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)


def rules(text: str) -> str:
    m = re.search(r"<!-- standing-rules:begin -->\n(.*?)<!-- standing-rules:end -->", text, re.S)
    assert m, "no standing-rules block"
    return m.group(1)


class Skills(unittest.TestCase):
    def test_method_skill_is_model_invocable_and_short(self):
        text = read("evidence-gates")
        fm = frontmatter(text)
        self.assertEqual(fm["name"], "evidence-gates")
        self.assertIn("Use before running anything", fm["description"])
        self.assertNotIn("disable-model-invocation", fm)
        self.assertLessEqual(len(text.splitlines()), 160)

    def test_commands_are_user_triggered_with_hints_and_scoped_tools(self):
        for name in COMMANDS:
            fm = frontmatter(read(name))
            self.assertEqual(fm["name"], name)
            self.assertEqual(fm["disable-model-invocation"], "true", name)
            self.assertTrue(fm.get("argument-hint"), name)
            for tool in ("Bash(git *)", "Bash(python3 *)"):
                self.assertIn(tool, fm["allowed-tools"], name)

    def test_standing_rules_identical(self):
        blocks = {name: rules(read(name)) for name in COMMANDS}
        self.assertEqual(len(set(blocks.values())), 1, "standing rules differ between commands")
        self.assertIn("Nothing above `## Outcome`", blocks["prereg"])

    def test_prereg_collision_stops_and_never_picks_another_slug(self):
        text = read("prereg")
        self.assertIn('check_prereg_append_only.py" --new docs/prereg/<slug>_PREDICTION.md', text)
        self.assertIn("Never pick a different slug yourself", text)
        self.assertIn("never overwrite a file or a tag", text)

    def test_outcome_checks_before_and_after(self):
        text = read("outcome")
        before = text.index('check_prereg_append_only.py" <file>')
        after = text.index('check_prereg_append_only.py" --check-verdicts <file>')
        self.assertLess(before, after)
        self.assertIn("Do not commit", text)

    def test_gate_ends_with_stop_and_injects_raw_checks(self):
        text = read("gate")
        self.assertIn("a line that holds only `STOP`", text)
        self.assertIn('!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_doc_citations.py"; echo "exit=$?"`', text)

    def test_no_fence_lines_in_skills(self):
        for name in ("evidence-gates",) + COMMANDS:
            for line in read(name).splitlines():
                self.assertFalse(line.lstrip().startswith(("```", "~~~")), "%s: %s" % (name, line))


if __name__ == "__main__":
    unittest.main()
