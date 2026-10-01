# DS-04 — plugin trust and supply chain (synthesis)

## Provenance

- Raw: `raw/ds-DS-04-plugin-trust.md`.
- Handoff: `DS-04 — plugin trust and supply chain` research directive supplied to the run.
- Session: Wave B Deep Research (self-contained handoff, run 2); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved from the report: **SD** = source-documented; **M** = inferred/modelled from source-documented facts; **U** = unverified/unknown. Evidence classes are kept distinct; nothing below is reported as measured or selected.
- Scope: read-only. The report states it performed no repository inspection, installation, signing, publication, deployment, provider/auth/configuration change or spending, and assumes no mandatory remote control plane.
- Source base: the report cites TUF Specification 1.0.36, the Sigstore threat model, WASI 0.3 / WebAssembly Component Model, SLSA v1.2 provenance, in-toto (USENIX Security 2019), SPDX 3.0.1, npm `package-lock.json`, Debian `apt-secure`, NIST SP 800-161, and the original 2021 dependency-confusion disclosure. All claims are attributed to "the report's sources"; no new facts or URLs are added.

## The question

How should Recursion v3 fix the semantics of maintainer signing, unsigned-plugin admission, authority grants, update/reload/revocation, and owner sovereignty? The report treats the supplied directive's premises — maintainer-signed trust, digest-aware acknowledgement, separately visible authority dimensions, five trust tiers, a discover-to-active lifecycle with quarantine and fencing, immediate blocking of new admission after revocation, a zero-effect disabled invariant, and no mandatory central marketplace — as requirements to operationalize, not hypotheses to reopen.

## Key findings

- **Trust evidence and execution authority are orthogonal (M).** The report's central conclusion is that a maintainer signature can authenticate an artifact or metadata under a configured trust policy but cannot establish that the artifact is benign, appropriate, entitled to credentials or network, or authorized to consume quota or money. The proposed contract is that a maintainer signature is an admission/review assertion over an exact artifact identity and is never, by itself, an authority grant.
- **Signature semantics are narrow (SD).** The report reads the Sigstore threat model as saying verification establishes authentication of the signing identity but not that the signer should have signed or that the artifact is good, and reads Debian's `apt-secure` documentation as distinguishing trust in an authenticated archive from trust in each package's behavior. The strongest defensible meaning is "this exact digest was accepted under the installation trust root's maintainer/review policy," contingent on the keys still being trusted and on the review-policy version.
- **Different mechanisms answer different questions (SD/M).** The report maps signatures to approval identity, TUF to freshness/rollback/freeze/wrong-file/mix-and-match protection (with targets treated as opaque), SLSA/in-toto to build provenance, lockfiles to resolved-source and integrity pinning, SBOMs to composition, capability systems to runtime confinement, and explicit local grants to spending and effects. It concludes no mechanism converts a cryptographic statement into a judgment that code deserves money, credentials, an account, arbitrary egress, or broad filesystem access.
- **Three independent axes (M).** The report proposes evidence/provenance, trust tier/isolation, and authority grants as separate axes. A T2 signed plugin with no network grant should have no network authority; a T1 signed built-in should not silently receive a spend budget; tier governs where and how code may execute, not privilege.
- **Unsigned local code keeps full expressiveness (M).** After a digest-specific owner acknowledgement recording unsigned status, source identity or absence, the displayed requested authority vector, and the local policy version, an unsigned plugin can receive the same typed capabilities as signed code if the owner grants them. The report frames this as full expressiveness without warning-only security.
- **Digest identity must cover the executable closure (M).** The report argues a top-level digest is only as strong as the closure it identifies; floating dependencies, unpinned resolvers, native downloads, or runtime-fetched code become new supply-chain events and should route through the same admission/update machinery. It cites lockfile integrity practice and the dependency-confusion disclosure as support.
- **Grant dimensions stay semantically separate (M).** The report lists functional API verbs, OS/workspace scope, network egress, credential access, model launch, route/account, subscription quota, metered spending, update, downgrade, and revocation as independently auditable records. Sharing one installation transaction does not merge the permissions; metered spending must never be inferred from install or trust acknowledgement.
- **A new digest is new code identity (M).** Replacement bytes do not silently inherit admission; an owner update policy may preauthorize a bounded class of transitions, but that policy is itself a separate local grant.
- **Lifecycle is a generation transition (M).** The report supports discovered → verified → admitted → staged → active with stage → drain → fence → activate for reload/update, and requires a generation identity on every effect-bearing packet, lease, subscription and broker handle so stale generation work fails closed.
- **Disabled is a zero-effect property (M).** The report argues the disabled invariant is stronger than "do not call the main entry point": discovery metadata needed to decide disabled must be readable without executing plugin code, because import-time initializers or installers could otherwise act first. It proposes tripwire tests with fake adapters and denied brokers whose pass condition is exactly zero.
- **Remote data is evidence, not authority (M/SD).** Maintainer advisories, transparency observations, registry status and revocation can feed a local policy engine to warn, reject future admission or quarantine, but must not be an unconditional remote kill/update primitive. TUF is cited as showing robust update authenticity without making the distribution system decide every application response.
- **The central-registry alternative fails sovereignty (M).** A mandatory central registry with remote revocation/update authority offers real benefits but conflates remote evidence with local authority; the report's decisive test is that a remote message alone cannot change the local installed digest, active state or grants against preconfigured local policy.

