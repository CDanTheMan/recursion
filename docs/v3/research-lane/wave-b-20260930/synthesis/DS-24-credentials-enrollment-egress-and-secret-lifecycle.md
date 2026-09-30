# DS-24 — credentials, enrollment, egress and secret lifecycle (synthesis)

## Provenance

- Raw report: `raw/ds-DS-24-credentials-egress.md` — "DS-24 Research Report: Credentials, Enrollment, Egress, and Secret Lifecycle". Handoff:
  `docs/v3/prompts/research-suite-20260929/DS-24-credentials-enrollment-egress-and-secret-lifecycle.md`.
- Session: Wave B Deep Research (self-contained handoff), retrieved 2026-09-30. Status: research evidence, not a decision; not independently verified
  by Recursion, no rerun. No node was enrolled, no secret read or written, no provider contacted, no configuration changed, and no real secret value
  appears. Provider/standard claims are *source-documented*; consequences are *inferred*; platform/entitlement/distribution questions stay *unknown*
  or *unverified*.
- Sources: current provider docs, IETF RFCs/BCPs (8252/212, 9110, 8484, 9052, 9700/240), NIST guidance (SP 800-63-4, 800-88r2, 800-207A), SPIFFE/SLSA,
  and GitHub secret-scanning docs; "current" is as of 2026-09-30 and must be revalidated.

## The question

Decide the credential broker, auth-route separation, egress/classification enforcement, node enrollment, and secret-lifecycle
contract so an admitted route never widens authority, never leaks a secret into model-visible output or a tracked file, and never
reconstitutes canonical identity from a provider session. It blocks `E-FHAR2-104`/`105` and the security direction's threat-tested
requirements; `OR-019` forbids any external account, session or harness from owning or recovering canonical identity. `recursiond`
is a hypothesis, not an implementation authorization.

## Key findings

- **One "auth" field cannot carry five meanings.** Keep the four DS-24 route labels (API-key/BYOK, SDK OAuth, native-binary login,
  subscription-backed) but split authentication mechanism, entitlement, billing basis, distribution permission, and terms-of-service evidence into
  separate typed fields. `route_class = subscription-backed` does **not** imply `auth_mechanism = subscription`; the report's provider sources show
  plan sign-in versus own-API-key billing as visibly distinct routes.
- **Authentication is not entitlement, distribution, or terms.** A successful OAuth exchange proves a principal to a route, not billing,
  redistributability, or terms compliance, and an open-source CLI/SDK license does not prove account access. Public evidence did **not** establish a
  blanket right to reuse a consumer-login token as an SDK credential — the report marks that entitlement, distribution and ToS *unknown* (inference
  from absent primary documentation). RFC 8252/BCP 212 (external browser, PKCE, no embedded user-agents) and RFC 9700/BCP 240 (minimum privilege,
  audience restriction, sender-constrained or rotated refresh tokens) are *source-documented*.
- **Credential brokering and least-visibility delivery.** `recursiond` should be the sole component permitted to resolve an opaque `credential_ref`
  into usable material. Secrets persist only in a provider-native auth home, an OS secret store, or a configured vault — never Git, SQLite, prompts,
  worktrees, telemetry, context artifacts, plugin manifests, or tracked files. Workers get only an opaque reference plus minimum route-specific
  temporary materialization in a private overlay/process channel; model-visible data carries only a pseudonym and capability/billing class. Teardown
  is not revocation (a copied bearer survives overlay deletion), so strong teardown needs process containment plus short-lived/sender-constrained
  credentials, provider revocation, or a worker that never receives reusable bytes; deletion is a proof state (`REVOKED` ≠ physical deletion,
  `KEY_DESTRUCTION_VERIFIED` ≠ proof no copy escaped, `DELETION_PROVED` needs evidence over every copy or a backup-expiry bound).
- **Per-project egress, deny-by-default, decided on exact bytes.** Base is `private`/deny by default; prompt/config text must not widen eligibility.
  The decision is a compiled intersection (`ProjectClassification ∩ GoalSpecNetworkGrant ∩ RouteEligibility ∩ ProviderDataUseProfile ∩
  DestinationAllowlist ∩ ProxyResolverProfile ∩ CredentialLease ∩ ArtifactClassification ∩ SecretScanPass ∩ BillingAuthority ∩
  RequiredOwnerAcknowledgement`); no input adds authority because another is broad. The broker assembles final outbound bytes in memory before any
  socket write, classifies them, and binds project-local audit identity to route and policy revision. Contributor/training routes need a
  route/project-scoped acknowledgement, not a global "allow training" preference. Inherited `HTTP_PROXY`/`HTTPS_PROXY`, arbitrary CONNECT, PAC, DNS
  rebinding, unconfigured DoH, redirects, TLS/SNI mismatch and TLS interception are admission decisions, not ambient state (RFC 9110 CONNECT-target
  warning, RFC 8484 configured-resolver rule).
- **Node identity, enrollment, revocation.** Keep five independent layers: installation trust root, operator identity, node/device key,
  role/capability grant, and credential reference — a device certificate identifies a device and grants no
  executor/verifier/credential/publication/spending authority. Enrollment requires fresh proof-of-possession over a one-time nonce plus out-of-band
  Owner step-up bound to the exact request digest. Work envelopes are signed, scoped, expiring and replay-protected; wire format is deliberately
  **not** selected (COSE_Sign1 is only a comparator; RFC 9052 notes signature validity still needs expected-identity and authorization checks).
  Offline revocation immediately blocks new admission and renewal; a disconnected node holds only pre-issued bounded rights, may spool signed
  evidence, and cannot publish, widen authority or mint a lease until reconnect revalidation. Split brain is resolved by monotonically ordered
  fencing.
