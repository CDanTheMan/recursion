# FU-04 — OS platform conformance (synthesis)

## Provenance

This synthesis summarizes the raw report `raw/ds-FU-04-os-conformance.md` (its own title:
"Operating system platform conformance fixtures"). It is a proposed qualification contract and
preregistered negative-trace catalog only: every platform case is Unqualified, no measured result
exists, and no OS, kernel, filesystem, terminal, runtime, store, process library or product
configuration was selected, certified or executed. Sources were checked 1–2 October 2026 after
the G04 and DS19 gaps. Its sources are public primary sources — standards texts, published API
and kernel documentation and pinned release tags — used as reference editions, not support floors;
this synthesis calls them "the report's sources" and invents no URLs. All schemas, rules and
fixtures are inferred, and no platform result was locally observed.

## The question

What exact, falsifiable platform qualification is needed before FU-02 (store/replay) and FU-05
(broker/chaos) may rely on a host or compatibility route? The report answers that qualification
attaches to an exact behavioral envelope — OS and updates, creation and containment, privileges
and namespaces, terminal and shell path, supervisor policy, storage stack, failure domain and adapter — not to a brand name. It proposes a machine-readable manifest and fingerprint, a
mandatory case catalog, a shared observation and recovery contract, twenty preregistered negative
traces, a durability failure-domain model and an exhaustive outcome rule.

## Key findings

### Fingerprint over the behavioral envelope

A pinned profile projects each known fact to its exact value and each justified `not_applicable`
fact to a literal marker, rejects any remaining unknown, wraps the projection in a domain-tagged
object, canonicalizes it with JCS and hashes it, yielding `fu04-p1:sha256:` plus 64 lowercase hex
digits. Any envelope-value change creates a new key. The key excludes fixture implementation but
includes the adapter artifact and configuration; each result separately pins fixture, harness,
contract, adapter, variant, cut point, failure domain, repetition and seed. Unknown,
not-applicable, zero and empty are four distinct states.

### Eleven mandatory profiles, expandable, never quietly removed

The manifest holds eleven pending rows: `native_windows`, `native_linux`, `wsl2_ext4`,
`wsl2_mntc`, `msys2`, `git_bash`, `embedded_windows`, `embedded_linux`, `smb_windows`,
`smb_linux`, `nfs_linux`. Each selected architecture, filesystem, terminal route, supervisor
policy or security mode expands the case into a distinct profile, and a combination gets its own
composite row. The Owner may exclude a category, but its mandatory row remains with the recorded
exclusion and a rejected/unsupported outcome; passing one profile qualifies no other.

### Five predicates that must not collapse

The report separates `transport_closed`, `client_disconnected`, `containment_empty`,
`process_exited` and `execution_settled`: closing a transport, disconnecting a client, observing
an empty containment scope, observing a process exit and settling an execution are independent. A
`ClosePseudoConsole` return is explicitly not an execution-completion oracle and its behavior
changes at a documented build boundary; a successful API call, absent notification, unrun fixture or implementer PASS cannot settle an execution. Membership-limited termination proves only that
processes remaining inside the named scope reached a terminal state, not complete descendant or
causal capture. The settled conjunction requires admission fenced, required work terminal or
explicitly excepted, scope empty, output drained or explicitly truncated, accounting finalized,
ownership reconciled, the canonical outcome committed under the chosen durability domain, and
recovery unable to reanimate stale execution.

### Twenty preregistered negative traces

PF01–PF20 cover containment escape and causal completeness; parent death before registration;
handle/scope lifetime and terminal teardown; signals and console scope; atomic replacement and
failure-domain or power interruption; locks and mapped-view bypass; PID reuse; disk/quota and
delayed write failure; memory throttling, refusal, process kill and group kill; supervisor restart
and stale-owner race; suspend/resume deadline semantics; network-storage ambiguity;
lost/duplicated/reordered notifications; compatibility and embedded-host boundaries; permission
and feature denial; resource accounting completeness; and combined failures with false-oracle
controls. Each is an unexecuted design with prerequisites, injected fault, observation oracle,
recovery oracle, stop conditions and named source mechanisms. The shared protocol fixes common
actors, barriers, generation-distinct content, independent witnesses and the rule that an
unreachable or indistinct cut point is unknown rather than a nearby pass.

### Durability domains, resource faults, proposed artifacts and the outcome rule

