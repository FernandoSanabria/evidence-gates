# P4: the guard (registered run)

The guard is `scripts/check_doc_citations.py` at `f10bf42`, the pushed commit. Before anything ran, its working-tree bytes and those of `scripts/gitcmd.py`, the module it imports, were compared with that commit by sha256. Both are equal ([00_guard-bytes.txt](00_guard-bytes.txt)). Every command and its full output is in the numbered `.txt` files next to this README.

## (a) Parity: HOLDS

- **The clone.** A fresh clone of rag-pipeline from GitHub, detached at the G8 merge Appendix B names (PR #41) ([01_clone.txt](01_clone.txt)). It matches Appendix B: 105 commits, not shallow, 17 tags, 40 tracked `*.md`. The legacy guard there has the sha256 Appendix B records.
- **The run** ([02_parity.txt](02_parity.txt)). Both scripts ran from the clone root with no options, in the same form as Appendix B:
  - `python3 -I scripts/check_doc_citations.py`, the legacy script, in the clone;
  - `python3 -I ".../plugin-evidence-gates/scripts/check_doc_citations.py"`, the new script.
- **The result.** Both print exactly the two registered lines: `OK: all 100 cited commit hashes across 40 tracked docs resolve.` and `OK: all 319 relative markdown links across 40 tracked docs resolve.`
  - A byte comparison prints `True` for legacy against registered, new against registered, and new against legacy.
  - Both exit 0.
  - The new checks report on their own lines after these two, as observations outside (a): 33 tags exist, every cited commit is durable, and 0 tokens were exempted.
- **N:** 1 commit, 40 docs.

## (b) A dead hash goes red: HOLDS

- **The setup** ([03_planted-dead-hash.txt](03_planted-dead-hash.txt)). A `cp -R` copy of the clone was used, so the P4(a) and P5(b) clone stays untouched.
- **The planted line.** A random 40-hex hash was generated, and `git cat-file -e <hash>^{commit}` showed it does not resolve (exit 128). One line citing it was then appended to `ARCHITECTURE.md`, the first `*.md` path in sorted order, as its line 320.
- **The result.** The guard, with no options, exits 1 and prints `ARCHITECTURE.md:320: <hash>`.
- **A note on the file.** The echoed `printf` command in that file shows its `\n` as a line break, because zsh's `echo` expands it. The command ran as written in the plan.

## (c) Exemptions: HOLDS

`python3 -m unittest tests.test_check_doc_citations -v` ran 29 tests, all OK ([04_exemption-tests.txt](04_exemption-tests.txt)).

- **Each exemption class.** Actions run IDs, UUIDs in any case, AWS case IDs and other-repository URLs each have a test.
- **The negative controls:**
  - a real dead hash beside an exempt form still fails;
  - an all-digit 8-character token outside any context is still a hash;
  - a hash in a URL to this repository's own remote is still checked;
  - a resolving token is never exempted.

## (d) The negative proof: HOLDS

`--negative-proof` planted a random dead hash in a temporary repository and exited 1: "the guard went red … Exit 1, as required" ([05_negative-proof.txt](05_negative-proof.txt)).

## Note A: row 6 re-coded with this plugin's guard

The owner's Note A: once (a) passes, row 6 is re-coded on both arms' final repositories with the new guard, and any difference is a finding.

- **The coder runs.** `code_rows.py` ran with `scripts/check_doc_citations.py` as the oracle, on copies of both evidence directories, so the original `coding.json` files were not overwritten. The results are `coding-newguard.json` in `docs/evidence/p3/` and `docs/evidence/p2/`.
- **The direct runs.** Both oracles were also run directly on a copy of each arm's final snapshot, with exit codes ([07_noteA-oracles-on-final-repos.txt](07_noteA-oracles-on-final-repos.txt)).

| arm | legacy oracle | new oracle |
|---|---|---|
| P3, without evidence-gates | FAIL: `README.md:5` dead link, exit 1 | FAIL: the same dead link, exit 1 |
| P2, with evidence-gates | PASS: 0 dead links, exit 0 | PASS: 0 dead links, exit 0 |

- **No difference.** Rows 1–5 are identical across the two oracles in both arms. P3's provisional row 6 stands.
- **One observation, outside row 6.** On P3's final repository the new guard's durability check warns that the commit the control cited in its README is reachable from neither main nor a tag. That is P3's row-5 failure, seen by the guard.
- **One invocation error, disclosed.** My first Note A run gave the oracle as a relative path. The coder runs it from inside a copy of the snapshot, where that path does not exist, and it ignores the oracle's exit code, so the empty output read as 0 dead links. Those outputs were never committed. The runs above use absolute paths, and every recorded `oracle_stdout` is non-empty. The coder's fail-open behaviour is reported in `docs/evidence/p2/README.md`.

## (e) Dogfood: preview here; the registered run is in the GATE packet

A preview at `b637351` reports 0 dead hashes, 0 dead links and 0 dead tags ([06_dogfood-preview.txt](06_dogfood-preview.txt)). The registered run is taken on the repository as it stands when the packet is written, immediately before the packet commit. That output is pasted in the packet, and if the two differ, the packet-time run decides.
