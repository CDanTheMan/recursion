---
title: DS-33 — Licensing, distribution, provenance, and IP clearance
status: proposed-inert
last-updated: 2026-09-29
parent-goal: goal-recursion-v2-execution-fabric
invocation: only after Lucas explicitly invokes this file in a new session
---

# DS-33 — Licensing, distribution, provenance, and IP clearance

This is an inert Deep Research handoff. It launches nothing, authorizes no provider call, write, spend or configuration change, and is inert until Lucas explicitly invokes this file in a new session. Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. It is a public/synthetic research lane. The report is research input, not legal advice, and must say so.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Hermes is the executive control plane. Workers are
bounded executors. An implementer's own PASS is never acceptance; independent review is
required, and missing verification is never a pass. `CONTROL_PLANE.md` is the operative
constitution; a research session may propose amendments but must never edit it. No research
session performs implementation, provider/model/authentication/configuration changes,
spending, deployment, publication or merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula,
captures and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs,
pinned source, licenses, peer-reviewed work). Classify every consequential claim as
source-documented, locally observed, inferred or unverified; keep `unknown` distinct from
zero. Model consensus and vendor marketing are not evidence. Every recommendation needs a
competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never
secrets, credentials, personal data, private repository content, local paths, or
account/infrastructure identifiers.

### Lane context

- Recursion v3 is a provider-neutral agent platform that explicitly reuses and adapts external harnesses and pinned libraries, and supports upstream engine adapters and plugin composition. Provider adapters, engine adapters and Recursion plugins have different ownership and billing boundaries.
- Distribution model: one codebase produces versioned release manifests (`core`, `standard`, `remote`, `full`, `custom`). A built-in registry plus filesystem/Git/package sources are each pinned to an immutable digest before activation, with a dependency lockfile, reproducible offline installation and a tested rollback. Installation should not download or start disabled heavy plugins. There is no mandatory central marketplace or remote vendor kill switch.
- Trust tiers are T0-kernel, T1-signed-built-in, T2-signed-isolated-third-party, T3-untrusted-view and T4-external-engine/provider; a tier is an isolation and review requirement, never an authority grant. Signed first-party releases and maintainer-approved plugins are rooted in the installation trust root, while unsigned local plugins remain installable after an explicit warning, exact digest pin and display of all requested authority. Signatures, SBOMs, transparency logs and provenance establish publisher/key role, artifact identity, traceability and freshness only within their threat models; they do not prove benign runtime behavior, fit for a project, quota entitlement or spending authority.
- The release contract this lane must clear is E-FHAR2-108: it requires file-level provenance and license notices, and it explicitly does not treat public visibility as clearance. A clean scan, a valid signature or public reachability is not legal clearance.
- License-obligation surface: upstream harnesses, pinned libraries, assets, binaries, container images, bundled runtimes, generated code, model weights and data can each carry separate terms from code. Attribution, NOTICE, source offer, modification disclosure and license-retention obligations differ by license. Mere interoperability (protocol invocation, a user-installed binary) differs from bundling or forking, and the upstream project's own documentation is the source for that distinction.
- Release-provenance identity: code signing, transparency logs and provenance attestations establish publisher identity, artifact integrity and freshness, but not a legal right to distribute; a valid signature must never be confused with distribution rights. SBOM formats (for example SPDX and CycloneDX) and license-scanning tools have detected and undetected gaps for transitive, vendored, dual-licensed, generated and model/data artifacts.
- Copyright and access constraints: private source is never sent to a public or contributor route without explicit eligible authority, credentials and institutional access remain opaque brokered references, and full papers are stored only when access and license permit (otherwise metadata, allowable excerpts and derived claims). Contributor or discounted model/data routes impose their own terms on outputs, redistribution or commercial use.
- Legal boundary: this lane evaluates legal risk; it does not give legal advice and must say so in its own text. Every legal conclusion is research input and must be labelled as such. Jurisdiction-dependent and terms-of-service questions (export, data residency, reverse-engineering exceptions, provider acceptable use) require qualified counsel rather than a settled answer, and the report must mark where a non-lawyer may no longer conclude.
- Research constraints: this is a public/synthetic lane and receives no private project content, transcripts, credentials or local paths. It performs no bundling, copying or distribution of any artifact and no provider, repository or package-registry calls or license trial run. It selects no license, distribution channel, store or hosted-service model; changes no auth, config, credentials, spending, deployment, publication or merge; and does not reopen accepted Owner decisions or the anchor scope.

## Purpose

Decide what must be cleared, documented and checked before any Recursion component is publicly released, so that reuse of upstream harnesses, libraries, assets and contributor routes does not create an unexamined distribution or attribution obligation. This is blocking because v3 explicitly reuses and adapts external harnesses and pinned libraries, and the accepted release contract (E-FHAR2-108) requires file-level provenance and license notices without claiming public visibility is clearance. The lane must state clearly where qualified legal counsel is required and must never present its own conclusions as legal advice.

## Authority and boundaries