Durability is an acknowledged outcome within a named failure domain: `process_crash`,
`guest_reset`, `host_reset`, `physical_power_loss`, `network_partition` and `server_restart` are
separate cells, and "survives power loss" is forbidden without the failed powered domain, cache
volatility, acknowledged flush/FUA boundary, witness survival and recovery procedure. Resource
exhaustion is a family — `throttle`, `allocation_refusal`, `process_kill`, `group_kill`,
`unknown` — that must not collapse into a portable OOM result; a Job committed-memory ceiling is
not a Linux group OOM kill, group-OOM evidence stays separate from containment emptiness, and
unknown never becomes zero. The report also ships proposed JSON artifacts: a platform-manifest
schema and manifest with the eleven pending profiles and an empty results array, a negative-traces
schema and catalog, a profile-field index and a source register. The `proposed_unexecuted` stage
structurally requires the empty results array, so no fixture ran and it must never be rendered as
a zero-failure or zero-duration run; validating the documents establishes artifact structure only.
A profile is
Qualified only after Owner scope inclusion, resolved identity pins, a frozen contract and harness,
confirmed injection with complete evidence at every required variant and cut point, passing
oracles, no contradictory mandatory result, and independent acceptance; Rejected/unsupported
covers witnessed violations, unavailable capabilities and Owner exclusions, and everything else is
Unknown, the initial state of all eleven cases.

## Recommendation and falsifier

Use exact behavioral fingerprints (R01); preserve the five predicates (R02); require
creation-time membership or a qualified gated alternative (R03); trust native queries and
identity references alongside notifications (R04); separate storage claims by failure domain
(R05); preregister publication cuts and first-recovery inspection (R06); keep resource faults a
family (R07); require independent acceptance and sensitive-oracle controls (R08); make
compatibility and network routes explicit mandatory cases (R09); keep unknown distinct from
rejected and zero (R10); fence recovery before automatic retry (R11); and run destructive
evidence only in isolated disposable targets (R12). Decisive falsifiers: two configurations with
the same fingerprint that differ in a mandatory observed behavior; a settled conjunction
satisfied while required work remains live, unfenced or uncommitted; first-runnable work outside
scope in the parent-death fixture; a dropped notification yielding false settlement; a known-bad
control that passes; and a consumer treating unknown as acceptance. Correct exclusion is not
a pass, and none of this proves liveness, bounded completion or immunity to hardware faults.

## Local execution handoff

Local sessions must implement and execute PF01–PF20 for every selected profile and applicable
variant, plus inventory, preregistration, evidence collection and independent acceptance. The
queue: obtain O01–O12 decisions and record candidate-in-scope or owner-excluded for every
category; inventory each authorized disposable host and composite route with effective
configurations; implement adapters and actors in an authorized engineering session; freeze a run
specification (profile key, contract and adapter digests, numeric budgets, finite cut list,
repetitions, seeds, allowed outcomes, witness placement, safety approvals) for a
non-implementer's review; run no-fault and known-bad oracle controls first; run process-identity, membership,
permission and lock fixtures, then per-route terminal/compatibility fixtures; run resource-failure
and accounting fixtures with independent headroom; run the publication fixture under
`process_crash` first and other failure domains separately with labels retained; run supervisor,
deadline and isolated network-storage fixtures; and run combined cases, returning first recovery
observations before cleanup. Destructive work needs disposable bounded targets, independent
witness power, a tested restore path and a human-approved interruption procedure; otherwise
`physical_power_loss` stays unknown and the weaker observed domains are stated exactly. The
returned bundle carries the pinned manifest, preregistration, raw observations, independent
witnesses, sequence-gap and clock records, before/first-after recovery digests, counter baselines
and finals, cleanup log, per-cell reasoning and the reviewer decision; an implementer's completion
message is not acceptance.

## What this does not prove

This is a specification and qualification protocol, not a platform certification or measured
performance result; every case remains Unqualified and document/schema validation establishes
only artifact structure. Source-documented mechanisms do not show that any target implements them
correctly, and an issue report cannot replace normative documentation or target evidence.
Membership at one moment is not membership since creation; emptiness is not non-repopulation;
atomicity is an observation contract about named objects and observers, not durability; and
surviving a finite power experiment is not a universal hardware guarantee. The report selects no
implementation language, library, store, protocol or platform.

## Open Owner decisions

O01 platform floor; O02 compatibility scope; O03 storage scope; O04 durability promise; O05
causal containment boundary; O06 terminal semantics; O07 deadline semantics; O08 resource policy;
O09 supervision and recovery; O10 experimental budgets; O11 evidence and independent acceptance;
O12 destructive authorization. These are required manifest facts rather than implied choices, and
Lucas remains the final Owner.

## Relevance to later waves

FU-04 is a prerequisite for FU-02 and FU-05. FU-02 must bind accepted profiles and use identical
canonical workload and CAS assumptions for both finalists, separately establishing replay parity,
stale-writer exclusion, duplicate-command reuse, consistent backup/restore and the precise
durability failure class — a process-kill pass is not a power-loss pass and a database writer
lock is not an authority lease. FU-05 requires accepted platform observations and approved or
narrowed native-support floors before its interoperability and chaos cells can advance. Later
waves may implement the proposed JSON specifications and run the preregistered fixtures, but the
empty results array means every profile remains Unqualified until the O01–O12 inputs are bound,
destructive prerequisites are met and independent review accepts retained evidence; no native or upstream inheritance is a shortcut.
