---
title: Recursion v3 R1-R17 reconstructed evidence matrix
status: reverified-evidence-with-explicit-open-tests
last-updated: 2026-09-03
---

# Recursion v3 R1-R17 reconstructed evidence matrix

This is the persistent evidence record for the R1-R17 architecture-proof lanes. It reconstructs
the evidence independently because the earlier campaign retained consolidated conclusions but
not its claimed worker packets. It does not recreate those packets, infer a v3 runtime, or turn
recommendations into Owner decisions. The exact lane questions are copied from
[RESEARCH-AGENDA.md](RESEARCH-AGENDA.md).

Evidence labels are normative for this artifact:

- **reverified** — the Sol lead opened the cited primary source on 2026-09-03 and checked the
  consequential passage; discovery workers independently checked the lane;
- **local inference** — a conclusion drawn from cited public primitives plus the repository's
  stated requirements, not a property proved by the public source;
- **Owner decision** — an authenticated direction recorded in local authority documents;
- **unrecovered prior assertion** — a prior-session statement whose supporting packet or exact
  input/output was not preserved and which is not reused as evidence;
- **unverified hypothesis** — a falsifiable proposition awaiting a local experiment.

Mutable vendor documentation is pinned by retrieval date and must be revalidated on relevant
provider, model, API, CLI, platform or release change. Pinned repository and standards links use
the stated immutable revision. Source identity and provenance support inspection; they do not
prove truth or applicability.

The exact consequential-source versions, source commits, locators, applicability limits and
revalidation triggers are canonical in [SOURCE-REGISTER.md](SOURCE-REGISTER.md). Lane prose below
is a claim projection and must not broaden those source records.

## R1 — headless native harness boundary

**Question:** Which semantics must Recursion implement natively, and which inner-loop features
should remain behind Codex, Claude Code, Cursor, Gemini, OpenCode, Hermes or other engines?

