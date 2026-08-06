#!/usr/bin/env bash
# portfolio-lint.sh — the registry decides what the control plane may touch, so it has to be
# true. Everything downstream trusts it: resync.sh syncs from it, work.sh takes deploy keys from
# it, and hermes-decide.sh reports it as ground truth. A row that is merely PLAUSIBLE — a path
# that does not exist, a key that was never provisioned, a repo marked pending after it was
# cloned — produces a confident answer about a repo nobody is actually watching.
#
# This lints the REAL state/portfolio.tsv (like authority-lint.sh lints the real docs), and its
# ★ CONTROL feeds a deliberately-broken registry through the same rules: a lint that cannot fail
# is a lint that passes everything, which is worse than no lint because it reads as verified.
#
#   run: bash scripts/tests/portfolio-lint.sh
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

# lint <file> -> prints one "<CODE> <detail>" line per problem; exit 0 iff clean
lint(){
  local reg="$1" bad=0 line project path remote branch key roadmap topic status
  [ -f "$reg" ] || { echo "MISSING $reg"; return 1; }
  # A column header must be present somewhere in the leading comment block — the real registry
  # opens with an explanation and carries '#project<TAB>path...' as its last comment line. The
  # header is not decoration: without it a reader cannot tell column 8 from column 7, and cut -f
  # on the wrong column "works" and returns something plausible.
  grep -q '^#project' "$reg" || { echo "NOHEADER no '#project' column header anywhere"; bad=1; }
  while IFS=$'\t' read -r project path remote branch key roadmap topic status; do
    case "$project" in \#*|"") continue ;; esac
    [ -n "$status" ] || { echo "SHORTROW $project has fewer than 8 columns"; bad=1; continue; }
    case "$status" in
      active|pending|reference) : ;;
      *) echo "BADSTATUS $project has status '$status'"; bad=1 ;;
    esac
    case "$branch" in ""|-) echo "NOBRANCH $project names no default branch"; bad=1 ;; esac
    case "$remote" in *github.com*|*git@*|*://*) : ;; *) echo "BADREMOTE $project remote '$remote'"; bad=1 ;; esac

    # The two directions that actually bite:
    #   an ACTIVE row is dispatched at, so its repo must exist;
    #   a PENDING row that HAS been cloned is stale — it is silently excluded from every sync,
    #   which is how a live repo stops being watched without anyone noticing.
    if [ "$status" = "active" ] && [ ! -d "$path/.git" ]; then
      echo "GHOST $project is active but $path is not a git repo"; bad=1
    fi
    if [ "$status" = "pending" ] && [ -d "$path/.git" ]; then
      echo "STALE $project is pending but $path already exists — promote it to active"; bad=1
    fi
    # A key that does not exist means every git op on this repo runs with no credential, and a
    # credential-less git op fails QUIETLY. Only checked for rows that will actually be used.
    if [ "$status" != "pending" ] && [ "$key" != "-" ] && [ -n "$key" ]; then
      local kp="${key/#\~/$HOME}"
      [ -f "$kp" ] || { echo "NOKEY $project deploy key $key is absent"; bad=1; }
    fi
    if [ "$roadmap" != "-" ] && [ -n "$roadmap" ] && [ ! -f "$ROOT/$roadmap" ]; then
      echo "NOROADMAP $project points at $roadmap which does not exist"; bad=1
    fi
  done < "$reg"

  # Duplicates: two rows for one project makes reg_find's `exit` pick an arbitrary one, so the
  # answer depends on file order rather than on intent.
  local d
  d="$(awk -F'\t' '$1 !~ /^#/ && NF>=8 {print $1}' "$reg" | LC_ALL=C sort | uniq -d)"
  [ -n "$d" ] && { echo "DUPPROJECT $d"; bad=1; }
  d="$(awk -F'\t' '$1 !~ /^#/ && NF>=8 {print $2}' "$reg" | LC_ALL=C sort | uniq -d)"
  [ -n "$d" ] && { echo "DUPPATH $d"; bad=1; }
  return "$bad"
}

# --- the real registry ----------------------------------------------------------------------
out="$(lint "$ROOT/state/portfolio.tsv" 2>&1)"
if [ -z "$out" ]; then
  ok "state/portfolio.tsv is internally consistent (paths, keys, roadmaps, statuses, uniqueness)"
else
  no "state/portfolio.tsv has problems:"; printf '%s\n' "$out" | sed 's/^/        /'
fi

# --- ★ CONTROL: the same rules must REJECT a registry that is wrong in each way ---------------
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
mkrow(){ printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$@"; }
GOODKEY="$(awk -F'\t' '$1 !~ /^#/ && $5 != "-" {print $5; exit}' "$ROOT/state/portfolio.tsv")"

check_control(){ # check_control <name> <expected-code> <registry-body>
  local name="$1" code="$2" body="$3" f="$TMP/reg.tsv" o
  # ★ printf '%s\n', not '%s': $(...) strips the trailing newline, and `while read` returns
  # FALSE on a final line without one — so the loop body never ran and every single-row control
  # came back "clean". Six controls passed vacuously until the inverse control made it obvious.
  { printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n'; printf '%s\n' "$body"; } > "$f"
  o="$(lint "$f" 2>&1)"
  if printf '%s' "$o" | grep -q "^$code"; then ok "CONTROL — $name is rejected ($code)"
  else no "CONTROL FAILED — $name was ACCEPTED (expected $code, got: ${o:-<clean>})"; fi
}

check_control "an active repo that does not exist"       GHOST      "$(mkrow p /nonexistent/xyz git@github.com:a/b.git main - - - active)"
check_control "a cloned repo still marked pending"       STALE      "$(mkrow p "$ROOT" git@github.com:a/b.git main - - - pending)"
check_control "a deploy key that was never provisioned"  NOKEY      "$(mkrow p "$ROOT" git@github.com:a/b.git main ~/.ssh/never_provisioned - - active)"
check_control "a roadmap pointer to a missing file"      NOROADMAP  "$(mkrow p "$ROOT" git@github.com:a/b.git main "$GOODKEY" state/roadmaps/nope.md - active)"
check_control "an unknown status value"                  BADSTATUS  "$(mkrow p "$ROOT" git@github.com:a/b.git main "$GOODKEY" - - archived)"
# Two rows, and the newline between them is explicit: $(...) strips each row's trailing
# newline, so writing them adjacent produced ONE glued line rather than a duplicate pair.
check_control "a duplicate project name"                 DUPPROJECT "$(mkrow p "$ROOT" git@github.com:a/b.git main "$GOODKEY" - - active)
$(mkrow p "$ROOT" git@github.com:a/b.git main "$GOODKEY" - - active)"
check_control "a row missing columns"                    SHORTROW   "p	/tmp	x	main
"

# ★ and the inverse control: a WELL-FORMED registry must come back clean, or every rejection
# above is satisfied by a lint that rejects everything.
{ printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n'
  mkrow good "$ROOT" git@github.com:a/b.git main "$GOODKEY" - - active; } > "$TMP/reg.tsv"
o="$(lint "$TMP/reg.tsv" 2>&1)"
[ -z "$o" ] && ok "★ CONTROL — a well-formed registry passes (the lint is not rejecting everything)" \
             || no "★ CONTROL FAILED — a valid registry was rejected: $o"

echo
[ "$fails" -eq 0 ] && { echo "portfolio-lint: ALL PASS"; exit 0; }
echo "portfolio-lint: $fails FAILED"; exit 1
