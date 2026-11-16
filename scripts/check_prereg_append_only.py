#!/usr/bin/env python3
"""Append-only guard for pre-registrations: nothing above the outcome is ever edited.

A pre-registration is frozen by an annotated `prereg/*` tag. From then on its bytes may only grow at the end: the
tagged bytes, and the bytes at HEAD, must both be a prefix of the new bytes. An insertion, deletion or edit anywhere
above the end is a violation. So is deleting the file, renaming it, or replacing it with bytes that are not a superset.

  check_prereg_append_only.py [--root DIR] [--tag TAG] [--staged] [--check-verdicts] [FILE ...]
      Check FILE (default: every file held by an annotated prereg/* tag) in the working tree, or in the index with
      --staged. --check-verdicts also checks the appended outcome: every HOLDS or FALSIFIED section carries a fenced
      block or a relative artifact link, and every NOT TESTED section carries `Reason:`.
      Exit 0 ok, 1 violation, 2 error.
  check_prereg_append_only.py [--root DIR] --new docs/prereg/<slug>_PREDICTION.md
      Collision check for /prereg: exit 1 if the file or the tag prereg/<slug> already exists. /prereg then stops;
      it never picks a different slug on its own.
  check_prereg_append_only.py --hook
      PreToolUse mode: read the hook JSON on stdin; on a `git commit`, check every frozen pre-registration of that
      repository in the working tree (the state the commit will be built from). Exit 2 to block, 0 to allow.

Reference tag for FILE: `prereg/<slug>` for docs/prereg/<slug>_PREDICTION.md when that tag holds it; otherwise the
newest annotated prereg/* tag whose commit holds FILE. A file that no tag holds is not frozen and passes with a note.
Standard library only; no network.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gitcmd import commit_dirs  # noqa: E402

PREREG_PATH = re.compile(r"^docs/prereg/(?P<slug>[A-Za-z0-9._-]+)_PREDICTION\.md$")
FROZEN_GLOBS = (re.compile(r"^docs/prereg/[^/]+_PREDICTION\.md$"), re.compile(r"^docs/PREREGISTRATION\.md$"))
VERDICT_HEAD = re.compile(r"^(#{2,4})\s.*\b(HOLDS|FALSIFIED|NOT TESTED)\b")


def git(root: str, *args: str, data: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", root, *args], input=data, capture_output=True)


def show(root: str, spec: str) -> bytes | None:
    p = git(root, "show", spec)
    return p.stdout if p.returncode == 0 else None


def annotated_prereg_tags(root: str) -> list[str]:
    """Annotated prereg/* tags, newest first; tags created in the same second are ordered by version, highest first
    (git: with several --sort keys, the last one is the primary key)."""
    p = git(root, "for-each-ref", "--sort=-version:refname", "--sort=-creatordate",
            "--format=%(refname:short)\t%(objecttype)", "refs/tags/prereg/")
    return [l.split("\t")[0] for l in p.stdout.decode().splitlines() if l.endswith("\ttag")]


def reference_tag(root: str, path: str, explicit: str | None = None) -> str | None:
    if explicit:
        return explicit
    tags = annotated_prereg_tags(root)
    m = PREREG_PATH.match(path)
    if m and ("prereg/" + m.group("slug")) in tags and show(root, "prereg/%s:%s" % (m.group("slug"), path)) is not None:
        return "prereg/" + m.group("slug")
    for t in tags:
        if git(root, "cat-file", "-e", "%s:%s" % (t, path)).returncode == 0:
            return t
    return None


def frozen_files(root: str) -> dict[str, str]:
    """Every pre-registration file held by an annotated prereg/* tag -> its reference tag."""
    out: dict[str, str] = {}
    for t in annotated_prereg_tags(root):
        names = git(root, "ls-tree", "-r", "--name-only", t).stdout.decode().splitlines()
        for n in names:
            if any(g.match(n) for g in FROZEN_GLOBS) and n not in out:
                out[n] = reference_tag(root, n) or t
    return out


def first_diff_line(old: bytes, new: bytes) -> int:
    o, n = old.decode("utf-8", "replace").split("\n"), new.decode("utf-8", "replace").split("\n")
    for i, (a, b) in enumerate(zip(o, n), 1):
        if a != b:
            return i
    return min(len(o), len(n)) + (0 if len(n) >= len(o) else 1)


def renamed_to(root: str, path: str) -> str | None:
    p = git(root, "diff", "--cached", "--name-status", "-M", "HEAD")
    for line in p.stdout.decode().splitlines():
        parts = line.split("\t")
        if parts and parts[0].startswith("R") and len(parts) == 3 and parts[1] == path:
            return parts[2]
    return None


def check_file(root: str, path: str, tag: str | None, staged: bool) -> list[str]:
    """Violations for one file, as `path:line: what` strings."""
    tag = reference_tag(root, path, tag)
    if tag is None:
        return []
    tagged = show(root, "%s:%s" % (tag, path))
    if tagged is None:
        return ["%s:1: the tag %s does not hold this file" % (path, tag)]
    if staged:
        new = show(root, ":" + path)
    else:
        full = os.path.join(root, path)
        new = open(full, "rb").read() if os.path.isfile(full) else None
    if new is None:
        moved = renamed_to(root, path)
        what = "renamed to %s" % moved if moved else "deleted"
        return ["%s:1: frozen by %s and %s; a pre-registration is never removed or moved" % (path, tag, what)]
    out = []
    if not new.startswith(tagged):
        out.append("%s:%d: differs from %s above the end of the frozen text (only appending is allowed)"
                   % (path, first_diff_line(tagged, new), tag))
    head = show(root, "HEAD:" + path)
    if head is not None and not new.startswith(head):
        out.append("%s:%d: differs from HEAD above its end (committed text, outcomes included, is append-only)"
                   % (path, first_diff_line(head, new)))
    return out


def check_verdicts(root: str, path: str, tag: str | None, staged: bool) -> list[str]:
    """In the text appended after the frozen prefix: HOLDS/FALSIFIED need pasted output or an artifact link, and
    NOT TESTED needs a reason."""
    tag = reference_tag(root, path, tag)
    tagged = show(root, "%s:%s" % (tag, path)) if tag else b""
    full = os.path.join(root, path)
    new = show(root, ":" + path) if staged else (open(full, "rb").read() if os.path.isfile(full) else b"")
    if not new.startswith(tagged or b""):
        return []
    appended = new[len(tagged or b""):].decode("utf-8", "replace")
    base_line = (tagged or b"").decode("utf-8", "replace").count("\n")
    lines = appended.split("\n")
    out = []
    for i, line in enumerate(lines):
        m = VERDICT_HEAD.match(line)
        if not m:
            continue
        level = len(m.group(1))
        body = []
        for nxt in lines[i + 1:]:
            h = re.match(r"^(#{1,6})\s", nxt)
            if h and len(h.group(1)) <= level:
                break
            body.append(nxt)
        text = "\n".join(body)
        where = "%s:%d" % (path, base_line + i + 1)
        if m.group(2) in ("HOLDS", "FALSIFIED"):
            fenced = re.search(r"^\s*(```|~~~)", text, re.M)
            link = re.search(r"\]\((?![a-z][a-z0-9+.-]*:)[^)#][^)]*\)", text)
            if not (fenced or link):
                out.append("%s: %s without pasted output (a fenced block) or an artifact link" % (where, m.group(2)))
        elif "Reason:" not in text:
            out.append("%s: NOT TESTED without a `Reason:` line" % where)
    return out


def new_collision(root: str, path: str) -> list[str]:
    m = PREREG_PATH.match(path)
    if not m:
        return ["%s: not a pre-registration path; expected docs/prereg/<slug>_PREDICTION.md" % path]
    slug, out = m.group("slug"), []
    if os.path.exists(os.path.join(root, path)) or show(root, ":" + path) is not None or show(root, "HEAD:" + path) is not None:
        out.append("%s already exists" % path)
    if git(root, "rev-parse", "-q", "--verify", "refs/tags/prereg/" + slug).returncode == 0:
        out.append("the tag prereg/%s already exists" % slug)
    return out


def toplevel(path: str) -> str | None:
    p = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def hook() -> int:
    try:
        data = json.load(sys.stdin)
        command = data["tool_input"]["command"]
        cwd = data.get("cwd") or os.getcwd()
    except Exception as e:  # noqa: BLE001 - any unreadable input fails closed
        print("evidence-gates: cannot read the hook input (%s); blocking the commit (fail closed)" % e, file=sys.stderr)
        return 2
    bad: list[str] = []
    for d in commit_dirs(command, cwd):
        root = toplevel(d)
        if root is None:
            continue
        for path, tag in sorted(frozen_files(root).items()):
            bad += check_file(root, path, tag, staged=False)
    if bad:
        print("evidence-gates: commit blocked. A pre-registration is append-only: nothing above its end is edited,"
              " and it is never deleted or moved.", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        print("Restore the frozen text and append your change below it instead.", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--root", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--check-verdicts", action="store_true")
    ap.add_argument("--new", default=None)
    ap.add_argument("--hook", action="store_true")
    a = ap.parse_args(argv)
    if a.hook:
        return hook()
    root = toplevel(a.root or os.getcwd())
    if root is None:
        print("check_prereg_append_only: not inside a git repository", file=sys.stderr)
        return 2
    if a.new:
        hits = new_collision(root, a.new)
        if hits:
            print("STOP: %s. A pre-registration is never overwritten, and no other slug is picked; ask the owner."
                  % "; ".join(hits))
            return 1
        print("OK: %s is free (no file, no tag)." % a.new)
        return 0
    targets = {f: a.tag for f in a.files} if a.files else frozen_files(root)
    if a.staged:
        for path, tag in frozen_files(root).items():
            targets.setdefault(path, tag)
    bad = []
    for path, tag in sorted(targets.items()):
        bad += check_file(root, path, tag, a.staged)
        if a.check_verdicts:
            bad += check_verdicts(root, path, tag, a.staged)
    if bad:
        print("Append-only violation(s):")
        for b in bad:
            print("  " + b)
        return 1
    print("OK: %d pre-registration file(s) are append-only against their tags and HEAD%s."
          % (len(targets), " and carry evidenced verdicts" if a.check_verdicts else ""))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # noqa: BLE001
        print("check_prereg_append_only: error: %s" % e, file=sys.stderr)
        sys.exit(2)