**Evidence and claims:** T3 Code's pinned architecture shows a serialized command worker,
idempotent command receipts, a pure decider and transactional event/projection append. DeepSeek
Harness records typed append-only session events, explicit flush and crash-detectable compaction
markers. Pi exposes model/tool lifecycle hooks, but an adapter hook is not a non-replaceable
authority boundary. These are **reverified** primitives from [T3 Code at
`5b8445b`](https://github.com/pingdotgg/t3code/blob/5b8445b7a777ab1070aa97b062b1618971073a96/docs/internals/overview.md),
[DeepSeek Harness session at `76fda72`](https://github.com/deepseek-ai/deepseek-harness/blob/76fda729799fe9b3848dbe2c211d4b231032b81e/docs/subsystems/session.md),
[its persistence contract](https://github.com/deepseek-ai/deepseek-harness/blob/76fda729799fe9b3848dbe2c211d4b231032b81e/docs/subsystems/persistence.md),
and [Pi agent lifecycle at `4e69b0c`](https://github.com/earendil-works/pi/blob/4e69b0c28060f0f02fbe38bfa7c21a2e2eb25057/packages/agent/README.md).
Exact locators and limitations are `SRC-V3-039`–`SRC-V3-041` in the source register.
The recommendation that Recursion's deterministic kernel own authority, budgets, PAUSE,
fencing, events, effect admission and publication while external loops own sampling and wire
protocol is a **local inference**, not a harness guarantee or Owner ratification.

**Contradiction/limit:** external adapters can duplicate semantics and may fail to expose a
required interrupt or observation. A bounded native loop may outperform them. No matched result
exists. **Decision:** adapt the command/event seam; retain Option 2 as a conditional
recommendation; reject measured-superiority language. **Confidence:** high for the ownership
boundary, medium for the implementation choice. **Falsifier:** a frozen compatibility fixture
loses an authority/evidence invariant, or a preregistered native-loop spike wins a declared
quality, continuity, security or total-resource metric. **Disposition:** LUNA-R1-R4 supported;
TERRA-AUTH conditionally supported the boundary and retained Option 2 as unratified.

## R2 — direct and collaborative ARM conversations

**Question:** How should `#general`, dedicated ARM topics and multi-ARM rooms map onto durable
actors without introducing an AI ARM Manager?

**Evidence and claims:** Kubernetes Lease records expose holder identity, duration, renewal and
transition fields, but the docs do not confer Recursion authority. This is **reverified** from
[Kubernetes Leases, retrieved 2026-09-03](https://kubernetes.io/docs/concepts/architecture/leases/).
Stable logical ARM identity plus a scoped, expiring `CoordinationLease`, event-mediated messages
and Head-controlled conflict settlement is a **local inference**. The Owner's actor boundary is
Lucas → Head Hermes → ARM executive → delegates; no AI ARM Manager exists (**Owner decision**).

**Contradiction/limit:** lease expiry is not an external-resource fence, and transcript arrival
order is not authority. Public multi-bot/shared-account interfaces generally expose weaker
security boundaries than Recursion requires. **Decision:** adapt identity and lease vocabulary;
reject direct peer delegation or shared-login order as authority. **Confidence:** high for the
transport/authority separation, medium for collaboration benefit. **Falsifier:** duplicate,
out-of-order, edited, restarted, revoked, expired and PAUSE fixtures allow anyone except Head or
the current scoped holder to commit a transition. **Disposition:** LUNA-R1-R4 supported;
TERRA-AUTH required the Head/ARM decomposition conflict to remain explicit for Lucas.

## R3 — PAUSE and cancellation semantics

**Question:** Can user-selectable pause policies let bounded operations finish without allowing
a compromised or disconnected actor to create new effects?

**Evidence and claims:** Python task cancellation is cooperative; Windows Job Objects and Linux
cgroup v2 offer bounded process containment with documented breakaway, migration, privilege or
platform limits. These are **reverified** from [Python 3.14 task
documentation](https://docs.python.org/3.14/library/asyncio-task.html), [Windows Job Objects source
revision `3aee48a`](https://github.com/MicrosoftDocs/win32/blob/3aee48ac3f48e187d17bdfd56951741737331749/desktop-src/ProcThread/job-objects.md) and [Linux cgroup v2
source revision `c3b510d`](https://github.com/torvalds/linux/blob/c3b510de420d70def08190083d388e0873c1aa84/Documentation/admin-guide/cgroup-v2.rst).
Exact headings and limitations are `SRC-V3-020`, `SRC-V3-022` and `SRC-V3-023`. Admission epochs, typed effect
states and reconciliation are **local inferences**. The operative constitution's immediate
PAUSE wins; checkpoint, interrupt, drain and emergency profiles are representable future
proposals only (**Owner/constitutional authority**, [CONTROL_PLANE.md](../../CONTROL_PLANE.md)).

**Contradiction/limit:** cancellation or killing a process cannot roll back a possibly accepted
external effect. The prior claim that checkpoint was already the operative default conflicts
with current authority and is rejected. **Decision:** adopt epoch rechecks, quarantine and
reconciliation; retain future policies as non-operative data. **Confidence:** high.
**Falsifier:** fault injection around admission/dispatch/response loss admits post-epoch work,
retries an ambiguous effect, or represents ambiguity as success. **Disposition:** LUNA-R1-R4
and TERRA-AUTH supported only with current-immediate PAUSE explicit and future modes non-operative.

## R4 — calibrated Full Access

**Question:** How can Full Access be genuinely expansive without becoming silent
self-escalation or unauditable ambient authority?

**Evidence and claims:** OAuth 2.0 scopes and Linux per-thread capabilities demonstrate bounded
privilege vocabularies; AWS permission boundaries define a maximum but document exceptions and
policy interactions. These are **reverified** from [RFC 6749 §3.3](https://www.rfc-editor.org/rfc/rfc6749#section-3.3),
[capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html) and [AWS IAM
permission boundaries](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html).
A Recursion capability vector, attenuation, expiry, revocation, step-up and before/after mutation
receipt are **local inferences**. Current authority forbids autonomous self-administration;
future `grant-admin`, trust-root and audit-retention powers require distinct Owner authority.

**Contradiction/limit:** these platforms do not define Recursion's grants; a maximum policy can
still interact unsafely with other policy types. **Decision:** adapt the decomposition; reject
an ambient Full Access boolean and silent self-grant. **Confidence:** high structurally, medium
for future UX/policy. **Falsifier:** a child widens authority, a stale/replayed mutation succeeds,
or grant administration can alter constitution/trust/audit history without an explicit separate
grant. **Disposition:** LUNA-R1-R4 and TERRA-AUTH supported the separation; the exact Owner
authorization and audit-administration boundary remain unresolved.

## R5 — risk-scaled independent verification

**Question:** Which independence dimensions materially improve defect detection for each risk
class?

**Evidence and claims:** NASA distinguishes technical, managerial and financial independence and
requires assurance proportionate to risk/resources; SLSA defines immutable revision/provenance
and two-party review properties. These are **reverified** from [NASA-STD-8739.8B, revision B,
2022-09-08, §§4.4.1–4.4.6](https://standards.nasa.gov/sites/default/files/standards/NASA/B/0/NASA-STD-87398RevB.pdf)
and [SLSA Source v1.2](https://slsa.dev/spec/v1.2/source-requirements). Mapping independence to
model, family, provider, account, host, session and evidence channel is a **local inference**.

**Contradiction/limit:** SLSA lineage is not semantic correctness; organizational independence
does not establish model-family defect diversity. Sol, Luna and Terra are one GPT-5.6 family.
**Decision:** adapt a risk-scaled explicit vector and downgrade receipt; reject same-family
agreement as cross-family independence. **Confidence:** high for evidence/repeatability, medium
for tier thresholds. **Falsifier:** a blind matched defect matrix shows no material benefit from
the proposed separation or produces review debt above the hard floor. **Disposition:**
LUNA-R5-R8 supported; final Terra review pending.

## R6 — plugin signing and unsigned local power

**Question:** What does maintainer approval prove, and how can unsigned local plugins retain full
feature expressiveness without warning-only supply-chain failure?

**Evidence and claims:** TUF 1.0.36 supplies expiring signed roles, thresholds, delegation and
rollback/freeze protections while treating target content as opaque. SLSA 1.2 provenance and
verification bind artifact/process identities within a stated threat model. These are
**reverified** from [TUF 1.0.36, source revision
`59e601e`](https://github.com/theupdateframework/specification/blob/59e601ed29c0d2e497264ae8b31c11b8ef07df1e/tuf-spec.md)
and [SLSA v1.2 artifact verification, source revision
`ae7fc76`](https://github.com/slsa-framework/slsa/blob/ae7fc76215004e8fae250c877eff8919bf048e3b/spec/verifying-artifacts.md).
Exact headings, licenses and limitations are `SRC-V3-004` and `SRC-V3-005`. Both specifications use the
Community Specification License 1.0 at these revisions.
Separating artifact trust, functional API, OS/network, route/account, quota, metered spend,
update and revocation grants is a **local inference**.

**Contradiction/limit:** a valid signature does not prove benign behavior, applicability or
spending authority. **Decision:** adopt pins/provenance/revocation metadata; adapt independent
effect grants; reject signature-as-safety. **Confidence:** high. **Falsifier:** a validly signed
adversarial fixture gains an unrelated effect or an unsigned acknowledged fixture silently gains
route/spend/update authority. **Disposition:** LUNA-R5-R8 supported; final Terra review pending.

## R7 — single-writer migration and effect rollback

**Question:** What exact checkpoint is sufficient to fence a legacy writer and transfer one
aggregate to v3?

**Evidence and claims:** SQLite provides serializable isolation by serializing writes: only one
writer can exist for a database at a time; WAL allows concurrent readers and one writer with
snapshot isolation. This is **reverified** from [SQLite Isolation, revision
2022-04-18](https://www.sqlite.org/isolation.html), not inferred only from the WAL overview.
[SQLite Transactions, revision 2026-02-18](https://www.sqlite.org/lang_transaction.html)
documents busy/error behavior. An application writer identity, monotonic epoch, external fence,
complete writer inventory and ambiguous-effect state are separate **local inferences**.

**Contradiction/limit:** SQLite cannot fence file, Git, other-store or remote writers and cannot
undo accepted external effects. Projection parity alone does not prove crash recovery or
authority. **Decision:** adopt SQLite only as a bounded persistence/concurrency primitive; reject
the broad OR-015 rehearsal until all writers share a tested fence. **Confidence:** high.
**Falsifier:** any enumerated stale writer succeeds, replay digests diverge, or recovery repeats a
possibly accepted effect under crash/disk-full/torn-tail tests. **Disposition:** LUNA-R5-R8
supported; final Terra review pending.

## R8 — adaptive branch and review-backlog capacity

**Question:** Which measured signals should bound new branches, worktrees and concurrent ARM
output?

**Evidence and claims:** Git 2.54.0 documents stable porcelain worktree inventory, lock, prune and
remove mechanics; Kubernetes HPA documents stabilization windows and distinct up/down behavior.
These are **reverified** from [Git worktree 2.54.0](https://git-scm.com/docs/git-worktree/2.54.0)
and [Kubernetes HPA, retrieved 2026-09-03](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/).
Using host pressure, conflict/staleness, unreviewed volume and measured Owner review service rate
with hysteresis is a **local inference**.

**Contradiction/limit:** HPA is an analogy, not branch-capacity evidence. Cheap branch creation
does not imply review capacity; the historical ceiling of 75 is not a validated v3 constant.
**Decision:** adapt measured admission; reject universal numeric capacity. **Confidence:** high
for signal separation, low-medium for thresholds. **Falsifier:** trace replay shows more review
debt/oscillation or no improvement over a conservative fixed policy. **Disposition:**
LUNA-R5-R8 supported; final Terra review pending.

## R9 — privacy-preserving retention and deletion

**Question:** How should raw private artifacts expire while durable lineage remains auditable?

**Evidence and claims:** NIST SP 800-88 Rev.2 covers logical/cloud media and limits cryptographic
erase when keys/copies are not all controllable. Versioned object storage can retain prior
versions after ordinary deletion. These are **reverified** from [NIST SP 800-88 Rev.2,
September 2025](https://doi.org/10.6028/NIST.SP.800-88r2) and [AWS S3 version deletion,
retrieved 2026-09-03](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeletingObjectVersions.html).
Scoped keys, complete copy inventory, verified/expiry-bound/legal-hold states and a minimal
non-sensitive tombstone implement the recorded **Owner direction**, but mechanics are unproved.

**Contradiction/limit:** local blob/key deletion cannot prove provider backup, replica or cache
deletion. Cryptographic erasure is not universal completion evidence. **Decision:** adapt the
direction with per-copy proof states; reject provider-wide completion inference. **Confidence:**
high for limits, medium for mechanics. **Falsifier:** a synthetic replica/version/backup/spool or
escrow-key copy remains recoverable while the record says `verified-complete`. **Disposition:**
LUNA-R9-R12 supported; final Terra review pending.

## R10 — private canary methodology

**Question:** What can `CANARY-01` prove without leaking its identity or allowing a successful
run to substitute for fault coverage?

**Evidence and claims:** Google's SRE canary guidance requires control/canary attribution,
representative load and staged analysis; NIST SP 800-115 requires authorized scope, rules of
engagement, data handling and stop/incident conditions. These are **reverified** from [Google
SRE Workbook, Canarying Releases](https://sre.google/workbook/canarying-releases/) and [NIST SP
800-115, September 2008, §§3.1–3.2](https://doi.org/10.6028/NIST.SP.800-115).
The local test-only fixture/baseline/failure-injection/clean-rerun protocol is a **local
inference** and Owner-bounded candidate, not an executed canary.

**Contradiction/limit:** artificial load and one successful run do not prove production behavior,
deployment safety or broad semantics. **Decision:** adapt the method; reject canary-as-runtime
proof. **Confidence:** high for method limits, low for outcomes because the canary was not run.
**Falsifier:** disclosure, scope, baseline, fault-injection or exact-candidate rerun gates fail.
**Disposition:** LUNA-R9-R12 supported; final Terra review pending.

## R11 — interactive terminal runtime and communication visualization

**Question:** Which persistent process, client protocol and terminal rendering architecture can
support several detachable Head/ARM/worker views with clean termination and negligible passive
overhead?

**Evidence and claims:** ConPTY supplies UTF-8/VT pseudoconsole transport; POSIX.1-2024 defines
terminal foreground process groups and group signals; SSH connection channels define windows,
PTY requests, resize, signals and exit status. Windows Job Objects and Linux cgroup v2 provide
qualified containment. These are **reverified** from [Microsoft Pseudoconsoles, source revision
`c303556`](https://github.com/MicrosoftDocs/Console-Docs/blob/c3035561c145c6c6c6b0d7a4f49a6d706256451e/docs/pseudoconsoles.md), [POSIX.1-2024
terminal interface](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap11.html),
[RFC 4254](https://www.rfc-editor.org/rfc/rfc4254.html), [Windows Job Objects, source revision
`3aee48a`](https://github.com/MicrosoftDocs/win32/blob/3aee48ac3f48e187d17bdfd56951741737331749/desktop-src/ProcThread/job-objects.md) and [Linux
cgroup v2, source revision `c3b510d`](https://github.com/torvalds/linux/blob/c3b510de420d70def08190083d388e0873c1aa84/Documentation/admin-guide/cgroup-v2.rst).
Exact locator/limit records are `SRC-V3-021`–`SRC-V3-025`.

**Contradiction/limit:** none defines Recursion actor identity, durable cursor replay, one input
lease, passive-view behavior or universal descendant containment. **Decision:** adapt native
primitives behind a broker; reject terminal-close-kills-work and universal-containment claims.
**Confidence:** high for protocol shape, low for untested compatibility/performance.
**Falsifier:** the Windows/Linux attach/crash/restart/orphan/high-output matrix loses/duplicates
events, violates input leases, blocks canonical state or leaves unaccounted descendants.
**Disposition:** LUNA-R9-R12 supported; final Terra review pending.

## R12 — whole-system performance and lean codebase

**Question:** Can v3 materially improve capability while keeping the privileged core and idle
installation small enough to understand, audit and run on the target coordinator?

**Evidence and claims:** SQLite's WAL documentation confirms one writer, checkpoint starvation
from long readers and version-sensitive recovery behavior. This is **reverified** from [SQLite
WAL, revision 2026-08-25](https://www.sqlite.org/wal.html). The small privileged kernel and
disabled-plugin zero-execution floor are **unverified hypotheses**; no v3 measurement exists.

**Contradiction/limit:** WAL does not prove lower latency or readiness. The WAL-reset bug history
makes an exact SQLite build part of any result. **Decision:** preregister matched baselines and
full denominators; reject `optimized`, `lightweight` or `better than v2`. **Confidence:** high
that no result exists, low for any expected improvement. **Falsifier:** measured startup,
idle/resource, replay/recovery, dependency, privileged-code and review/maintenance vectors miss a
floor or show no benefit. **Disposition:** LUNA-R9-R12 supported; final Terra review pending.

## R13 — model performance, routing and delegation science

**Question:** Which models, harnesses, delegation shapes and verifier combinations maximize
accepted outcomes per quota/cost/resource/review unit for each task class?

**Evidence and claims:** RouteLLM evaluates preference-trained strong/weak routing and FrugalGPT
evaluates budget-constrained cascades on public tasks. These are **reverified** from [RouteLLM
arXiv v4, 2025-02-23](https://arxiv.org/abs/2406.18665v4) and [FrugalGPT arXiv v1,
2023-05-09](https://arxiv.org/abs/2305.05176v1). Task-specific routing and bounded delegation are
therefore plausible **unverified hypotheses**, not Recursion results.

**Contradiction/limit:** the studies' tasks, cost surfaces and call patterns do not establish
software/research performance or subscription accounting. This campaign lacks a frozen corpus,
Sol-only control, blind outcome set and complete quota/review denominator. **Decision:** adapt
their experiment structures; reject universal rankings and campaign-efficiency claims.
**Confidence:** high for the limitation, low for local benefit. **Falsifier:** a preregistered
matched evaluation misses quality/source floors or yields no accepted nonduplicate improvement
per complete observed vector. **Disposition:** LUNA-R13-R17 supported; final Terra review pending.

## R14 — context, compaction and cache manipulation

**Question:** Which lawful, documented cache/session/context controls reduce repeated work
without hidden coupling, privacy leakage or fidelity loss?

**Evidence and claims:** OpenAI's API exposes model-dependent automatic prefix caching,
`prompt_cache_key`, retention controls and `cached_tokens`; Anthropic exposes automatic/explicit
breakpoints, five-minute/one-hour TTL choices and read/write counters; Gemini distinguishes
implicit from explicit cached content and reports cached-token metadata. These are **reverified**
from [OpenAI API prompt caching, retrieved 2026-09-03](https://developers.openai.com/api/docs/guides/prompt-caching),
[Anthropic API prompt caching, retrieved 2026-09-03](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
and [Gemini API context caching, updated 2026-09-02](https://ai.google.dev/gemini-api/docs/caching).

**Contradiction/limit:** controls, locality, TTL, retention and counters are not uniform or
portable. API documentation does not prove Codex OAuth CLI behavior, subscription debit or
cross-provider reuse. **Decision:** adapt exact expiring `RouteCapabilityDescriptor` fields and
provider-neutral content-addressed evidence; reject inferred hits/savings/portability.
**Confidence:** high. **Falsifier:** direct route counters and fidelity/privacy fixtures disagree
with a descriptor or a semantic capsule fails invalidation, isolation or cold recovery.
**Disposition:** LUNA-R13-R17 supported; final Terra review pending.

## R15 — configuration architecture and operator control

**Question:** Can one schema make deep customization predictable across files, interactive CLI,
Telegram, editions, goals, tasks, plugins, routes, nodes, PAUSE, Full Access and terminal layouts?

**Evidence and claims:** JSON Schema 2020-12 supplies structural validation vocabulary and RFC
8785 supplies deterministic JSON canonicalization for hashing/signing. These are **reverified**
from [JSON Schema Core 2020-12](https://json-schema.org/draft/2020-12/json-schema-core) and [RFC
8785, June 2020](https://www.rfc-editor.org/rfc/rfc8785.html). Provenance, explicit narrowing,
authorized widening, compare-and-swap digest/version and transactional receipts are **local
inferences**.

**Contradiction/limit:** schema and canonical bytes do not define semantic authority, merge
precedence, amendment or permission safety; RFC 8785 is informational. **Decision:** adopt them
as bounded components; reject single-schema-determinism claims. **Confidence:** high.
**Falsifier:** duplicate/unknown fields, stale concurrent edits, path normalization or scope
fixtures yield nondeterminism, last-write-wins or unauthorized widening. **Disposition:**
LUNA-R13-R17 supported; final Terra review pending.

## R16 — scientific research ARM and scholarly evidence

**Question:** Can Recursion find papers and standards, reconcile conflicting evidence, design
experiments and produce reproducible architecture claims within privacy, copyright and budget
limits?

**Evidence and claims:** W3C PROV-DM defines entity/activity/agent provenance; Crossref/Crossmark,
DataCite 4.5 and arXiv expose different identifiers, metadata, relations and update signals.
These are **reverified** from [W3C PROV-DM Recommendation 2013-04-30](https://www.w3.org/TR/2013/REC-prov-dm-20130430/),
[Crossref REST](https://www.crossref.org/documentation/retrieve-metadata/rest-api/),
[Crossmark](https://www.crossref.org/documentation/crossmark/), [DataCite Metadata Schema 4.5,
2024-01-22](https://schema.datacite.org/meta/kernel-4.5/) and [arXiv API
manual](https://info.arxiv.org/help/api/user-manual.html). Generic `SourceRecord`, claim and
typed evidence-edge semantics are **local inferences**.
Exact version/locator/expiry records are `SRC-V3-006` and `SRC-V3-030`–`SRC-V3-033`.

**Contradiction/limit:** provenance, metadata, registration, citation count or consensus does not
prove scientific truth. Crossref says Crossmark presence is not a guarantee of complete updates;
aggregated text is untrusted input. **Decision:** adopt generic records and explicit lifecycle,
contradiction/applicability/revalidation; keep adapters optional; reject metadata-as-veracity.
**Confidence:** high for record shape, low for comparative benefit. **Falsifier:** adversarial
false-ID, stale/retracted, near-match, paywall, hostile-text, duplicate-version or license
fixtures admit a bad current source. **Disposition:** LUNA-R13-R17 supported; final Terra review
pending.

## R17 — comparative architecture benefit and complexity budget

**Question:** Does v3's additional machinery outperform v2 and simpler alternatives enough to
justify its code, operational and cognitive cost?

**Evidence and claims:** The verified R1-R16 sources establish useful primitives and important
limits, not a comparative Recursion result. Option 2's recommendation is a **local inference**;
whole-system benefit, performance, maintenance cost and owner-review benefit remain
**unverified hypotheses**. Current v2 tests can prove v2 regression behavior only.

**Contradiction/limit:** Option 1 may have a cheaper transition; a bounded native loop may win;
adapter duplication and privileged-code cost are unmeasured. **Decision:** admit only the lean
M1A planning/replay contract; defer provider, process, plugin, database and scientific adapters;
reject any v3-superiority claim. **Confidence:** high for the narrowed scope, low for comparative
benefit. **Falsifier:** matched v2/Option 1/Option 2/native scenarios and ablations show no
user-visible/safety/measured-efficiency benefit or miss a hard floor. **Disposition:**
LUNA-R13-R17 supported; lean adversary and final Terra review pending.

## Reconstructed packet and route disposition

| Packet | Route | Lanes | Outcome |
|---|---|---|---|
| WP-V3DF-101 | `gpt-5.6-luna`, `xhigh` | R1-R4 | supported with PAUSE, cancellation, ARM-layer and performance-language corrections |
| WP-V3DF-102 | `gpt-5.6-luna`, `xhigh` | R5-R8 | supported with verifier-vector, SQLite/fence and adaptive-capacity limitations |
| WP-V3DF-103 | `gpt-5.6-luna`, `xhigh` | R9-R12 | supported; no deletion, canary, process, performance or runtime result claimed |
| WP-V3DF-104 | `gpt-5.6-luna`, `xhigh` | R13-R17 | supported; cache/API, scholarly-truth and comparative-benefit inferences narrowed |

No Contributor or other external-family route received a packet in this reconstruction. The
lead could not establish from an already approved route record both current non-metered status
and an exact privacy/model mapping without changing or inspecting forbidden account/provider
configuration. No route was enabled, no billing was accepted, and privacy was not weakened.
Consequently there is no campaign Contributor packet or verdict to preserve. The earlier
`XFR-001` assertion about a Muse packet lacks a preserved exact input/output and is classified
as an **unrecovered prior assertion**, not reused evidence.

## Source expiry and revalidation triggers

- Immutable repository revisions, dated W3C Recommendations, RFCs, published standards and
  versioned TUF/SLSA/DataCite pages remain pinned; recheck only on adoption of a successor or a
  disclosed correction/withdrawal.
- SQLite pages are revalidated when the deployed SQLite build, journaling/sync/checkpoint
  policy, filesystem or upstream page revision changes.
- Provider cache/model/CLI pages are revalidated before an experiment and whenever provider,
  route, account type, endpoint, model, SDK/CLI or retention/billing policy changes.
- Kubernetes, Git, Python, Microsoft, Linux, AWS and scholarly API pages are revalidated before
  implementation on a new supported release or when the linked mutable page changes.
- A correction, retraction, license/access change or resolver disagreement immediately makes a
  scholarly source stale until reverified.
