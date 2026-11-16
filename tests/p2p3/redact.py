#!/usr/bin/env python3
"""Redact token values in one evidence file and log the redaction in docs/evidence/REDACTIONS.md.

  redact.py <raw-file> <redacted-out> <repo-path-of-out> <redactions.md>

Replaces the value of any NAME=value whose NAME ends in MESSAGING_TOKEN or OAUTH_TOKEN with [REDACTED-TOKEN], and
any `Bearer <16+ token characters>` with `Bearer [REDACTED-TOKEN]`. A value ends at whitespace, a quote, a backslash
(so a JSON `\\n` escape ends it) or a comma. The raw file is never modified and must live outside the repository.
Appends one row per file: path, lines, count, sha256 of the raw file and of the redacted file. Prints the same row.
"""
from __future__ import annotations

import hashlib
import re
import sys

PATTERNS = [
    (re.compile(r"((?:[A-Z_]*MESSAGING_TOKEN|[A-Z_]*OAUTH_TOKEN)=)[^\s\"'\\,]+"), r"\1[REDACTED-TOKEN]"),
    (re.compile(r"(Bearer )[A-Za-z0-9._~+/-]{16,}=*"), r"\1[REDACTED-TOKEN]"),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main(raw: str, out: str, repo_path: str, log: str) -> int:
    data = open(raw, "rb").read()
    text = data.decode("utf-8")
    lines_out, hit_lines, count = [], [], 0
    for i, line in enumerate(text.split("\n"), 1):
        n_line = 0
        for pat, rep in PATTERNS:
            line, n = pat.subn(rep, line)
            n_line += n
        if n_line:
            hit_lines.append(i)
            count += n_line
        lines_out.append(line)
    redacted = "\n".join(lines_out).encode("utf-8")
    open(out, "wb").write(redacted)
    row = "| `%s` | %s | %d | `%s` | `%s` | [REDACTED-TOKEN] |" % (
        repo_path, ", ".join(map(str, hit_lines)) or "none", count, sha(data), sha(redacted))
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(row + "\n")
    print(row)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:5]))
