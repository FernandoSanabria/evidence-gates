"""Tests for scripts/check_doc_citations.py: the legacy link helpers, hashes, exemptions (with negative controls),
tag citations, durability, --glob, --negative-proof and --hook."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
from helpers import Repo, hook_payload  # noqa: E402
from check_doc_citations import is_relative_target, iter_links, relative_target_dead  # noqa: E402


class LinkHelpers(unittest.TestCase):
    """Ported from rag-pipeline's tests for the relative-link helpers."""

    def test_inline_link_extracted_with_lineno(self):
        self.assertEqual(list(iter_links("intro\nsee [b](a.md) here\n")), [(2, "a.md")])

    def test_fenced_links_ignored(self):
        text = "before [r](real.md)\n```bash\necho [x](fake.md)\n```\nafter [y](also.md)\n~~~\n[z](f2.md)\n~~~\n"
        self.assertEqual([t for _, t in iter_links(text)], ["real.md", "also.md"])

    def test_classification(self):
        self.assertFalse(is_relative_target("#anchor"))
        self.assertFalse(is_relative_target("https://example.com/x"))
        self.assertFalse(is_relative_target("mailto:me@example.com"))
        self.assertTrue(is_relative_target("../eval/M.md"))
        self.assertTrue(is_relative_target("render.yaml"))
        self.assertTrue(is_relative_target("sibling.md#section"))

    def test_resolution(self):
        d = tempfile.mkdtemp()
        open(os.path.join(d, "t.md"), "w").close()
        os.makedirs(os.path.join(d, "eval"))
        open(os.path.join(d, "eval", "M.md"), "w").close()
        os.makedirs(os.path.join(d, "blog"))
        self.assertFalse(relative_target_dead("t.md", d))
        self.assertTrue(relative_target_dead("nope.md", d))
        self.assertFalse(relative_target_dead("../eval/M.md", os.path.join(d, "blog")))
        self.assertFalse(relative_target_dead("t.md#a", d))
        self.assertTrue(relative_target_dead("gone.md#a", d))
        self.assertFalse(relative_target_dead("#same", d))
        self.assertFalse(relative_target_dead("https://example.com/missing", d))
        self.assertTrue(relative_target_dead("src/config.py", d))


