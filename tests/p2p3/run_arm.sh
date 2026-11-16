#!/usr/bin/env bash
# evidence-gates harness runner: every preflight and scored `claude -p` session goes through this script.
#
#   run_arm.sh envlist   <run-id>                         print the session environment (no secrets in it)
#   run_arm.sh probe     <run-id> <evidence-dir>          the owner's auth probe, verbatim command
#   run_arm.sh hookproof <run-id> <evidence-dir>          hooks fire under bypassPermissions; environment dumps
#   run_arm.sh control   <run-id> <evidence-dir>          P3: Appendix A, no plugin
#   run_arm.sh plugin    <run-id> <evidence-dir> <profile> P2: Appendix A in the P1 profile (plugin installed)
#   run_arm.sh pilot     <run-id> <evidence-dir> <plugin-dir>  unregistered pilot, at most $1.00 in total
#   run_arm.sh outcome   <run-id> <evidence-dir> <profile> <cwd> <message>
#   run_arm.sh cli       <run-id> <profile> <claude args...>  e.g. `plugin install …`; no session, no ledger row
#
# Session environment: `env -i` plus exactly HOME (a fresh per-run directory), USER, LOGNAME, TMPDIR, SHELL, PATH,
# CLAUDE_CONFIG_DIR, DISABLE_AUTOUPDATER=1, GIT_CONFIG_GLOBAL (the run's gitconfig). Nothing else.
# Auth: each fresh profile gets a settings.json with exactly one key, apiKeyHelper. ANTHROPIC_API_KEY is never
# exported by this script or by anything it starts. This script never prints its environment beyond `envlist`.
set -u

HERE=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$HERE/../.." && pwd)
EG=/Users/akasha/.evidence-gates
CC="$EG/bin/claude-2.1.325"
CC_SHA256=84590fefe6338be9087f5814b61f9a54c5f21524163a4c127cb5a808e31009f2
CC_VERSION="2.1.325 (Claude Code)"
RUNS="$EG/runs"
LEDGER="$REPO_ROOT/docs/evidence/COST.md"
MESSAGES="$HERE/messages.txt"
SETTINGS_JSON='{"apiKeyHelper": "/Users/akasha/.evidence-gates/bin/key-helper.sh"}'
CLEAN_PATH=/Library/Frameworks/Python.framework/Versions/3.11/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
ARM_FLAGS=(--model claude-sonnet-5-5 --permission-mode bypassPermissions --max-turns 30 --output-format stream-json --verbose)
SESSION_USER=akasha
SESSION_TMPDIR=/var/folders/6x/f_ljx_vj5nx_ft0jlvm2xz4m0000gn/T/

die() { echo "run_arm: $1" >&2; exit "${2:-2}"; }

# Fail closed if key material or an ANTHROPIC variable is in the environment this script was started from.
if env | grep -q -e '^ANTHROPIC' -e 'sk-ant-'; then die "refusing: an ANTHROPIC variable or key material is in the environment" 2; fi

mode=${1:-}; RUN_ID=${2:-}
[ -n "$mode" ] && [ -n "$RUN_ID" ] || die "usage: see the header of $0"
RUN="$RUNS/$RUN_ID"

senv() {  # senv <profile>: fill SENV with the session environment
  SENV=(HOME="$RUN/home" USER="$SESSION_USER" LOGNAME="$SESSION_USER" TMPDIR="$SESSION_TMPDIR" SHELL=/bin/zsh
        PATH="$CLEAN_PATH" CLAUDE_CONFIG_DIR="$1" DISABLE_AUTOUPDATER=1 GIT_CONFIG_GLOBAL="$RUN/gitconfig")
}

assert_binary() {
  [ -x "$CC" ] || die "instrument missing: $CC (STOP)" 4
  local sha ver
  sha=$(shasum -a 256 "$CC" | cut -d' ' -f1)
  [ "$sha" = "$CC_SHA256" ] || die "instrument sha256 changed: $sha (STOP)" 4
  ver=$("$CC" --version 2>&1 | head -1)
  [ "$ver" = "$CC_VERSION" ] || die "instrument version changed: $ver (STOP)" 4
}

spend_sum() { python3 -I "$HERE/ledger.py" sum "$LEDGER"; }
spend_gate() {
  python3 -I -c 'import sys; sys.exit(0 if float(sys.argv[1]) < 10.0 else 1)' "$(spend_sum)" \
    || { echo "run_arm: running sum >= \$10.00; spend cap, no session started" >&2; return 3; }
}

new_run() {  # fresh run directory: home, gitconfig, stderr
  [ -e "$RUN" ] && die "run $RUN_ID already exists; every run is fresh"
  mkdir -p "$RUN/home" "$RUN/stderr" "$RUN/snap" || die "cannot create $RUN"
  printf '[user]\n\tname = eg-throwaway\n\temail = eg-throwaway\n[init]\n\tdefaultBranch = main\n' > "$RUN/gitconfig"
}