The shared authority constraints are in `## Baked context`. Preserve the current constitution; write proposed reconciliation, never edit it. Public or synthetic briefs only — never private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. Do not reopen accepted Owner decisions or anchor scope, and do not select a license, distribution channel or store as a product decision. This lane evaluates legal risk; it does not give legal advice and must flag every point where counsel is required.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Upstream harness licenses and obligation compatibility

1. For each upstream harness Recursion may reuse, adapt or interoperate with, what license governs the code, and what obligations attach to modification, linking, subprocess invocation and redistribution?
2. Which combinations of permissive, weak-copyleft, strong-copyleft and proprietary terms create an actual or arguable incompatibility for a distributed Recursion build, and what is the source of each claim?
3. Where does mere interoperability (protocol invocation, user-installed binary) differ from bundling or forking, and which distinction is documented by the upstream project itself?
4. Which upstream terms are about authentication, subscription or acceptable use rather than copyright, and how do those interact with distribution and with Recursion's provider-neutral claims?

### Distribution rights, attribution, and NOTICE

5. What precisely does each license require for attribution, NOTICE files, source offer, modification disclosure and license retention in a redistributed build?
6. Where is personal, source-available or self-hosted use legally distinct from public distribution, and what threshold (public release, binary distribution, hosted service) changes the obligation?
7. How should a project-wide NOTICE and per-file provenance header be structured so copied or adapted code remains traceable, as E-FHAR2-108 requires, and what documentation standard makes "this was reused lawfully" auditable without a lawyer re-deriving it from scratch?

### SBOM, scanning, and dependency provenance

8. Which SBOM formats (for example SPDX, CycloneDX) and license-scanning tools are currently maintained, and what do they detect versus miss for transitive and vendored dependencies?
9. How are license conflicts, unknown licenses and dual-licensed dependencies surfaced and resolved before release, and what is the conservative default when a license is unknown?
10. How are pinned dependency digests, build provenance and reproducibility evidence tied to the released artifact, what trust does each provide (and not provide), and what gaps remain after scanning, such as license-text conflicts, generated code, model weights or data with separate terms?

### Assets, binaries, and redistribution

11. What asset classes (fonts, icons, models, datasets, test corpora, captured data) carry separate licenses from code, and which must be cleared independently before redistribution?
12. How are binary redistributions, container images and bundled runtimes governed, where does a build cross from source reuse into binary redistribution, and how are game, media or third-party assets handled when the artifact is provenance evidence rather than shippable content?

### Code signing and release provenance

13. What do code signing, transparency logs and provenance attestations establish about publisher identity, artifact integrity and freshness, and what do they explicitly not establish?
14. How are signing keys, trust roots and revocation handled so a valid signature is never confused with a legal right to distribute?
15. How does release provenance interact with the license and SBOM record so the same artifact identity is auditable?

### Contributor routes, terms of service, and jurisdiction

16. What terms attach to contributor or discounted model/data routes, and what obligations or restrictions do they place on outputs, redistribution or commercial use?
17. Which jurisdictional and terms-of-service boundaries (export, data residency, reverse-engineering exceptions, provider acceptable-use) require jurisdiction-specific counsel rather than a general report?
18. Where does the research itself reach the limit of what a non-lawyer may conclude, and how is that boundary marked?

### Clearance before public release

19. What is the minimum clearance checklist that must be complete before any public release, and which items are hard blockers versus documented risks?
20. What evidence, sign-off and expiry apply to each clearance item so a change in an upstream license or term triggers re-clearance?

## Deliverable

- A source-pinned claim table (claim, source, version/date, classification as fact/inference/hypothesis/proposal, confidence, expiry or falsifier trigger), with every legal conclusion labelled as research input, not legal advice.
- A license-obligation matrix for each reused upstream, with unknown or arguable cells marked unknown or arguable rather than resolved.
- A pre-release clearance checklist separating hard blockers, documented risks and counsel-required items.
- A NOTICE and per-file provenance standard, plus an SBOM and scanning recommendation with detected and undetected gaps named.
- One recommendation tied to a named competing option and a decisive falsifier, plus open Owner questions that require Lucas or counsel.

## Non-goals

- No legal advice, no conclusion of law, and no guarantee of compliance.
- No selection of a license, distribution channel, store or hosted-service model.
- No change to auth, config, credentials, spending, deployment, publication or merge.
- No bundling, copying or distributing any artifact as part of this research.
- No importing private project content, transcripts, credentials or local paths.
- No reopening accepted Owner decisions or anchor scope.
- No treating a clean scan, a valid signature or public visibility as legal clearance.
- No provider, model, repository or package-registry calls, and no license trial run.

## Completion gate

- Every license and obligation claim is pinned to the upstream license text or an authoritative source, with version or retrieval date, or marked unverified.
- The report states in its own text that it is research input and not legal advice.
- Every jurisdiction-dependent or terms-of-service question is flagged as requiring qualified counsel, not answered as settled.
- The clearance checklist separates hard blockers from documented risks and names the evidence for each.
- Unknown and arguable license combinations are marked unknown or arguable, not resolved by inference.
- NOTICE and provenance requirements are stated as concrete documentation deliverables.
- Every recommendation names a competing option and a decisive falsifier.
- No artifact is copied, bundled or distributed and no protected path is edited.
- Open Owner and counsel questions are listed separately from research findings.
