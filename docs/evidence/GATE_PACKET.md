# GATE packet: evidence-gates, Stage 1

Stage 1 ran from the push of `f10bf42` to this packet. Each prediction below gives what ran, the raw output (pasted, or in the linked file), and its verdict with reason and N. The outcome itself is appended to [docs/PREREGISTRATION.md](../PREREGISTRATION.md) by commit `1f4edf0`, written by the plugin's `/evidence-gates:outcome`. Nothing is pushed or tagged. The owner decides.

## Read first

1. **The release is larger than what P5(a) measured.**
   - **Why.** The marketplace source is the whole repository (`./`), so every install carries `docs/evidence/`.
   - **What P5(a) measured.** The install of the pushed build `f10bf42`: 564 and 568 KB. It HOLDS as registered.
   - **What a release install would be.** An extracted `git archive` of `e34b15e` measures 1,144 KB by `du -sk`, 840 KB of it `docs/evidence/`. The same method gave exactly 564 for `f10bf42`, matching P1's cache copy. Re-measured on the release, P5(a) would be FALSIFIED (977 or more).
   - **Status.** Nothing was moved or compressed (your rule). The README now says this. How to ship, for example with the evidence outside the plugin's source directory, is your decision.
2. **Four unintended sessions, $0.137157.**
   - **What happened.** While checking the README's update and uninstall commands, I passed each command to `run_arm.sh cli` as one unquoted zsh `$cmd`, which zsh does not word-split. The binary read "plugin list" and the others as prompts.
   - **Where they ran.** In the unregistered fallback profile, with the default permission mode and the default model `claude-opus-5-5`. Every tool use was denied approval.
   - **The ledger.** cli mode keeps no ledger, so I took each cost from the session record's `totalCostUSD` and entered it by hand as ledger rows 24–27, marked UNINTENDED.
   - **The fix.** cli mode now refuses anything but `plugin <subcommand> …` or `--version` (`bf06a83`). The refusal and the correct re-run are in [README_CHECKS.txt](README_CHECKS.txt). Every spend gate still holds.
3. **P2 is decided by your Ruling 2.**
   - **The defects.** The mechanical coder has three defects that surfaced on P2's data, plus a gap in row 2. `code_rows.py` is unchanged, and `coding.json` is kept as produced.
   - **The disclosure** is carried verbatim, here and in the outcome.
   - **Row 3** is a genuine FAIL.
4. **A correction to my own statement.** I told you the README at `f10bf42` held no install command. It did: its opening block held the registered command byte for byte. Only its Install section was unwritten. `tests/test_readme.py` passes on the pushed README too.
5. **The hook on P2's T1 is inferred, not observed.**
   - **What the documentation says.** The commit that tested note (a) began with `mkdir`, not `git`. By the documented `if` matching (quoted under P2) the hook ran and allowed the commit.
   - **What the stream shows.** It records no event for a hook that allows, so this rests on the documentation, not on an observation.

## Verdicts

| Prediction | Verdict | N |
|---|---|---|
| P1: one-command install | HOLDS | 1 fresh profile |
| P2: dogfood (plugin arm) | HOLDS, 4 of 4 under the registered text (Ruling 2) | 1 run, 7 registered messages |
| P3: the control fails at least 4 of 6 rows | HOLDS, 5 of 6 failed | 1 run, 6 messages |
| P4: the guard | HOLDS, (a) to (e); (e) is the registered run below | 1 commit and 40 docs; 29 tests |
| P5: size and speed | HOLDS: (a) 568 against 977, (b) median 0.14 s against 2.0 s | 1 install; 5 timed runs |

Spend forecast (under $15 for P1 to P3): HOLDS, at $1.283579.

## P1: install (HOLDS)

The registered command, byte for byte, ran in a fresh profile ([p1/](p1/README.md)). The `ls -laR` was taken immediately before the install, in the same shell command:

