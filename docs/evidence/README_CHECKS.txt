README commands checked on the pinned binary in the unregistered fallback profile (no session, no spend)
$ date -u +%FT%TZ
2026-11-16T20:50:48Z
$ claude plugin list
I couldn't run `claude plugin list` because the command needs your approval, so I don't have the full list.

From what this session can see, one plugin is loaded: **evidence-gates**. It adds a skill called `evidence-gates:evidence-gates`, which sets rules for scored or measured runs: you record the plan before running, results can't be edited afterwards, and only one revision is allowed.

To see the complete list, either:
- type `/plugin` here to open the plugin manager, or
- approve the command and I'll run `claude plugin list` again.
exit=0
$ claude plugin update evidence-gates@evidence-gates
The `claude plugin update evidence-gates@evidence-gates` command needs your approval before it can run, and I couldn't get that approval from here, so the plugin hasn't been updated.

You can run it yourself in your terminal:

```
claude plugin update evidence-gates@evidence-gates
```

Or approve the command when I try again. Restart Claude Code afterwards so the updated plugin loads.
exit=0
$ claude plugin uninstall evidence-gates@evidence-gates
I couldn't uninstall the plugin: running `claude plugin uninstall evidence-gates@evidence-gates` needs your approval, and it wasn't given.

To remove it, either approve the command when I run it again, or type it in your own terminal:

```
claude plugin uninstall evidence-gates@evidence-gates
```

You can also run `/plugin` in this session and remove it from there. You may need to restart the session before its skills stop showing up.
exit=0
$ claude plugin list
I couldn't run `claude plugin list` because it needs your approval, so I can't give you the full installed list.

What I can tell from this session's loaded skills is that one plugin is active: **evidence-gates**, which provides the `evidence-gates:evidence-gates` skill. All the other skills available here (`dataviz`, `code-review`, `simplify`, `loop`, `run` and so on) are built-in or user/project skills, not plugin ones.

To see every installed plugin, including disabled ones and which marketplace each came from, either:
- type `/plugin` here to open the plugin manager, or
- run `claude plugin list` in your terminal, or approve the command if you'd like me to run it.
exit=0

Case-study pin, re-checked on the fresh P4 clone of rag-pipeline:
$ git -C <clone> rev-parse 92cff85^{commit}; git -C <clone> log -1 --format='%cI %s' 92cff85
92cff850993f6331ed23e12331edf687b4d86645
2026-10-12T23:23:24-05:00 docs: correct 19 stale or contradicting claims found by the study-bank verification (#42)
$ git -C <clone> branch -r --contains 92cff85
  origin/HEAD -> origin/main
  origin/main
$ git -C <clone> cat-file -e 92cff85:eval/g8_PREDICTION.md; echo exit
exit=0
$ git -C <clone> cat-file -e 92cff85:eval/g11_design.md; echo exit
exit=0
$ git -C <clone> cat-file -e 92cff85:scripts/check_doc_citations.py; echo exit
exit=0
$ git -C <clone> show 92cff85:eval/g11_design.md | grep -n 'GATE 1 decisions'
55:## GATE 1 decisions (accepted 2026-10-12)

== Correction (2026-11-16): the four commands above did not run as CLI subcommands. Each was passed to the runner
   as one unsplit string (zsh does not word-split an unquoted $cmd), and the binary read it as a prompt: four
   unintended sessions, ledger rows 24-27 ($0.137157). The runner's cli mode now refuses such input:
$ tests/p2p3/run_arm.sh cli guard-test <scratch profile> "plugin list"; echo exit
run_arm: cli mode runs only `plugin <subcommand> …` or `--version` (got: 'plugin list'); nothing run
exit=2
$ ls -d <runs>/guard-test <scratch profile> 2>&1   (nothing created)
ls: /Users/akasha/.evidence-gates/runs/guard-test: No such file or directory
ls: <scratch>: No such file or directory

== The README commands, re-run as separate words, in the unregistered fallback profile:
$ date -u +%FT%TZ
2026-11-16T20:53:00Z
$ claude plugin list
Installed plugins:

  ❯ evidence-gates@evidence-gates
    Version: 0.1.0
    Scope: user
    Status: ✔ enabled

exit=0
$ claude plugin update evidence-gates@evidence-gates
Checking for updates for plugin "evidence-gates@evidence-gates"…
✔ evidence-gates is already at the latest version (0.1.0).
exit=0
$ claude plugin uninstall evidence-gates@evidence-gates
✔ Successfully uninstalled plugin: evidence-gates (scope: user)
exit=0
$ claude plugin list
No plugins installed. Use `claude plugin install` to install a plugin.
exit=0