class Guard(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Repo()
        self.r.write("README.md", "start\n")
        self.c1 = self.r.commit("first")
        self.short = self.c1[:7]

    def tearDown(self) -> None:
        self.r.close()

    def guard(self, *args: str):
        return self.r.run("check_doc_citations.py", *args)

    def doc(self, text: str) -> None:
        self.r.write("docs/note.md", text)
        self.r.commit("doc")

    def test_resolving_hash_and_link_green(self):
        self.r.write("docs/target.md", "t\n")
        self.doc("cites %s and [t](target.md)\n" % self.short)
        p = self.guard()
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("OK: all 1 cited commit hashes across 3 tracked docs resolve.", p.stdout)
        self.assertIn("OK: all 1 relative markdown links across 3 tracked docs resolve.", p.stdout)

    def test_dead_hash_red_with_file_line(self):
        self.doc("line one\ncites deadbeefcafe0123 here\n")
        p = self.guard()
        self.assertEqual(p.returncode, 1)
        self.assertIn("  docs/note.md:2: deadbeefcafe0123", p.stdout)

    def test_dead_link_red(self):
        self.doc("see [r](results.md)\n")
        p = self.guard()
        self.assertEqual(p.returncode, 1)
        self.assertIn("  docs/note.md:1: results.md", p.stdout)

    def test_exempt_actions_run_id(self):
        self.doc("run https://github.com/o/r/actions/runs/12345678901/job/98765432101\n")
        p = self.guard()
        self.assertEqual(p.returncode, 0, p.stdout)

    def test_exempt_run_id_without_url_is_not_exempt(self):
        self.doc("run 12345678901 passed\n")
        self.assertEqual(self.guard().returncode, 1)

    def test_exempt_uuid_any_case(self):
        self.doc("thread 3f2504e0-4f89-11d3-9a0c-0305e82c3301 and 3F2504E0-4F89-11D3-9A0C-0305E82C3302\n")
        p = self.guard()
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("uuid 2", p.stdout)

    def test_exempt_aws_case_id(self):
        self.doc("AWS support case 177000000000001 was routed to sales\n")
        p = self.guard()
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("aws-case-id 1", p.stdout)

    def test_case_word_too_far_is_not_exempt(self):
        self.doc("case: " + "x" * 50 + " 177000000000001\n")
        self.assertEqual(self.guard().returncode, 1)

    def test_exempt_other_repo_url(self):
        self.doc("pinned at [c](https://github.com/someone/else/commit/92cff85)\n")
        p = self.guard()
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("other-repo-url 1", p.stdout)

    def test_negative_control_own_remote_url_still_checked(self):
        self.r.git("remote", "add", "origin", "git@github.com:me/this-repo.git")
        self.doc("see https://github.com/me/this-repo/commit/deadbeefcafe0123\n")
        p = self.guard()
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("deadbeefcafe0123", p.stdout)

    def test_negative_control_self_url_flag(self):
        self.doc("see https://github.com/me/this-repo/commit/deadbeefcafe0123\n")
        self.assertEqual(self.guard().returncode, 0)
        self.assertEqual(self.guard("--self-url", "https://github.com/me/this-repo").returncode, 1)

    def test_negative_control_dead_hash_beside_exempt_form(self):
        self.doc("thread 3f2504e0-4f89-11d3-9a0c-0305e82c3301 and commit deadbeefcafe0123\n")
        p = self.guard()
        self.assertEqual(p.returncode, 1)
        self.assertIn("deadbeefcafe0123", p.stdout)

    def test_negative_control_all_digit_token_is_a_hash(self):
        self.doc("value 12345678 here\n")
        p = self.guard()
        self.assertEqual(p.returncode, 1)
        self.assertIn("docs/note.md:1: 12345678", p.stdout)

    def test_negative_control_resolving_token_never_exempted(self):
        self.doc("see https://github.com/someone/else/commit/%s\n" % self.short)
        p = self.guard()
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("other-repo-url 0", p.stdout)
        self.assertIn("OK: all 1 cited commit hashes", p.stdout)

    def test_tag_citations(self):
        self.r.tag("prereg/calc")
        self.doc("frozen as `prereg/calc`; evidence in `docs/evidence/HOURS.md` and `docs/prereg/x_PREDICTION.md`\n")
        p = self.guard()
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("OK: all 1 cited prereg/evidence tags exist.", p.stdout)
        self.doc("see `evidence/missing-build`.\n")
        p = self.guard()
        self.assertEqual(p.returncode, 1)
        self.assertIn("docs/note.md:1: evidence/missing-build", p.stdout)
        self.assertEqual(self.guard("--tag-ns", "").returncode, 0)

    def test_tag_shapes_outside_code_spans_are_not_citations(self):
        # The dogfood finding: prose "evidence/prereg" and the repository name prereg/prereg in a pasted search result.
        self.doc("names containing evidence/prereg\n"
                 "```console\n"
                 "prereg/prereg\t1\t2023-04-26T09:11:47Z\n"
                 "`prereg/in-a-fence`\n"
                 "```\n"
                 "after the fence: `git tag -a prereg/dead -m x`\n")
        p = self.guard()
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("docs/note.md:6: prereg/dead", p.stdout)
        for absent in ("evidence/prereg", "prereg/prereg", "prereg/in-a-fence"):
            self.assertNotIn(absent, p.stdout)

    def test_durability(self):
        self.r.git("checkout", "-q", "-b", "feat")
        self.r.write("x.txt", "x\n")
        side = self.r.commit("side")
        self.r.git("checkout", "-q", "main")
        self.doc("cites %s\n" % side[:7])
        p = self.guard()
        self.assertEqual(p.returncode, 0)
        self.assertIn("Warning, not durable", p.stdout)
        self.assertEqual(self.guard("--require-durable").returncode, 1)
        self.r.tag("evidence/side", side)
        self.assertEqual(self.guard("--require-durable").returncode, 0)

    def test_glob(self):
        self.r.write("notes.txt", "cites deadbeefcafe0123\n")
        self.r.commit("txt")
        self.assertEqual(self.guard().returncode, 0)
        self.assertEqual(self.guard("--glob", "*.txt").returncode, 1)

    def test_negative_proof_exits_one(self):
        p = self.guard("--negative-proof")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("went red", p.stdout)


class HookMode(unittest.TestCase):
    def setUp(self) -> None:
        self.r = Repo()
        self.r.write("README.md", "start\n")
        self.r.commit()

    def tearDown(self) -> None:
        self.r.close()

    def hook(self, command: str, stdin: str | None = None):
        return self.r.run("check_doc_citations.py", "--hook", stdin=stdin or hook_payload(command, self.r.dir))

    def test_non_commit_allows(self):
        self.r.write("README.md", "[x](missing.md)\n")
        self.assertEqual(self.hook("git status").returncode, 0)

    def test_commit_with_dead_link_blocks(self):
        self.r.write("README.md", "start\n[r](docs/results.md)\n")
        p = self.hook("git add README.md && git commit -m link")
        self.assertEqual(p.returncode, 2)
        self.assertIn("README.md:2: dead relative link docs/results.md", p.stderr)

    def test_untracked_new_doc_in_add_all_commit_blocks(self):
        self.r.write("docs/new.md", "cites deadbeefcafe0123\n")
        p = self.hook("git add -A && git commit -m new")
        self.assertEqual(p.returncode, 2)
        self.assertIn("docs/new.md:1: dead commit hash deadbeefcafe0123", p.stderr)

    def test_dash_c_commit(self):
        sub = Repo()
        try:
            sub.write("a.md", "[x](nope.md)\n")
            sub.commit()
            p = self.r.run("check_doc_citations.py", "--hook", stdin=hook_payload("git -C %s commit -m x" % sub.dir, "/"))
            self.assertEqual(p.returncode, 2)
        finally:
            sub.close()

    def test_unparseable_blocks(self):
        self.assertEqual(self.hook("", stdin="{not json} commit").returncode, 2)

    def test_clean_commit_allows(self):
        self.r.write("README.md", "start\nfine\n")
        self.assertEqual(self.hook("git commit -am ok").returncode, 0)


if __name__ == "__main__":
    unittest.main()
