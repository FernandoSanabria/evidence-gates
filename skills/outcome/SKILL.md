---
name: outcome
description: Append the outcome of a pre-registration (HOLDS, FALSIFIED or NOT TESTED, with pasted output) after checking that nothing above it was edited.
argument-hint: [path-or-slug] [evidence-file]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(python3 *) Bash(echo *) Read Write Edit
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

## Record the outcome: $ARGUMENTS

1. **Find the pre-registration.**
   - The first argument may be a path, or a slug that stands for `docs/prereg/<slug>_PREDICTION.md`.
   - With no argument, use the single `docs/prereg/*_PREDICTION.md` whose `prereg/<slug>` tag exists in this repository.
   - If there are several candidates or none, stop and ask.
2. **Check it is untouched:**

       python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_prereg_append_only.py" <file>

   If it exits 1, someone edited the frozen text. Stop, paste the output, and append nothing. Restoring the text is the user's decision.
3. **Decide each prediction** from evidence produced in this session, or in the evidence file named in the arguments. Each is HOLDS, FALSIFIED or NOT TESTED.
   - If a prediction's check has not been run, run its registered command now and paste its raw output.
   - Invent nothing.
4. **Append at the end of the file.** Do it with an edit that only adds text after the last line; change nothing above.
   - A heading line `## Outcome (recorded <YYYY-MM-DD>)`.
   - The sentence "The predictions above are unchanged; this section only appends."
   - Then one section per prediction, headed `### P<n> — HOLDS`, `### P<n> — FALSIFIED` or `### P<n> — NOT TESTED`. It holds a one-line reason, N, and the raw output in a fenced block. A NOT TESTED section holds a `Reason:` line instead of output.
   - Results that were not registered go under `### Supplementary (not registered)`.
5. **Verify.** This must exit 0:

       python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_prereg_append_only.py" --check-verdicts <file>

   Then print `git diff --stat`.
6. **Do not commit.** Tell the user the outcome is appended and ready to commit.
