#!/usr/bin/env bash
# Scrub the staged diff before any commit that touches docs/evidence/. Prints every result; exits 1 if any check fails.
# The owner's rules (2026-11-16): no work-email domain; no e-mail-shaped string outside the exact seven-string
# allow-list; no key-shaped string (the literal `sk-ant-` pattern text is only counted); no token values.
set -u
ALLOW=(evidence-gates@evidence-gates noreply@anthropic.com cc-plugin-agents-md@builtin cc-plugin-plugin-authoring@builtin
       cc-plugin-privacy@builtin cc-plugin-telemetry@builtin evidence-gates@inline)
diff=$(git diff --cached)
fail=0

n=$(printf '%s\n' "$diff" | grep -ic fullstacklabs)
echo "fullstacklabs: $n (must be 0)"; [ "$n" -eq 0 ] || fail=1

raw=$(printf '%s\n' "$diff" | grep -Eo '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+' | grep -v users.noreply.github.com | sort -u)
echo "e-mail-shaped strings, raw (after the noreply filter):"; printf '%s\n' "$raw" | sed '/^$/d; s/^/  /'
args=(); for a in "${ALLOW[@]}"; do args+=(-e "$a"); done
filtered=$(printf '%s\n' "$raw" | sed '/^$/d' | grep -v -x -F "${args[@]}")
echo "e-mail-shaped strings outside the seven-string allow-list (must be empty):"; printf '%s\n' "$filtered" | sed '/^$/d; s/^/  /'
[ -z "$filtered" ] || fail=1

lit=$(printf '%s\n' "$diff" | grep -c 'sk-ant-')
key=$(printf '%s\n' "$diff" | grep -cE 'sk-ant-[A-Za-z0-9_-]{20,}')
echo "literal sk-ant- lines (pattern text, logged only): $lit; key-shaped sk-ant-[A-Za-z0-9_-]{20,}: $key (must be 0)"
[ "$key" -eq 0 ] || fail=1

for p in 'MESSAGING_TOKEN=[A-Za-z0-9]' 'OAUTH_TOKEN=[A-Za-z0-9]' 'Bearer [A-Za-z0-9._~+/-]{16,}'; do
  c=$(printf '%s\n' "$diff" | grep -cE "$p")
  echo "$p: $c (must be 0)"; [ "$c" -eq 0 ] || fail=1
done
echo "scrub verdict: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
