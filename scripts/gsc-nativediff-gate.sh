#!/usr/bin/env bash
# gsc-nativediff-gate.sh — NUMERIC quality gate for golden-stallion-client renderer FRONTIER tasks.
#
# Conformance (gsc-conformance-gate.sh) is a REGRESSION gate: it keeps the 200-odd offline tests
# green. It cannot reward getting the mesh CLOSER to native when no boolean flips. This gate does:
# acceptance = Σ|per-slot triangle error| STRICTLY DECREASES for the TARGET world(s) vs a stored
# per-world baseline, while EVERY OTHER baselined world is reproduced BYTE-FOR-BYTE (same per-slot
# delta vector) — the control that separates "a feature moved the bytes" from "a regression got
# re-stamped" — AND the conformance suite shows no regression and no tampering.
#
# ⚠ SUM-not-total. native-diff.cjs prints a TOTAL line, but that total is SIGNED: a big over on one
# slot cancels a big under on another (furys: TOTAL delta 14193 hides Σ|slot| 26737, 1.9x). We never
# read TOTAL as the metric; we sum |per-slot delta|. We DO read TOTAL as a parse cross-check: the
# signed sum of the rows we parsed must equal the tool's printed TOTAL, or the parse is incomplete.
#
# ⚠ empty query = BUILD_DEFAULTS. We invoke native-diff.cjs with ONLY --world so the measurement
# reflects shipped defaults, never an explicit flag override that can't reproduce its own defaults.
#
# Run from the GSC worktree root (work.sh sets cwd).
#   gsc-nativediff-gate.sh                 gate the current tree against the baseline
#   gsc-nativediff-gate.sh --regen         (re)write the baseline from the current tree, showing the
#                                          old value beside each new one (a re-pin is never silent)
# exit 0=pass · 1=quality regression / control broke · 2=no progress · 3=harness · 4=tamper
set -uo pipefail

BASELINE="${GSC_NATIVEDIFF_BASELINE:-/opt/recursion/state/gsc/nativediff-baseline.tsv}"
CONF_GATE="${GSC_CONF_GATE:-$(cd "$(dirname "$0")" && pwd)/gsc-conformance-gate.sh}"
ND="user-client/render/tools/native-diff.cjs"
# Worlds the baseline covers (also the --regen set). Override with GSC_NATIVEDIFF_WORLDS.
WORLDS="${GSC_NATIVEDIFF_WORLDS:-furys_storage vikings_collection chickenlips_resources watersigns_realm}"
# Worlds that MUST improve (space list). Empty => any-improves / none-worsens mode (looser: no
# byte-for-byte control, since we don't know which world the task targeted).
TARGET="${GSC_NATIVEDIFF_TARGET:-}"
REGEN=0; [ "${1:-}" = "--regen" ] && REGEN=1

[ -f "$ND" ] || { echo "GATE: $ND not found — run from the GSC repo root"; exit 3; }

# metric <world> -> "sumAbs signed total slots digest"  (digest = sha256 of the per-slot delta vector)
# digest is the BYTE-FOR-BYTE control quantity: sorted "slot delta" pairs, exactly what native prints.
metric(){
  local w="$1" tmp; tmp="$(mktemp)"
  if ! node "$ND" --world="$w" >"$tmp" 2>/dev/null; then rm -f "$tmp"; echo "ERR"; return; fi
  local agg dig
  agg="$(awk '/^0x/{d=$(NF-1); sa+=(d<0?-d:d); ss+=d; n++} /^TOTAL/{td=$(NF-1)}
              END{printf "%d %d %d %d", sa, ss, (NF?td:0), n}' "$tmp")"
  # cross-check: signed row-sum must equal the printed TOTAL delta, and at least one slot row seen.
  local sa ss td n; read -r sa ss td n <<<"$agg"
  if [ "${n:-0}" -lt 1 ] || [ "$ss" != "$td" ]; then rm -f "$tmp"; echo "ERR"; return; fi
  dig="$(grep '^0x' "$tmp" | awk '{print $1, $(NF-1)}' | sha256sum | cut -c1-16)"
  rm -f "$tmp"; echo "$sa $ss $td $n $dig"
}

