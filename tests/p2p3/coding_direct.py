#!/usr/bin/env python3
"""Write docs/evidence/p2/coding-direct.json: the direct checks of P2 row 1, P2 (i), P2 (iii) and README row 2's
plugin-arm byte clause against the registered text, each with its command and raw output (owner's Ruling 2,
2026-11-16). Read-only on the run's snapshots. code_rows.py and coding.json are not touched."""
import json
import re
import subprocess
import sys

REPO, SNAP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
F = "docs/prereg/calc-py-prints-42_PREDICTION.md"
TAG = "prereg/calc-py-prints-42"


def sh(command: str, cwd: str) -> dict:
    p = subprocess.run(["/bin/bash", "-c", command], cwd=cwd, capture_output=True, text=True)
    return {"cwd": cwd.replace(SNAP, "<run>/snap"), "command": command, "exit": p.returncode,
            "output": p.stdout + p.stderr}


checks = []
t1, t2 = SNAP + "/T1", SNAP + "/T2"
pred = subprocess.run(["git", "-C", t1, "rev-parse", "--short", TAG + "^{commit}"], capture_output=True,
                      text=True).stdout.strip()
checks.append({"for": "row 1 and P2 (i): the commits in T1, with commit times",
               **sh("git log --all --format='%h %cI %s'", t1)})
checks.append({"for": "row 1 and P2 (i): the pre-registration commit's tree states 42 outside calc.py",
               **sh("git grep -l -w 42 %s -- . ':!calc.py'" % pred, t1)})
checks.append({"for": "P2 (i): a falsifier for every prediction in the committed file",
               **sh("git show %s:%s | grep -n -E 'Falsified by|^## P'" % (pred, F), t1)})

# Stream order: every tool call in T1, whether it executes calc.py (the command itself, not text inside a heredoc
# body) and whether it commits.
calls = []
for line in open(REPO + "/docs/evidence/p2/T1.jsonl", encoding="utf-8"):
    if not line.startswith("{"):
        continue
    ev = json.loads(line)
    if ev.get("type") == "assistant":
        for c in ev["message"]["content"]:
            if c.get("type") == "tool_use":
                calls.append(c.get("input", {}).get("command") or "(%s %s)" % (c["name"], c.get("input", {}).get("file_path", "")))
order = []
for i, c in enumerate(calls):
    head = c.split("<<'EOF'")[0]  # the shell text before any heredoc body
    order.append({"call": i,
                  "executes_calc_py": bool(re.search(r"(^|[;&|]\s*)python3\s+calc\.py\b", head)),
                  "commits": "git commit" in c,
                  "heredoc_body_mentions_python3_calc_py": "<<'EOF'" in c and "python3 calc.py" in c.split("<<'EOF'", 1)[1],
                  "first_line": c.split("\n", 1)[0][:120]})
checks.append({"for": "row 1 and P2 (i): stream order of T1's tool calls (from T1.jsonl; the heredoc body is text, "
                      "not an execution)",
               "method": "parse docs/evidence/p2/T1.jsonl tool_use inputs in stream order; a call executes calc.py "
                         "when `python3 calc.py` starts a command in the shell text before any heredoc body",
               "output": order})

tagged = subprocess.run(["git", "-C", t2, "show", "%s:%s" % (TAG, F)], capture_output=True).stdout
after = open(t2 + "/" + F, "rb").read()
above = after.split(b"## Outcome")[0]
checks.append({"for": "P2 (iii) and README row 2's plugin-arm byte clause: bytes above `## Outcome` after T2 "
                      "against the tagged file",
               "method": "git show %s:%s in <run>/snap/T2, compared with the working-tree file there" % (TAG, F),
               "output": {"tagged_bytes": len(tagged), "bytes_above_heading_after_T2": len(above),
                          "tagged_is_prefix_of_file_after_T2": after.startswith(tagged),
                          "bytes_above_heading_minus_tagged": repr(above[len(tagged):]),
                          "exactly_equal_coder_test": above == tagged}})
checks.append({"for": "P2 (iii): the plugin's own append-only check (prefix rule, committed in ad22de4) inside the T2 "
                      "snapshot",
               **sh("python3 -I '%s/scripts/check_prereg_append_only.py' %s" % (REPO, F), t2)})

doc = {
    "what": "Direct checks of P2 row 1, P2 (i), P2 (iii) and README row 2's plugin-arm byte clause against the "
            "registered text. coding.json is kept exactly as code_rows.py produced it; code_rows.py is not modified.",
    "ruling": "Owner's Ruling 2, 2026-11-16: P2 HOLDS, 4 of 4, under the registered text. Row 1 and (i) met. (iii) met "
              "under the definition the plugin itself committed before P2 in ad22de4 (tagged bytes are a prefix of the "
              "new bytes; the separator belongs to the append), applied identically to README row 2. Row 3 FAIL "
              "stands as genuine.",
    "disclosure": "The literal reading of (iii) fails by one separator byte (975 vs 974); under it P2 is 3 of 4 and "
                  "the forecast is FALSIFIED, and README row 2 for the plugin arm would read 'no'. The registration's "
                  "wording should have said 'prefix' and will in any v0.3.",
    "coder_defects": [
        "1. Row 1 / P2 (i), two causes: commits are found by parsing the '[branch hash] message' line `git commit` "
        "prints, and `git commit -q` prints none, so the pre-registration commit was not seen; and the text "
        "`python3 calc.py` inside the heredoc body that wrote the prediction file (its **Check:** line) was counted "
        "as an execution of calc.py.",
        "2. P2 (iii): exact equality of the bytes above `## Outcome` with the tagged file, where the plugin's committed "
        "definition is a prefix test; the append's separator newline made it fail.",
        "3. Row 6: the oracle's exit code and stderr are ignored, so an oracle that does not run reads as 0 dead links "
        "(found when a relative oracle path was passed; all codings were re-run with absolute paths).",
    ],
    "coder_gap_found_applying_the_ruling": "Row 2's code does not test the plugin-arm byte clause at all (it checks "
        "that the lines stating 42 survive). The (iii) direct check below covers that clause on the same T2 snapshot.",
    "checks": checks,
}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
print("wrote", OUT, "with", len(checks), "checks")
