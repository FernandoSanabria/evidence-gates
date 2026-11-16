---
name: prereg
description: Pre-register a prediction before running what tests it. Writes docs/prereg/<slug>_PREDICTION.md with a falsifier for every prediction, commits it, and tags it prereg/<slug>.
argument-hint: <one-line goal>
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

## Pre-register: $ARGUMENTS

1. **Setup first.** Do the setup the request asks for that tests nothing, such as creating and switching to a branch. Run nothing that tests the prediction.
2. **Write down each prediction.** For each prediction the request implies, give:
   - a hypothesis;
   - its falsifier: an observable result that would show it wrong;
   - N: how many runs, rows or trials;
   - a forecast;
   - the exact command that decides it.

   If a prediction has no observable falsifier, derive the most direct one and state it. If none can be stated, stop and ask the user, and write nothing.
3. **Choose a slug.** Lowercase words from the goal, joined by hyphens, at most 40 characters. Check that it is free:

       python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_prereg_append_only.py" --new docs/prereg/<slug>_PREDICTION.md

   If it exits 1, stop and tell the user what already exists. Never pick a different slug yourself, and never overwrite a file or a tag. The user decides.
4. **Write the file.** Write `docs/prereg/<slug>_PREDICTION.md` from the template below.
5. **Commit only that file:** `git add docs/prereg/<slug>_PREDICTION.md` and `git commit -m "pre-register <slug>"`.
6. **Tag it** with `git tag -a prereg/<slug> -m "pre-registration: <slug>"`. Then print the commit's short hash and the tag.
7. **Only now carry on** with the rest of the request, under the standing rules. Results are recorded with `/evidence-gates:outcome`, which the user runs. Report what you found, but do not write an outcome into the pre-registration yourself.

## Template

    # <goal, in a few words>: pre-registration

    This file is committed **before** anything that tests it runs. Outcomes are **appended** below in later
    commits; the predictions are never edited. Recorded <YYYY-MM-DD>.

    **Evidence chain.** This commit gets the annotated tag `prereg/<slug>`.

    **HARD STOP:** <date or budget>. Anything unmeasured by then is NOT TESTED.

    **Each prediction states a hypothesis, its falsifier, N and a forecast.** Where the forecast is FALSIFIED,
    the expected failure is still a measurement. Counts come with N. Verdicts are HOLDS, FALSIFIED or NOT TESTED,
    each with a reason.

    ## P1 — <name>
    **Hypothesis.** <what you expect>
    **Falsified by:** <the observable result that would show it wrong>
    **N:** <how many>
    **Forecast:** <HOLDS or FALSIFIED>
    **Check:** <the exact command that decides it>
