#!/usr/bin/env bash
# authority-lint.sh — no unresolved authority contradiction may sit in a tracked doc.
#
# WHY. The rebase plan's Task-1 validation was "a repository-wide search for `reactive`,
# `never writes code`, `mailbox`, and `supervisor` finds no unresolved authority
# contradiction." A human grep is not a gate: it passes silently the day someone reopens
# the question in a new file. This makes it mechanical.
#
# THE RULE. A phrase describing the OLD authority model (Hermes as front/router/mailbox/
# stateless summariser/reactive console; Claude as conductor) may appear in a tracked doc
# ONLY inside a block that is explicitly marked superseded. The marker is:
#
#     <!-- superseded-by: CONTROL_PLANE.md ... -->
#
# and it must appear within SCAN_BACK lines EITHER SIDE of the hit — a supersede note is as
# often written just below the claim it annotates as above it. Proximity is the point: a
# file-level blanket marker would exempt a whole file forever, so it is deliberately not
# supported. Each superseded claim gets its own adjacent marker. Marking is cheap;
# what it buys is that every such line has been consciously reconciled rather than left to
# rot. Superseding also requires preserving WHY the old model was believed — that is a
# review obligation this lint cannot check, stated here so it is not forgotten.
#
#   run: bash scripts/tests/authority-lint.sh
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$ROOT"
SCAN_BACK="${AUTHORITY_LINT_SCAN_BACK:-14}"
fails=0

# Phrases that assert the OLD model. Kept narrow on purpose: a broad pattern (e.g. bare
# "supervisor") matches hundreds of legitimate mechanical references and trains people to
# ignore the lint. These are the load-bearing authority claims.
PATTERNS=(
  'front/router'
  'never writes code'
  'Never writes code'
  'stateless (text )?transform'
  'reactive[, ].*(console|root)'
  'the conductor session you drop into'
  'mailbox'
)

# Files that are ALLOWED to discuss the old model freely: the constitution defines the new
# one by contrast, the decision log records the change, and the plan archive is history.
is_exempt(){
  case "$1" in
    ./CONTROL_PLANE.md|./state/DECISIONS.md) return 0 ;;
    ./.hermes/plans/*|./docs/plans/*)        return 0 ;;
    ./scripts/tests/authority-lint.sh)       return 0 ;;
    *) return 1 ;;
  esac
}

# Only TRACKED markdown — an untracked scratch file is not a claim the repo makes.
mapfile -t DOCS < <(git ls-files '*.md' | sed 's#^#./#')
[ "${#DOCS[@]}" -gt 0 ] || { echo "authority-lint: no tracked .md files found"; exit 1; }

for f in "${DOCS[@]}"; do
  is_exempt "$f" && continue
  [ -f "$f" ] || continue
  for pat in "${PATTERNS[@]}"; do
    while IFS=: read -r ln _; do
      [ -n "${ln:-}" ] || continue
      start=$(( ln - SCAN_BACK )); [ "$start" -lt 1 ] && start=1
      end=$(( ln + SCAN_BACK ))
      if sed -n "${start},${end}p" "$f" | grep -q 'superseded-by: CONTROL_PLANE.md'; then
        continue   # consciously reconciled
      fi
      echo "FAIL  $f:$ln — unresolved authority claim matching /$pat/"
      sed -n "${ln}p" "$f" | sed 's/^/        /' | cut -c1-110
      fails=$((fails+1))
    done < <(grep -nE "$pat" "$f" 2>/dev/null || true)
  done
done

# The constitution must exist and must actually name Hermes as the executive — otherwise
# every "superseded-by" marker above points at nothing.
if [ ! -f CONTROL_PLANE.md ]; then
  echo "FAIL  CONTROL_PLANE.md is missing — the supersede markers point nowhere"
  fails=$((fails+1))
elif ! grep -qi 'Hermes.*executive control plane' CONTROL_PLANE.md; then
  echo "FAIL  CONTROL_PLANE.md does not name Hermes as the executive control plane"
  fails=$((fails+1))
fi

echo
if [ "$fails" -eq 0 ]; then
  echo "authority-lint: PASS — no unresolved authority contradiction in tracked docs"
  exit 0
fi
echo "authority-lint: $fails unresolved claim(s). Either update the text, or mark the block:"
echo "    <!-- superseded-by: CONTROL_PLANE.md (YYYY-MM-DD, D-0NN) -->"
echo "  and PRESERVE the reason the old model was believed — do not compress it to 'superseded'."
exit 1
