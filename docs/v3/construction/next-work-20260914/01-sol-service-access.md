# Sol: external construction service access

Parent: goal-recursion-v2-execution-fabric. Apply COMMON.md. Suggested reviewer: Astra. This is infrastructure used by workers building Recursion v3; it is not a replacement for the product kernel research.

Deliver the read-only portion of continuous-service P2. Relevant contracts: construction-swarm/CONTINUOUS-OPERATION.md CW-03/04/05/17 and scenarios S03/S04. Existing P1 core is fake-boundary evidence and cannot be represented as a live Hermes integration. Existing foundry.report exposes actual completed/run evidence without canonical acceptance.

Implement an explicitly started native service with a versioned authenticated Unix-socket read protocol, a native CLI, and a thin stdio MCP bridge suitable for independent Windows/WSL clients. Follow the specified read operations status, tasks, task, events and artifact. Transport-bound caller identity and project/read capability must gate responses. A body-supplied actor name grants nothing. Use a fake canonical adapter in tests; expose canonical fields as unavailable when no real adapter exists.

Every response carries source commit, service instance/fence if known, observation time, freshness, last event cursor and unavailable fields. Missing/stale data must never turn into zero active jobs or a fabricated healthy status. Bound pages, requests and artifact sizes; reject symlink/path escape and cross-project handles. Cursor replay gaps demand a new snapshot. Deny mutation verbs in this slice.

The CLI/MCP client only connects. It must not launch a scheduler, provider, leader or hidden background service. Client disconnect/reconnect must not kill the independently owned test service. Do not alter installed Codex/Cursor configuration or existing auth. Test bridges with isolated clients and temporary fixtures. Provide exact smoke commands for separately enabled actual clients, labelled unrun until observed.

Allowed new paths only:
- tools/construction_swarm/p2_access.py
- tools/construction_swarm/p2_cli.py
- tools/construction_swarm/p2_mcp.py
- tools/construction_swarm/test_p2_access.py
- docs/v3/construction/p2-access-20260914/README.md
- docs/v3/construction/p2-access-20260914/PROGRESS.md

NEW acceptance command to implement:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_access
```

Required cases: two independent clients see the same bounded snapshot; project isolation and spoofed actor refusal; no mutation/provider launch from any exposed read verb; missing ledger/current canonical adapter explicitly unavailable; stale snapshot after server loss; event replay gap; malformed/oversize request refusal; artifact path/symlink escape; bridge disconnect preserves the independently owned service; reconnect recovers current source/cursor; bounded status remains responsive under a saturated read queue. Use actual local processes/sockets where that behavior is claimed, and record Windows versus Linux coverage honestly.

Existing regression after integration:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p1_core
```

Initial construction budget: no provider inference; each fake test child gets a 15-second deadline, total focused suite at most 120 seconds, temporary artifacts at most 32 MiB. Own and clean every child; no Windows reboot/WSL shutdown during the ordinary test gate. Independent review plus exact final source/scope checks are required.

Done means the read-only P2 slice works and has review evidence. Remaining P2 host-start/sign-out/reboot/lifecycle scenarios must be listed as unimplemented or unrun; do not mark P2 or24/7 complete from a stdio demo. Deliver the next bounded host-lifecycle packet after this review instead of installing startup policy as a shortcut.
