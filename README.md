# evidence-gates

No silent green: a check that did not run, or ran without pasted output, counts as not run.

```bash
claude plugin install evidence-gates --marketplace FernandoSanabria/evidence-gates
```

*Unverified until P1.* Needs Claude Code 2.1.292 or later. On an older CLI: `claude plugin marketplace add FernandoSanabria/evidence-gates && claude plugin install evidence-gates@evidence-gates` (also unverified until P1).

> **Status: pre-build scaffold.** Nothing here is a claim yet. The pre-registration is [docs/PREREGISTRATION.md](docs/PREREGISTRATION.md). This README is filled in after P2 to P4, from their artifacts, and the table below stays empty until then.

## What this adds

<!-- The cells are filled at Stage 1 from the P2 and P3 transcripts and from nothing else. -->

| | Coding agent as shipped | With evidence-gates |
|---|---|---|
| Prediction written before the run | | |
| Outcome editable after | | |
| Revisions bounded | | |
| Claims carry pasted output | | |
| Cited commits survive squash-merge | | |
| Dead links fail | | |

## What it does not do

- It does not run your evals.
- It does not judge quality.
- It does not replace review.

## Case study: rag-pipeline

[rag-pipeline](https://github.com/FernandoSanabria/rag-pipeline) is the case study. Three files to read, pinned to [one commit](https://github.com/FernandoSanabria/rag-pipeline/commit/92cff85):

- [`eval/g8_PREDICTION.md`](https://github.com/FernandoSanabria/rag-pipeline/blob/92cff85/eval/g8_PREDICTION.md): a pre-registration, with its outcome appended.
- [`eval/g11_design.md`](https://github.com/FernandoSanabria/rag-pipeline/blob/92cff85/eval/g11_design.md): the gate rulings, in the section "GATE 1 decisions".
- [`scripts/check_doc_citations.py`](https://github.com/FernandoSanabria/rag-pipeline/blob/92cff85/scripts/check_doc_citations.py): the guard this plugin generalizes.

<!-- The pin is stated at Stage 1: the first main commit after rag-pipeline PR #42 merged, else the G8 merge. PR #42 merged on 2026-10-13 as the pinned commit, and all three paths were checked there on 2026-10-14. Re-check at Stage 1. -->

## Install

Written at Stage 1: requirements (Claude Code 2.1.292 or later for the one-line install, 2.1.295 or later for the fail-closed hook, git, python3), scopes, update, uninstall.

## Commands

Written at Stage 1: `/evidence-gates:prereg`, `/evidence-gates:gate` and `/evidence-gates:outcome`.

## The method, in one page

Written at Stage 1, as a link to the skill that carries it (`skills/evidence-gates/SKILL.md`).

## License

MIT. See [LICENSE](LICENSE).
