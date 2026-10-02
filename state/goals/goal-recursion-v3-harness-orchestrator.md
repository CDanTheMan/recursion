schema_version: 1
id: goal-recursion-v3-harness-orchestrator
project_id: recursion
status: active
outcome: >-
  Ship Recursion v3 as a community, open-source agent harness that is both a first-class native
  harness and a trusted orchestrator across other harnesses and providers, without ecosystem
  lock-in: one place to connect subscriptions and keys, route requests through any harness or its
  own, and preserve authority, evidence, accounting, privacy and recovery across every route and
  machine.
acceptance_suite: >-
  The docs/v3/PRODUCT.md first-usable-release contract, the product promises, and the accepted
  Owner decisions D-018..D-033, each with independent evidence.
falsifier: >-
  Recursion cannot deliver cross-harness work without holding credentials it was not granted, or
  its measured quota/usage burden does not improve over driving each harness directly, or a
  required mechanism fails at the D-028 platform floors.
budget: Human-approved included capacity only; no on-demand or metered spend without explicit policy.

Lineage: supersedes goal-recursion-v2-execution-fabric. The v2 control-plane and Hermes-led
executive framing was retired on 2026-09-28 (state/DECISIONS.md D-017); Hermes is now an optional
upstream integration, not the executive control plane.
