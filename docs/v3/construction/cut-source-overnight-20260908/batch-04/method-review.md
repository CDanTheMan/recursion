# Prospective review — 2026-09-09

Two independent read-only workers inspected original source and retained evidence.
They performed no tests/model traversals, writes, settings changes or delegation.
Packets were bounded to 1200 seconds. Exact-source review follows preregistration.

The relation reviewer confirmed that the first-attestation-floor candidate is
usefully falsifiable. It closes the retained S0/Q1 first-attestation endpoint but
collapses the following S0-to-S1 restart to Q1-to-Q1 while the original Q reducer
advances Q1-to-Q2. It also leaves signed generation-0 envelopes unchanged, so Q
staging from a lifted generation-1 prestate must differ. No re-signing, rehashing,
identity renaming or history-aware auxiliary state is introduced to hide these gaps.

Every modeled decision remains an exact transition output. State matches cannot
conceal response differences, and source-only operations cannot be hidden without
a separately justified action contract. The checker binds source edge, projected
target prestate, target successor, relation identity and both responses. Representative
examples include stale collection, incomplete inventory, stale publication, restart,
staging, reconciliation and durable duplicate outcomes.

The gate reviewer found that Batch03's local 500000-state check resets each call.
The successor adds durable admission reservations and includes two historical full
source traversals plus their truncated calibrations: the inherited total is 89834,
superseding the initial 53898 mapping-only estimate. No prior receipt is rewritten.

The new full gate contains 47 commands and preserves old wrappers. It copies and
adapts the enclosing Batch03 gate into the additive Batch04 path; importing the old
full_gate module directly would incorrectly bind its unqualified import of run.
It retains the unchanged OwnedJob helper and read-only historical verification
functions, and adds Batch03's final completion to the existing closure map.

Both reviews distinguish finite local correspondence from original target reachability,
whole-prefix composition, fairness or source truth. Known failed relations are
research evidence; they are not authorization to change original model semantics.

The first focused run on db96ae2c050f6350cc35e781962aeb4f1d759846 passed. Before
finalization, the root continued independent eligible proof work within this scope.
The same relation reviewer confirmed a restricted contradiction in the retained
consecutive attestation/stage prefix: one shared Q intermediate generation must
equal both token 1 and token 0 when only top-level generation may differ. The
successor certificate binds adjacency, responses, guards, typed values and exact
source/function anchors. It does not assert impossibility for richer envelope
relations, different action translations or inserted target steps. The original
successful run and its audit remain retained; no failure is relabeled as success.
