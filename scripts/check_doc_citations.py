#!/usr/bin/env python3
"""Doc-citation guard: a doc's evidence chain is machine-verified. Every cited commit hash must resolve to a commit,
every relative markdown link must point at a file that exists, and every cited prereg/* or evidence/* tag must exist.

Generalized from rag-pipeline's scripts/check_doc_citations.py (the copy in tests/legacy_check_doc_citations.py).
With no options, its two `OK:` lines, its counts and its exit codes match that script's. Everything new reports on
its own lines after those two.

Usage (run from the repository, or pass --root):
  check_doc_citations.py [--glob G ...] [--tag-ns prereg,evidence] [--require-durable] [--self-url URL ...]
  check_doc_citations.py --negative-proof     plant a dead hash in a temporary repository; exit 1 = went red
  check_doc_citations.py --hook               PreToolUse mode: stdin JSON; on a `git commit`, exit 2 to block
  In --hook mode a pre-registration's citation of its own tag (`prereg/<slug>` inside docs/prereg/<slug>_PREDICTION.md)
  does not block: /prereg creates that tag right after the commit, so it cannot exist yet. A plain run (and /gate)
  still reports it as dead until the tag exists.

What it checks:
- Commit hashes. Any run of 7-40 lowercase hex not flanked by [0-9A-Za-z_], on any line (fenced or not), counted once
  per line, resolved in one batched `git cat-file --batch-check` as `<token>^{commit}`.
- Relative links. Inline `[text](target)` only, fenced blocks skipped, path#fragment checked by its path, any URI scheme
  skipped, existence checked with os.path.exists against the checkout (case-sensitive on Linux, not on macOS).
- Exemptions. Only a token that does NOT resolve can be exempted, and only when every occurrence of it on its line sits
  inside one of four contexts. Each class is counted on its own line and left out of the checked count:
  actions-run-id (digits after /actions/runs/ or /job/), uuid (RFC 4122 8-4-4-4-12, any case), aws-case-id (9+
  digits within 40 characters after the word "case"), other-repo-url (inside an http(s) URL whose host/owner/repo is
  not one of this repository's remotes or --self-url). A URL to this repository's own remote is still checked.
- Tag citations (--tag-ns, default prereg,evidence; "" turns it off). A `prereg/<name>` or `evidence/<name>` written
  inside an inline code span (backticks), outside fenced blocks, is a citation and must exist as a tag. Prose such as
  "evidence/prereg", a repository name such as prereg/prereg, and paths such as docs/evidence/... are not citations.
- Durability. A cited commit should be reachable from main (refs/heads/main, else refs/remotes/origin/main) or from a
  tag in those namespaces; otherwise a squash-merge or a deleted branch can orphan it. Warning by default, a failure
  with --require-durable.

Exit codes: 0 green, 1 red (a dead hash, link or tag; or a non-durable hash with --require-durable), 2 error.
In --hook mode, 2 blocks the commit. Requires full history (fetch-depth 0 in CI). Standard library only; no network.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gitcmd import commit_dirs  # noqa: E402

HASH = re.compile(r"(?<![0-9A-Za-z_])[0-9a-f]{7,40}(?![0-9A-Za-z_])")
# Inline markdown link: capture the target inside `](...)`. Reference-style links are not supported.
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# A leading URI scheme (`http:`, `https:`, `mailto:`, ...) marks an absolute/remote target we skip.
SCHEME = re.compile(r"^[a-z][a-z0-9+.\-]*:")

ACTIONS = re.compile(r"/actions/runs/(\d+)|/job/(\d+)")
UUID = re.compile(r"(?<![0-9A-Za-z])[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}(?![0-9A-Za-z])")
CASE_WORD = re.compile(r"(?i)\bcases?\b")
LONG_DIGITS = re.compile(r"(?<!\d)\d{9,}(?!\d)")
URL = re.compile(r"https?://[^\s)<>\]\"'`]+")
TAG_CITE = re.compile(r"(?<![\w/.-])((?:%s)/[A-Za-z0-9._-]*[A-Za-z0-9_-])")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
OWN_PREREG = re.compile(r"(?:^|/)docs/prereg/([A-Za-z0-9._-]+)_PREDICTION\.md$")


def own_tag(path: str, tag: str) -> bool:
    """True when `tag` is the pre-registration tag of the file at `path` (prereg/<slug> for <slug>_PREDICTION.md)."""
    m = OWN_PREREG.search(path.replace(os.sep, "/"))
    return bool(m) and tag == "prereg/" + m.group(1)
CLASSES = ("actions-run-id", "uuid", "aws-case-id", "other-repo-url")


def git(*args: str, data: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], input=data, capture_output=True, text=True)


def doc_files(globs: list[str], include_untracked: bool) -> list[str]:
    args = ["ls-files"] + (["--cached", "--others", "--exclude-standard"] if include_untracked else []) + ["--", *globs]
    out = git(*args)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return sorted(set(out.stdout.split()), key=out.stdout.split().index)


def iter_links(text: str):
    """Yield (lineno, target) for each inline [text](target) link, skipping fenced code blocks.

    Line numbers are preserved (fenced lines are skipped in place, not deleted) so a dead link reports its true
    file:line. Fence state toggles on any line whose first non-space run is ``` or ~~~; this assumes balanced fences.
    """
    in_fence = False
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in LINK.finditer(line):
            yield i, m.group(1)


def _target_path(target: str) -> str:
    """The path portion of a link target, with any #fragment removed ('' for a pure #anchor)."""
    return target.strip().split("#", 1)[0]


def is_relative_target(target: str) -> bool:
    """True if `target` is a relative file path this guard should validate: not a pure #anchor and not a URI."""
    path = _target_path(target)
    return bool(path) and not SCHEME.match(path.lower())


def relative_target_dead(target: str, base_dir: str) -> bool:
    """True iff `target` is a relative link whose file does not exist under `base_dir`."""
    if not is_relative_target(target):
        return False
    resolved = os.path.normpath(os.path.join(base_dir, _target_path(target)))
    return not os.path.exists(resolved)


def resolve_all(tokens: set[str]) -> dict[str, str | None]:
    """token -> full commit id, or None when `<token>^{commit}` does not resolve (missing or ambiguous)."""
    order = sorted(tokens)
    if not order:
        return {}
    p = git("cat-file", "--batch-check", data="".join(t + "^{commit}\n" for t in order))
    lines = p.stdout.splitlines()
    out: dict[str, str | None] = {}
    for tok, line in zip(order, lines):
        parts = line.split()
        out[tok] = parts[0] if len(parts) == 3 and parts[1] == "commit" else None
    return out


def repo_id(url: str) -> str | None:
    """host/owner/repo, lowercased, for an http(s) or scp-style git URL; None when there is no owner/repo."""
    m = re.match(r"^(?:https?://|ssh://)?(?:[^@/]+@)?([^/:]+)[/:]([^/]+)/([^/#?]+)", url.strip())
    if not m:
        return None
    repo = m.group(3)
    repo = repo[:-4] if repo.endswith(".git") else repo
    return "/".join(x.lower() for x in (m.group(1), m.group(2), repo))


def self_ids(self_urls: list[str]) -> set[str]:
    ids = {repo_id(u) for u in self_urls}
    for line in git("remote", "-v").stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            ids.add(repo_id(parts[1]))
    return {i for i in ids if i}


def context_spans(line: str, mine: set[str]) -> list[tuple[int, int, str]]:
    spans = []
    for m in ACTIONS.finditer(line):
        g = 1 if m.group(1) else 2
        spans.append((m.start(g), m.end(g), "actions-run-id"))
    for m in UUID.finditer(line):
        spans.append((m.start(), m.end(), "uuid"))
    for m in CASE_WORD.finditer(line):
        window = line[m.end(): m.end() + 40]
        for d in LONG_DIGITS.finditer(window):
            spans.append((m.end() + d.start(), m.end() + d.end(), "aws-case-id"))
    for m in URL.finditer(line):
        if repo_id(m.group(0)) not in mine:
            spans.append((m.start(), m.end(), "other-repo-url"))
    return spans


def exempt_class(line: str, token: str, mine: set[str]) -> str | None:
    spans = context_spans(line, mine)
    classes = []
    for m in re.finditer(r"(?<![0-9A-Za-z_])%s(?![0-9A-Za-z_])" % re.escape(token), line):
        inside = [c for (a, b, c) in spans if a <= m.start() and m.end() <= b]
        if not inside:
            return None
        classes.append(inside[0])
    return classes[0] if classes else None


def reachable_roots(namespaces: list[str]) -> list[str]:
    roots = []
    for ref in ("refs/heads/main", "refs/remotes/origin/main"):
        if git("rev-parse", "-q", "--verify", ref).returncode == 0:
            roots.append(ref)
            break
    for ns in namespaces:
        roots += git("for-each-ref", "--format=%(refname)", "refs/tags/%s/" % ns).stdout.split()
    return roots


def check(globs: list[str], include_untracked: bool, namespaces: list[str], self_urls: list[str]) -> dict:
    files = doc_files(globs, include_untracked)
    mine = self_ids(self_urls)
    entries = []  # (file, lineno, token, line)
    links_checked, dead_links = 0, []
    tag_cites = []  # (file, lineno, tag)
    tag_re = re.compile(TAG_CITE.pattern % "|".join(map(re.escape, namespaces))) if namespaces else None
    for f in files:
        text = open(f, encoding="utf-8").read()
        base = os.path.dirname(f)
        in_fence = False
        for i, line in enumerate(text.splitlines(), 1):
            for sha in sorted(set(HASH.findall(line))):
                entries.append((f, i, sha, line))
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if tag_re and not in_fence:
                for span in CODE_SPAN.finditer(line):
                    for m in tag_re.finditer(span.group(2)):
                        tag_cites.append((f, i, m.group(1)))
        for i, target in iter_links(text):
            if not is_relative_target(target):
                continue
            links_checked += 1
            if relative_target_dead(target, base):
                dead_links.append((f, i, target))
    resolved = resolve_all({sha for _, _, sha, _ in entries})
    dead_hashes, exempt, cited_commits = [], {c: 0 for c in CLASSES}, {}
    for f, i, sha, line in entries:
        if resolved.get(sha):
            cited_commits.setdefault(resolved[sha], []).append((f, i, sha))
            continue
        cls = exempt_class(line, sha, mine)
        if cls:
            exempt[cls] += 1
        else:
            dead_hashes.append((f, i, sha))
    tags = set(git("for-each-ref", "--format=%(refname:short)", "refs/tags").stdout.split())
    dead_tags = [(f, i, t) for f, i, t in tag_cites if t not in tags]
    non_durable = []
    roots = reachable_roots(namespaces)
    durability_checked = bool(roots) and any(r.endswith("/main") for r in roots)
    if cited_commits and durability_checked:
        reach = set(git("rev-list", *roots).stdout.split())
        for oid, uses in cited_commits.items():
            if oid not in reach:
                non_durable += uses
    return {"files": files, "hashes_checked": len(entries) - sum(exempt.values()), "dead_hashes": dead_hashes,
            "links_checked": links_checked, "dead_links": dead_links, "exempt": exempt,
            "tags_checked": len(tag_cites), "dead_tags": dead_tags, "namespaces": namespaces,
            "non_durable": sorted(non_durable), "durability_checked": durability_checked}


def report(r: dict, require_durable: bool, out=sys.stdout) -> int:
    n = len(r["files"])
    if r["dead_hashes"]:
        print("Dead commit-hash citation(s) — these do not resolve to a commit in history:", file=out)
        for f, i, sha in r["dead_hashes"]:
            print(f"  {f}:{i}: {sha}", file=out)
        print("\nIf commit hashes were rewritten, remap the citations old->new.", file=out)
    else:
        print(f"OK: all {r['hashes_checked']} cited commit hashes across {n} tracked docs resolve.", file=out)
    if r["dead_links"]:
        print("\nDead relative link(s) — these targets do not exist in the checkout:", file=out)
        for f, i, target in r["dead_links"]:
            print(f"  {f}:{i}: {target}", file=out)
        print("\nFix the link or the target. Illustrative link syntax belongs in a fenced code block "
              "(which this check skips), not an inline `code` span.", file=out)
    else:
        print(f"OK: all {r['links_checked']} relative markdown links across {n} tracked docs resolve.", file=out)
    e = r["exempt"]
    print("Exempt (do not resolve, and sit only inside an exempt context): " +
          ", ".join(f"{c} {e[c]}" for c in CLASSES) + ".", file=out)
    if r["namespaces"]:
        if r["dead_tags"]:
            print("Dead tag citation(s) — these tags do not exist:", file=out)
            for f, i, t in r["dead_tags"]:
                print(f"  {f}:{i}: {t}", file=out)
        else:
            print(f"OK: all {r['tags_checked']} cited {'/'.join(r['namespaces'])} tags exist.", file=out)
    if not r["durability_checked"]:
        print("Durability: not checked (no main branch found).", file=out)
    elif r["non_durable"]:
        label = "Not durable" if require_durable else "Warning, not durable"
        print(f"{label}: cited commit(s) reachable from neither main nor a {'/'.join(r['namespaces']) or 'namespaced'} "
              "tag; a squash-merge or a deleted branch can orphan them. Tag them or cite the merged commit:", file=out)
        for f, i, sha in r["non_durable"]:
            print(f"  {f}:{i}: {sha}", file=out)
    else:
        print("Durability: every cited commit is reachable from main or a namespaced tag.", file=out)
    red = r["dead_hashes"] or r["dead_links"] or r["dead_tags"] or (require_durable and r["non_durable"])
    return 1 if red else 0


def negative_proof() -> int:
    tmp = tempfile.mkdtemp(prefix="eg-negative-proof-")
    planted = secrets.token_hex(20)
    try:
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        run = lambda *a: subprocess.run(["git", "-C", tmp, *a], capture_output=True, env=env, check=True)  # noqa: E731
        run("init", "-q", "-b", "main")
        with open(os.path.join(tmp, "PROOF.md"), "w", encoding="utf-8") as fh:
            fh.write("This doc cites commit %s, which does not exist.\n" % planted)
        run("add", "-A")
        run("-c", "user.name=proof", "-c", "user.email=proof", "commit", "-q", "-m", "plant a dead hash")
        here = os.getcwd()
        os.chdir(tmp)
        try:
            r = check(["*.md"], False, [], [])
        finally:
            os.chdir(here)
        went_red = any(sha == planted for _, _, sha in r["dead_hashes"])
        if went_red:
            print("NEGATIVE PROOF: the guard went red on the planted dead hash %s (PROOF.md:1). Exit 1, as required." % planted)
            return 1
        print("NEGATIVE PROOF BROKEN: the guard stayed green on a planted dead hash %s." % planted)
        return 0
    except Exception as ex:  # noqa: BLE001
        print("negative proof error: %s" % ex, file=sys.stderr)
        return 2
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def hook(namespaces: list[str]) -> int:
    try:
        data = json.load(sys.stdin)
        command = data["tool_input"]["command"]
        cwd = data.get("cwd") or os.getcwd()
    except Exception as ex:  # noqa: BLE001 - unreadable input fails closed
        print("evidence-gates: cannot read the hook input (%s); blocking the commit (fail closed)" % ex, file=sys.stderr)
        return 2
    blocked = False
    for d in commit_dirs(command, cwd):
        top = git("-C", d, "rev-parse", "--show-toplevel")
        if top.returncode != 0:
            continue
        here = os.getcwd()
        os.chdir(top.stdout.strip())
        try:
            r = check(["*.md"], True, namespaces, [])
        finally:
            os.chdir(here)
        bad = ([f"{f}:{i}: dead commit hash {s} (does not resolve)" for f, i, s in r["dead_hashes"]] +
               [f"{f}:{i}: dead relative link {t} (no such file)" for f, i, t in r["dead_links"]] +
               [f"{f}:{i}: dead tag citation {t} (no such tag)" for f, i, t in r["dead_tags"] if not own_tag(f, t)])
        if bad:
            blocked = True
            print("evidence-gates: commit blocked. The docs cite things that do not exist:", file=sys.stderr)
            for b in bad:
                print("  " + b, file=sys.stderr)
            print("Fix the doc or create the target, then commit again. Do not bypass this check.", file=sys.stderr)
    return 2 if blocked else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=None)
    ap.add_argument("--glob", action="append", default=None)
    ap.add_argument("--tag-ns", default="prereg,evidence")
    ap.add_argument("--require-durable", action="store_true")
    ap.add_argument("--self-url", action="append", default=[])
    ap.add_argument("--include-untracked", action="store_true")
    ap.add_argument("--negative-proof", action="store_true")
    ap.add_argument("--hook", action="store_true")
    a = ap.parse_args(argv)
    namespaces = [n for n in a.tag_ns.split(",") if n]
    if a.negative_proof:
        return negative_proof()
    if a.hook:
        return hook(namespaces)
    if a.root:
        os.chdir(a.root)
    r = check(a.glob or ["*.md"], a.include_untracked, namespaces, a.self_url)
    return report(r, a.require_durable)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as ex:  # noqa: BLE001
        print("check_doc_citations: error: %s" % ex, file=sys.stderr)
        sys.exit(2)
