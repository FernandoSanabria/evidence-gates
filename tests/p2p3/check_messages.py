#!/usr/bin/env python3
"""Assert that tests/p2p3/messages.txt holds the Appendix A messages of docs/PREREGISTRATION.md byte for byte.

Run from anywhere: `python3 -I tests/p2p3/check_messages.py`. Exit 0 when every registered message matches, 1 otherwise.
The PILOT* lines are the unregistered pilot's and are not checked against the registration.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "docs", "PREREGISTRATION.md")
MSG = os.path.join(ROOT, "tests", "p2p3", "messages.txt")


def registered() -> dict[str, str]:
    """Label -> verbatim message from the Appendix A table (the first backtick span of each row)."""
    out: dict[str, str] = {}
    for line in open(REG, encoding="utf-8"):
        m = re.match(r"^\| (T1b|T1|T2|T3a|T3b|T4|T5) \| (.*) \| [0-9, ]+ \|$", line.rstrip("\n"))
        if not m:
            continue
        label, cell = m.groups()
        spans = re.findall(r"`([^`]*)`", cell)
        out[label] = spans[0]
        if label == "T1":
            prefix = re.search(r"prefixed with `([^`]*)`", cell)
            out["T1_PREFIX+space"] = prefix.group(1) if prefix else ""
    return out


def ours() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in open(MSG, encoding="utf-8"):
        label, _, text = line.rstrip("\n").partition("\t")
        out[label] = text
    return out


def main() -> int:
    reg, msg = registered(), ours()
    wanted = ["T1", "T1b", "T2", "T3a", "T3b", "T4", "T5"]
    bad = 0
    for label in wanted:
        ok = reg.get(label) is not None and reg[label] == msg.get(label)
        bad += not ok
        print("%-4s %s" % (label, "matches the registration" if ok else "MISMATCH"))
    ok = reg.get("T1_PREFIX+space") == msg.get("T1_PREFIX", "") + " "
    bad += not ok
    print("T1 prefix %s" % ("matches the registration (with its trailing space)" if ok else "MISMATCH"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