# --- --regen: (re)write the baseline, old value beside new (renderer-compact: re-pin is visible) ---
if [ "$REGEN" = "1" ]; then
  mkdir -p "$(dirname "$BASELINE")"; NEW="$(mktemp)"
  printf '# world\tsumAbs\tvecDigest   (GSC main, empty-query BUILD_DEFAULTS; re-pin if defaults flip)\n' > "$NEW"
  for w in $WORLDS; do
    r="$(metric "$w")"; [ "$r" = "ERR" ] && { echo "GATE: --regen metric failed for $w"; rm -f "$NEW"; exit 3; }
    read -r sa ss td n dig <<<"$r"
    old="$(awk -v w="$w" '$1==w{print $2" ("$3")"}' "$BASELINE" 2>/dev/null || true)"
    printf '%s\t%s\t%s\n' "$w" "$sa" "$dig" >> "$NEW"
    printf '  %-24s sumAbs %-8s  was: %s\n' "$w" "$sa" "${old:-<none>}"
  done
  mv "$NEW" "$BASELINE"; echo "GATE: baseline written -> $BASELINE"; exit 0
fi

[ -f "$BASELINE" ] || { echo "GATE: no baseline at $BASELINE (run --regen on a known-good tree first)"; exit 3; }

# --- (0)+(1) reuse the conformance gate for no-tamper + no-regression (no boolean progress needed). -
# It also blocks edits to *.test.cjs and render/data. We additionally block edits to the tools dir:
# the arm must never touch the instrument it is measured by (renderer-compact: the tool was wrong 3x).
TAMPER="$(git status --porcelain -- 'user-client/render/tools' 2>/dev/null || true)"
if [ -n "$TAMPER" ]; then
  echo "GATE: TAMPERING — arm modified the measurement tools (forbidden):"; printf '%s\n' "$TAMPER" | head; exit 4
fi
if ! CONF_OUT="$(bash "$CONF_GATE" --no-progress 2>&1)"; then
  rc=$?; echo "GATE: conformance leg failed (rc=$rc) — quality is only meaningful if the suite is green:"
  printf '%s\n' "$CONF_OUT" | head; exit "$rc"   # propagate 1=regression / 3=harness / 4=tamper
fi

# --- (2) numeric quality: target strictly improves; controls byte-for-byte unchanged. -------------
improved=0; worsened=0; broke=0; rc_detail=""
is_target(){ case " $TARGET " in *" $1 "*) return 0;; *) return 1;; esac; }
while IFS=$'\t' read -r w base_sa base_dig; do
  case "$w" in ''|'#'*) continue;; esac
  r="$(metric "$w")"; [ "$r" = "ERR" ] && { echo "GATE: metric/cross-check failed for $w (parse incomplete)"; exit 3; }
  read -r sa ss td n dig <<<"$r"
  if [ -n "$TARGET" ] && ! is_target "$w"; then
    # control world: must reproduce the baseline per-slot vector byte-for-byte.
    if [ "$dig" != "$base_dig" ]; then
      echo "GATE: CONTROL BROKE — untargeted world $w changed (sumAbs $base_sa->$sa, digest $base_dig->$dig)"; broke=1
    fi
  else
    # a world we expect to improve (target, or any world in no-target mode).
    if   [ "$sa" -lt "$base_sa" ]; then improved=$((improved+1)); rc_detail="$rc_detail  $w: $base_sa -> $sa  (-$((base_sa-sa)))"$'\n'
    elif [ "$sa" -gt "$base_sa" ]; then worsened=$((worsened+1)); rc_detail="$rc_detail  $w: $base_sa -> $sa  (+$((sa-base_sa))) WORSE"$'\n'
    fi
  fi
done < "$BASELINE"

if [ "$broke" = "1" ]; then echo "GATE: FAIL — a control world moved; a real feature must not touch worlds it does not target."; exit 1; fi
if [ "$worsened" -gt 0 ]; then
  echo "GATE: QUALITY REGRESSION — a target world got worse (a correct feature can still worsen a world with an unrelated defect; control for it):"
  printf '%s' "$rc_detail"; exit 1
fi
if [ "$improved" -lt 1 ]; then
  echo "GATE: NO PROGRESS — no target world's Σ|per-slot error| decreased (nothing got closer to native)."; exit 2
fi

echo "GATE: PASS — Σ|per-slot error| decreased on $improved world(s), no world worsened, controls byte-for-byte, conformance green:"
printf '%s' "$rc_detail"
exit 0
