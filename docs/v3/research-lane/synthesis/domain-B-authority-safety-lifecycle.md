# Domain B — authority, safety and lifecycle (synthesis)

## Scope and lanes

This file consolidates the per-lane syntheses of the authority/safety/lifecycle cluster. It
aggregates only the eight listed lane syntheses; it does not rerun the lanes, inspect raw reports
beyond them, add facts or URLs, or assert any ratification. Every lane is research evidence, not a
decision, is not independently verified by Recursion, and reports no rerun.

Lanes consolidated:

- DS-01 pause, cancellation and effect fencing (Wave B, run 2).
- DS-02 Full Access and calibrated authority (Wave B, run 2).
- DS-03 risk-scaled verifier independence (Wave B, run 2).
- DS-04 plugin trust and supply chain (Wave B, run 2).
- DS-05 single-writer migration and effect rollback (Wave C).
- DS-07 privacy-preserving retention and deletion (Wave B, run 2).
- DS-08 private canary methodology (Wave B, run 2).
- DS-24 credentials, enrollment, egress and secret lifecycle (Wave B).

The domain reading is: how an admitted actor, route or artifact is granted bounded authority; how
that authority is fenced where an effect actually happens; how independent verification and
admission gate consequential transitions; how lifecycle events (update, migration, retention,
deletion, credential teardown, canary) are made evidence-backed rather than optimistically
asserted.

## Lane digests

### DS-01 — pause, cancellation and effect fencing

- **Bottom line:** freeze the future pause family around explicit admission fencing (a monotonic
  admission epoch), mode-specific continuation boundaries (`checkpoint`, `interrupt`, explicit
  `drain`, independent emergency stop), typed ambiguity and proof-based quiescence — not around
  cancellation requests. A controller-only `paused=true` is not proof; the invariant is receiver-side
  fencing immediately before an irreversible boundary.
- **Confidence/evidence class:** source-documented primitives (Chubby delayed-lock-holder reasoning,
  Linux cgroup v2, Windows Job Objects, Slurm TERM→KillWait→KILL, provider turn/message lifecycle
  contracts) with an inferred pause state machine and 28 pinned class×mode claims.
- **Does not prove:** that every provider adapter can place a fence close to its irreversible
  boundary, that opaque harnesses expose equivalent turn boundaries, that provider
  idempotency/status stays queryable, or that every publication backend supports conditional
  visibility — and it selects no containment technology or timeout.

### DS-02 — Full Access and calibrated authority

- **Bottom line:** Full Access is an explicit capability catalog plus typed grants, not an ambient
  boolean; effective authority is computed deterministically at effect-admission time as an
  intersection of installation maximum, valid grant chain, policy/version, temporal/revocation
  state, authentication/step-up and limits. Delegation is monotonic attenuation; `grant-admin`
  self-mutation uses two-phase prepare/commit with a single-use step-up receipt; audit receipts are
  kept separate from raw artifacts.
- **Confidence/evidence class:** source-documented precedents (permission boundaries, Kubernetes
  `escalate`/`bind`, seL4 restricted rights, Biscuit offline attenuation, OAuth audience/delegation/
  PoP/step-up specs, transparency logs) with an inferred Recursion design (`E = M ∩ G_s ∩ P ∩ T ∩ A ∩ L`).
- **Does not prove:** that the current kernel or adapters implement the model; that subset checking
  alone prevents confused deputies, replay or malicious providers; that a revocation check can
  rewind an effect a remote system already committed; or which adapters honor fencing/idempotency.

### DS-03 — risk-scaled verifier independence

- **Bottom line:** retain risk-scaled `V0`–`V3` verification with an explicit independence-vector
  record; keep exact deterministic gates non-substitutable; require a genuinely different failure
  domain for `V2`/`V3`; treat unknown relationship metadata as unknown; and use a blinded
  preregistered matrix to establish which dimensions actually reduce false-green gates.
- **Confidence/evidence class:** source-documented high confidence for actor, evidence acquisition
  and implementation authorship; medium/inferred for model family and the tier rule;
  unverified/low confidence for provider and account/capacity-pool semantic detection; the
  480-candidate measurement design is a proposal, not a result.
