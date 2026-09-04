---
title: M1B route, plugin and process requirement contracts
status: construction-contract
last-updated: 2026-09-04
---

# M1B route, plugin and process requirement contracts

## Boundary

M1B freezes the inert execution-plane requirements that a later route fabric, plugin kernel and
managed process broker must satisfy. It consumes M1A identities and digests only as opaque,
immutable bindings. It does not extend the M1A planning kernel, call a provider, choose a model,
load or execute a plugin, launch or observe a real process, persist runtime state, or admit an
external effect.

The pure test-only surfaces are:

```text
validate_m1b(bytes, schema_epoch) -> typed record or refusal
resolve_route(fixture input) -> exact expected eligibility decision
resolve_plugins(fixture input) -> exact graph/effective-grant decision
evaluate_process(fixture input) -> exact requirement/capability decision
replay_broker_trace(fixture input) -> exact protocol decision
```

They observe no wall time, environment, filesystem beyond committed fixtures, network, process,
provider, credential, plugin implementation, random source or mutable global state.

## Route contract

A route is a complete reference tuple over engine, provider, model, capacity pool, opaque account
credential reference, host and sandbox. No component implies another. A descriptor carries dated
evidence and explicit eligibility state. A successful historical dispatch does not establish
current entitlement, privacy, billing, cache or capacity.

Resolution receives an ordered, unique candidate list produced by policy/routing logic outside
M1B. It evaluates each candidate in that order and selects the first candidate for which every
required capability and every authority, privacy, egress, billing, pool, host and sandbox bound is
satisfied. Every candidate receives a complete sorted rejection list. If none is eligible, the
result is blocked. The oracle never invents a route, silently substitutes an unlisted candidate or
turns subscription exhaustion/unknown billing into metered authorization.

`verified-current` is the only directly selectable descriptor state. `documented`,
`observed-uncertain`, `stale` and `unavailable` all block autonomous selection. A required
tri-state capability must be `supported`; `unknown` is not weak support.

## Plugin contract

Resolution reads a bounded `PluginManifest@1` without importing implementation code. The manifest
binds the full artifact digest and transitive dependency-lock digest, protocol, trust tier,
provided/required capabilities, dependencies, exclusive resources, conflicts, isolation,
subscriptions, requested grant dimensions, resource envelope, provenance and license.

The resolver rejects unknown protocol/capability values, missing dependencies, dependency cycles,
digest or dependency-lock substitution, explicit conflicts and unordered exclusive-resource
ownership. Required capabilities resolve to exactly one declared dependency provider; missing,
ambiguous or rejected providers block their dependents. A valid signature or trust tier is
identity/review evidence, never runtime authority.

Effective authority is an intersection. Functional capability and workspace scope require exact
digest-bound grants whose GoalSpec and policy digests match the active policy envelope. Lifecycle
artifact and epoch bindings must match too. Credential, network, model-launch, route/account,
quota, spend, update, downgrade and grant-administration dimensions remain independently
represented. A deny at any source remains in the explanation. No manifest, edition, signature,
acknowledgement or dependency can widen GoalSpec/policy authority.

Lifecycle is:

```text
discovered -> verified -> admitted -> staged -> active
      |            |          |          |        |
      +-------- quarantined/rejected -----+--------+
active -> drain-and-fence -> retired | replaced
active -> revoked -> drain-and-fence -> retained-evidence | retired
```

Replacement verifies and stages the new digest, stops new admission to the old epoch, drains or
cancels only as operative policy permits, fences old packets/leases/subscriptions, preserves prior
evidence, advances the epoch and only then activates. Revocation blocks new admission immediately
without claiming that a remote effect stopped.

A disabled plugin is metadata only. Its trace must show zero implementation import/compile/
instantiate, filesystem payload scan, process/thread/timer/watcher, network, credential access,
quota reservation, spend, cache write, context injection, tool registration, executing callback
or event subscription.

## Process requirement contract

`ProcessRequirement@1` describes required transport, containment, cancellation, output and
identity properties. `ProcessCapabilityDescriptor@1` reports explicit source-bound observations.
The two are never collapsed. A host/OS label does not prove a Job Object, cgroup, pidfd, process
group, descendant capture or breakaway prevention property.

Every required capability must be `supported`. `unsupported`, `unknown`, stale evidence, platform
mismatch or identity mismatch blocks. The admission result is only a requirement decision; it
does not launch a process.

`ProcessTerminationObservation@1` records process-tree status separately from an
`effect_conclusion` fixed to `not-evaluated`. Termination, terminal close, EOF, job notification or
missing PID cannot prove a remote/external effect succeeded, failed or rolled back.

The operative PAUSE field is fixed to `current-immediate`. Future checkpoint, interrupt, drain and
emergency profiles may be listed as representable alternatives, but M1B cannot select or execute
them.

## Broker protocol contract

The broker—not a PTY, renderer or terminal view—owns process identity, cursors, input/resize
leases, recovery and fanout. The closed message union is `HELLO`, `WELCOME`, `SNAPSHOT`, `EVENT`,
`ACK`, `CREDIT`, `INPUT`, `RESIZE` and `RESET`.

- Raw-output cursors count UTF-8 bytes; canonical-event cursors count events. Units never mix.
- Daemon and process epochs fence stale clients.
- One current input lease and one current resize lease may write; passive clients cannot.
- Commands are idempotency-bound.
- Credit is explicit and cumulatively consumed by decoded bytes and event count; each client's
  unacknowledged queue is cumulatively bounded.
- ACK cannot advance beyond emitted output. Stream, client and WELCOME lease bindings are exact.
- A gap yields explicit `RESET` with reason `gap` and a current snapshot cursor.
- Slow or absent clients cannot block canonical append or cause an unbounded queue.
- Attach, detach, replay and reset never launch a process/model turn or create an actor/effect.
- Output bytes are untrusted data and never interpreted as broker commands.

## Closed outcome/reason ownership

The exact JSON representation and reason alphabets are owned by
[M1B-WIRE-PROFILE.md](M1B-WIRE-PROFILE.md). The 24 required outcomes are owned by
[M1B-FIXTURE-ORACLES.md](M1B-FIXTURE-ORACLES.md). Unknown reason, message, capability, lifecycle,
trust or version arms fail closed rather than being retained as extension fields.

## Acceptance

M1B is complete only when the fourteen gates in
[M1B-CONSTRUCTION-CAMPAIGN.md](M1B-CONSTRUCTION-CAMPAIGN.md#machine-checkable-gates) pass on one
exact candidate and an independent verifier repeats the gates and records limitations. Passing
M1B proves only schema/oracle conformance over sanitized in-memory fixtures. It does not prove a
provider route, plugin sandbox, process containment primitive, terminal application, performance
budget, daemon, runtime, production system or constitutional policy.