- **Conformance is asymmetric and provider refusals are typed.** Full adversarial conformance gates an official release claim; an ordinary install
  needs integrity checks plus deterministic preflight and quarantines only the failing remote capability, never local recovery. A model refusal is
  advisory and cannot override local credential/privacy/budget/egress/node-identity/publication boundaries; refusals are recorded with typed classes,
  and alternates are allowed only when the GoalSpec and local policy already authorize a compatible privacy/billing/egress route — never to evade a
  safeguard. Every model-using dependency resolves its own route and billing pool; a helper call is not automatically subscription-backed.
- **The threat list is a fixed adversarial suite, not prose.** Twelve required threats (stolen node credential, replayed work packet, malicious
  project config widening egress/permissions, prompt/tool-output exfiltration, plugin dependency confusion/update compromise, symlink/reparse/path
  traversal, stale route/GoalSpec after revocation, provider response forging evidence/completion, split-brain leases, disconnected node publishing
  stale work, public event metadata leaking private membership, owner-hostile defaults preventing local recovery) each get a concrete fault injection
  and decisive falsifier, plus proxy/DNS traces (DNS public-to-private rebinding, CONNECT to an unapproved port, inherited proxy rewriting an approved
  destination, unconfigured DoH resolution).
- **Scanning and preflight are supporting controls.** Redaction/scanning is layered and sink-enforced (architectural prevention, broker-known
  matching, provider-format rules, generic detection, bounded decoding, and a sink gate that scans before model visibility, evidence, telemetry,
  publication and tracked-file writes; scanner errors fail closed; alerts report field/path/class/ref, never bytes). Zero-model preflight is a pure
  deterministic function of local trust inputs (release/runtime/dependency/adapter/plugin/config/trust-bundle digests, certificate identity/expiry,
  revocation epoch, protocol/schema versions, permission snapshot, OS containment capability, egress/proxy/resolver profiles, broker contract version,
  clock health); it makes no model call and caches only while every trust-relevant key is unchanged. The report sets a measurement vector, not a
  threshold.

## Recommendation and falsifier

The recommended architecture is **Brokered Capability Intersection**: stable opaque credential references; route-specific
materialization only when required; broker-owned egress; short leases; process containment; signed node envelopes; and
authentication/entitlement/billing/distribution/ToS kept independent. It preserves native subscription clients, API/BYOK routes
and local recovery while maintaining a single authority boundary and failing closed on unknowns. Named competitors: **host
credential inheritance** (ambient provider sessions; fails on account enumeration, billing fallback, secret leakage, weak
revocation) and a **universal central API proxy** (cleanest secrets but breaks required native/subscription routes and may violate
provider boundaries).

- **Decisive falsifier:** the recommendation fails if an admitted route can cause any outbound provider byte or credential use outside the
  broker/enforced route boundary, or if a revoked credential lease can still be exercised by an owned descendant after a successful
  revocation/teardown receipt. A single reproducible bypass means the route must be narrowed, isolated differently, or marked unsupported — not
  relabeled a limitation.

## What this does not prove

- It does not certify live account entitlement, runtime conformance, or any provider's actual authentication behavior; route source evidence is not
  live entitlement evidence, and unknown entitlement/distribution/ToS cells stay `unknown`.
- It does not select a secret-store/vault product, wire serialization, language, or runtime, and does not authorize implementing `recursiond`.
- It does not prove overlay teardown actually revokes copied bearer material, nor that scanning catches every secret form; those remain falsifiable
  fixtures.
- It contains no Recursion measurements (preflight latency, resource use, bypass counts); it establishes the scorecard, not results.

## Open Owner decisions

- **Installation maximum:** whether a "full" installation may contain the broker/adapters without possessing a credential or holding egress/spending
  grants, and how easily a local installation may graduate to maximum credential/grant capability (the report favors separating installed capability
  from active authority).
- **Step-up cadence:** risk-triggered step-up plus a finite validity window; the maximum routine high-trust session period, and whether
  credential/grant administration requires step-up on every consequential operation (NIST AAL2 ≤24 h / AAL3 ≤12 h are comparators, not product
  policy).
- **Delegated credential administration:** whether delegated operators may select/rotate/disable/revoke already-approved opaque references inside an
  existing envelope without seeing values, while new-credential creation, export, trust-root changes and billing/egress widening stay Owner-only.
- **Secret-store/vault product and distribution/billing/entitlement policy** remain unselected.

## Relevance to later waves

DS-24 blocks `E-FHAR2-104`/`105` and the security direction's threat-tested boundaries, and supplies the semantic schemas
(`RouteDescriptor`, `CredentialRef`, `CredentialLease`, `EgressDecision`, `NodeIdentity`, `RoleGrant`, `WorkEnvelope`,
`StepUpReceipt`, refusal and teardown receipts) and the construction order (schemas → pure policy compiler → fake broker/synthetic
sinks → network harness → envelope verifier → zero-model preflight → one adapter at a time → full conformance). It fixes the
falsifiable acceptance vector — zero token-intermediation, secret-sink, unadmitted-egress, stale/replayed-packet and stale-fence
successes, zero preflight model calls, and explicit counting of unknown route fields — for the wave that builds the canonical
writer and credential/egress boundary.
