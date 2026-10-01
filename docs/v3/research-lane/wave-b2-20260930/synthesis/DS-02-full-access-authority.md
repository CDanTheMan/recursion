# DS-02 — Full Access and calibrated authority (synthesis)

## Provenance

- Raw report: `raw/ds-DS-02-full-access-authority.md`.
- Source prompt: DS-02 — Full Access and calibrated authority.
- Session: Wave B Deep Research (self-contained handoff, run 2); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved: source-documented, locally observed, inferred, and unverified.
- The report states it did not modify any system, grant authority, private repository, provider, credential, spend, deployment, merge, publication, or the operative constitution.

## The question

What authority model should Recursion v3 freeze for Full Access, the `sovereign` preset, `grant-admin`, break-glass elevation, grant inheritance/revocation, replay and stale-parent prevention, audit separation, blast-radius acknowledgement and recovery?

- The report treats the ratified premises as constraints, not questions to reopen: `sovereign` may explicitly include `grant-admin`; a `sovereign` actor may modify its own grants attributably; installing the `full` edition never implies `sovereign`; model text is not authority; grant administration stays distinct from audit-retention and audit-erasure; and the output is recommendations rather than decisions.

## Key findings

**(a) Full Access should be an explicit capability catalog plus typed grants, not an ambient boolean.**

- "Full Access" is recommended as a user-facing description of the effective vector only when that vector contains every grantable capability in the installation's declared catalog at the displayed scopes and limits.
- A `sovereign` preset may construct such a vector, but a preset must never itself authorize anything.
- The report cites precedent that grants and ceilings are separate: AWS permission boundaries and organization policies define maxima; Kubernetes protects `escalate`/`bind`; seL4 copies carry restricted rights; Biscuit attests to offline attenuation.
- The competing single-boolean design is falsified by any two legitimate "full" grants that differ only in scope, lifetime, spend, delegation, or authentication age.

**(b) The high-impact vector separates at least a dozen authority domains.**

- Cited domains: control-plane authoring, credential administration, credential-material revelation (if supported), provider enrollment (if supported), metered spending, publication, merge, deployment, service control, grant administration, audit-retention administration, and audit erasure.
- These are not interchangeable: merge need not imply deployment, deployment need not imply service lifecycle control, and `grant-admin` must not imply erasing evidence of grant mutation.

**(c) A grant is admitted only by a full deterministic predicate, not by a signature.**

- Required checks include structural validity; issuer/subject/installation/audience/capability/effect/scope match; time within `[not_before, expiry)`; authentication/step-up; spend/resource/rate limits; parent digest and delegation depth; componentwise child-subset of parent; current revocation epoch; and the currently admissible fencing value.
- The report argues OAuth's separate audience, delegation, proof-of-possession/replay, step-up, and fine-grained-authorization specifications show these properties cannot be collapsed into "validly signed."

**(d) `grant-admin` self-mutation uses two-phase prepare/commit.**

- Preparation canonicalizes the requested before/after grant and yields a blast-radius preview plus digest.
- Commit requires a fresh, single-use step-up receipt bound to that exact digest, checks current authority and the installation maximum, atomically consumes the receipt, increments the relevant mutation/revocation generation, writes the new grant state, and appends an immutable receipt.
- Natural-language text may motivate a request but is never evaluated as an authorization statement.

**(e) Ordinary delegation is monotonic attenuation.**

- A valid child must be a subset of its parent in every ordered dimension (effects, scope, resource/spend/rate limits, `not_before`, `expires_at`, delegation depth).
- `unknown`, absent, malformed, and incomparable values must cause rejection rather than being coerced to zero or "unlimited"; genuine `unbounded` must be an explicit tagged value.
- Narrowing or revoking a parent invalidates affected descendants; widening a parent does not widen an existing child.

**(f) Validity is computed, not inherited from issuance.**

