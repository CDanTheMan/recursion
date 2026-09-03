---
title: Recursion v3 CLI hypothesis
status: hypothesis
last-updated: 2026-09-02
---

# Recursion v3 CLI hypothesis

## Product requirement

The first CLI is for direct operation of Lucas's deployment. It must let an owner configure and inspect Recursion without asking an agent to edit files or call commands. The same design should remain teachable enough for later public users.

The CLI is a schema-driven editor, validator, explainer, and control surface over human-readable configuration. It is not the only copy of settings and does not hide policy in an opaque database.

## Configuration hierarchy

```text
built-in schema defaults
  < edition preset
  < installation/authority-domain config
  < project config
  < parent-goal config
  < task override
  < explicit ephemeral operator override
```

The most specific valid value wins. Child scopes may narrow hard bounds. Widening authority, privacy exposure, credentials, network, spending, or publication rights requires an explicit acknowledged operation at that scope.

Configuration contains credential references only. Machine-private configuration remains outside the public source checkout; projects may carry safe `.recursion.yaml` files whose requested capabilities are admitted by the owner/controller.

## Setting lifecycle

Schema metadata classifies every field as:

- `goal-frozen`: snapshotted into GoalSpec and changed only by amendment;
- `checkpoint-applied`: takes effect at the next machine-valid checkpoint;
- `live`: safe operational control such as lower concurrency or notification preference;
- `restart-required`: daemon/plugin lifecycle change.

Restrictions may tighten immediately. A command explains effective value, provenance, validation, and application time before making a change.

## Candidate command surface

```text
recursion init
recursion configure [--profile ...]
recursion config get|set|edit|validate|diff|apply|explain|migrate
recursion provider add|auth|probe|disable|list
recursion model list|show|suite|pin
recursion pool list|status|reserve|disable
recursion route explain|simulate|probe
recursion node enroll|list|show|revoke|doctor
recursion project add|list|show|classify|doctor
recursion goal grill|draft|accept|amend|status|stop
recursion arm list|show|checkpoint|replace|pause|resume
recursion queue list|explain|prioritize
recursion context inspect|compact|rehydrate|doctor
recursion evidence show|verify|export
recursion branch inventory|explain|prune-safe
recursion doctor [--quick|--full|--component ...]
recursion pause|resume
recursion observe|status|events|budget
```

Names are hypotheses. Research should compare established CLI conventions in the reference repositories and test discoverability.

## Zero-model configuration wizard

`recursion init` and `recursion configure` render from the versioned configuration schema. They:

- discover installed CLIs and supported local capabilities without reading secret values;
- offer minimal, standard, remote, full, and custom manifests;
- explain subscription versus metered billing boundaries;
- show privacy/egress implications;
- validate provider-native authentication in place;
- write only the requested config scope;
- produce a before/after diff and rollback file;
- require no model call.

Advanced users retain manual file editing. CLI and file validation are generated from the same schema so they cannot drift.

## Doctor tiers

- `startup`: cached, zero-token checks necessary to use enabled features; target seconds.
- `quick`: configuration, writable paths, SQLite health, Git, enabled plugin manifests, provider executable presence, and current PAUSE.
- `component`: focused provider, node, route, context, gate, or plugin diagnostics.
- `full`: release/conformance suite; never an ordinary startup dependency.

Successful checks are cached against all relevant hashes and invalidated precisely.

## Explainability

`route explain`, `route simulate`, `queue explain`, `capacity plan`, and `config explain` do not invoke a model. They show:

- candidate routes and rejection reasons;
- inherited and overridden settings;
- quality/cost/quota/privacy/resource inputs;
- current reservations and waits;
- checkpoint at which a change applies;
- whether an action crosses a billing or authority boundary.

## Full-access UX

The CLI must expose owner-authorized full-access and provider-native dangerous permission modes. It should use explicit names, display affected projects/nodes/credentials, record acknowledgement, and provide a reversible downgrade command. Warnings inform owner choice; they are not a remote approval service.

## Stable observer interface

Scheduled tasks and external assistants receive a versioned read-only interface for status, events, budgets, blockers, health, and evidence references. Scoped control is a separate authenticated capability. This lets monitoring tools check Recursion without parsing terminal prose or receiving implementation authority.
