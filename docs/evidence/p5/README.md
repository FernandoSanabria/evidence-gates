# P5: size and speed (registered run)

## (a) Size of the installed plugin directory: HOLDS

- **The definition** was recorded in `docs/evidence/HOURS.md` before any install, in commit `b637351`:
  - the path `plugin details` reports, or else the single cache directory holding the plugin's `.claude-plugin/plugin.json`;
  - measured with `du -sk` exactly as found, `.git` included if present;
  - `du -sk` ≥ 977 falsifies;
  - two measurements, and the larger decides.
- **The two measurements:**

| when | `du -sk` | what it held |
|---|--:|---|
| right after the P1 install, before any session | 564 | no `.git`, no `__pycache__` ([../p1/05_p5a-first-measurement.txt](../p1/05_p5a-first-measurement.txt)) |
| after P2 | 568 | adds `scripts/__pycache__/gitcmd.cpython-311.pyc`, 4 KB ([01_p5a-second-measurement.txt](01_p5a-second-measurement.txt)) |

- **The deciding number is 568,** under 977, so HOLDS. Under the MiB reading (≥ 1024 falsifies) it also holds, so the two readings agree.
- **Next to it,** `git archive f10bf42…` gives 491,520 bytes.
- **Growth from the plugin's own runtime (`__pycache__`): 4 KB.** The hook's scripts import `gitcmd`, so Python writes its bytecode into the installed `scripts/` directory the first time the hook runs a check.
- **The install path.** In both measurements `plugin details` reported no path, and its two outputs are identical.
- **N:** 1 install.

## (b) Speed: HOLDS

The procedure was fixed before it ran. The driver is [p5b_timing.sh](p5b_timing.sh), and its full output is [02_p5b-timing.txt](02_p5b-timing.txt).

- **The checkout.** The untouched P4(a) clone, at the G8 merge, with `git status` clean.
- **The 30 docs.** The first 30 paths of `git ls-files '*.md' | LC_ALL=C sort`. None contains a pathspec glob character.
- **How the guard gets them.** As an explicit list of 30 repeated `--glob <path>` options. Every run reports "across 30 tracked docs".
- **The runs.** `/usr/bin/time -p python3 -I <guard> --glob …`, 5 runs, `real` seconds:

| docs | real (s), in run order | median |
|---|---|--:|
| 30 (registered) | 0.18, 0.14, 0.13, 0.13, 0.14 | **0.14** |
| 40 (supplementary; the default invocation, no options) | 0.14, 0.13, 0.16, 0.13, 0.13 | 0.13 |

- **Result.** A median of 0.14 s on 30 docs, against a falsifier of 2.0 s, so HOLDS.
- **Scale only.** The legacy script took 1.02 s in Stage 0 (Appendix B), over 40 docs, not 30. It is not compared with the registered number. The new guard resolves all hashes in one batched `git cat-file --batch-check`, where the legacy script starts one `git` process per hash.
- **N:** 5 timed runs.