- **Does not prove:** that public standards converged on `V0`–`V3`; that any dimension raises defect
  recall by a known amount; that higher tiers are always economically optimal; or that the tiers
  are legally mandated. Deterministic gates establish only their encoded property.

### DS-04 — plugin trust and supply chain

- **Bottom line:** keep evidence/provenance, trust tier/isolation and authority grants as three
  independent axes; a maintainer signature authenticates a digest under a review policy but never
  grants authority. Admission is digest-specific over the executable closure; unsigned local plugins
  keep full expressiveness under explicit grants; update/reload is a generation transition
  (`stage → drain → fence → activate`); disabled is a zero-effect tripwire property; remote data is
  evidence, never a remote kill/update primitive.
- **Confidence/evidence class:** mixed source-documented/inferred/unverified; TUF, Sigstore threat
  model, WASI, SLSA, in-toto, SPDX and package-manager practice are cited; cross-runtime capability
  enforcement is labelled medium; some licensing pages are left unverified.
- **Does not prove:** that signed or admitted code is safe; that native-plugin containment is settled;
  that a local fence cancels an already-accepted remote effect; that any runtime, language, sandbox,
  signing root or package format is selected; or what consent batching is optimal.

### DS-05 — single-writer migration and effect rollback

- **Bottom line:** freeze the single-writer contract first on the synthetic execution-attempt/lease
  aggregate. The sufficient cutover boundary is a versioned ownership checkpoint proving writer
  enumeration, quiescence, a monotonically higher writer epoch enforced at admission and durable
  commit, order-sensitive event-prefix parity, deterministic crash recovery, a tested backup and
  reverse-reader path, and exclusive v3 ownership. After an effect may have been accepted, the rule
  is forward reconciliation, never relabeling as rolled back.
- **Confidence/evidence class:** inferred with high confidence, consistent across primary evidence on
  fencing, conditional mutation, event replay, outbox duplicates, failure ambiguity and
  external-effect semantics; source-documented standards and vendor docs are cited.
- **Does not prove:** that a complete writer inventory already exists, that every storage path can
  enforce epochs, that a reverse-reader currently exists, that success on one aggregate generalizes
  to task lifecycle/assignment/run-evidence/result-ledger/journal, or any exactly-once guarantee.

### DS-07 — privacy-preserving retention and deletion

- **Bottom line:** standardize a deletion evidence contract — a closed per-request copy inventory and
  separate key-recovery ledger, explicit per-copy predicates, a strict distinction among `partial`,
  `blocked`, `expiry-bound` and `verified-complete`, a policy-generation guard for pin/legal-hold
  races, scope separation of identity/address/key/request, a minimal signed non-sensitive tombstone,
  and independent review — rather than a single key granularity. `verified-complete` is a read-only
  derived state no component may set directly.
- **Confidence/evidence class:** source-documented (NIST SP 800-88 Rev. 2, key-destruction
  definitions, KMS provider docs, deduplication side-channel research, GDPR Article 17) with an
  inferred evidence state machine; the report contains no measured cells.
- **Does not prove:** that cryptographic erasure removes every copy, that an escrowed/exported/
  restored key cannot re-enable ciphertext, that a provider attestation is direct physical
  observation, or any physical-destruction proof for an arbitrary disconnected node (explicitly
  unknown). No key granularity, epoch, provider or storage engine is selected.

### DS-08 — private canary methodology

- **Bottom line:** use a sealed two-layer, alias-only protocol — preventive test/fixture-only
  filesystem enforcement plus a complete machine-readable write audit, an independent-oracle label,
  a mandatory contrastive sensitivity test, all five failure injections, a fresh-state independent
  rerun, independent review, and exactly one local candidate commit. A characterization pass is not
  a correctness pass, and `unknown` is not zero. No canary has run.
- **Confidence/evidence class:** inferred protocol with source-documented Git/SLSA/OWASP/NIST
  references; the only locally observed fact is the no-start statement for this research session;
  existence of an independent authoritative oracle is unverified.
- **Does not prove:** correctness of a production rule (absent an independent oracle), migration
  correctness, security, exhaustive fault coverage, route reliability, release readiness or
  Recursion-wide conformance; it is not a repository-level secret scan. Correct state is
  "not-ready-to-run".

