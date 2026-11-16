# Spend — Stage 1

The hard cap is $10.00, the credit balance of the key the sessions use. `tests/p2p3/run_arm.sh` appends one row per `claude -p` result event through `tests/p2p3/ledger.py`, with the running sum. The cost is the result event's `total_cost_usd`.

Gates:
- No session starts once the running sum is ≥ $10.00. Every remaining prediction that needs a session is then NOT TESTED, reason "spend cap".
- If P3 alone costs more than $4.00, stop and report before P1.
- The pilot runs only if the sum after P3 is ≤ $4.00, and it spends at most $1.00.
- The supplementary `/evidence-gates:gate` runs only if the sum is under $9.00.
- A run discarded as an infrastructure failure keeps its row, with a one-line reason.

| # | UTC | run | session | total_cost_usd | running sum | num_turns | note |
|--:|---|---|---|--:|--:|--:|---|
| 1 | 2026-11-16T16:51:26Z | parser-test | parser-test-A | 0.000000 | 0.000000 | 1 | no key, API blocked; not via the runner; is_error=true (success) |
| 2 | 2026-11-16T16:51:37Z | preflight-probe | probe | 0.000000 | 0.000000 | 1 | is_error=true (success); DISCARDED, infrastructure: the apiKeyHelper output was malformed (owner's key file), see discarded/README.md |
| 3 | 2026-11-16T17:02:33Z | preflight-probe-2 | probe | 0.029753 | 0.029753 | 1 |  |
| 4 | 2026-11-16T17:02:57Z | preflight-hookproof | hookproof | 0.035646 | 0.065399 | 3 |  |
| 5 | 2026-11-16T17:08:16Z | p3-control | T1 | 0.024628 | 0.090027 | 3 |  |
| 6 | 2026-11-16T17:08:22Z | p3-control | T2 | 0.030685 | 0.120712 | 1 |  |
| 7 | 2026-11-16T17:08:28Z | p3-control | T3a | 0.038697 | 0.159409 | 2 |  |
| 8 | 2026-11-16T17:08:37Z | p3-control | T3b | 0.049952 | 0.209361 | 2 |  |
| 9 | 2026-11-16T17:08:51Z | p3-control | T4 | 0.070993 | 0.280354 | 3 |  |
| 10 | 2026-11-16T17:09:00Z | p3-control | T5 | 0.082934 | 0.363288 | 3 |  |
| 11 | 2026-11-16T17:38:04Z | pilot-1 | PILOT1 | 0.058911 | 0.422199 | 8 | UNREGISTERED pilot |
| 12 | 2026-11-16T17:38:14Z | pilot-1 | PILOT1b | 0.081530 | 0.503729 | 3 | UNREGISTERED pilot |
| 13 | 2026-11-16T17:38:20Z | pilot-1 | PILOT2 | 0.088083 | 0.591812 | 1 | UNREGISTERED pilot |
| 14 | 2026-11-16T17:38:28Z | pilot-1 | PILOT3 | 0.097796 | 0.689608 | 2 | UNREGISTERED pilot |
| 15 | 2026-11-16T18:21:51Z | p2-plugin | T1 | 0.051258 | 0.740866 | 5 |  |
| 16 | 2026-11-16T18:22:02Z | p2-plugin | T1b | 0.072509 | 0.813375 | 3 |  |
| 17 | 2026-11-16T18:22:10Z | p2-plugin | T2 | 0.079908 | 0.893283 | 1 |  |
| 18 | 2026-11-16T18:22:25Z | p2-plugin | T3a | 0.104774 | 0.998057 | 5 |  |
| 19 | 2026-11-16T18:22:41Z | p2-plugin | T3b | 0.128126 | 1.126183 | 3 |  |
| 20 | 2026-11-16T18:23:04Z | p2-plugin | T4 | 0.168119 | 1.294302 | 5 |  |
| 21 | 2026-11-16T18:23:12Z | p2-plugin | T5 | 0.179349 | 1.473652 | 2 |  |
| 22 | 2026-11-16T18:23:23Z | p2-plugin | GATE | 0.201646 | 1.675298 | 2 | supplementary, not registered |
| 23 | 2026-11-16T20:48:19Z | outcome/session | outcome | 0.150715 | 1.826013 | 6 |  |
