#!/bin/bash
# P5(b) timing, as fixed in the plan before it ran. Run from the untouched P4(a) clone root.
set -u
G="/Users/akasha/Documents/Priority Projects/plugin-evidence-gates/scripts/check_doc_citations.py"
LIST="$1"   # where the 30 paths are written
echo "P5(b): timing on the untouched P4(a) clone"
echo "\$ date -u +%FT%TZ"; date -u +%FT%TZ
echo "\$ pwd; git rev-parse HEAD; git status --short (empty = clean)"; pwd; git rev-parse HEAD; git status --short; echo "(end)"
echo "\$ git ls-files '*.md' | LC_ALL=C sort | head -30"
git ls-files '*.md' | LC_ALL=C sort | head -30 > "$LIST"
cat "$LIST"
echo "count: $(wc -l < "$LIST" | tr -d ' '); paths with a pathspec glob character (*?[): $(grep -c '[][*?]' "$LIST")"
args=()
while IFS= read -r p; do args+=(--glob "$p"); done < "$LIST"
echo "== 30 docs: \$ /usr/bin/time -p python3 -I <new guard> --glob <p1> ... --glob <p30>   (5 runs)"
for n in 1 2 3 4 5; do echo "-- run $n"; /usr/bin/time -p python3 -I "$G" "${args[@]}"; echo "exit=$?"; done
echo "== 40 docs (supplementary): \$ /usr/bin/time -p python3 -I <new guard>   (5 runs, no options)"
for n in 1 2 3 4 5; do echo "-- run $n"; /usr/bin/time -p python3 -I "$G"; echo "exit=$?"; done
