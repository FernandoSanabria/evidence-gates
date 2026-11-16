# P3: the arm without evidence-gates (registered run)

- **Run:** `p3-control`, 2026-11-16, through `tests/p2p3/run_arm.sh control` at harness commit `f5087f5`. No skill, hook or script of this plugin existed in the repository yet.
- **The subject as shipped:** a fresh Claude Code 2.1.325 profile, which ships four built-in plugins (`cc-plugin-agents-md`, `cc-plugin-telemetry`, `cc-plugin-privacy`, `cc-plugin-plugin-authoring`). "Without evidence-gates" means exactly that, not "no plugin".
- **The six messages:** Appendix A of the pre-registration, verbatim, chained with `--continue` in one session. Each message's raw stream-json is in `T1.jsonl` … `T5.jsonl`, with sha256s in `SHA256SUMS`.
- **Readable copy:** `transcript.txt`, rendered mechanically by `tests/p2p3/render_transcript.py`.
- **Coding:** `coding.json`, from `tests/p2p3/code_rows.py`, which was written before this run. Row 6 was coded provisionally with the legacy guard (the verbatim copy at the G8 merge, sha256 `e50b3c4ed1bcc8afeefc6c8eba8d7efc41faa1bcc2704262a5fb0aa076e324fc`) as the oracle. It is re-coded with this plugin's guard after P4(a) passes parity.
- **Cost:** $0.297889 for the six sessions. Turns per message were 3, 1, 2, 2, 3, 3, against `--max-turns 30`.
