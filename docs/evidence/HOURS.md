# Hours — Stage 1

The logged-hours clock started at 2026-11-16T15:53:21Z, when the owner's Stage 1 GO was read. Kill rule: 16 logged hours or two build-days, whichever comes first. A build-day is a calendar day with logged work. Anything unmeasured at that point is NOT TESTED.

Time spent waiting for the owner (plan approval, the one push) is not logged. Session 1 includes planning and the plan-approval round trips, which can't be separated out, so they count as working time (the conservative choice).

| # | start (UTC) | stop (UTC) | hours | what |
|--:|---|---|--:|---|
| 1 | 2026-11-16T15:53:21Z | 2026-11-16T16:52:42Z | 0.99 | Stage 1 planning; steps 1–4 (logs, pinned instrument, parser test, runner and harness pieces, auth probe). Stopped at step 4: the probe could not authenticate because the key file's value is malformed (owner's file). |
| 2 | 2026-11-16T17:02:20Z | 2026-11-16T17:09:52Z | 0.13 | Steps 4–7: auth probe re-run, hook proof, environment check, coding and rendering tools, harness commit, P3 (control), coding. Stopped at the $4.00 checkpoint to report. |
| 3 | 2026-11-16T17:18:19Z | 2026-11-16T17:46:13Z | 0.47 | Rulings read; evidence redaction and commit; build (step 8); pilot; pilot and dogfood fixes; pre-push gate. Stopped to ask for the push. |
| 4 | 2026-11-16T18:04:49Z | 2026-11-16T18:29:58Z | 0.42 | Push confirmed (`f10bf42` on origin/main); P5(a) measurement defined before any install; P1, P2, P4 with Note A, P5. Stopped before the outcome for the owner's ruling on three coder defects found on P2 data. |
| 5 | 2026-11-16T20:41:34Z | 2026-11-16T20:58:09Z | 0.28 | Owner's Rulings 1 and 2 read (allow-list, SSH resolution, P2 coding); evidence commit; outcome via /outcome; README; CHANGELOG; GATE packet. Stopped at the packet. |

Running total: 2.29 h of 16.

## P5(a) measurement, defined before any install (recorded 2026-11-16T18:19:46Z)

Recorded before any P1 command has run. The owner's definition, verbatim:

> "the installed plugin directory" is the path that `claude plugin details evidence-gates` reports for the install (or, if it reports none, the directory under the P1 profile's plugins cache that holds the plugin's .claude-plugin/plugin.json), measured with `du -sk` exactly as found, including any .git it contains. If the number is over 1 MB, P5(a) is FALSIFIED; nothing is deleted or excluded to change it.

**The procedure, in order** (the owner's correction: the definition must not decide in advance whether a `.git` is included):

1. **Ask the install for its path.** Run `tests/p2p3/run_arm.sh cli <run> <P1 profile> plugin details evidence-gates`. If it reports a path, that path is the directory, wherever it lives. That includes anywhere under `plugins/marketplaces/`, and any `.git` inside it. (In the dry run, `plugin details` printed no path.)
2. **Only if it reports no path, search the cache.** Run `find <P1 profile>/plugins/cache -path '*/.claude-plugin/plugin.json'` and keep the matches whose `name` is `evidence-gates`. The directory is the parent of `.claude-plugin`. Exactly one match is expected; zero or several means STOP and report before measuring.
3. **Measure.** Run `du -sk <dir>` on the directory exactly as found, and paste the output raw.

**Threshold** (owner's ruling, decided before any measurement):
- `du -sk` ≥ 977 falsifies P5(a). This reads 1 MB as 10^6 bytes, the strictest reading: 977 × 1024 bytes is 1,000,448.
- The registered falsifier, "1 MB or more", governs the boundary.
- The MiB reading (falsified at ≥ 1024) is reported next to it. A number from 977 to 1023 is FALSIFIED, and the packet says that the looser reading would have passed.
- A fresh clone's `.git` is about 336 KB (the owner's measurement), which would put a `.git`-inclusive install near the 977 line. It is measured as defined and reported as found.

**When** (owner's ruling):
- **Twice.** Once right after the P1 install, before any session, and again at P5 time, after P2.
- **The larger number decides.** Both numbers are pasted.
- **The difference** is reported as "growth from the plugin's own runtime (`__pycache__`)". The hook's scripts import `gitcmd`, so Python can write bytecode into the installed `scripts/` directory.

**Next to it,** "the size of `git archive HEAD`" means the commit that was installed. `git ls-remote origin refs/heads/main` is pasted immediately before the install, and `git archive <that commit> | wc -c` is reported.

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
