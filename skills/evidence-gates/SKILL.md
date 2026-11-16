---
name: evidence-gates
description: The evidence-gates method. Pre-register before any scored or measured run, append outcomes and never edit them, allow one revision behind a held-out test, cite only commits that survive, and report gates with pasted evidence. Use before running anything whose result will be scored, measured or cited as evidence, and whenever recording, revising or reporting such a result.
---

# evidence-gates: the method

The metric triages; the artifact arbitrates. A score, a green check mark or a matcher's verdict is good at telling you where to look and bad at telling you what is true. The raw output underneath is the only arbiter.

## The rhythm

plan → review → refine → build → gate.

- A plan is reviewed and refined before anything is built.
- The build is measured against predictions written before it ran.
- Each gate is a packet the owner reads. Work stops there until the owner rules.

## Evidence, not assertion

- **No pasted output, no check.** A check without pasted output counts as not run. Paste the raw output, never a summary of it.
- **Read the raw artifact on the rows that matter.** Reading only the rows the metric already flagged is confirmation bias with extra steps.
- **Make every instrument go red once.** An instrument is only worth anything if it can go red. Make it fail on purpose once, then read the raw log of that failure. A red run where you wanted a red run proves nothing until you have seen that it failed for the right reason.
- **Verify where the claim lives.** A passing check at one layer certifies nothing about the layer above it.

## Pre-registration

- **Write it before the run.** Write down what you expect, falsifiably and specifically, and commit it to a file *before* you run the thing that tests it. A prediction recorded *after* the result is a rationalization you can always dress up as foresight.
- **What each prediction states.** A hypothesis, its falsifier (the observable result that would show it wrong), N, and your forecast. Where the forecast is FALSIFIED, the expected failure is still a measurement.
- **Set a HARD STOP.** A date or a budget. Anything unmeasured by then is NOT TESTED.
- **Commit and tag it first.** The file is committed before any code it tests, as the first commit of the work. It gets an annotated tag `prereg/<slug>` before anything that tests it runs.
- **Command:** `/evidence-gates:prereg <goal>`.

## Outcomes

- **Append, never edit.** Outcomes are appended below the predictions in later commits; the predictions are never edited. Each outcome section opens with: "The predictions above are unchanged; this section only appends."
- **Verdicts.** HOLDS, FALSIFIED or NOT TESTED, each with a reason. Counts come with N.
- **A falsified prediction is a result, not a failure.** If nothing you commit to ever dies on the record, you are performing the forms, not running the method.
- **Unregistered results** go under "Supplementary (not registered)".
- **The frozen text stays frozen.** Nothing above `## Outcome` is ever edited, deleted or moved, not even when the user asks. Explain why, and offer an appended correction instead.
- **Command:** `/evidence-gates:outcome`.

## One revision only

After a falsified result, the thing under test gets one revision:

1. held-out tests are committed first;
2. then the revision is pre-registered in a later section of the same file;
3. then it gets one run.

If the revision misses, it does not ship, and a second revision is not yours to make: stop and hand it to the owner. The one-shot rule is what stops a v3.

## Gate packets

- **Contents.** For each prediction: what ran (the exact command), the pasted raw output, and the verdict with its reason and N. Then hours and spend against the budget.
- **Ending.** The packet ends with STOP. Do not continue past it on your own.
- **Command:** `/evidence-gates:gate [since=<start time>]`.

## Tags and citations

- **Tag names.** `prereg/<slug>` marks a pre-registration; `evidence/<slug>` marks a measured build.
- **Cite commits that survive.** A commit hash cited in a doc must resolve from main or from one of those tags. A squash-merge or a deleted branch orphans every commit it does not keep, so tag what you cite before the squash, or cite the merged commit afterwards.
- **No dead links.** Never commit a link to a file that does not exist.
- **The commit hook.** It blocks dead hashes, dead links and dead tags. Fix the doc; never bypass the hook.

## What the owner decides

- **Never decided alone.** Shipping defaults, licensing, secrets and credentials, merges, pushes and releases. Stop and ask.
- **Flipping a shipped default is a stop-and-ask,** even when the measurement favours it. The switch changes other things, and each of those has its own gate.
- **Never fabricate.** Never fabricate a source or a ground-truth answer. If you don't know, write TODO_VERIFY and stop for human review.

The method in one line: trust the artifact over the instrument, and build the habits that let you do it on purpose rather than only in hindsight.
