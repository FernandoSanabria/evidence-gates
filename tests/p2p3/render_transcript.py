#!/usr/bin/env python3
"""Render per-message stream-json transcripts as one readable text file, mechanically and completely.

  render_transcript.py <evidence-dir> <label> [<label> ...]  > transcript.txt

For each label, prints the message as sent (from messages.txt; the plugin arm's T1 carries the prefix), then every
assistant text, tool call (name and full input) and tool result (full content, error flag) in stream order, then the
result event's cost and turns. Nothing is summarised or truncated. Text output, not Markdown, so the doc-citation
guard does not read throwaway-repository hashes as citations of this repository.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def messages() -> dict[str, str]:
    out = {}
    for line in open(os.path.join(HERE, "messages.txt"), encoding="utf-8"):
        k, _, v = line.rstrip("\n").partition("\t")
        out[k] = v
    return out


def text_of(content) -> str:
    return content if isinstance(content, str) else "".join(x.get("text", "") for x in content or [])


def sent(label: str, msgs: dict[str, str], evid: str) -> str:
    plugin = os.path.exists(os.path.join(evid, "T1b.jsonl"))
    if label == "T1" and plugin:
        return msgs["T1_PREFIX"] + " " + msgs["T1"]
    if label == "GATE":
        return msgs["GATE"]
    return msgs.get(label, "(not in messages.txt)")


def render(evid: str, label: str, msgs: dict[str, str]) -> None:
    path = os.path.join(evid, label + ".jsonl")
    print("=" * 100)
    print("MESSAGE %s (user, as sent):\n%s" % (label, sent(label, msgs, evid)))
    print("=" * 100)
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        ev = json.loads(line)
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init":
            print("[init] claude_code_version=%s model=%s permissionMode=%s apiKeySource=%s plugins=%s"
                  % (ev.get("claude_code_version"), ev.get("model"), ev.get("permissionMode"), ev.get("apiKeySource"),
                     [p.get("name") for p in ev.get("plugins", [])]))
        elif t == "assistant":
            for c in ev["message"]["content"]:
                if c.get("type") == "text":
                    print("\n[assistant]\n" + c["text"])
                elif c.get("type") == "tool_use":
                    print("\n[tool call %s] %s" % (c["name"], json.dumps(c.get("input", {}), ensure_ascii=False, indent=1)))
        elif t == "user" and isinstance(ev["message"]["content"], list):
            for c in ev["message"]["content"]:
                if c.get("type") == "tool_result":
                    print("\n[tool result%s]\n%s" % (" ERROR" if c.get("is_error") else "", text_of(c.get("content"))))
        elif t == "result":
            print("\n[result] num_turns=%s total_cost_usd=%s is_error=%s terminal_reason=%s"
                  % (ev.get("num_turns"), ev.get("total_cost_usd"), ev.get("is_error"), ev.get("terminal_reason")))
    print()


def main(evid: str, labels: list[str]) -> int:
    msgs = messages()
    for label in labels:
        if os.path.exists(os.path.join(evid, label + ".jsonl")):
            render(evid, label, msgs)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2:]))
