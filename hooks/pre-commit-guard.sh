#!/bin/sh
# evidence-gates PreToolUse hook (Bash, `if: Bash(git *)`): before Claude runs a `git commit`, check the docs'
# citations and the pre-registrations. Exit 0 allows the tool call, exit 2 blocks it, and stderr tells Claude why.
#
# Fail closed: a commit is blocked when python3 is missing, when the hook input cannot be read, or when a check
# crashes. A command without the word "commit" exits 0 at once, without starting Python, so a broken Python never
# blocks anything but commits. Scope: only commits Claude runs through its Bash tool; commits made elsewhere are not seen.
input=$(cat)
case $input in
  *commit*) ;;
  *) exit 0 ;;
esac
root=${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
if ! command -v python3 >/dev/null 2>&1; then
  echo "evidence-gates: python3 was not found, so the doc-citation and pre-registration checks cannot run." >&2
  echo "This git commit is blocked (fail closed). Install python3 3.8 or later, or disable the plugin." >&2
  exit 2
fi
printf '%s' "$input" | python3 -I "$root/scripts/check_doc_citations.py" --hook
docs=$?
printf '%s' "$input" | python3 -I "$root/scripts/check_prereg_append_only.py" --hook
prereg=$?
if [ "$docs" -eq 0 ] && [ "$prereg" -eq 0 ]; then
  exit 0
fi
exit 2