## Recommendation and falsifier

The report freezes an architectural contract and pairs each recommendation with a competing option and a decisive falsifier:

1. Keep evidence, isolation tier and authority as three independent axes; falsified if signed/tier status alone creates an otherwise absent network, credential, account, model, quota or spend permission.
2. Make admission digest-specific and pin or separately admit the executable dependency closure; falsified if the same recorded admission can run materially different executable bytes without another verified transition.
3. Permit unsigned local plugins full API expressiveness under the same explicit grants and required isolation; falsified if unsigned status alone blocks a fully granted legitimate operation, or if acknowledgement alone enables an ungranted effect.
4. Route filesystem, network, secrets, model launch, routing, quota and spending through effect brokers/capability interfaces with native escape paths equivalently enforced; falsified by a single reproducible bypass that reaches an effect directly.
5. Treat update/reload as generation transitions with stage → drain → fence → activate; falsified if any old-generation packet, lease or subscription can cause a new external effect after its fence.
6. Express update, downgrade, support windows and emergency refusal as explicit local owner policies fed by external evidence; falsified if a remote source alone disables, replaces or changes authority without a preconfigured local rule.
7. Keep metered spending a separately explicit grant even when a novice flow co-presents it; falsified if a billable effect can begin with no locally inspectable spend rule.
8. Make disabled a zero-effect property verified by tripwires rather than a callback convention; falsified by any non-zero import/install/process/network/credential/model/quota sentinel in the disabled state.

The report also records a recommended contract to freeze: maintainer approval authenticates a digest under a review identity; unsigned owner approval authenticates a local decision about a digest; neither is an authority grant; every consequential effect remains separately authorized and broker-enforced; updates create new code identity unless local policy delegates a bounded transition; revocation fences new local authority but does not rewrite history about remote effects; trust tier governs isolation; remote maintainers provide evidence, not veto power.

## What this does not prove

- No plugin runtime, language, sandbox, signing root, package format or UX flow is selected; nothing is implemented, installed, signed, published, deployed or spent.
- It does not prove that signed or admitted code is safe; allowed capabilities can still be abused.
- Capability enforcement for native plugins is not settled by the WASI evidence; the report calls cross-runtime enforcement **medium** and says native execution paths need their own containment proof.
- External-effect cancellation is provider-specific; a local fence cannot establish that an already-accepted remote request was canceled, so ambiguous outcomes remain for reconciliation.
- Usability remains an unresolved security parameter; optimal consent batching is explicitly left open.
- Licensing evidence is uneven at the documentation layer: some page licenses were left **unverified** rather than inferred.

## Open Owner decisions

- Which grant dimensions may be confirmed in one user interaction?
- What exact authority, if any, carries from digest D to an approved update D′?
- How is executable dependency closure defined for interpreted/dynamic plugins?
- Which tiers may use native execution rather than component-style isolation?
- What are default support-window and unmaintained-source policies?
- What is the default local reaction to a credible emergency advisory?
- How granular is downgrade authority (per digest, version range, channel, one-time)?
- How are in-flight model/spend operations handled at revocation under each effect-specific PAUSE rule?
- What trust-root/review-policy metadata is signed or recorded with maintainer approval?

## Relevance to later waves

This lane is a constraint source for plugin admission, capability brokering, update/revocation and the disabled-plugin invariant. Later waves should consume the three-axis separation, digest-closure requirement, generation-fencing rule and tripwire suite as tests to be designed and run — not as a chosen runtime, trust root or consent flow. The report's falsifiers (change the bytes, exceed a capability, replay a stale generation, substitute a dependency source, exceed a budget, or issue a remote revocation against local policy) are the candidate acceptance probes for any later implementation.