new_profile() {  # new_profile <dir>: a fresh profile whose settings.json holds exactly one key, apiKeyHelper
  [ -e "$1" ] && die "profile $1 already exists; every profile is fresh"
  mkdir -p "$1" && printf '%s\n' "$SETTINGS_JSON" > "$1/settings.json"
}

msg() { awk -F'\t' -v k="$1" '$1 == k { print substr($0, length(k) + 2); found = 1 } END { exit !found }' "$MESSAGES"; }

run_claude() {  # run_claude <session> <cwd> <profile> <outfile> <claude args...>
  local session=$1 cwd=$2 profile=$3 outfile=$4; shift 4
  assert_binary
  spend_gate || return 3
  senv "$profile"
  ( cd "$cwd" || exit 2; exec env -i "${SENV[@]}" "$CC" "$@" < /dev/null ) > "$outfile" 2> "$RUN/stderr/$session.txt"
  local rc=$?
  python3 -I "$HERE/ledger.py" add "$LEDGER" "$RUN_ID" "$session" "$outfile" "$rc" "${NOTE:-}"
  local lrc=$?
  echo "session $session: exit=$rc"
  [ "$rc" -eq 0 ] && [ "$lrc" -eq 0 ]
}

snapshot() { cp -R "$1" "$RUN/snap/$2"; }

chain() {  # chain <evid> <repo> <profile> <label> <message> [<label> <message> ...]: one session, --continue after the first
  local evid=$1 repo=$2 profile=$3; shift 3
  local first=1
  while [ $# -ge 2 ]; do
    local label=$1 text=$2; shift 2
    local cont=(); [ $first -eq 1 ] || cont=(--continue)
    run_claude "$label" "$repo" "$profile" "$evid/$label.jsonl" -p "$text" "${cont[@]+"${cont[@]}"}" "${ARM_FLAGS[@]}" "${EXTRA[@]+"${EXTRA[@]}"}" \
      || { snapshot "$repo" "$label"; echo "run_arm: session $label failed; chain stopped" >&2; return 1; }
    snapshot "$repo" "$label"
    first=0
  done
}

case $mode in
  envlist)
    senv "$RUN/profile"
    printf '%s\n' "${SENV[@]}" | sort
    ;;
  probe)
    evid=${3:?evidence dir}; mkdir -p "$evid"
    new_run; new_profile "$RUN/profile"; mkdir -p "$RUN/work"
    run_claude probe "$RUN/work" "$RUN/profile" "$evid/probe.json" -p "reply with the single word ok" --output-format json
    ;;
  hookproof)
    evid=${3:?evidence dir}; mkdir -p "$evid"
    new_run; new_profile "$RUN/profile"; mkdir -p "$RUN/work/.claude"
    hook="in=\$(cat); { echo \"--- hook call\"; env | sort; } >> $RUN/hookproof.env; echo \"fired key_vars=\$(env | grep -c -e ANTHROPIC -e sk-ant-) git_config_global=\$(env | grep -c GIT_CONFIG_GLOBAL)\" >> $RUN/hookproof.log; case \"\$in\" in *\"echo hello\"*) echo 'hookproof: blocked' >&2; exit 2;; esac; exit 0"
    python3 -I -c 'import json, sys