### DS-24 — credentials, enrollment, egress and secret lifecycle

- **Bottom line:** the recommended "Brokered Capability Intersection" keeps stable opaque credential
  references with route-specific materialization only when required, broker-owned egress decided on
  exact compiled bytes and deny-by-default, short leases, process containment, signed node
  envelopes, and authentication/entitlement/billing/distribution/ToS as independent typed fields.
  Refusals are typed and advisory; conformance is asymmetric (full adversarial conformance gates a
  release claim, an ordinary install needs integrity checks plus deterministic zero-model preflight).
- **Confidence/evidence class:** source-documented provider/RFC/NIST/SPIFFE/SLSA claims with inferred
  consequences; entitlement, distribution and ToS cells remain unknown from absent primary
  documentation; no Recursion measurements.
- **Does not prove:** live account entitlement or provider authentication behavior; that overlay
  teardown revokes copied bearer material; that scanning catches every secret form; any secret-store/
  vault product, wire serialization, language or runtime; and it does not authorize implementing the
  hypothesized broker.

## Cross-lane consistency and contradictions

Recurring themes across the cluster:

- **Routing or visibility is not authority.** DS-02 states model text is never an authorization
  statement; DS-04 states a signature authenticates a digest but is not an authority grant; DS-24
  states authentication is not entitlement, distribution or terms; DS-03 states "stronger model" is
  not an evidence class. Visible trust or a successful exchange never widens capability.
- **Fencing must be enforced where the effect happens, not only upstream.** DS-01's receiver-side
  invariant; DS-05's requirement that the epoch/sequence check recur at the durable mutation
  boundary, not only a router; DS-02's fencing value inside grant admission; DS-04's generation
  identity on every effect-bearing packet, lease, subscription and broker handle; DS-24's split-brain
  fencing and stale-fence threat; DS-07's policy-generation guard before irreversible operations.
- **Typed ambiguity, quarantine and forward-only reconciliation.** DS-01 (`ambiguous`/`quarantined`),
  DS-05 (`UNKNOWN` is not zero; dependents stay blocked), DS-24 (typed refusals) and DS-04 (ambiguous
  remote outcomes remain for reconciliation) share the same posture; DS-02's receipts are
  forward-only. No lane treats a missing receipt as evidence an effect did not occur.
- **Completion is derived and independently accepted, not asserted.** DS-07 `verified-complete` as
  read-only derived state; DS-05 checkpoint gate; DS-08 independent clean rerun and review; DS-03
  tier contract with no edge from missing evidence to ordinary pass.
- **Unknown is kept distinct from zero/absent.** DS-07, DS-08, DS-24 and DS-05 all state this
  explicitly; DS-03 requires unknown relationship metadata to stay unknown rather than count as
  independence.

Apparent tensions, none resolved here:

- **`drain` arbitration is open in two lanes.** DS-01 leaves `drain` vs `checkpoint` exclusivity and
  the drain allowlist unresolved; DS-04 also places `drain` inside the generation transition without
  fixing the same arbitration. They agree on vocabulary, not on precedence.
- **Credential material as a grantable capability.** DS-02 lists credential-material revelation as a
  possible high-impact domain but leaves it an Owner question; DS-24 keeps credential
  administration delegated but value-visibility Owner-only. The two are compatible but not yet
  reconciled into one rule.
- **Two different "broker" senses.** DS-05 treats a message/outbox broker as replaceable transport
  unless a decisive test shows its offset/ack state is needed; DS-24 uses "broker" for the
  credential/egress boundary that must be authoritative. This is a homonym, not a conflict, but the
  vocabulary can be misread.
- **Provider/account/host value.** DS-03 marks their semantic-verification value unverified while
  DS-24 relies on provider route separation. These are different claims (semantic defect detection
  vs entitlement/threat separation) and should not be collapsed.
- **Unsigned plugin expressiveness (DS-04) vs broker-enforced effects (DS-24):** consistent only if
  "full expressiveness" continues to mean full API reach under explicit grants and enforced brokers,
  which both lanes state.

## Cross-lane dependencies