- Recommended formula: `E(s,t,a) = M ∩ G_s ∩ P ∩ T ∩ A ∩ L` — installation maximum, valid grant chain, policy/version constraints, temporal/revocation state, authentication/step-up, and limits.
- The report calls this an inferred Recursion design synthesized from the intersection/guardrail model plus temporal, delegation, and authentication mechanisms.

**(g) Audit separates receipts from raw artifacts.**

- Receipts are append-only evidence; raw artifacts may have a separately governed lifecycle.
- Receipts retain hashes, before/after digests, actor, issuer, reason, authentication receipt identity, and outcomes, so raw content can later be deleted without deleting proof that a privileged event occurred.
- Transparency-log designs (Merkle inclusion/consistency proofs) are the closest analogue; they detect misbehavior, do not by themselves prevent a bad action, and need independent monitoring to detect equivocation.

**(h) Threat modeling must cover valid actors using valid artifacts in the wrong context.**

- Enumerated threats: confused deputy/wrong audience, privilege accumulation, authority bundling, replay, stale parent, stale authentication, delegation-depth escape, preview/commit TOCTOU, self-approval collapse, audit concealment, and irreversible side effects after revocation.
- The "signatures-only falsifier": sign a child, revoke the parent without changing the child's bytes, and confirm the child is denied.

**(i) Staging and independent approval are distinct knobs.**

- Recommended for self-widening, credential revelation/rotation, spending-ceiling widening, public publication, policy-changing control-plane writes, and audit-policy changes.
- Two humans are not universally required; multi-person approval is an Owner-configurable policy for the most destructive scopes.
- Its decisive falsifier is evidence that the staged path makes required emergency recovery impossible even when no approver is configured.

**(j) The completion gate is a set of deterministic denial tests.**

- `edition=full` with no `sovereign` grant denies every sovereign-only effect; a preset alone changes nothing.
- Child effects/scope/limits/lifetime/delegation cannot widen; unknown limits reject; parent revocation kills a stale child; parent widening does not widen a child.
- Step-up is one-use and action-bound; preview is commit-bound; `grant-admin` does not imply audit erasure; receipts are forward-only.
- The report labels all of these as recommendations and states implementation status is unverified.

## Recommendation and falsifier

- Freeze a typed capability-vector model: installation maximum catalog, exact capability/effect pairs with scope, explicit limits, timing, delegation depth, parent digest, policy/GoalSpec versions, authentication requirement, revocation generation, lease/fence metadata, and opaque credential references; compute effective authority deterministically at effect-admission time.
- The competing option is a confirmed ambient Full Access boolean, falsified by two legitimate full grants that require differing scope/lifetime/spend/delegation/authentication semantics.
- Each recommendation in the report is paired with a competing option, a decisive falsifier, and a statement of what it does not prove.

## What this does not prove

- It does not show that the current Recursion kernel or adapters implement this model.
- Subset checking alone does not prevent confused deputies, replay, or malicious provider behavior; a revocation check cannot rewind an effect a remote system already committed.
- A captured reason can be dishonest, so reason capture is attribution rather than authorization; append-only storage does not solve split-view or monitoring failure.
- Which external adapters can honor fencing/idempotency is explicitly unverified, as are installation topology, credential storage, deployment targets, quorum rules, and disaster-recovery implementation.

## Open Owner decisions

- Audit-retention duration and authority; audit-erasure authority and eligible artifact classes.
- Step-up cadence by capability class.
- Whether sovereign self-widening requires an independent human.
- Whether raw credential material is ever a grantable capability.
- Maximum spend policy and the meaning of "unbounded."
- The out-of-band recovery/root mechanism.
- Which external adapters can honor fencing/idempotency (explicitly unverified).

## Relevance to later waves

- The capability/effect catalog, typed grant schema, subset lattice, and prepare/commit `grant-admin` action are the vocabulary later authority, elevation, audit, and recovery lanes must reuse.
- The explicitly unverified adapter fencing/idempotency behavior and current implementation status are concrete gaps for implementation and verification lanes, not research conclusions.
- The open policy values are candidates for explicit Owner decision records.
