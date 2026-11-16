#!/usr/bin/env python3
"""Spend ledger for docs/evidence/COST.md.

  ledger.py sum LEDGER
      Print the running sum in USD (0.000000 when the table has no rows).
  ledger.py add LEDGER RUN SESSION OUTFILE RC [NOTE]
      Read the result event from OUTFILE (a `--output-format json` object or a stream-json transcript), append
      one row with its total_cost_usd and the new running sum, and print `cost=… sum=… num_turns=… is_error=…`.
      Exit 5 when OUTFILE holds no result event (the row is still written, with cost n/a).

Standard library only. Reads nothing but OUTFILE and LEDGER.
"""
from __future__ import annotations

import datetime
import json
import sys


def rows(ledger: str) -> list[list[str]]:
    out = []
    for line in open(ledger, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells and cells[0].isdigit():
            out.append(cells)
    return out


def running_sum(ledger: str) -> float:
    r = rows(ledger)
    return float(r[-1][5]) if r else 0.0


def result_event(outfile: str) -> dict | None:
    text = open(outfile, encoding="utf-8", errors="replace").read()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and obj.get("type") == "result":
            return obj
        if isinstance(obj, list):
            found = [o for o in obj if isinstance(o, dict) and o.get("type") == "result"]
            return found[-1] if found else None
    except ValueError:
        pass
    found = None
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if obj.get("type") == "result":
            found = obj
    return found


def add(ledger: str, run: str, session: str, outfile: str, rc: str, note: str = "") -> int:
    ev = result_event(outfile)
    n = len(rows(ledger)) + 1
    prev = running_sum(ledger)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if ev is None:
        cost_s, total, turns = "n/a", prev, "n/a"
        note = (note + "; " if note else "") + "no result event (rc=%s)" % rc
    else:
        cost = float(ev.get("total_cost_usd") or 0.0)
        total = prev + cost
        cost_s, turns = "%.6f" % cost, str(ev.get("num_turns", "n/a"))
        if ev.get("is_error"):
            note = (note + "; " if note else "") + "is_error=true (%s)" % ev.get("subtype", "")
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write("| %d | %s | %s | %s | %s | %.6f | %s | %s |\n" % (n, stamp, run, session, cost_s, total, turns, note))
    print("cost=%s sum=%.6f num_turns=%s is_error=%s" % (cost_s, total, turns, (ev or {}).get("is_error")))
    return 5 if ev is None else 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "sum":
        print("%.6f" % running_sum(argv[1]))
        return 0
    if len(argv) >= 6 and argv[0] == "add":
        return add(*argv[1:7])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
