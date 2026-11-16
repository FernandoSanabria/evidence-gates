# P1: install (registered run)

**Registered.** On a fresh profile with Claude Code 2.1.292 or later, the single command `claude plugin install evidence-gates --marketplace FernandoSanabria/evidence-gates` must:
- (a) exit 0;
- (b) make `/evidence-gates:prereg` available in the first session started afterwards: typed as a message, it runs and does not answer "Unknown command";
- (c) appear in `claude plugin details evidence-gates`, which lists the skill.

No other step is allowed.

Every command ran through `tests/p2p3/run_arm.sh cli`: the pinned 2.1.325 binary, the clean nine-variable environment, and the run's own HOME. The numbered `.txt` files hold each command with its full output.

## The steps

1. **Pin the commit** ([01_ls-remote.txt](01_ls-remote.txt)). `git ls-remote origin refs/heads/main` returned `f10bf4233a9899228faadc33157bfb092f2c4710`, the commit the owner pushed. That is what the install fetched and what `git archive` measures for P5(a).
2. **Create the profile** ([02_profile-after-version.txt](02_profile-after-version.txt)).
   - `run_arm.sh cli p1 <profile> --version` created the run and the profile, and printed `2.1.325 (Claude Code)`.
   - `--version` wrote nothing into the profile: `ls -laR` shows exactly one file, `settings.json` (68 bytes).
   - The owner's fallback (delete, then recreate without the binary) was not needed.
3. **Install, P1(a)** ([03_install.txt](03_install.txt)).
   - **Before.** `ls -laR` of the profile, taken immediately before the install in the same shell command, shows exactly `settings.json`. That file is the authentication prerequisite the pre-registration carves out (one key, `apiKeyHelper`). It is not an install step.
   - **The command.** The registered command ran byte for byte.
   - **Result.** It added the marketplace, installed `evidence-gates@evidence-gates` (scope: user) and exited 0. There was no prompt and no second command, and no file was edited.
4. **Listing, P1(b)** ([04_details.txt](04_details.txt)). `plugin details evidence-gates` lists 4 skills (`evidence-gates`, `gate`, `outcome`, `prereg`) and 1 PreToolUse hook. It reports no install path.
5. **The first session, P1(b).** The first session started in this profile is P2's T1 ([../p2/](../p2/README.md)).
   - Its init event lists `evidence-gates:prereg` among the slash commands, with the plugin `evidence-gates@evidence-gates`.
   - T1 began with `/evidence-gates:prereg `, and the command ran: the subject ran the plugin's collision check from the installed path, then wrote and committed the pre-registration.
   - "Unknown command" appears nowhere in `T1.jsonl`.
6. **P5(a), first measurement** ([05_p5a-first-measurement.txt](05_p5a-first-measurement.txt)), taken before any session and following the definition in `docs/evidence/HOURS.md`.
   - **Locating the directory.** `plugin details` reported no path, so the cache search applies. It found exactly one `.claude-plugin/plugin.json` named `evidence-gates`, under `plugins/cache/evidence-gates/evidence-gates/0.1.0`.
   - **Result.** `du -sk` gives **564**. The directory has no `.git`.
   - **Next to it,** `git archive f10bf42…` gives 491,520 bytes.
7. **Two-command fallback, UNREGISTERED** ([06_fallback-unregistered.txt](06_fallback-unregistered.txt)). On a second fresh profile, `plugin marketplace add FernandoSanabria/evidence-gates` and `plugin install evidence-gates@evidence-gates` both exited 0.

## Verdict: P1 HOLDS

(a) and (b) both happened, with no manual step. **N:** 1 fresh profile.

## Findings and disclosures

- **The install authenticated over SSH; it did not fall back to HTTPS.** This is resolved from raw output in [07_ssh-resolution.txt](07_ssh-resolution.txt), the owner's Ruling 1.
  - **The install's output.** It shows "Cloning via SSH: git@github.com:FernandoSanabria/evidence-gates.git", then "Clone complete", in both profiles. No failure, retry or HTTPS line appears.
  - **The key.** The run's HOME is empty, with no `.ssh`. OpenSSH takes `~/.ssh` from the account's home (`/Users/akasha`), not from `$HOME`. Run under exactly the cli mode's nine variables and working directory, with `BatchMode=yes`, `ssh -v -T git@github.com` read `/Users/akasha/.ssh/config`. GitHub accepted the account's key file `~/.ssh/id_ed25519` ("Authenticated to github.com … using publickey"; "Hi FernandoSanabria!").
  - **Implication.** The clean environment does not isolate SSH. The P1 install used the owner's own GitHub SSH key from disk. How the install behaves on a machine with no GitHub SSH key was not tested.
- **Harness fact, next to P1(a): cli mode against session mode.**
  - **Same variables.** Both call the runner's same `senv()`, so the variable set is identical: the nine allow-listed variables, with HOME and GIT_CONFIG_GLOBAL per run and CLAUDE_CONFIG_DIR the profile.
  - **Working directory.** cli mode runs in `<run>/work`, while a session runs in its repository.
  - **Output.** cli mode keeps no ledger row and no stream-json, because it starts no session.
  - The `envlist` output for P1 and P2 is in the same file.
- **The README and the registered command.** P1 ran the command as quoted in the pre-registration (the owner's ruling). The README's Install section is written afterwards from that command.
  - My question to the owner wrongly said that the README at `f10bf42` held no install command. In fact its opening block already held the same string, byte for byte; only its Install *section* was unwritten.
  - `tests/test_readme.py` asserts the equality, and it passes on the pushed README as well.
