# Discarded runs

Runs that failed for infrastructure reasons before any model output. Each keeps its row in [COST.md](../COST.md) and its raw output here.

| file | run | when (UTC) | cost | reason |
|---|---|---|--:|---|
| `probe-1.json` | preflight-probe | 2026-11-16T16:51:37Z | $0.00 | The auth probe got a 401. Claude Code's diagnostic: "apiKeyHelper failed: returned output that cannot be used as an API key: it contains a control character at character 207 (407 characters)". The owner's key file held a malformed value; the owner rewrote it (one line, 132 bytes, no control characters), and the probe was re-run as `preflight-probe-2`. |

**Restoration note for `probe-1.json`.** The original file was overwritten. My move command used `git mv -k`, which is a silent no-op that exits 0 on an untracked file, so the fallback `mv` never ran, and the re-run `preflight-probe-2` then wrote its own `probe.json` to the same path. This file was restored byte for byte from the verbatim terminal capture of the original (printed with `cat` before the re-run). The sha256 of the original bytes was never recorded, so it cannot be shown. The session's stderr, which holds Claude Code's diagnostic, was not overwritten; the diagnostic is quoted in the table above.
