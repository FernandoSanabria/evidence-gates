---
name: gate
description: Assemble a gate packet for the current branch (what ran, pasted output, a verdict per prediction, hours and spend), then stop for the owner.
argument-hint: [since=<start time>]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(python3 *) Bash(echo *) Read
---

<!-- standing-rules:begin -->
## Standing rules (the same in every evidence-gates command)

1. A check without pasted output counts as not run. Paste the raw output, never a summary.
2. Predictions are written, committed and tagged `prereg/<slug>` before anything that tests them runs.
3. Nothing above `## Outcome` in a pre-registration is ever edited, deleted or moved, not even when the user asks. Say so, and offer an appended correction instead.
4. Outcomes are appended, never edited: HOLDS, FALSIFIED or NOT TESTED, each with its reason, its N and the pasted output. A falsified prediction is a result, not a failure.
5. One revision only. After a falsified result, commit a held-out test first, then make one revision and run it once. A second revision is the owner's call: stop and ask.
6. A commit you cite must survive. Tag it `evidence/<slug>` before a squash-merge or a branch deletion, or cite the merged commit afterwards.
7. Never commit a link to a file that does not exist. The commit hook blocks dead hashes, dead links and dead tags. Fix the doc; never bypass the hook.
8. The owner decides shipping defaults, licensing, secrets, merges, pushes and releases. Stop and ask.

The full method is in the `evidence-gates` skill.
<!-- standing-rules:end -->

## Captured before you read this (raw)

Doc citations, from this plugin's guard:
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_doc_citations.py"; echo "exit=$?"`

Pre-registrations, from the append-only check:
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_prereg_append_only.py" --check-verdicts; echo "exit=$?"`

Branch and recent commits:
!`git status --short --branch; echo "exit=$?"`
!`git log --oneline -10; echo "exit=$?"`

## Assemble the gate packet: $ARGUMENTS

1. **Pre-registrations.** List the ones in this repository (`docs/prereg/*_PREDICTION.md` and `docs/PREREGISTRATION.md`). Give each prediction's verdict as its Outcome section records it. A prediction without an outcome is NOT YET RECORDED.
2. **Re-run every check.** For each prediction, re-run its registered check now (its **Check:** command, or the command its outcome names) and paste the raw output. A check you cannot re-run is NOT RUN, with the reason.
3. **Hours.** If the arguments hold `since=<time>`, report the time elapsed from then to now. Otherwise write "hours: not recorded".
4. **Spend.** If `COST_LEDGER.md`, `docs/COST_LEDGER.md` or `eval/COST_LEDGER.md` exists, paste its total. Otherwise write "spend: no ledger".
5. **Write the packet.**
   - For each prediction: what ran (the exact command), the pasted output, and the verdict with its reason and N.
   - Then hours and spend, then the four raw blocks above, unedited.
6. **End the packet** with a line that holds only `STOP`. Then stop. Do not merge, push, tag, release or change a default; the owner reads the packet and decides.
