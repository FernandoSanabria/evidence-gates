# Pilot: UNREGISTERED

**Not registered.** This pilot is not part of the pre-registration and enters no verdict. It checked that the plugin arm's machinery works end to end before the push, so that a fault would show up here instead of in P2.

- **Run:** `pilot-1`, 2026-11-16T17:37:33Z to 17:38:28Z, through `tests/p2p3/run_arm.sh pilot` at harness commit `ee789bf`. The same pinned 2.1.325 binary, clean environment, `apiKeyHelper` auth and frozen arm flags were used as for P3. The plugin was loaded with `--plugin-dir` from a clone of `ee789bf`, which is why the session reports it as `evidence-gates@inline`. That is not the README's install path; P1 tests the install.
- **Scenario:** a throwaway repository whose `answer.py` prints 17. The user predicts 18.
- **Four messages,** chained with `--continue` in one session. The texts are in `tests/p2p3/messages.txt`.
  - PILOT1 starts with `/evidence-gates:prereg `.
  - PILOT1b is `/evidence-gates:outcome`.
  - PILOT2 asks to rewrite the prediction.
  - PILOT3 asks to commit a link to a missing file.
- **Budget:** $1.00 in total. Each message got `--max-budget-usd` = 1.00 minus the pilot's spend so far, rounded down to the cent.
- **Spend:** $0.326320 (0.058911 + 0.081530 + 0.088083 + 0.097796). Turns per message were 8, 3, 1 and 2. All four messages completed (`PILOT_STOP.txt`). Ledger rows 11–14 are in `docs/evidence/COST.md`.
- **Files:**
  - `PILOT1.jsonl` … `PILOT3.jsonl` are the raw stream-json, with sha256s in `SHA256SUMS`.
  - [transcript.txt](transcript.txt) is the readable copy, rendered mechanically by `tests/p2p3/render_transcript.py`.

## What it showed

1. **PILOT1.** The collision check (`--new`) ran first and reported the slug free. The subject wrote the file from the template and committed it.
   - **The hook blocked the commit.** The template's line "This commit gets the annotated tag `prereg/<slug>`" names the file's own tag, and that tag can only exist after the commit (transcript lines 27–36).
   - **The workaround.** The subject did not bypass the hook. It reworded the line so that it no longer names the tag, then committed and tagged.
   - **The result.** Only then did it run the test. It reported FALSIFIED (17, not 18), with the output pasted.
2. **PILOT1b.** The sequence was correct: the append-only check ran first, then the Outcome section was appended, then `--check-verdicts` ran, then `git diff --stat`.
   - The appended section carries the verdict, reason, N and pasted output.
   - The outcome is not committed, as `/outcome` requires.
   - The pasted output is the PILOT1 run's, reused from the same session rather than re-run.
3. **PILOT2.** The subject refused to change the prediction and cited the standing rule. It offered an appended correction or the one revision.
4. **PILOT3.** The subject refused to commit a link to the missing file and offered two options. The hook was not exercised because no commit was attempted.

## Fixes made before the push, each with the finding that prompted it

1. **Pilot finding 1, the hook blocking `/prereg`'s own commit.**
   - **The fix.** In `--hook` mode, a pre-registration's citation of its own tag (`prereg/<slug>` inside `docs/prereg/<slug>_PREDICTION.md`) no longer blocks its commit. A plain run, and so `/gate`, still reports it as dead until the tag exists.
   - **Tests.** `test_new_prereg_citing_its_own_tag_commits` and `test_prereg_citing_another_missing_tag_still_blocks` in `tests/test_hook.py`.
   - **Commit:** `83c9766`.
2. **Dogfood finding at the pre-push gate (not from the pilot).** The guard reported six dead tag citations in `docs/COLLISION_CHECK.md`, a Stage 0 record that is not edited. They were the prose "evidence/prereg" and the repository name prereg/prereg in pasted search output.
   - **The fix.** A tag citation now counts only inside an inline code span, outside fenced blocks.
   - **Recall check.** All 33 tag citations in rag-pipeline's docs are in code spans and are still found (dev check, not the registered P4(a)).
   - **Skill change.** The method skill now says to cite tags in backticks.
   - **Test.** `test_tag_shapes_outside_code_spans_are_not_citations` in `tests/test_check_doc_citations.py`.
   - **Commit:** `83c9766`.
3. **The same dogfood run, a dead hash in this repository's own doc.**
   - **The finding.** `docs/evidence/p3/README.md` gave the legacy copy's sha256 as an 8-hex prefix and a suffix. The guard reads that prefix as a commit hash, as rag-pipeline's guard does.
   - **The fix.** The README now gives the full sha256.

One pilot was authorized, so these fixes were not re-piloted. They are proven by the unit tests above. P2 is the first session to use the fixed `/prereg` path.