- **DS-01 pause/fencing is substrate.** DS-04 generation fencing, DS-02's grant-admission fencing
  value, DS-05's writer epoch, DS-24's stale-fence/replay threats and DS-07's policy-generation guard
  all depend on the epoch/fence vocabulary DS-01 supplies.
- **DS-02 capability grants feed DS-04 and DS-24.** The typed capability/effect catalog, subset
  lattice and prepare/commit `grant-admin` action are the authority vocabulary DS-04's authority axis
  and DS-24's role grants must reuse.
- **DS-03 verification governs acceptance across lanes.** DS-07 completion acceptance, DS-08
  independent rerun/review, DS-05 cutover rehearsal validation and DS-24 full-conformance gating all
  need a verifier-independence contract.
- **DS-04 consumes DS-01 and DS-02, and feeds DS-24.** Plugin generation fencing needs DS-01; plugin
  authority admission needs DS-02; DS-24's dependency-confusion/update-compromise and
  model-launch/route threats include plugin paths.
- **DS-24 supplies effect brokers DS-04 requires.** DS-04's filesystem/network/secrets/model/routing/
  quota/spend brokers are the same mediation surface DS-24 defines as the sole credential resolver
  and egress decider.
- **DS-05 depends on DS-01 and DS-24.** Migration fencing is a fencing application; distributed
  writers need DS-24 node identity/envelopes and offline revocation; the rehearsal is a DS-03-style
  verification artifact.
- **DS-08 is a gate-shaping input to DS-03 and DS-05.** Its independent-oracle/rerun/review structure
  is the same shape DS-03 wants and DS-05's cutover rehearsal requires.
- **DS-07 intersects DS-02 and DS-24.** Audit receipts vs raw-artifact lifecycle (DS-02) and secret
  teardown/deletion-proof states (DS-24, where `REVOKED` ≠ physical deletion) share DS-07's copy/key
  ledger distinction; DS-05's external-effect watermark interacts with retention of checkpoint
  evidence.

## Consolidated open Owner decisions

Unresolved choices aggregated across lanes; none is decided here.

- **Sovereign grant-admin scope:** whether sovereign self-widening requires an independent human;
  whether raw credential material is ever a grantable capability; the out-of-band recovery/root
  mechanism; installation maximum vs active authority; delegated credential administration bounds
  (DS-02, DS-24).
- **Audit retention and erasure:** retention duration and authority; erasure authority and eligible
  artifact classes; internal-only vs exportable tombstone (DS-02, DS-07).
- **Route classes:** which grant dimensions may be confirmed in one interaction; which authorizes
  route/billing/entitlement evidence; default local reaction to an emergency advisory; support-window
  and unmaintained-source policy; downgrade granularity; maximum spend and "unbounded" meaning
  (DS-02, DS-04, DS-24).
- **Release-vs-install conformance:** what authority carries from digest D to an approved update D′;
  how the executable dependency closure is defined for interpreted/dynamic plugins; which tiers may
  use native execution; which adapters honor fencing/idempotency (DS-02, DS-04, DS-24).
- **Migration target:** whether the first checkpoint must contain a post-cutover `H+1` command;
  whether the broker is outside the aggregate boundary; writer identity as logical capability vs
  concrete process; rollback eligibility duration; whether all aggregates share a global epoch; the
  canonical event-equivalence rule (DS-05).
- **Pause semantics:** `drain` vs `checkpoint` exclusivity and the drain allowlist; whether
  publication is drain-eligible; emergency reconciliation reads; `paused_with_ambiguity`; per-effect
  deadlines; capacity-exhaustion field; auto-quarantine duration; quiescence-proof type (DS-01).
- **Retention/deletion semantics:** whether `expiry-bound` is user-visible and non-complete; the
  artifact-level claim when a shared key stays live; acceptable coupling window; cross-project dedup
  participation; pin vs legal-hold authority; provider evidence tier; lost-node irrecoverability;
  post-expiry verification; the independent reviewer role (DS-07).
- **Verification policy:** canonical risk-class boundary examples; which vector relationships must be
  positively evidenced vs allowed unknown; the materiality margin; human-review qualification and
  conflict-of-interest policy; receipt lifetime; whether provider/account/host claims stay
  hypotheses (DS-03).
