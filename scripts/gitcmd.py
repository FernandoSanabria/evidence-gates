"""Find the `git commit` invocations in a shell command string, as a PreToolUse hook sees it.

Shared by check_doc_citations.py and check_prereg_append_only.py (both add this directory to sys.path themselves,
because they run under `python3 -I`). Standard library only.
"""
from __future__ import annotations

import os
import re
import shlex

# Split on the shell's command separators. Quoting is handled by shlex inside each segment; a separator inside quotes
# can split a segment wrongly, which errs toward reporting a commit (the safe side for a guard).
_SEP = re.compile(r"&&|\|\||;|\||\n|\$\(|`|\(|\)")
_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}


def commit_dirs(command: str, cwd: str) -> list[str]:
    """Directories in which `command` runs `git … commit`, resolved against `cwd`. Empty when there is none.

    Recognises `git commit`, `git -C <dir> commit`, `git -c k=v commit`, `git --no-pager commit`, leading `VAR=value`
    assignments, and commits inside compound commands. A segment that shlex cannot parse but mentions both `git` and
    `commit` is reported as a commit in `cwd`, so an unparseable command cannot slip past the guard.
    """
    out: list[str] = []
    for seg in _SEP.split(command or ""):
        if "commit" not in seg or "git" not in seg:
            continue
        try:
            words = shlex.split(seg, posix=True)
        except ValueError:
            out.append(cwd)
            continue
        i = 0
        while i < len(words) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[i]):
            i += 1
        while i < len(words) and os.path.basename(words[i]) != "git":
            i += 1
        if i >= len(words):
            continue
        i += 1
        where = cwd
        while i < len(words) and words[i].startswith("-"):
            opt = words[i]
            if opt in _OPTS_WITH_VALUE and i + 1 < len(words):
                if opt == "-C":
                    where = os.path.join(where, words[i + 1])
                i += 2
            else:
                i += 1
        if i < len(words) and words[i] == "commit":
            out.append(os.path.normpath(where))
    return out
