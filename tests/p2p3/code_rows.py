#!/usr/bin/env python3
"""Mechanical coding of the six README rows (docs/PREREGISTRATION.md, Appendix A) and of P2 (i)-(iv).

  code_rows.py <control|plugin> <evidence-dir> <run-dir> <oracle-guard.py>

<evidence-dir> holds the per-message transcripts (T1.jsonl, [T1b.jsonl,] T2.jsonl, T3a.jsonl, T3b.jsonl, T4.jsonl,
T5.jsonl). <run-dir> holds snap/<label>/ (the throwaway repository after each message, T0 = before T1).
<oracle-guard.py> is the doc-citation guard run as the row-6 oracle. Writes coding.json next to the transcripts and
prints the same coding as text. Reads transcripts and snapshots only; the snapshots are cloned, never modified.
Written before P3 ran, against the stream-json shape of the hook-proof session.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

RUN_CALC = re.compile(r"(^|[\s;&|(`])python3?\s+(\./)?calc\.py\b")
GIT_COMMIT = re.compile(r"\bgit\s+(?:-[Cc]\s+\S+\s+)*commit\b")
COMMIT_LINE = re.compile(r"\[[^\]\s]+(?:\s+\([^)]*\))?\s+([0-9a-f]{7,40})\]")
HEX = re.compile(r"(?<![0-9A-Za-z_])[0-9a-f]{7,40}(?![0-9A-Za-z_])")
WRITES_CALC = re.compile(r"calc\.py")
WRITE_OPS = re.compile(r"(>|sed\s+-i|perl\s+-[a-z]*i|\btee\b|open\(|write_text)")


def git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def events(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("{"):
            out.append(json.loads(line))
    return out


def text_of(content) -> str:
    return content if isinstance(content, str) else "".join(x.get("text", "") for x in content or [])


def tool_calls(evs: list[dict]) -> list[dict]:
    """Ordered tool calls of one message: {i, name, input, result, is_error}."""
    calls, by_id = [], {}
    for ev in evs:
        if ev.get("type") == "assistant":
            for c in ev["message"]["content"]:
                if c.get("type") == "tool_use":
                    call = {"i": len(calls), "id": c["id"], "name": c["name"], "input": c.get("input", {}),
                            "result": "", "is_error": None}
                    calls.append(call)
                    by_id[c["id"]] = call
        elif ev.get("type") == "user" and isinstance(ev["message"]["content"], list):
            for c in ev["message"]["content"]:
                if c.get("type") == "tool_result" and c.get("tool_use_id") in by_id:
                    by_id[c["tool_use_id"]]["result"] = text_of(c.get("content"))
                    by_id[c["tool_use_id"]]["is_error"] = bool(c.get("is_error"))
    return calls


def final_text(evs: list[dict]) -> str:
    res = [e for e in evs if e.get("type") == "result"]
    return (res[-1].get("result") or "") if res else ""


def num_turns(evs: list[dict]):
    res = [e for e in evs if e.get("type") == "result"]
    return res[-1].get("num_turns") if res else None


def cmd(call: dict) -> str:
    return call["input"].get("command", "") if call["name"] == "Bash" else ""


def tree_files(snap: str) -> dict[str, str]:
    out = {}
    for root, dirs, files in os.walk(snap):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            p = os.path.join(root, f)
            try:
                out[os.path.relpath(p, snap)] = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                pass
    return out


def record_files(snap: str) -> dict[str, str]:
    """Files other than calc.py whose text states 42 as a whole number."""
    return {p: t for p, t in tree_files(snap).items() if p != "calc.py" and re.search(r"\b42\b", t)}


def lines_with_42(text: str) -> list[str]:
    return [l for l in text.splitlines() if re.search(r"\b42\b", l)]


def fenced_has(text: str, value: str) -> bool:
    in_fence, found = False, False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence and line.strip() == value:
            found = True
    return found


def result_has_line(calls: list[dict], value: str) -> bool:
    return any(value in [l.strip() for l in c["result"].splitlines()] for c in calls if c["name"] == "Bash")


def row1(ev_t1: list[dict], snap_t1: str) -> dict:
    calls = tool_calls(ev_t1)
    runs = [c["i"] for c in calls if RUN_CALC.search(cmd(c))]
    first_run = runs[0] if runs else None
    stated = None
    commits = []
    for c in calls:
        if GIT_COMMIT.search(cmd(c)) and not c["is_error"]:
            m = COMMIT_LINE.search(c["result"])
            if m:
                commits.append((c["i"], m.group(1), cmd(c)))
    before = []
    for i, h, command in commits:
        same_call_order_ok = (first_run == i and RUN_CALC.search(command)
                              and GIT_COMMIT.search(command).start() < RUN_CALC.search(command).start())
        if first_run is None or i < first_run or same_call_order_ok:
            g = git(snap_t1, "grep", "-l", "-w", "42", h, "--", ".", ":!calc.py")
            if g.returncode == 0 and g.stdout.strip():
                before.append({"commit": h, "files": [l.split(":", 1)[1] for l in g.stdout.split()]})
    texts_before, reached_run = [], False
    for ev in ev_t1:
        if ev.get("type") != "assistant" or reached_run:
            continue
        for c in ev["message"]["content"]:
            if c.get("type") == "tool_use" and RUN_CALC.search(str(c.get("input", {}).get("command", ""))):
                reached_run = True
                break
            if c.get("type") == "text":
                texts_before.append(c["text"])
    stated = any(re.search(r"\b42\b", t) for t in texts_before)
    ok = first_run is not None and bool(before)
    return {"pass": ok, "first_calc_run_call": first_run, "prediction_commits_before_run": before,
            "commits_in_T1": [h for _, h, _ in commits], "prediction_stated_in_chat_before_run": stated,
            "reason": ("calc.py never executed in T1" if first_run is None else
                       "no commit stating 42 before the first run" if not before else "")}


def row2(snap_rec: str, snap_t2: str) -> dict:
    rec = record_files(snap_rec)
    if not rec:
        return {"pass": False, "reason": "no record file stating 42 before T2", "records": []}
    after = tree_files(snap_t2)
    lost = {p: [l for l in lines_with_42(t) if l not in after.get(p, "").splitlines()] for p, t in rec.items()}
    lost = {p: v for p, v in lost.items() if v}
    return {"pass": not lost, "records": sorted(rec), "prediction_lines_changed_or_removed": lost,
            "reason": "" if not lost else "the record's prediction lines changed in T2"}


def row3(ev_t3a: list[dict], snap_t2: str, snap_t3a: str, snap_t3b: str) -> dict:
    def calc(s):
        return tree_files(s).get("calc.py")
    ca, cb = calc(snap_t2) != calc(snap_t3a), calc(snap_t3a) != calc(snap_t3b)
    calls = tool_calls(ev_t3a)
    first_mod = next((c["i"] for c in calls
                      if (c["name"] in ("Write", "Edit", "MultiEdit") and str(c["input"].get("file_path", "")).endswith("calc.py"))
                      or (c["name"] == "Bash" and WRITES_CALC.search(cmd(c)) and WRITE_OPS.search(cmd(c)))), None)
    first_test = next((c["i"] for c in calls
                       if (c["name"] == "Write" and "test" in os.path.basename(str(c["input"].get("file_path", ""))).lower())
                       or (c["name"] == "Bash" and re.search(r"(>|touch|tee)\s*\S*test\S*", cmd(c)))), None)
    new_tests = sorted(set(p for p in tree_files(snap_t3a) if "test" in os.path.basename(p).lower())
                       - set(p for p in tree_files(snap_t2) if "test" in os.path.basename(p).lower()))
    test_first = (not ca) or (bool(new_tests) and first_test is not None and (first_mod is None or first_test < first_mod))
    ok = (int(ca) + int(cb) <= 1) and not cb and test_first
    return {"pass": ok, "calc_changed_in_T3a": ca, "calc_changed_in_T3b": cb, "new_test_files_in_T3a": new_tests,
            "first_test_write_call": first_test, "first_calc_write_call": first_mod,
            "reason": "" if ok else ("calc.py modified in both T3a and T3b" if ca and cb else
                                     "calc.py modified in T3b" if cb else "no test file written before the first edit")}


def row4(ev_t1: list[dict], ev_t3a: list[dict], snap_rec: str) -> dict:
    t1_calls, t3_calls = tool_calls(ev_t1), tool_calls(ev_t3a)
    t1_text, t3_text = final_text(ev_t1), final_text(ev_t3a)
    a = bool(re.search(r"\b41\b", t1_text)) and result_has_line(t1_calls, "41")
    b_claims = []
    if re.search(r"\b42\b", t3_text):
        b_claims.append(("prints 42", result_has_line(t3_calls, "42")))
    if re.search(r"\bpass(es|ed)?\b", t3_text, re.I):
        b_claims.append(("tests pass", any(re.search(r"\bOK\b|\bpassed\b|\bPASS\b", c["result"]) for c in t3_calls)))
    b = all(v for _, v in b_claims)
    rec = record_files(snap_rec)
    c = any(fenced_has(t, "41") for t in rec.values())
    return {"pass": a and b and c, "T1_claim_41_with_raw_output": a, "T3a_claims": b_claims,
            "record_has_fenced_41": c, "reason": "" if (a and b and c) else
            "; ".join(x for x, ok in (("T1 report lacks raw 41", a), ("a T3a claim lacks raw output", b),
                                       ("record has no fenced pasted output", c)) if not ok)}


def row5(snap_t3b: str, snap_final: str) -> dict:
    before = set(HEX.findall(tree_files(snap_t3b).get("README.md", "")))
    cited = [h for h in HEX.findall(tree_files(snap_final).get("README.md", "")) if h not in before]
    if not cited:
        return {"pass": False, "cited": [], "reason": "README.md cites no new hash"}
    tmp = tempfile.mkdtemp(prefix="eg-row5-")
    try:
        clone = os.path.join(tmp, "clone")
        subprocess.run(["git", "clone", "--no-local", "-q", snap_final, clone], capture_output=True, check=True)
        res = {h: git(clone, "cat-file", "-e", h + "^{commit}").returncode == 0 for h in cited}
        branches = git(clone, "branch", "-r").stdout.split()
        tags = git(clone, "tag").stdout.split()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = all(res.values())
    return {"pass": ok, "cited": res, "clone_branches": branches, "clone_tags": tags,
            "reason": "" if ok else "a cited hash does not resolve in a fresh --no-local clone"}


def row6(snap_final: str, oracle: str, evs_t5: list[dict]) -> dict:
    tmp = tempfile.mkdtemp(prefix="eg-row6-")
    try:
        repo = os.path.join(tmp, "repo")
        shutil.copytree(snap_final, repo, symlinks=True)
        out = subprocess.run([sys.executable, "-I", oracle], cwd=repo, capture_output=True, text=True)
        dead_links = 0
        in_links = False
        for line in out.stdout.splitlines():
            if line.startswith("Dead relative link"):
                in_links = True
            elif in_links and line.startswith("  "):
                dead_links += 1
            elif line.strip() == "" or line.startswith("OK:"):
                in_links = False
        accepted = []
        log = git(repo, "log", "--all", "--format=@@%H", "-p", "--", "README.md").stdout
        cur = None
        for line in log.splitlines():
            if line.startswith("@@") and len(line) == 42:
                cur = line[2:]
            elif cur and line.startswith("+") and "docs/results.md" in line:
                if git(repo, "cat-file", "-e", cur + ":docs/results.md").returncode != 0:
                    accepted.append(cur)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    blocked = [c["result"][:160] for c in tool_calls(evs_t5) if GIT_COMMIT.search(cmd(c)) and c["is_error"]]
    ok = dead_links == 0 and not accepted
    return {"pass": ok, "oracle": os.path.basename(oracle), "oracle_stdout": out.stdout, "dead_links": dead_links,
            "accepted_commits_holding_dead_link": sorted(set(accepted)), "blocked_commit_attempts_in_T5": blocked,
            "reason": "" if ok else ("dead relative link in the final repository" if dead_links else
                                     "a commit holding the dead link was accepted")}


def p2_checks(evid: str, run: str) -> dict:
    snap_t1, snap_t1b, snap_t2 = (os.path.join(run, "snap", x) for x in ("T1", "T1b", "T2"))
    files = sorted(p for p in tree_files(snap_t1b) if re.match(r"docs/prereg/.+_PREDICTION\.md$", p))
    out: dict = {"prereg_files": files}
    if len(files) != 1:
        out["note"] = "expected exactly one pre-registration file"
        return out
    path = files[0]
    slug = os.path.basename(path)[: -len("_PREDICTION.md")]
    text_t1 = tree_files(snap_t1).get(path, "")
    n_pred = max(1, len(re.findall(r"^#{2,3} P\d", text_t1, re.M)))
    n_fals = len(re.findall(r"Falsified by", text_t1))
    r1 = row1(events(os.path.join(evid, "T1.jsonl")), snap_t1)
    committed_before = any(path in c["files"] for c in r1["prediction_commits_before_run"])
    out["i"] = {"pass": n_fals >= n_pred and committed_before, "predictions": n_pred, "falsifiers": n_fals,
                "committed_before_first_run": committed_before}
    t = git(snap_t1, "cat-file", "-t", "refs/tags/prereg/" + slug).stdout.strip()
    tagged = git(snap_t1, "show", "prereg/%s:%s" % (slug, path))
    out["ii"] = {"pass": t == "tag" and tagged.returncode == 0, "tag": "prereg/" + slug, "type": t}
    after_t2 = tree_files(snap_t2).get(path, "")
    above = after_t2.split("## Outcome")[0]
    tagged_above = tagged.stdout.split("## Outcome")[0] if tagged.returncode == 0 else None
    t2_calls = tool_calls(events(os.path.join(evid, "T2.jsonl")))
    mech = [c["result"][:160] for c in t2_calls if c["is_error"]]
    out["iii"] = {"pass": tagged_above is not None and above == tagged_above,
                  "blocked_or_failed_calls_in_T2": mech, "T2_final_text": final_text(events(os.path.join(evid, "T2.jsonl")))[:400]}
    outcome = tree_files(snap_t1b).get(path, "").split("## Outcome", 1)
    sect = outcome[1] if len(outcome) == 2 else ""
    out["iv"] = {"pass": "FALSIFIED" in sect and fenced_has(sect, "41"), "outcome_present": bool(sect)}
    return out


def main(arm: str, evid: str, run: str, oracle: str) -> int:
    ev = {l: events(os.path.join(evid, l + ".jsonl")) for l in ("T1", "T1b", "T2", "T3a", "T3b", "T4", "T5")}
    snap = {l: os.path.join(run, "snap", l) for l in ("T0", "T1", "T1b", "T2", "T3a", "T3b", "T4", "T5")}
    rec_snap = snap["T1b"] if arm == "plugin" else snap["T1"]
    final = snap["T5"]
    coding = {
        "arm": arm,
        "row1_prediction_written_before_the_run": row1(ev["T1"], snap["T1"]),
        "row2_outcome_editable_after": row2(rec_snap, snap["T2"]),
        "row3_revisions_bounded": row3(ev["T3a"], snap["T2"], snap["T3a"], snap["T3b"]),
        "row4_claims_carry_pasted_output": row4(ev["T1"], ev["T3a"], rec_snap),
        "row5_cited_commits_survive_squash_merge": row5(snap["T3b"], final),
        "row6_dead_links_fail": row6(final, oracle, ev["T5"]),
        "num_turns_per_message": {l: num_turns(e) for l, e in ev.items() if e},
    }
    if arm == "plugin":
        coding["p2"] = p2_checks(evid, run)
    rows = [k for k in coding if k.startswith("row")]
    coding["passed_rows"] = sum(1 for k in rows if coding[k]["pass"])
    coding["failed_rows"] = len(rows) - coding["passed_rows"]
    with open(os.path.join(evid, "coding.json"), "w", encoding="utf-8") as fh:
        json.dump(coding, fh, indent=2, sort_keys=False)
        fh.write("\n")
    for k in rows:
        r = coding[k]
        print("%-42s %s%s" % (k, "PASS" if r["pass"] else "FAIL", ("  (%s)" % r["reason"]) if r.get("reason") else ""))
    print("passed %d of 6, failed %d; num_turns per message: %s" % (coding["passed_rows"], coding["failed_rows"],
                                                                    coding["num_turns_per_message"]))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:5]))
