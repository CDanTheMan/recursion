---
name: recursion-ops
description: "Receive Lucas's Recursion requests through Telegram as durable instructions; never execute control-plane operations from the gateway session."
version: 2.0.0
author: Recursion (authored)
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Recursion, Intake, Supervision, Guardrails]
    related_skills: [recursion-status]
---

# Recursion gateway instruction intake

The Telegram gateway is an authenticated conversation and status surface. It is not an operator
shell and it is not a second actuator. Every state-changing request from Lucas is persisted by the
gateway, projected by `scripts/intake.sh` into one durable instruction, decided by Head Hermes, and
executed only by the supervised deterministic actuator.

## What to do

- For a status question, use the read-only `recursion-status` skill and answer from current state.
- For a request to change state, confirm that the request has been received. Do not claim that it
  already ran. Intake will attach the authenticated principal, topic/project, reply correlation,
  and deduplication identity.
- If the request concerns spending, credentials, deployment, merging, PAUSE removal, policy, or
  control-plane configuration, say that it requires Lucas's explicit reviewed operator action.
- If a request is ambiguous, ask one concise clarifying question. Do not guess and do not translate
  ambiguity into a command.

## Hard boundary

Do not invoke the Recursion CLI, a shell, a tool-calling subagent, or a state-writing helper from
this gateway skill. In particular, planning, worker launch, queue drain, publication, escalation
resolution, assist answers, and kill-switch changes all travel through durable instruction ->
schema-checked decision -> Phase 2 action record -> actuator.

Never edit auth, provider routing, model selection, cron, service units, `.env`, autonomy flags,
deploy keys, or control-plane policy. Never merge, deploy, or push a default branch. Status remains
available while PAUSE is present; execution does not.

## Reply discipline

Say what was received and, when useful, which project topic it belongs to. Do not fabricate an
action ID: the exact action link exists only after the actuator claims a validated decision. A
handled instruction is acknowledged only after that linked durable action reaches `succeeded`.