- **Canary parameters:** the private prefixes for `ALLOW_TEST`/`ALLOW_FIXTURE`/`DENY`; the
  authoritative oracle source; what qualifies as an independent rerun; retention/access policy for
  route-approval evidence and the candidate revision; candidate-commit retention (DS-08).

## Domain gaps and open unknowns

- **Unrun experiments.** DS-03's preregistered 480-candidate blinded matrix (120 per risk class, six
  defect families, treatments T0–T7) has not run. DS-08's canary has never executed: no route was
  exercised and no candidate commit was created. DS-05 ran no cutover and no restore/reverse-reader
  rehearsal. DS-24 reports no measurements (preflight latency, resource use, bypass counts). DS-07
  contains no measured cells.
- **`unknown` cells.** DS-07 leaves physical destruction on an arbitrary disconnected node unknown,
  and keeps deletion proof states (`partial`/`blocked`/`expiry-bound`/`verified-complete`) as an
  unresolved evidence contract. DS-03 leaves provider, account/capacity-pool and host
  semantic-verification effects unverified. DS-24 leaves entitlement, distribution and ToS unknown
  and the wire format unselected. DS-02 leaves adapter fencing/idempotency, topology, credential
  storage, quorum and disaster recovery unverified. DS-04 leaves native-plugin containment,
  licensing pages and optimal consent batching open.
- **Implementation and inventory unknowns.** No lane shows the current kernel/adapters implement the
  contracts; no lane establishes a complete writer inventory or that every storage path can enforce
  epochs; no reverse-reader is shown to exist; no independent authoritative oracle is shown to exist
  for the canary rule.
- **What an architecture phase would still need.** Selection of language, store, runtime, sandbox,
  secret store/vault, broker, wire serialization and signing root (none selected by any lane);
  definition of the canonical schemas and the pure deterministic policy compiler; construction of
  the negative fixtures (DS-07's list, DS-04's tripwires, DS-24's adversarial threat suite); a
  measurement harness for DS-03/DS-24; a canonical writer boundary and per-aggregate writer
  manifests; adapter-by-adapter conformance; and instantiation of private canary values. DS-05's
  recovery-reservation ledger and DS-07's legal-hold/counsel questions remain explicitly outside the
  research scope.

## Evidence-quality notes

- **Evidence classes preserved per lane.** DS-01: source-documented plus inferred. DS-02:
  source-documented precedents plus inferred design. DS-03: source-documented (high for
  actor/evidence/authorship), medium/inferred (model family, tier rule), unverified/low (provider,
  account/capacity pool). DS-04: source-documented/inferred/unverified, with cross-runtime
  enforcement medium. DS-05: inferred with high confidence, consistent across primary sources.
  DS-07: source-documented plus inferred, measured = none. DS-08: inferred protocol,
  source-documented references, one locally observed no-start fact, independent-oracle existence
  unverified. DS-24: source-documented, inferred consequences, unknown entitlement/distribution/ToS,
  no measurements.
- **Weak points.** No lane was independently verified by Recursion and no lane reran. Confidence
  values describe research support, not probability; expiry values are review triggers, not claims
  that older evidence is false. Several provider and NIST references are explicitly time-bound
  ("current" as of a stated date, e.g. 2026-09-30 for DS-24) and must be revalidated. DS-04 notes
  some licensing pages and DS-08 notes NIST SP 800-218 v1.2 as a draft. Many recommendations are
  inferred designs synthesized from source-documented primitives rather than measured Recursion
  behavior (DS-02, DS-05, DS-07, DS-24).
- **Bounded proof statements.** DS-08's no-start fact is scoped to the research session only and is
  not evidence about any other actor. DS-05's prior failed partial plan was preserved and not
  accepted; this synthesis draws on the successful rerun. DS-04 and DS-07 state that a signature or
  signed tombstone proves integrity/inclusion, not benign behavior or physical deletion.
- **Aggregation limits.** This file is itself a summary of summaries. It inherits each lane's
  evidence-class boundaries, adds no revalidation, and must not be read as an accepted decision or
  as authorization to implement, cut over, delete, enroll, publish, spend or run anything.