json.dump({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": sys.argv[2]}]}]}},
          open(sys.argv[1], "w"), indent=2)' "$RUN/work/.claude/settings.json" "$hook"
    text='Use the Bash tool to run `echo hello`, then report exactly what happened. Then use the Bash tool to run exactly this one command and report its output verbatim: env | grep -c -e ANTHROPIC -e sk-ant- ; env | grep -c GIT_CONFIG_GLOBAL ; env | sort'
    run_claude hookproof "$RUN/work" "$RUN/profile" "$evid/hookproof.jsonl" -p "$text" "${ARM_FLAGS[@]}"
    ;;
  control|plugin)
    evid=${3:?evidence dir}; mkdir -p "$evid"
    python3 -I "$HERE/check_messages.py" || die "messages.txt does not match Appendix A; nothing run"
    new_run
    if [ "$mode" = control ]; then
      profile="$RUN/profile"; new_profile "$profile"
    else
      profile=${4:?the P1 profile}; [ -d "$profile" ] || die "P1 profile $profile not found"
    fi
    senv "$profile"; env -i "${SENV[@]}" /bin/bash "$HERE/make_repo.sh" "$RUN/repo" scenario || die "make_repo failed"
    snapshot "$RUN/repo" T0
    EXTRA=()
    if [ "$mode" = control ]; then
      chain "$evid" "$RUN/repo" "$profile" \
        T1 "$(msg T1)" T2 "$(msg T2)" T3a "$(msg T3a)" T3b "$(msg T3b)" T4 "$(msg T4)" T5 "$(msg T5)"
    else
      chain "$evid" "$RUN/repo" "$profile" \
        T1 "$(msg T1_PREFIX) $(msg T1)" T1b "$(msg T1b)" T2 "$(msg T2)" T3a "$(msg T3a)" T3b "$(msg T3b)" \
        T4 "$(msg T4)" T5 "$(msg T5)" || exit 1
      if python3 -I -c 'import sys; sys.exit(0 if float(sys.argv[1]) < 9.0 else 1)' "$(spend_sum)"; then
        NOTE="supplementary, not registered" run_claude GATE "$RUN/repo" "$profile" "$evid/GATE.jsonl" \
          -p "$(msg GATE)" --continue "${ARM_FLAGS[@]}" && snapshot "$RUN/repo" GATE
      else
        echo "run_arm: running sum >= \$9.00; supplementary /evidence-gates:gate skipped" >&2
      fi
    fi
    ;;
  pilot)
    evid=${3:?evidence dir}; plugdir=${4:?plugin dir}; mkdir -p "$evid"
    new_run; new_profile "$RUN/profile"
    senv "$RUN/profile"; env -i "${SENV[@]}" /bin/bash "$HERE/make_repo.sh" "$RUN/repo" pilot || die "make_repo failed"
    snapshot "$RUN/repo" P0
    first=1; spent=0
    for label in PILOT1 PILOT1b PILOT2 PILOT3; do
      case $label in
        PILOT1) text="$(msg T1_PREFIX) $(msg PILOT1)" ;; PILOT1b) text="$(msg T1b)" ;; *) text="$(msg "$label")" ;;
      esac
      # The $1.00 is a total: each message may spend what is left, rounded down to the cent; at 0.00 the pilot stops.
      left=$(python3 -I -c 'import math, sys; print("%.2f" % (math.floor((1.00 - float(sys.argv[1])) * 100 + 1e-9) / 100))' "$spent")
      if ! python3 -I -c 'import sys; sys.exit(0 if float(sys.argv[1]) > 0 else 1)' "$left"; then
        echo "pilot stopped before $label: the \$1.00 total is spent (spent $spent)" | tee "$evid/PILOT_STOP.txt"
        break
      fi
      cont=(); [ $first -eq 1 ] || cont=(--continue)
      before=$(spend_sum)
      NOTE="UNREGISTERED pilot" run_claude "$label" "$RUN/repo" "$RUN/profile" "$evid/$label.jsonl" -p "$text" \
        "${cont[@]+"${cont[@]}"}" "${ARM_FLAGS[@]}" --plugin-dir "$plugdir" --max-budget-usd "$left"
      prc=$?
      snapshot "$RUN/repo" "$label"
      spent=$(python3 -I -c 'import sys; print(float(sys.argv[1]) + float(sys.argv[2]) - float(sys.argv[3]))' "$spent" "$(spend_sum)" "$before")
      if [ $prc -ne 0 ]; then
        echo "pilot stopped at $label: the session exited non-zero (see the ledger note and the transcript)" | tee "$evid/PILOT_STOP.txt"
        break
      fi
      first=0
    done
    [ -e "$evid/PILOT_STOP.txt" ] || echo "pilot completed all four messages; spent $spent of \$1.00" | tee "$evid/PILOT_STOP.txt"
    ;;
  cli)
    # A `claude plugin …` (or other non-session) command in the clean environment, in a profile that is created fresh
    # with the one-key settings.json when it does not exist yet. No session, no result event, no ledger row.
    profile=${3:?profile dir}; shift 3
    # Guard (added 2026-11-16 after four unintended sessions): only `plugin <subcommand> …` or `--version` may pass.
    # A single argument such as "plugin list" (an unsplit string) would be read by the binary as a prompt and start
    # an unrecorded session in default permission mode.
    case "${1:-}" in
      plugin) [ -n "${2:-}" ] || die "cli mode: \`plugin\` needs a subcommand" ;;
      --version) [ $# -eq 1 ] || die "cli mode: \`--version\` takes no other argument" ;;
      *) die "cli mode runs only \`plugin <subcommand> …\` or \`--version\` (got: '${1:-}'); nothing run" ;;
    esac
    [ -e "$RUN" ] || new_run
    [ -e "$profile" ] || new_profile "$profile"
    mkdir -p "$RUN/work"
    assert_binary
    senv "$profile"
    ( cd "$RUN/work" && exec env -i "${SENV[@]}" "$CC" "$@" < /dev/null )
    ;;
  outcome)
    evid=${3:?evidence dir}; profile=${4:?profile}; cwd=${5:?cwd}; text=${6:?message}; mkdir -p "$evid"
    [ -e "$RUN" ] || new_run
    run_claude outcome "$cwd" "$profile" "$evid/outcome.jsonl" -p "$text" "${ARM_FLAGS[@]}"
    ;;
  *) die "unknown mode $mode" ;;
esac
