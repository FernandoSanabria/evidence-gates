# Hours — Stage 1

The logged-hours clock started at 2026-11-16T15:53:21Z, when the owner's Stage 1 GO was read. Kill rule: 16 logged hours or two build-days, whichever comes first. A build-day is a calendar day with logged work. Anything unmeasured at that point is NOT TESTED.

Time spent waiting for the owner (plan approval, the one push) is not logged. Session 1 includes planning and the plan-approval round trips, which can't be separated out, so they count as working time (the conservative choice).

| # | start (UTC) | stop (UTC) | hours | what |
|--:|---|---|--:|---|
| 1 | 2026-11-16T15:53:21Z | 2026-11-16T16:52:42Z | 0.99 | Stage 1 planning; steps 1–4 (logs, pinned instrument, parser test, runner and harness pieces, auth probe). Stopped at step 4: the probe could not authenticate because the key file's value is malformed (owner's file). |
| 2 | 2026-11-16T17:02:20Z | 2026-11-16T17:09:52Z | 0.13 | Steps 4–7: auth probe re-run, hook proof, environment check, coding and rendering tools, harness commit, P3 (control), coding. Stopped at the $4.00 checkpoint to report. |
| 3 | 2026-11-16T17:18:19Z | 2026-11-16T17:46:13Z | 0.47 | Rulings read; evidence redaction and commit; build (step 8); pilot; pilot and dogfood fixes; pre-push gate. Stopped to ask for the push. |

Running total: 1.59 h of 16.

## Entry check (2026-11-16, before any Stage 1 work)

```console
$ git ls-remote --tags origin
ca9d02ab9a442d2852acc9a945d7d2b8092bc39b	refs/tags/prereg/v0.1
ede60036a0d68b480432d0b2522e8ab0d8407559	refs/tags/prereg/v0.1^{}
ce03793dbfc6c1fcf22b4a04bf63d6566a20b2db	refs/tags/prereg/v0.2
35883aa7fcc4c8fdd9295ee1bd2c47e87e9c27b5	refs/tags/prereg/v0.2^{}
$ git ls-remote origin refs/heads/main
35883aa7fcc4c8fdd9295ee1bd2c47e87e9c27b5	refs/heads/main
```

The local refs are identical: `prereg/v0.1` is tag object `ca9d02a…` on commit `ede6003`, `prereg/v0.2` is `ce03793…` on `35883aa`, and `main` is `35883aa`. The check passed.
