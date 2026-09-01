# Recursion v2 MVP — Chiron source-only pilot

Date: 2026-08-31  
Status: source gate passed; v6 study pilot not ready

## Bound task

Determine, without editing Chiron or invoking a provider, whether the canonical Chiron
source is ready for the v6 intro-mechanics study pilot. The source was freshly fetched and
checked out detached at `origin/main@7525af525ab538f31c2e5b6f117a83fe8e4ac6d2` in a clean
worktree. `AGENTS.md`, `CLAUDE.md`, and `PRODUCT.md` were read before running the repository
gates.

## Evidence

| Command | Result |
|---|---|
| `git fetch origin main` | pass; canonical ref resolved to `7525af525ab538f31c2e5b6f117a83fe8e4ac6d2` |
| `node features.cjs --validate` | pass; 39-slice ledger valid |
| `npm ci` | pass; 28 packages installed; npm reported 3 high-severity dependency findings |
| `npm run verify` | pass; ledger validation, `tsc --noEmit`, and Next.js production build completed |
| `node features.cjs --next` | `H2`, the browser smoke gate |
| `node features.cjs --escalate` | `B0`, human infrastructure choices |
| `npm run smoke` | expected fail; the script does not exist because H2 remains open |
| final `git status --short` | empty |

No file was changed, no provider was called, no key was used, and no branch was published.

## Readiness result

The existing keyless learn loop is source-buildable: its ledger, TypeScript checks, and
production build pass at the exact canonical commit. That does not make the v6 product ready
for the intro-mechanics study pilot.

The canonical queue reports two buildable slices, with H2 next. H2's browser smoke gate is not
implemented. B0 remains escalated for the private brain repository, hosting, billing provider,
and service accounts. B10, the pilot-quality intro-mechanics course, remains open behind B2,
B4, B5, B6, S5, and S6. The dependency audit also reports three high-severity findings in the
current installed graph; this session did not mutate the lockfile or apply an unreviewed major
upgrade.

Therefore `/chiron` must report the exact split: the current keyless core passes its source gate,
while the v6 intro-mechanics study pilot is **not ready**. The next repository-authorized task is
H2; F1 is also buildable, and B0 requires Lucas. No product implementation was authorized by
this readiness task.
