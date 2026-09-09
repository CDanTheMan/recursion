# Prospective method review — 2026-09-09

Two independent read-only workers inspected the merged baseline. They did not execute
models, modify files, alter settings or delegate. Each packet was limited to20 minutes.

The contract reviewer proposed nine requirements and exact function/evidence anchors.
The root encoded these in contracts.json. Existing conditions, correspondence obligations
and external assumptions stay distinct. Q1–Q6 and the original dependency graph remain
verbatim; new requirement-to-question links are explicitly proposed responsibility links.

The mapping reviewer independently confirmed a retained first-attestation counterexample:
pending-success/event/1 source-attest@17 and current-success/event/1 source-attest@8
have identical Q-visible prestates after hiding done/decision, but their successors
differ in source_generation. The utf8-byte pair has the same obstruction. This is
existing finite evidence, not a new source-validity or malformed-input experiment.

An initial candidate approach was to audit only the retained representative traces.
Those cover104 traces and2588 edges, while the admitted graphs contain31140 edges.
The approved implementation plan reproduces the unchanged complete original graph family
and checks its exact hashes, then classifies all edges locally. The representative-only
approach is superseded because it cannot support complete finite-edge coverage.

Both root and reviewer rejected treating local projected Q steps as proof of Q graph
reachability or schedule refinement. Source bookkeeping is retained for checker calls;
only done/decision are hidden in observations. Rejections that stutter do not establish
response-label equivalence or fairness. Generation renaming and envelope changes are
excluded. Full composition remains unproved if any mapping gap remains.

The reviewer suggested a decreasing finite schedule rank and corruption of mapping
certificates rather than protocol inputs. The registered checker includes these controls.
Final execution results and exact-candidate review remain separate requirements.

Before execution, root identified that the new direct source imports require an
explicit additional s_split.py snapshot. The inherited source model had previously
been checked in its frozen worktree. The new packet checks all loaded local module
paths against its own input/source manifest before traversing a graph.

Prospective implementation review caught a retained-artifact schema mismatch: S
stores its representative trace at trace, whereas Q stores witness/events. The
initial Q trace lookup was repaired before execution. The original evidence is unchanged.

The reviewer also corrected witness wording: first encounter under per-profile BFS does
not imply a shortest witness across different profiles. The specification now states
first-discovered evidence and makes no cross-profile shortestness claim.