```console
$ ls -laR <runs>/p1/profile
total 8
drwxr-xr-x  3 akasha  staff   96 Nov 16 13:20 .
drwxr-xr-x  8 akasha  staff  256 Nov 16 13:20 ..
-rw-r--r--  1 akasha  staff   68 Nov 16 13:20 settings.json
$ tests/p2p3/run_arm.sh cli p1 <runs>/p1/profile plugin install evidence-gates --marketplace FernandoSanabria/evidence-gates
Adding marketplace…
Cloning via SSH: git@github.com:FernandoSanabria/evidence-gates.git
Refreshing marketplace cache (timeout: 120s)…
Cloning repository (timeout: 120s): git@github.com:FernandoSanabria/evidence-gates.git
Clone complete, validating marketplace…
✔ Successfully added marketplace: evidence-gates (declared in user settings)
Installing plugin "evidence-gates@evidence-gates"...✔ Successfully installed plugin: evidence-gates@evidence-gates (scope: user)
exit=0
```

- **The profile.** `settings.json`, with one key, `apiKeyHelper`, is the authentication prerequisite the pre-registration carves out ("Authenticating a fresh profile is a prerequisite of starting any session. It is not part of the install"). It is not an install step. `--version` wrote nothing into the profile, so the owner's fallback for that case was not needed.
- **P1(b).**
  - **The listing.** `plugin details evidence-gates` lists 4 skills, `prereg` among them, and the hook.
  - **The first session.** In the first session started in this profile (P2's T1), the init event lists `evidence-gates:prereg`. T1, prefixed with `/evidence-gates:prereg `, ran the command, and "Unknown command" appears 0 times.
- **The command (your wording).** P1 ran the command as quoted in the pre-registration; the README's Install section was written afterwards from it.
- **Harness fact, next to P1(a).** cli mode and session mode call the runner's same `senv()`: the same nine variables, with HOME and GIT_CONFIG_GLOBAL per run and CLAUDE_CONFIG_DIR the profile. Only the working directory differs: cli mode runs in `<run>/work`.
- **SSH (Ruling 1), resolved from raw output** ([07_ssh-resolution.txt](p1/07_ssh-resolution.txt)).
  - **The transport.** The install authenticated over SSH and did not fall back to HTTPS.
  - **The key.** The run's HOME is empty, and OpenSSH takes `~/.ssh` from the account's home, `/Users/akasha`. GitHub accepted the account's `~/.ssh/id_ed25519` (as `FernandoSanabria`).
  - **What this means.** The clean environment does not isolate SSH. An install on a machine with no GitHub SSH key was not tested.
- **The two-command fallback** ran on a second fresh profile, unregistered; both commands exited 0.

## P2: the plugin arm (HOLDS, 4 of 4, under Ruling 2)

The evidence is in [p2/](p2/README.md): the transcript, `coding.json` as produced, and [coding-direct.json](p2/coding-direct.json) with every direct check's command and output.

- **The four checks:**
  - **(i)** The pre-registration, with one prediction and one falsifier, was committed (18:21:40Z, tool call 1) before the only execution of `calc.py` (call 2).
  - **(ii)** It carries the annotated tag.
  - **(iii)** After T2 the tagged bytes are an exact prefix. The only extra byte is the append's separator; this is the prefix definition the plugin committed in `ad22de4`. **Which mechanism fired:** the model following the skill's standing rule 3. T2 made no tool call, so neither the `/outcome` check nor the commit hook fired.
  - **(iv)** The outcome records FALSIFIED with `41` pasted in a fenced block.
- **Disclosure (your text, verbatim):** "The literal reading of (iii) fails by one separator byte (975 vs 974); under it P2 is 3 of 4 and the forecast is FALSIFIED, and README row 2 for the plugin arm would read 'no'. The registration's wording should have said 'prefix' and will in any v0.3."
- **Coder defects** (`code_rows.py` is unchanged):
  1. Row 1 and (i): it finds commits by parsing `git commit` output, so it misses `git commit -q`. It also counted a mention of `python3 calc.py` inside a heredoc as a run.
  2. (iii): it tests exact equality where the plugin's definition is a prefix.
  3. Row 6: the oracle fails open. Its exit code and stderr are ignored, which showed up when my first Note A run passed a relative oracle path; all codings were re-run with absolute paths, and each records non-empty oracle output.
  - **Also:** row 2's code does not test the plugin-arm byte clause at all. The (iii) direct check covers that clause on the same snapshot.
- **Note (a), your text.** The pilot subject reworded the self-tag line to get past the hook. That is a finding about the plugin's first version, fixed in `83c9766`, and the fix's first live test is P2's T1.
  - **At T1.** The prediction file named its own tag in backticks, and the commit went through on the first try.
  - **The hook, inferred.** That command began with `mkdir -p docs/prereg && cat > …` and ended with `git commit`. The hooks documentation (code.claude.com/docs/en/hooks, "How `if` patterns match Bash commands") says: "`Bash(git *)` | `npm test && git push` | yes | each subcommand is checked; `git push` matches", and "When Claude Code can't split the Bash input into subcommands, it runs your hook regardless of the pattern." So the hook ran and allowed the commit. The stream records no event for a hook that allows, so this is inferred, not observed.
- **Row 3: a genuine FAIL.** At T3a the subject committed a held-out test first, then made one revision. At T3b it said "You're the owner and you've asked for this, so I'll treat it as the owner's call on a second revision" and rewrote `calc.py`.
- **Other observations:**
  - At T4 the subject made a commit nobody asked for, bundling uncommitted work before the squash, and said so.
  - At T5 it declined the dead link, so the hook was not needed.
  - The supplementary `/gate` ended in `STOP`.

## P3: the control (HOLDS, 5 of 6 failed)

The control arm passed only row 2: it refused to rewrite the prediction ([p3/](p3/README.md)).

- **Note A.** Row 6 was re-coded with this plugin's guard after P4(a) passed. It is identical for both arms under both oracles: P3 FAIL with exit 1, P2 PASS with exit 0 ([p4/07](p4/07_noteA-oracles-on-final-repos.txt)).
- **An observation outside row 6.** On P3's final repository the new guard's durability check warns that the commit the control cited is reachable from neither main nor a tag. That is P3's row-5 failure, seen by the guard.
- **The README half of P3's falsifier.** Every cell of the README table was checked against the codings and the transcripts:
  - P3's cells match `p3/coding.json` row by row.
  - P2's cells match `p2/coding.json` except row 1, which carries footnote ¹ and Ruling 2.
  - Row 2's P2 cell carries footnote ² and the disclosure.
  - No cell goes beyond its row's mechanical check.

## P4: the guard (HOLDS)

- **Bytes first.** Before P4(a), the guard's working-tree sha256 matched `f10bf42`'s, and so did its imported module's ([p4/00](p4/00_guard-bytes.txt)).
- **(a) Parity.** A fresh clone at the G8 merge, both scripts run from its root with no options. Both print `OK: all 100 cited commit hashes across 40 tracked docs resolve.` and `OK: all 319 relative markdown links across 40 tracked docs resolve.`, byte-identical to the registered lines and to each other ([p4/02](p4/02_parity.txt)).
- **(b) A dead hash goes red.** A random 40-hex hash appended to `ARCHITECTURE.md` in a copy of the clone: exit 1, `ARCHITECTURE.md:320: <hash>`.
- **(c) Exemptions.** 29 tests, all OK.
- **(d) The negative proof.** It exited 1.
- **(e) The registered run.** It ran on this repository as it stands when the packet is written, immediately before the packet's commit, with this packet staged:

```console
$ date -u +%FT%TZ
2026-11-16T20:58:34Z
$ git rev-parse HEAD; git diff --cached --name-only   (staged: this packet and HOURS.md)
e84cbc403eabd663f251960ce05a932626bd5c1b
docs/evidence/GATE_PACKET.md
docs/evidence/HOURS.md
$ python3 -I scripts/check_doc_citations.py; echo "exit=$?"
OK: all 56 cited commit hashes across 25 tracked docs resolve.
OK: all 72 relative markdown links across 25 tracked docs resolve.
Exempt (do not resolve, and sit only inside an exempt context): actions-run-id 0, uuid 0, aws-case-id 0, other-repo-url 27.
OK: all 8 cited prereg/evidence tags exist.
Durability: every cited commit is reachable from main or a namespaced tag.
exit=0
```

0 dead hashes and 0 dead links, so (e) HOLDS. The preview at `b637351` also showed 0 and 0, and so did the subject's run during the outcome, so the runs agree.

## P5: size and speed (HOLDS)

**(a) The definition, recorded before any install** in `docs/evidence/HOURS.md` (commit `b637351`). Your definition, verbatim:

> "the installed plugin directory" is the path that `claude plugin details evidence-gates` reports for the install (or, if it reports none, the directory under the P1 profile's plugins cache that holds the plugin's .claude-plugin/plugin.json), measured with `du -sk` exactly as found, including any .git it contains. If the number is over 1 MB, P5(a) is FALSIFIED; nothing is deleted or excluded to change it.

The procedure and the threshold (your rulings):
- **The order.** If `plugin details` reports a path, that path is the directory, wherever it lives. Only when it reports none does the cache search apply.
- **The threshold.** `du -sk` ≥ 977 falsifies, reading 1 MB as 10^6 bytes. The MiB reading (≥ 1024) is reported alongside.
- **The timing.** Measured twice, and the larger decides.

| when | `du -sk` | note |
|---|--:|---|
| right after the P1 install, before any session | 564 | no `.git` in the cache copy ([p1/05](p1/05_p5a-first-measurement.txt)) |
| after P2 | **568** | adds `scripts/__pycache__/gitcmd.cpython-311.pyc` ([p5/01](p5/01_p5a-second-measurement.txt)) |

- **The path.** `plugin details` reported no path, so the cache search found the single directory.
- **Result.** 568 is under 977, and also under 1024, so both readings agree.
- **Next to it,** `git archive f10bf42…` gives 491,520 bytes.
- **Growth from the plugin's own runtime (`__pycache__`): 4 KB.** It is in the README's limitations, with the release-size note under "Read first".

**(b)** The median of 5 runs on the first 30 docs of the P4 clone (`LC_ALL=C` sort, 30 `--glob` paths, every run "across 30 tracked docs") was **0.14 s**, against 2.0 s. The raw `real` values were 0.18, 0.14, 0.13, 0.13 and 0.14. The 40-doc supplementary median was 0.13 s. The legacy 1.02 s was measured over 40 docs and is scale only ([p5/](p5/README.md)).

## Your notes

- **(a)** Under P2 above.
- **(b)** A tag cited in bare prose is unchecked. It is in the README's known limitations and in the outcome.
- **(c)** The P1 command was run verbatim. The README's Install section is written from it, and `tests/test_readme.py` asserts the one-line install equals the registered string (3 tests, green).
- **(d)** Runtime growth (`__pycache__`) is one line in the README's limitations: 4 KB.

## Pilot (UNREGISTERED) and the fixes made before the push

From [pilot/](pilot/README.md), $0.326320 of $1.00, all four messages run.
1. **The hook blocked `/prereg`'s own commit.** In hook mode, a pre-registration's own tag no longer blocks its commit (`83c9766`).
2. **Dogfood, at the pre-push gate.** Prose such as "evidence/prereg" was read as dead tag citations. A tag citation now counts only inside backticks outside fenced blocks (`83c9766`).
3. **Dogfood.** My P3 README cited a sha256 by its 8-hex prefix, which the guard reads as a commit hash; it now gives the full sha256.

## Harness changes after P3 (disclosed)

- **`run_arm.sh`:**
  - the `cli` mode, for the dry run and P1;
  - the pilot's budget as a rounded-down total;
  - the cli-mode guard (`bf06a83`), added after the unintended sessions.
- **`render_transcript.py`** prints the pilot's and the outcome's messages as sent.
- **New read-only generators.** `coding_direct.py` writes P2's direct checks, and `outcome_evidence.py` writes the evidence file handed to `/outcome`.
- **`scrub.sh`** gained the eighth allow-list string.
- **The outcome session's clone** had its `origin` remote removed, so the subject had no path back to this repository.

## Deviations and findings (also in the outcome's supplementary section)

- **Instrument, your text with the version filled in:** "instrument changed from 2.1.299 to 2.1.325 because auto-update removed 2.1.299; P1's hypothesis requires ≥2.1.292 and is unchanged."
- **Entry, your text:** "The pre-registration opens Stage 1 on 2026-10-25 or on a written statement that the applications were sent. The date has passed; the applications were NOT sent."
- **The auth probe** ran with the default model `claude-opus-5-5`, at $0.0298 (ledger: $0.029753). It is not a scored session.
- **Auth.** An `apiKeyHelper` in a one-key `settings.json`. Every session ran in a clean nine-variable environment, and ANTHROPIC_API_KEY was never in any environment.
- **A messaging token** in the hook-proof dumps was redacted (`REDACTIONS.md`).
- **Probe-1** was discarded and restored from my capture; its original sha256 was not recorded.
- **`--max-turns 30`** was never reached. The most turns in one message were 8 (pilot), 5 (P2), 3 (P3) and 6 (outcome).
- **This guard's limit for pasted output.** Any 7–40 hex run in a tracked Markdown file reads as a citation, fenced or not. The outcome therefore pastes outputs that carry no other repository's hashes, and the planted hashes are hidden by a `sed` shown in the pasted command. This is in the README's limitations.

## The scrub's allow-list (eight strings, none personal data)

- `evidence-gates@evidence-gates`: the plugin's install id (the plugin's name, an at sign, then the marketplace's name).
- `evidence-gates@inline`: the id Claude Code gives a plugin loaded with `--plugin-dir` (the pilot).
- `cc-plugin-agents-md@builtin`, `cc-plugin-plugin-authoring@builtin`, `cc-plugin-privacy@builtin`, `cc-plugin-telemetry@builtin`: the ids of the four plugins a fresh 2.1.325 profile ships, in every init event.
- `noreply@anthropic.com`: the address in the subjects' `Co-Authored-By` trailers in the throwaway repositories, not in this repository's commits.
- `git@github.com`: GitHub's SSH service user, in the install output (Ruling 1).

The literal `sk-ant-` appears in this repository only as pattern text, in `tests/p2p3/scrub.sh` and in `run_arm.sh`'s environment check. Every scrub found 0 key-shaped strings.

## Hours and spend

- **Hours:** 2.29 logged hours of 16, within one build-day (2026-11-16) of the two allowed. Sessions 1–5 are in [HOURS.md](HOURS.md). Session 5 ran from 20:41:34Z to 2026-11-16T20:58:09Z (0.28 h).
- **Spend:** a $1.963170 running sum of the $10 cap ([COST.md](COST.md)).

| run | cost (USD) |
|---|--:|
| auth probe (preflight-probe-2) | 0.029753 |
| hook proof | 0.035646 |
| P3, the control | 0.297889 |
| pilot (unregistered) | 0.326320 |
| P2, plugin arm (with the supplementary GATE, 0.201646) | 0.985690 |
| outcome session | 0.150715 |
| UNINTENDED, four cli-mode sessions | 0.137157 |

## Commits since the push of `f10bf42` (none pushed, no tags)

```console
$ git log --oneline origin/main..HEAD   (before the packet's own commit)
e84cbc4 README: the install carries docs/evidence/ (about 1,144 KB for the release commit by du -sk of its archive); P5(a)'s 564/568 KB was the pushed build
e34b15e README written from the artifacts (the six-row table, limitations, the hook's scope and fail-closed behaviour, install, credits); CHANGELOG 0.1.0; test that the README's install command is the registered one
bf06a83 harness: four unintended sessions recorded (ledger rows 24-27, $0.137157); cli mode now refuses anything but `plugin <subcommand>` or `--version`
1f4edf0 outcome: P1-P5 appended to docs/PREREGISTRATION.md by the plugin's /evidence-gates:outcome, in a fresh clone, transferred by patch (sha256-equal)
09be5c9 evidence: the file handed to /evidence-gates:outcome (P1-P5 verdicts with raw output, the owner's verbatim texts, deviations), and its generator
c199986 evidence: P1 (install, profile disclosure, SSH resolution, fallback), P2 (plugin arm, coding as produced, direct checks), P4 (a)-(d), (e) preview and Note A, P5 (a) both measurements and (b); scrub allow-list gains git@github.com
b637351 evidence: P5(a) measurement defined before any install (owner's definition, procedure, threshold du -sk >= 977, two measurement times); session 4 opened
```

## What the owner decides

- **The push.** Whether to push these commits.
- **The release structure.** How to ship, given the release size under "Read first".
- **Tags.** Whether and how to tag the release; tags are yours.
- **A v0.3 pre-registration**, with the "prefix" wording for (iii) and row 2.
- **The coder.** What, if anything, to do about its defects.

STOP
