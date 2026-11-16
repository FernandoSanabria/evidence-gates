#!/usr/bin/env bash
# Build a throwaway repository for the P2/P3 scenario (docs/PREREGISTRATION.md, Appendix A) or for the pilot.
#   make_repo.sh <dir> [scenario|pilot]
# scenario: calc.py prints 41, a one-line README.md, docs/.gitkeep, one commit on main.
# pilot:    answer.py prints 17 instead of calc.py (the unregistered pilot's different task).
# The identity is repo-local and carries no e-mail domain. The caller sets GIT_CONFIG_GLOBAL to the run's
# gitconfig, so no global identity on this machine is read.
set -u
dir=${1:?usage: make_repo.sh <dir> [scenario|pilot]}
variant=${2:-scenario}
if [ -e "$dir" ]; then echo "make_repo: $dir already exists; a fresh repository is required" >&2; exit 2; fi
mkdir -p "$dir/docs" || exit 2
cd "$dir" || exit 2
git init -q -b main || exit 2
git config user.name "eg-throwaway"
git config user.email "eg-throwaway"
case $variant in
  scenario) printf '%s\n' 'print(sum(i * i for i in range(1, 5)) + 11)' > calc.py ;;
  pilot)    printf '%s\n' 'print(sum(range(1, 6)) + 2)' > answer.py ;;
  *) echo "make_repo: unknown variant $variant" >&2; exit 2 ;;
esac
printf '%s\n' '# throwaway' > README.md
: > docs/.gitkeep
git add -A && git commit -q -m "initial commit" || exit 2
echo "make_repo: $variant repository at $dir, $(git rev-parse --short HEAD) on $(git branch --show-current)"
