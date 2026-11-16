# The outcome, recorded through the plugin's `/outcome`

The `## Outcome (recorded 2026-11-16)` section of `docs/PREREGISTRATION.md` was written by a subject session using the installed plugin's `/evidence-gates:outcome`. This repository then received exactly those bytes. The session ran in a fresh clone, never in this repository (the owner's refinement 1).

## The steps

1. **The clone** ([01_clone.txt](01_clone.txt)).
   - **What was cloned.** A fresh clone of this repository at `09be5c9`, which holds the evidence file `docs/evidence/OUTCOME_EVIDENCE.md`. Both `prereg/` tags came with it.
   - **No path back.** Its `origin` remote was removed, so the subject had no path back to this repository. This is a harness detail, disclosed here.
2. **The session.**
   - **How it ran.** Through `tests/p2p3/run_arm.sh outcome`, as run `outcome/session`, in the P1 profile with the plugin as installed, using the same binary, clean environment, auth and arm flags as P2.
   - **The message.** [outcome.message.txt](outcome.message.txt): `/evidence-gates:outcome docs/PREREGISTRATION.md docs/evidence/OUTCOME_EVIDENCE.md`.
   - **Cost.** $0.150715 over 6 turns (ledger row 23).
   - **Files.** The raw stream-json is `outcome.jsonl`, and [transcript.txt](transcript.txt) is the rendered copy.
3. **What the subject did.**
   - **Before.** It ran the append-only check first (exit 0) and read both files. It also ran the guard on the clone.
   - **The append.** It appended one `## Outcome` section with `### P1 — HOLDS` … `### P5 — HOLDS` and `### Supplementary (not registered)`, then ran `--check-verdicts` (exit 0) and `git diff --stat`.
   - **No commit.** It did not commit.
   - **Faithful to the evidence.** It carried each verdict, reason, N, evidence link and the owner's verbatim texts as given in the evidence file.
   - **Changes of form.** These differ from the evidence file:
     - each prediction's fenced blocks are merged into one block, and my wrapper `sed -n` command lines are dropped;
     - P4's heading is `### P4 — HOLDS`, the skill's required form, where the evidence file read "HOLDS on (a) to (d)". The reason keeps the caveat that the run before the gate packet's commit decides (e);
     - it re-ran the guard on the clone for (e) before appending, as the skill directs for a check not yet run. That run showed 0 dead hashes and 0 dead links;
     - it added one sentence naming the source of the pasted output.
4. **Checks in the clone** ([02_clone-checks.txt](02_clone-checks.txt)).
   - **What changed.** `git status` shows only `docs/PREREGISTRATION.md` modified. The diff against the original HEAD is 187 insertions and 0 deletions.
   - **Nothing else.** The subject made no commit, tag, branch or stash, and left no untracked file.
   - **The checks.** The append-only check and `--check-verdicts` both exit 0.
   - **Nothing to discard.** The subject touched nothing else, so there was no finding to record and nothing to discard.
5. **The transfer** ([03_transfer.txt](03_transfer.txt)).
   - **The patch.** `git -C <clone> diff 09be5c9… -- docs/PREREGISTRATION.md` produced [append.patch](append.patch), and `git apply --check` then `git apply` applied it here.
   - **The bytes.** Both `PREREGISTRATION.md` files have the sha256 `6792dc562b4be688f840dda606b461a49224c4bf9467f7b51d7a7656cd7ff0fb`, and `cmp` exits 0.
   - **The checks here.** The append-only check and `--check-verdicts` both exit 0.
   - **The commit.** It is made with the noreply identity.

`SHA256SUMS` covers `outcome.jsonl` and `append.patch`.
