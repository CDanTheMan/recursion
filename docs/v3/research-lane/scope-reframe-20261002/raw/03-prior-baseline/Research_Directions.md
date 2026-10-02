# Recursion research directions after FU01 to FU05

Research recommendations for Lucas

2 October 2026 · Proposed local experiments · No experiment results claimed

Repository basis: NotSkittlz/recursion at 3a542c6bbd88351e6f6c5eceffd317bc2450fcad

## 1 Executive decision map

The highest-value next research is to test whether Recursion can preserve a correct, currently authorized continuation across context loss and harness boundaries, and whether its evaluator can detect when it fails. Begin with three inert experiments: account for every task and attempt, recover an actionable control state, and translate upstream events into only the facts they establish. These make later runtime, context, and route comparisons interpretable without choosing a product default prematurely.

The existing contracts, fixtures, finite models, and completed FU01–05 reports are the foundation. The integrated runtime remains unimplemented in the audited snapshot. This proposal adds discriminating experiments at their boundaries; it does not restart the research program, replace existing local work, or declare a gap closed because a design is written.

**Recommended first sequence.** Complete the audit's LP-0 authority and evidence reconciliation. Admit R01 first, then R02 and R03 as review capacity permits. Apply the independent-oracle challenge from R04 before accepting their results. The full R04 comparative campaign and the other ten experiments are a dependency-ordered backlog, not a request to open fourteen sessions at once.

### Decisions the research should change

| Decision | Recommendation now | Evidence that would change it |
|---|---|---|
| What to test first | R01 recorder integrity, R02 actionable restore, R03 semantic translation | Equivalent current, independently accepted evidence already covers the exact seam and candidate |
| What must survive context loss | Exact control projection plus scoped, addressable evidence and explicit gaps | A simpler representation preserves all required actions, holds, provenance, and recovery outcomes at lower total cost |
| Which context mechanism deserves the baseline | Reversible observation masking with exact hydration handles | Dense or long-range workloads show materially worse continuation or total work than qualified folding/selective access |
| How to integrate upstream harnesses | One expressive contract supporting per-effect mediation and bounded session delegation | One approach demonstrates required coverage, hard floors, and a decisive practical advantage across the admitted profiles |
| How to evaluate gains | Qualified demand/attempt census, independently challenged oracle, whole-workflow outcomes | A simpler recorder or verifier proves equivalent reconstruction and defect detection within the same scope |
| When to study adaptive routing | After fixed policies and route economics are interpretable | Current fixed policies already have accepted fresh-task evidence, complete feedback, and an identified decision that adaptation could improve |

A favorable average cannot compensate for lost authority, hidden model connections, fabricated evidence, or an unresolved effect retried blindly. Within the hard floors, preserve the accepted objective order: responsiveness, subscription efficiency, then completion. No single token-efficiency score should replace that order. [Product release scope](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/PRODUCT.md#L71-L93), [performance objective](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/PERFORMANCE-PLAN.md#L155-L184)

### How to use this report

Sections 1–5 explain the decisions, architecture alternatives, and order of work. Section 6 contains three bounded handoff packets. Section 7 retains the complete experiment protocols: hypotheses, baselines, workload units, ablations, controls, observables, uncertainty, stop conditions, and Owner inputs. Section 8 explains how to use results. The appendices preserve the memo-ID crosswalk and evidence boundaries.

The recommendation is for local sessions. Proposed paths are additive experiment destinations, not permission to modify protected governance, decisions, frozen M1 contracts, or historical evidence. Live routes, models, accounts, credentials, host faults, and production changes require their own admitted scope.

## 2 Preserve the existing foundation

### What the repository establishes

The audited tree has three product-side pure planning modules. M1A implements strict decoding, contract validation, admission, reduction, and replay against supplied fixture authority and an in-memory receipt journal. M1B and M1C add substantial schemas, literal fixtures, and test-only oracles. Their route, process, effect, evidence, and retention facts are supplied premises; the oracles do not enforce them on real runtimes. The tree's 71 fixture bundles and 17 test programs are useful inventory denominators, not a claim of 71 or 17 newly passing tests. [Pure planning boundary](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/planning/static.test.py#L11-L21), [admission API](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/v3/planning/replay/kernel.py#L517-L599), [execution oracle](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/execution/reference_oracle.py#L1-L21), [integrity oracle](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/integrity/reference_oracle.py#L1-L7)

Preserve the literal contracts as predecessor evidence. The next tests should bind a proposed new behavior to the existing record or invariant, identify the exact additional premise, and ask the enforcing component for evidence. For example, the current disabled-plugin oracle produces zero activity counters; an eventual plugin runtime must establish that no import, process, network, or filesystem activity actually occurred. A modeled zero is not an instrumented zero. [Disabled-path oracle](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/execution/reference_oracle.py#L385-L390)

The planning records already distinguish accepted Owner intent, goal constraints, route/privacy/budget bounds, work-packet bindings, and checkpoints with ambiguous effects. M1C already has ResearchClaim, EvidenceEdge, GateEvidence, and EffectIntent shapes. The new research can import these references rather than creating a competing writable plan or an untyped summary-based authority system. [Planning schema](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/schemas/control-plane/v3/planning/schema.json#L2975-L3071), [integrity evidence records](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/schemas/control-plane/v3/integrity/schema.json#L1003-L1064)

### Constraints that stay closed

Native-only, independently useful upstream-only, and combined execution are all release requirements. Upstream-only includes planning, review, compaction, retrieval planning, recovery, and other reasoning roles. A deterministic validator or context governor is compatible with that mode; an undeclared native model call is not. The seven launch-critical integration names remain Grok, Cursor, Gemini, Claude, Hermes, OpenCode, and ChatGPT, alongside the broader route inventory. A difficult qualification cell remains an obligation or explicit Owner decision, not a reason to silently remove a route. [Accepted scope](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/DECISION-REGISTER.md#L85-L89), [route inventory](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/foundation-research/mark2-research/compatibility.json)

The Hermes-led repository executive is retired. Optional Hermes Agent integration is a different product concern. Follow the current governance and D-017 rather than stale operative-Hermes or v2 migration instructions in lower-priority documents. Preserve useful historical evidence with its supersession, and preserve future v3 upgrade/rollback obligations. [Current governance](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/CONTROL_PLANE.md#L3-L26), [D-017](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/state/DECISIONS.md#L11-L33)

Do not merge canonical-byte epochs. M1A rejects floats and lexical negative zero and uses its own canonicalization; M1B and M1C have separately frozen profiles. FU01's prospective JCS work and FU03's restricted CBOR/RCV1 test interchange are candidates with different purposes. An imported reference must name its schema, format/profile, original bytes, and original digest. RCV1 is not an adopted production wire format. [M1A](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/M1A-WIRE-PROFILE.md#L16-L54), [M1B](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/M1B-WIRE-PROFILE.md#L9-L20), [M1C](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/M1C-WIRE-PROFILE.md#L9-L20)

### Where FU01 to FU05 fit

| Existing packet | Evidence this program consumes | Boundary still open |
|---|---|---|
| FU01 runtime comparison | Equivalent byte/refusal contract and whole-process comparison design | Actual candidate implementations, hard-floor passes, and matched resource measurements |
| FU02 canonical writer | Candidate-neutral append/replay/effect and coherent restore obligations | Physical writer durability, fault outcomes, and artifact closure |
| FU03 model and conformance | Candidate finite model, mutants, vectors, refusal and trace mapping | Actual exploration, independent oracles, frozen-M1 bridge, and implementation correspondence |
| FU04 platform semantics | Exact OS/filesystem/process/terminal qualification profiles | Actual qualified target cells; process crash is not power loss |
| FU05 broker protocol | Candidate lifecycle, receipts, framing, cursor and ownership rules | HOLD items including SM-01 snapshot materialization and native chaos evidence |

These reports are completed research inputs. They do not establish that a target platform, protocol, store, language, or integrated seam has passed. Existing local sessions own their outcomes; this backlog consumes exact accepted evidence when available and keeps missing prerequisites visible.

## 3 Competing architecture directions

### Recoverable context with evidence outside the prompt

The most useful common representation is a deterministic control projection with an independently addressable evidence set. It should preserve the exact accepted intent and current authority/configuration bindings, plus pending questions, approvals, blockers, unsettled effects, required gates, candidate/source identity, and the next permitted action or hold. Evidence atoms preserve observed bytes, source/version, applicability, provenance, and retention/access status. Summaries, indexes, and renderings are derived views with named inputs and outputs.

This is a proposal for a recovery contract, not a demand to retain hidden reasoning or every byte forever. Reversibility ends when retention or access requires deletion. A missing required artifact produces an evidence gap and a hold. A fresh query against changed external state cannot impersonate a retained historical observation. Authentic provenance also does not prove a source is true; contradictory and unreliable claims remain qualified.

The mechanism comparison should keep this exact control layer constant:

| Mechanism | Strongest use case | Decisive risk or losing case |
|---|---|---|
| Reversible masking with a recent tail | Repetitive observation-heavy work with exact cheap hydration | Repeated hydration reconstructs nearly all context, or an old critical fact lacks a useful locator |
| Structured summary and phase folding | Long-range relationships and meaningful phase boundaries | Lost exceptions, accumulated summary drift, training mismatch, creation cost never amortized |
| Bounded selective access without sub-model calls | Large corpora with sparse identifiable evidence or structured aggregation | Dense queries, repeated overlapping reads, tool latency, weak locator/query ability |
| Learned or recursive policies | A qualified task/model stratum where simpler policies lose | Extra inference, tail variance, hidden roles, training dependence, opaque authority |
| Upstream-owned compaction | A route's supported native continuation behavior | Opaque or post-hoc rewriting cannot establish prior validation of exact control preservation |

The Complexity Trap provides a strong reason to include deterministic masking: it was often competitive and cheaper in the tested SWE-agent configurations. Its results also include a configuration where both masking and summarization lowered solve rate. AgentFold motivates multi-scale folding, but its trained model-policy combination is not evidence that an arbitrary prompt-only wrapper obtains the same benefit. RLMs motivate separating selective external access from recursive inference and report task/model-dependent costs and weaknesses. None measures Recursion's recovery or authority correctness. [Complexity Trap v3](https://arxiv.org/html/2508.21433v3), [AgentFold v1](https://arxiv.org/html/2510.24699v1), [RLMs v1](https://arxiv.org/html/2512.24601v1)

Reuse should resemble dependency-checked compilation. Validate direct inputs, transform/profile identity, actual intermediate output identity, and scope before skipping recomputation. A model-generated intermediate can change even when its root source bytes do not. Build-system dependency traces and Salsa's actual-output equality are useful models for this experiment; they do not prove stochastic transforms deterministic. Reuse immutable evidence bytes while renewing the admission envelope. [Build Systems à la Carte](https://www.microsoft.com/en-us/research/wp-content/uploads/2018/03/build-systems.pdf), [Salsa algorithm](https://salsa-rs.github.io/salsa/reference/algorithm.html)

Provider caches are a separate layer. Prompt-prefix reuse, provider request state, content omitted from a request, retained local evidence, and reuse of a derived context are different observations. None grants authority or establishes factual freshness. API token price is not a subscription debit meter. A session-fresh trial may still be provider-cache-warm; label cache state documented disabled, observed, or unknown. [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)

### Mediate effects or delegate a bounded session

Both approaches below can preserve native-only, upstream-only, and combined workflows. The key choice is the enforcement boundary required by a particular task, rather than a universal preference for one adapter shape.

**Per-effect mediation.** The native or upstream harness owns its reasoning. Recursion translates selected tool or resource requests into exact operation proposals, admits them under current authority, and performs them through an enforcing broker/resource adapter. This can give precise target approval, stable operation identity, and strong fencing at resources it controls. It is credible only if every relevant effect passes that boundary or is constrained by a separately enforced envelope. A callback present in an SDK does not prove complete mediation of built-ins, startup actions, descendants, connectors, or nested agents. ACP terminal operations and Codex dynamic tools illustrate possible surfaces; they do not prove exclusivity. [ACP terminals](https://agentclientprotocol.com/protocol/v1/terminals), [Codex App Server](https://learn.chatgpt.com/docs/app-server)

**Bounded session delegation.** Recursion admits a finite work interval with an enforced workspace, tool/effect classes, route, privacy boundary, resources, descendants, and return contract. The upstream retains its supported inner tools and scheduling. Recursion verifies artifacts and reconciles observations before admitting subsequent work. This can preserve richer upstream behavior without per-tool callbacks, especially for local artifact production. The envelope must actually be enforced. A prompt, tool allow rule, PID, timer, or SDK label alone is not containment. Coarser Stop boundaries, opaque internal usage, and external work that survives the session are explicit costs and uncertainties.

| Question | Per-effect mediation | Bounded session delegation |
|---|---|---|
| Authority unit | Resource operation plus explicitly granted local envelope | Work interval and declared descendants |
| Strongest advantage | Exact admission and reconciliation at controlled resources | Faithful use of rich native harness behavior |
| Main integration burden | Complete effect coverage and loss-aware translation | Proving the envelope and accounting for residual uncertainty |
| Recovery object | Operation records plus recoverable context | Artifacts/checkpoints plus resumed or new admitted session |
| Evidence that favors the other | Partial mediation is unavoidable or translation destroys required functionality | Required target/effect control cannot be enforced at session granularity |

Use one descriptive contract that can express either approach. That is not a recommendation to implement both everywhere. First test that it faithfully represents supported, unsupported, and unknown cells. Then choose route-specific realizations from required coverage and measured tradeoffs. Keep rich namespaced extensions when qualified instead of flattening every route to the smallest common protocol.

### Compose meanings rather than feature names

The contract needs separate identities for protocol, adapter, configuration, semantic interpreter, and platform profile. It should distinguish advertised capability, documentary support, actual observations, qualification, enforcement component, lifecycle, owners, helper dependencies, units, and losses. These are compiler inputs and evidence, not grants.

Concrete public examples show why this matters. ACP capability absence and field-specific empty objects have defined meanings; Claude SDK allowed_tools is an approval mechanism rather than a closed inventory, and permission evaluation can bypass a later callback. MCP's dated protocol carries per-request metadata/capabilities, while self-reported implementation identity is not authentication. A2A's Send Message idempotency is optional. WIT's types and resource ownership do not establish behavioral equivalence. A restricted explicit translation language with literal accepted/refused traces is a safer starting experiment than guessed schema coercion. [ACP initialization](https://agentclientprotocol.com/protocol/v1/initialization), [Claude SDK permissions](https://code.claude.com/docs/en/agent-sdk/permissions), [MCP basic protocol](https://modelcontextprotocol.io/specification/2026-07-28/basic), [A2A idempotency](https://a2a-protocol.org/latest/specification/#331-idempotency), [WIT](https://component-model.bytecodealliance.org/design/wit.html)

Authority must survive both outward delegation and returned handles. Pin audience, object identity, units, interpreter revision, parent ceiling, and current recipient freshness at actual use. A returned URI may be data, a locator needing fresh authorization, or an authority-bearing handle under a specific contract. Possession of a string must not silently choose the third interpretation. OAuth token exchange does not automatically create tight revocation linkage; multi-audience tokens have cross-target risks. Macaroons illustrate conjunctive restrictions, but application semantics still matter. [RFC 8693](https://www.rfc-editor.org/rfc/rfc8693.html), [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707.html), [Macaroons](https://theory.stanford.edu/~ataly/Papers/macaroons.pdf), [MCP tool handles](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

Bidirectional capability membranes are a useful analogy for returned authority. The cited Miller evidence is limited to the primary indexed Figure 9.3 and caption, not a fully inspected dissertation. UCAN's revocation comparison is a release candidate, v1.0.0-rc.1, not a ratified standard; alternate proof paths and eventual propagation reinforce the need to specify exactly what withdrawal means. Neither source selects a Recursion credential scheme. [Miller Figure 9.3](https://jscholarship.library.jhu.edu/bitstreams/c2c3ea50-2613-47a7-b33c-9383c706ee63/download), [UCAN revocation candidate](https://github.com/ucan-wg/revocation)

## 4 Shared correctness and evaluation contract

### Cancellation and effect state must remain separate

Normalize observations only to facts they support. The UI can truthfully show a cancellation request, an interrupted turn, an empty local process scope, and an unresolved remote effect simultaneously. One terminal label cannot represent all four.

| Observation | Supported conclusion | Still not established |
|---|---|---|
| ACP presents cancellation after sending the request | User-facing cancellation intent | Receipt by agent, descendant exit, or effect settlement |
| Codex interrupt acknowledgment then interrupted turn event | Request acknowledgment and source turn lifecycle | Full process census or remote operation outcome |
| OpenCode abort boolean or MCP stream closure | Source-defined response or cancellation signal | Guaranteed rollback, complete cancellation, or zero usage |
| Qualified local process scope is empty | Those owned local processes are gone | Service work they previously started has stopped |
| Trusted matching recipient outcome | That operation's reconciliation | Authority for a new invocation |

These source contracts differ; retain the raw source event with its interpretation profile. ACP permits late updates before the cancelled prompt result; Codex separates interrupt from later completion; MCP cancellation has non-cancellable/completed-request cases. FU05's noted subscription-teardown discrepancy remains unresolved. [ACP prompt lifecycle](https://agentclientprotocol.com/protocol/v1/prompt-turn), [Codex App Server](https://learn.chatgpt.com/docs/app-server), [OpenCode server](https://opencode.ai/docs/server/), [MCP cancellation](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/cancellation)

Define one owner for admission/fence, local process scope, exact upstream turn cancellation, context transition, each retry layer, reservation, and reconciliation. During update or reconnect, a handover binds old/new incarnations, unresolved operations, reservations, pending interactions, and context revision. An old event can establish old history without updating new authority. Transport retry and effect retry require separate identities. Unrelated admitted work may progress while one effect remains uncertain if its authority and resources are independent.

Reservations must use their declared accounting model. For a fixed-effect-charge fixture, only proven nonexecution releases the unused effect reservation; known success consumes its charge. In upper-bound accounting, a trusted success can settle actual use below the reservation and release the remainder. [Fixed-effect example](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/EXECUTION-FABRIC.md#L433-L455), [upper-bound ledger settlement](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/experiments/v3/recovery-ledger-20260914/ledger.py#L516-L539). An unknown outcome releases neither by guess. Source counter reset does not replenish the parent allowance. Claude SDK documents reset/resume and incomplete crash-counter behavior; model-visible task budgets are advisory. Subscription consumption remains unknown without adequate route evidence. [Claude cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking), [Anthropic task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets)

### One context epoch oracle across two experiment questions

Specify the shared context-epoch and ownership oracle before R06. R06 uses it first; R08 reuses and extends its source-translation and accounting assertions. Both share context-epoch identities, owner-transfer semantics, canonical event cuts, and trace IDs. This is a shared contract prerequisite, not a requirement that both experiments finish before either can start. R06 asks whether concurrent compaction, new input, revocation, and crashes preserve an admissible continuation. R08 asks whether source events and handovers preserve cumulative accounting and responsibilities. Separate their assertions and outcome fields, but do not maintain subtly different candidate state machines for the same transition.

The unconditional safety property is at most one admitted successor per parent. Zero successors is correct if every proposal is invalid or the parent is revoked. Eventual acceptance of one successor is a separate progress requirement after quiescence, with a valid admissible proposal, available writer/dependencies, and declared fair scheduling/delivery. Neither canonical replay agreement nor a post-hoc upstream callback proves an upstream honored the actual effect fence.

OpenAI compaction has opaque encrypted state; Claude's documented threshold path has a pause affordance; Pi documents a pre-compaction extension and kept-entry boundary; Codex code distinguishes history replacement and initial-context reinjection. These are current documentary examples, not equivalent installed-route guarantees. A route may be interceptable, observable-only, or opaque. Reconcile at an actual observable boundary and hold consequential work as required; do not call an unobservable rewrite prevalidated. [OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction), [Claude threshold compaction](https://platform.claude.com/docs/en/build-with-claude/compaction-threshold), [Pi compaction](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/compaction.md), [Codex compact.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/compact.rs)

### Qualify the recorder and the oracle

The permanent experiment inventory starts with offered demand and assigned tasks, not just successful runs. Record attempt intent before effects, every retry and verifier, all terminal or unresolved states, and late amendments. Final result rows are insufficient: Inspect's pinned scanner design describes retry/cleanup behavior that can omit intermediate attempts from settled rows or delete earlier logs. This is a documented design concern at one revision, not an audit of every Inspect release. [Inspect scanner design](https://github.com/UKGovernmentBEIS/inspect_ai/blob/617d06c72bcde8d6988e200f98946797614e29c2/design/eval-set-scanners.md#L257-L317)

Independent code or different model branding does not establish an independent specification. The repository records compared reducers agreeing on a bug. R04 therefore measures whether independently constructed behavioral oracles detect consequential common-mode misses, while retaining valid alternative implementations as positive controls. Preserve the existing DS-03 independence vector and V0–V3 floors. Execution, specification, semantic detection, and failure-domain independence are distinct views, not a replacement tier system. Public studies of correlated model/judge errors motivate measuring shared misses, but do not supply a Recursion code-review error rate. [Repository counterexample](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/construction/typed-consultation-20260908/findings.md#L35-L61), [Kim et al. v1](https://arxiv.org/html/2506.07962v1), [Kohli v1](https://arxiv.org/html/2605.29800v1#Sx1)

Public benchmark names are not sufficient identities. OpenAI's 2026 SWE-Bench Pro review concerns the 731-task public split: 286 flagged tasks, 200 labeled broken by deeper agent-assisted review, and 249 by its human campaign. The flagged-subset procedure and missing dataset commit prevent treating these as Recursion's error rate or every-version estimates. The pinned Tau successor marks a banking_knowledge scoring change at v1.0.1 and separates final-state/required-communication reward from diagnostic natural-language assertions. Qualify a pinned task, scorer, and enforced requirement before using the score. [OpenAI audit](https://openai.com/index/separating-signal-from-noise-coding-evaluations/), [Tau version warning](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/README.md#L16-L30), [Tau evaluator semantics](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/docs/evaluation.md#L8-L60)

Challenge the grader itself. SWE-bench's pinned scorer checks skipped fail-to-pass tests and nonzero exit status despite apparent passing logs. EvalPlus shows that stronger tests expose misses in bounded code synthesis; additional tests derived from one mistaken reference still do not establish an independent specification. AgentDojo motivates measuring attack resistance and benign utility separately. Reject-all systems must fail positive-control adequacy. [SWE-bench scorer](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/grading.py#L49-L176), [EvalPlus](https://arxiv.org/abs/2305.01210), [AgentDojo](https://arxiv.org/abs/2406.13352)

### Measure the question actually being asked

**Attribution** asks whether Recursion helps with the same engine/model/tools and admissible envelope. **Deployment utility** compares complete native-only, upstream-only, and combined configurations with their real capability differences. **Release conformance** asks whether every required cell satisfies its obligations. Report these separately. Restricting analysis to the mutually available easy tasks can conceal a deployment failure; removing capability differences can conceal a real utility advantage. Agent-evaluation research supports cost and holdout discipline without identifying Recursion's optimum. [AI Agents That Matter](https://arxiv.org/abs/2407.01502v1), [Anthropic evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

Count family, unique task, attempt, artifact, and assessor-arm workload separately. Repeated checkpoints, seeds, judges, or four policies over the same artifact do not create additional independent tasks. Finite-suite reliability is distinct from transfer to a population of future tasks; a bootstrap does not make a curated set representative. Preserve the current no-favorable-interim-stop rule and require a prospective amendment for a different sequential design. Report task/family-clustered uncertainty, family-level sensitivity when clusters are few, practical margins, exclusions, and multiplicity. [Existing statistical protocol](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/FRONTIER-HARNESS-EVIDENCE.md#L301-L335), [statistical precedent](https://proceedings.neurips.cc/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf), [time-uniform inference](https://doi.org/10.1214/20-AOS1991)

At the deadline, unresolved tasks are non-completions for the deadline endpoint. Informative route failure, quota exhaustion, or refusal must not be treated as harmless censoring. For N assigned tasks, S verified successes, and U unresolved eventual labels, the interval S/N to (S+U)/N is an identification bound, not a confidence interval. Invalid-task corrections retain the original all-assigned result plus a blinded, reason-coded sensitivity analysis. Zero observed failures does not prove zero risk: the illustrative iid Bernoulli one-sided 95% upper failure bound is 1 − 0.05^(1/n), about 9.5% at n = 30. Correlated tasks and selected seeded defects do not satisfy that simple incidence model. [NIST exact-binomial method](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbici.htm)

For each resource dimension, report the whole cohort total and total divided by unique verified closures under the fixed policy/cutoff. Include failed tasks, planning, compaction, retrieval, support roles, retries, verification, human repair, waiting, recovery, and downstream correction. Zero verified closures makes cost per closure undefined. Keep currency, subscription-native allowance/window change, observed token classes, CPU/memory-time/I/O, human minutes, and calendar latency separate. Unknown is not zero; unallocated account use is an unreconciled bucket. Freeze guaranteed resources, hard ceilings, and load because infrastructure changes can alter task outcomes. [Infrastructure study](https://www.anthropic.com/engineering/infrastructure-noise)

Report cold one-shot, actual reuse horizon, and no-future-work cases. A forked trial pays the shared experimental prefix once in actual-spend accounting, but each deployment counterfactual needs its full prefix cost unless the declared question is marginal recovery from a checkpoint. Distinguish first-review acceptance, verified closure by deadline, and escaped defects during a finite downstream-use window. METR's task time horizon measures difficulty through human completion time at a success probability; it is not an unattended-uptime guarantee. [METR paper v4](https://arxiv.org/abs/2503.14499v4), [METR limitations](https://metr.substack.com/p/2026-01-22-time-horizon-limitations)

## 5 Dependency ordered experiment program

Every R identifier below is unique across this synthesis. Stage labels describe what evidence is needed, not permission to execute. The numerical bounds in Section 7 are exploratory design caps, not power calculations, product minima, or spending authority.

| ID | Experiment | Main dependency | Earliest useful stage |
|---|---|---|---|
| R01 | Denominator and recorder metrology | LP-0 and DS-26 semantics | Inert histories |
| R02 | Actionable control restoration | LP-0 and imported-reference bridge | Inert timelines |
| R03 | Semantic translation and workflow closure | LP-0, M1B bridge, candidate FU03 reconciliation | Inert source profiles |
| R04 | Oracle custody and shared defects | R01; independent oracle custody begins in R01–R03 | Deterministic challenge before later model arms |
| R05 | Two hop attenuation and returned handles | R03; explicit offline/revocation policy | Inert recipient model |
| R06 | Compaction arbitration | R02–R03; shared epoch oracle with R08 | Inert race traces |
| R07 | Dependency safe context reuse | R02; typed evidence/transform identities | Literal DAG mutations |
| R08 | Joined ownership and accounting | R01, R03, R05–R06; reconciled FU03/FU05 contracts | Inert composed traces |
| R09 | Causal work coverage | R03, R05, R08; actual FU04/FU05 facts for later stage | Inert boundary graph first |
| R10 | Masking versus folding and selective access | R02; R04-qualified evaluation; R01 accounting | Offline mechanisms, then admitted semantic trials |
| R11 | Cold restore and complete costs | R02, R06–R07; eligible R10 mechanism; R08–R09 | Fake routes, then admitted real routes |
| R12 | Route complete workflow economics | Qualified native and upstream slices, R01/R04, R03/R08/R09 | Admitted end-to-end routes |
| R13 | Recovery through downstream use | R11, R01/R04; accepted FU store/OS/broker facts | Admitted task graphs |
| R14 | Adaptation and fresh task generalization | R01/R12; fixed filters and feedback qualification | Synthetic replay, then separately admitted live learning |

R04 is intentionally both a cross-cutting acceptance dependency and a later bounded comparative experiment. For the first three packets, independently authored expected outcomes and blind challenge cases are required immediately. The full 72-artifact assessor comparison is unnecessary before writing a recorder; accepting a recorder solely because its author wrote matching expectations is equally unacceptable.

R06 and R08 consume one shared transition oracle. R11 and R13 share one checkpoint, fault, and evidence-accounting manifest where applicable. R11 addresses cold reconstruction and initial useful continuation; R13 evaluates whether that continuation remains correct when a sealed downstream task uses its output. Their endpoint records are separate, and the same restore is not counted as two independent trials. R12 answers deployment economics; R14 studies adaptation only after its fixed-policy and accounting prerequisites exist. This division avoids four competing recovery campaigns or a second state machine.

### Coordination with current local work

The new inert packets can proceed without a language or storage selection. When they touch durability, platform enforcement, or broker materialization, they must stop at the corresponding accepted FU evidence. A fake process fact cannot fill an unqualified FU04 cell; a simulated snapshot cannot close FU05 SM-01. Use existing local outcomes rather than commissioning duplicate native fault matrices.

The full product still needs actual plugins, native execution, upstream adapters, operator interaction, node transport, and recovery. These experiments should expose each obligation early in the composed seam, but a useful kernel spike is not a complete v3 release. Keep adapter-free canonical status/replay and the required website preview, bug fix, interrupted refactor, and upstream-only acceptance scenarios. [Acceptance scenarios](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/ACCEPTANCE.md#L132-L165), [release gate](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/ACCEPTANCE.md#L407-L419)

## 6 Three first local handoff packets

These packets are ready to narrow and admit. Lucas still selects the source/candidate, allowed paths, finite resource budget, and independent verifier. The following text does not authorize execution or editing outside those paths.

### Handoff R01 Account for every attempt

Build an inert recorder comparison in the proposed experiments/v3/evaluation-integrity/ path, with matching construction documentation. Consume DS-26 field semantics and a literal synthetic receipt corpus. Compare the runner's final export, an additive attempt-intent ledger, and independent reconstruction. Start with 36 histories plus six independently authored hidden challenges; make no provider calls.

Return the exact task/attempt census, raw receipts and retry ancestry, orphaned/unallocated costs, explicit zero/unknown cases, late-correction history, and a small reconstruction checker. The independent verifier must reconstruct totals without trusting the final dashboard. Every omitted assigned task, missing started attempt, duplicated charge, erased failure, or fabricated counter is a rejection. Unknown outcomes can pass truthfulness but cannot become verified success. Report recorder overhead without a performance PASS until Lucas sets an overhead margin.

**Decision enabled:** whether later comparisons have an admissible denominator and cost record. **Reversal:** an existing recorder already provides equivalent exact-candidate reconstruction and adversarial evidence; reuse it rather than create another.

### Handoff R02 Recover the next authorized action

Build a new research projection in experiments/v3/context-actionability/, with an explicit imported-reference bridge to frozen M1A/M1C. Use 24 independently specified timelines and paired distractor versions. Compare full typed state, a summary/ID-list negative comparator, and an exact control projection with addressable evidence. No model, production context service, or new canonical writer is needed.

Return literal event cuts, allowed/forbidden action sets, required hold reasons, decision/provenance paths, source/profile identities, candidate bytes, and minimized failures. Include forged approval text in raw logs, retrieved snippets, and folded summaries, plus genuine attributable amendments that must progress. Drop provenance/target/supersession/authority/applicability fields one at a time. Reject any unsafe admission, promoted proposal, forged grant, lost unsettled effect, or blanket refusal of positive cases.

**Decision enabled:** what exact state and evidence a useful capsule must preserve. **Reversal:** the richer projection does not improve correct action/hold reconstruction over a simpler lawful representation, or cannot preserve privacy/retention while doing so. Structural success remains insufficient for semantic quality.

### Handoff R03 Translate source events without upgrading their meaning

Build a restricted semantic mapping prototype in experiments/v3/harness-composition-contracts/semantic-mapping/, with separate source profiles outside M1B. Use four synthetic profiles, two semantic revisions, six controls, and constructive native-only, upstream-only, and combined witnesses. Reconcile the candidate FU03 type/byte bridge; do not choose a production protocol.

Return raw event → target fact mappings, supported/unsupported/unknown outcomes, loss explanations, all-role dependency closure, and independent literal expected traces. Challenge empty-object semantics, allowed_tools versus inventory, queue versus active steering, UI cancellation versus settlement, hidden helpers, and optional idempotency. Valid richer extensions and a complete upstream-only planner/worker/reviewer closure must pass without a direct-API fallback.

**Decision enabled:** whether one contract can describe both mediated effects and bounded sessions without erasing capabilities or inventing enforcement. **Reversal:** a simpler route-specific mapping supplies the same qualified workflow coverage with less maintenance, or the shared contract repeatedly obscures consequential source semantics.

## 7 Complete experiment protocols

All experiments in this section are proposed and unrun. Each retains an independent positive witness and a negative challenge, exact evidence lineage, finite stopping rule, and Owner inputs. References to execution describe future admitted work. A failing hard-floor candidate is stopped; repair creates a new candidate binding rather than an edited old PASS.

### R01 Denominator and recorder metrology

**Origin:** Evaluation memo EVAL-01. **Depends on:** LP-0 and DS-26 semantics; independent literal census.

**Decision and hypothesis.** Can the chosen evaluation runner produce a reconstructable census of demand, attempts, outcomes, and resource use despite retries and crashes? Hypothesis: a pre-start intent ledger plus independent raw-receipt reconciliation reveals omissions hidden by final-result exports, at bounded recorder overhead.

**Prerequisites.** Accepted field semantics from DS-26; synthetic source/receipt fixtures; no real model or provider required. This can start before runtime selection. It tests research instrumentation, not FU-02 product-store durability.

**Competitors and baselines.** A: runner-native final export only. B: export plus additive attempt-intent/terminal ledger. C: B plus independent side-channel reconstruction. A is a measurement control, not an admissible reporting policy if it loses attempts. Use a literal externally authored expected census as ground truth.

**Bounded workload.** Thirty-six scripted histories: 12 ordinary, 12 retries/partial failures, 12 interrupted/late/duplicate evidence cases. Include crash before a result exists; provider accepted request but response lost; verifier unavailable; retry cost omitted; duplicate receipt; account-window reset; task becomes unsupported after assignment; late billing correction; final-log cleanup; conflicting rerun IDs. Do not call a provider to simulate these.

**Ablations.** Remove pre-start record; drop retry-parent ID; omit verifier lineage; merge unavailable with zero; enable destructive retry cleanup in an isolated fixture; remove account-window identity. Each mutation has an expected conservation violation. Include valid zero-use and correctly de-duplicated positive controls.

**Leakage controls.** Freeze literal histories and expected census before recorder implementation; independent reviewer authors at least six additional blinded cases. Keep helper recorder output outside the target's writable result directory. Hash input, implementation, configuration, and expected output.

**Observables.** Missing/extra/duplicated tasks and attempts; orphaned charges; unknown-to-zero conversions; unallocated consumption; latency attribution gaps; recoverability of original versus corrected results; recorder wall/CPU/storage overhead on this bounded fixture corpus.

**Falsifiers and gate.** Any omitted assigned task, missing started attempt, duplicate charge, silently erased failure, or fabricated numeric counter rejects the recorder. A correct explicit unresolved state passes truthfulness but cannot count as success. Independent reproduction must recover identical cohort totals and state counts from retained bytes, without trusting the runner's headline status.

**Stop.** Stop after all 36 plus six challenge histories have final dispositions and the exact candidate is independently checked; or immediately on an unexplained conservation mismatch. Repair creates a new candidate and reruns the relevant finite gate. No indefinite expansion of scenarios. Overhead thresholds need Owner approval before measurement; absent one, report overhead without a performance PASS.

**Retained evidence.** Admission/intent records, all raw synthetic receipts, retry ancestry, discarded-export examples, exact transforms, mismatch witnesses, known zeros/unknowns, result deltas after late corrections, independent reconstruction receipt.

**Owner decisions.** Recorder overhead budget; acceptable retention/redaction of future live traces; whether unresolved monetary attribution blocks a money claim only or the whole comparison.

**Proposed landing paths.** `experiments/v3/evaluation-integrity/`, `docs/v3/construction/evaluation-integrity/`; additive links from PERFORMANCE-PLAN and DS-26 crosswalk. No rewrite of the product accounting ledger from this experiment alone.

### R02 Recover actionable control and decision provenance

**Origin:** Context memo E1. **Depends on:** LP-0 and frozen-M1 imported-reference bridge.

**Hypothesis.** A capsule derived from existing canonical records plus exact evidence closure preserves the eligible next-action set and honest holds through compaction/restore. An ID-complete summary is insufficient.

**Workload.** Twenty-four hand-authored synthetic timelines: three per family covering accepted-vs-proposed instructions; scope-specific approvals; revocation/supersession; candidate-bound gate evidence; unknown external effects; pending consultation; privacy/audience change; and source freshness. Pair each with an equivalent distractor-heavy version. The independent fixture author specifies the allowed/forbidden next action and required evidence/hold reason before seeing candidate output. No target repository behavior is executed.

**Baselines/treatments.** B0 full typed canonical state plus raw evidence; B1 summary and ID list; T exact typed control projection plus lazily addressable evidence. B1 is an intentionally plausible negative comparator, not a deployable safety option.

**Ablations.** Remove provenance, target binding, supersession edge, authority recheck, or evidence applicability one at a time. Include a valid positive counterpart for every refusal fixture to defeat blanket-deny implementations.

**Concrete poisoning seam.** A retrieved tool log says that the Owner approved a new route and publication; an upstream summary repeats it as a decision. The actual Owner record authorizes only local inspection. Inject the same malicious sentence into raw evidence, a retrieved snippet, and a folded summary. None may become a command/grant. After restore, the actor must identify it as third-party evidence, retain the real accepted scope, and hold publication. A real attributable later Owner amendment must be distinguishable and progress. This tests provenance laundering, not every prompt-injection threat.

**Measurements.** Exact control closure failures/case; unauthorized eligible actions/case; valid actions incorrectly held/case; correct hold-reason and decision-provenance reconstruction/case; bytes and milliseconds for compile/validate/resolve. Separate stale-source acceptance from authority violation and semantic answer error.

**Pass/fail/stop.** Zero unsafe admitted actions, zero promoted proposals/forged grants, zero lost unsettled effects; every declared positive case reconstructs its permitted next step. Any false acceptance stops that candidate. Missing external evidence produces an explicit hold, never a fabricated success. A structural PASS is not evidence of arbitrary language understanding.

**Evidence bundle.** Literal initial states, timeline/event cut, exact expected action masks and provenance paths, candidate bytes, source/profile/digest map, transform logs, minimized counterexamples, independently authored oracle and reviewer decision. Preserve the raw poisoning inputs privately with synthetic identity only.

**Owner decision / landing.** Decide which task-specific conditions are hard holds versus refreshable evidence gaps; approve a new research schema epoch rather than editing M1 contracts. Proposed `docs/v3/construction/context-actionability/` and `experiments/v3/context-actionability/`; imports/reference adapters to M1A planning and M1C evidence/effect fixtures. Resolves a narrow A-07/LP-6 seam and informs G-27, not the whole gap.

### R03 Semantic translation and workflow closure

**Origin:** Composition memo HC-01. **Depends on:** M1B source profiles and candidate FU03 reconciliation.

**Hypothesis.** A typed, versioned behavior contract catches dangerous equivalences that a boolean feature matrix misses while admitting useful rich workflows.

**Baseline.** Feature-name support plus matching JSON method/schema names. **Treatment.** Restricted explicit mapping rules with lifecycle/ownership/effect/unit profiles and inspectable losses. **Ablations.** Remove semantic revision; remove per-request capability refresh; remove dependency closure; replace partial/unknown with false or true.

**Finite scope.** Four synthetic source profiles inspired by ACP, MCP, Codex and Claude SDK; two semantic revisions; six controls (tools, permissions, cancellation, continuation, compaction, extension invocation); three execution modes. Preserve the complete real route inventory as coverage rows without claiming all rows implemented.

**Positive controls.** An exact tool ceiling enforced by an appropriate surface; an explicitly allowed richer upstream extension; a bounded upstream-only planning/worker/reviewer closure with no direct-API dependency; matching empty-capability interpretation.

**Negative controls.** `allowed_tools` mistaken for inventory; ACP/MCP empty-object conflation; queue mistaken for steer; user-interface cancellation mistaken for settlement; opaque helper requiring a new route; optional source idempotency promoted to guaranteed effect deduplication.

**Evidence/oracle.** Independently authored literal source traces and expected target facts; raw event retained beside normalized record; a three-valued supported/unsupported/unknown outcome plus loss explanation. All three required modes must have constructive witnesses. A safety-only compiler rejecting everything fails adequacy.

**Stop.** All frozen cases have independent expected dispositions and both ordinary and adversarial mappings agree; otherwise retain exact unresolved cell. No additional routes are removed to obtain a pass.

**Owner inputs and dependencies.** Accept which workflow transformations are alternatives rather than equivalent controls; preserve answered ten-control requirements. Uses M1B fixtures and FU03's reconciled byte/type bridge; does not require selecting a runtime.

**Landing.** Proposed `experiments/v3/harness-composition-contracts/semantic-mapping/` and `docs/v3/construction/harness-composition-contracts/`; keep source profiles outside frozen M1 schemas.

### R04 Oracle custody and common mode defect challenge

**Origin:** Evaluation memo EVAL-02. **Depends on:** R01; oracle-custody controls already apply to R01 through R03.

**Decision and hypothesis.** Does independent specification/evidence construction detect consequential errors missed by nominally diverse reviewers sharing the same flawed gate? Hypothesis: extra oracle independence contributes more conditional detection than another reviewer who sees the same rubric and candidate narrative. This is a focused precursor to DS-03's 480-candidate matrix, not a competing independence-tier system.

**Prerequisites.** R01 census; stable task spec; qualified deterministic runner. Model-assisted arms remain separately authorized. No V0–V3 floor is removed in production or release acceptance.

**Competitors and baselines.** T0: existing gate and existing independent-review policy. T1: additional capable different-family reviewer using the same spec and gate. T2: independently authored behavioral oracle plus clean rerun, followed by the same reviewer resources as T1. T3: independent qualified human assessment without seeing prior verdicts. Compare T1/T2 only under a declared time/resource envelope; report unequal effort rather than claiming pure semantic attribution.

**Bounded workload.** Twenty-four distinct synthetic tasks across six families, each containing a clean alternative implementation, a visible-test-passing semantic defect, and a correct implementation rejected by an overly narrow test: **72 unique artifacts**, clustered by source task. Assess every artifact once under each of T0–T3: **288 primary arm-assessments**, including 72 independent-human T3 assessments. No outcome-selected repeats. Half the tasks target code behavior; half target research/tool workflows with independently checkable state or source requirements. Add four controlled evaluator-integrity faults as separate harness checks, not extra independent tasks. Cap additional adjudication at 24 artifact reviews: 12 randomly selected agreement cases and up to 12 disagreement cases selected under a frozen severity-first rule with random tie-breaking. Any remaining disagreements stay unresolved. A primary arm-assessment can contain its specified gate/reviewer steps; freeze those steps and per-assessment time/model-call limits before execution. Owner approval of the total human-hour and resource ceiling is an admission prerequisite. Extend only through a new preregistration if the pilot supports a worthwhile confirmatory decision.

**Defect focus.** Shared misunderstood requirement; reference-derived tests duplicating the candidate bug; omitted negative side effect; stale or mismatched candidate; fabricated pass log/skipped test; valid alternative algorithm rejected; citation that exists but does not support the claim; obsolete source overriding a current one. This samples cases that gate-only evaluation can systematically mislabel, not merely random code mutations.

**Ablations.** Same versus independently constructed evidence; prior implementer rationale visible versus withheld; task authorship shared versus separated; wrong but plausible reference patch versus no reference; model-family difference with all other evidence fixed. Do not demand every crossing of the DS-03 vector in this packet.

**Leakage controls.** Oracle authors cannot inspect candidate implementation or existing tests until their first contract is committed. Candidate authors cannot see hidden cases. Reviewers receive anonymized artifacts and randomized order; obtain initial labels before rationale/other-reviewer disclosure. Hold out entire task families and mutation mechanisms. Track shared source/spec/reference ancestry; merely hiding model names does not remove code-style clues.

**Observables.** False-green rate among independently established defects; false-block rate among valid controls; conditional detection given the baseline miss; common-mode misses by defect family; disagreements and unresolved ground truth; human effort; evaluator tamper detection. Agreement is diagnostic, not accuracy. Adjudicate the capped disagreement sample and the 12 preregistered randomly sampled agreement cases; report unadjudicated disagreements explicitly. This avoids looking only where judges disagree without hiding additional review work.

**Falsifiers and gate.** A shared wrong oracle that survives T1 but is exposed by T2 is a counterexample to “diverse reviewers suffice,” not proof T2 is universally superior. If T2 adds no useful detection and exceeds the approved effort margin, its proposed increment fails for this scope. Any clean control incorrectly blocked requires label/spec review; do not improve defect recall by failing everything. Unresolved gold labels stay unresolved and enter best/worst-case sensitivity, not majority-vote truth. Seeded defects measure sensitivity on this corpus, not real-world defect prevalence.

**Stop.** Complete the fixed allocation of 72 unique artifacts × four policies = 288 primary arm-assessments, at most 24 additional adjudication reviews, and four harness challenges, or suspend on corrupted/blinded ground truth or the admitted time/resource ceiling. Unfinished assessment cells remain unavailable; the cap never permits dropping difficult cases from the denominator. Stop tuning judges at the discovery boundary; any tuned judge is tested only on new held-out families. No superiority claim from an underpowered pilot.

**Retained evidence.** Original task contract, independent oracle draft timestamps/hashes, candidate/gate lineage, blinded initial verdicts, source verification, adjudication evidence, all agreements sampled, defect provenance, escaped-mutant witnesses, exact per-artifact cost.

**Owner decisions.** Qualified adjudicator; acceptable false-block/effort tradeoff; minimum practical conditional-detection gain; which future defect classes merit a larger DS-03 stratum. Mandatory verifier requirements remain closed unless separately changed by the Owner.

**Proposed landing paths.** `experiments/v3/evaluator-oracle-challenge/`, `docs/v3/construction/evaluator-oracle-challenge/`; map findings into existing DS-03/G-12 and scientific-evidence G-28 rather than create a new acceptance authority.

### R05 Two hop attenuation including returned authority

**Origin:** Composition memo HC-02. **Depends on:** R03; explicit offline, freshness, and revocation policy.

**Hypothesis.** Preserving the original ceiling and semantic interpreter at the final effect boundary prevents widening that handoff-only checks miss, including returned handles.

**Baseline.** Validate the parent grant at session launch, then trust adapter-derived scopes and returned handles. **Treatment.** Parent-conjunct preservation, exact audience/object/unit binding, interpretation revision and recipient freshness check. **Ablations.** Drop one original caveat; allow multi-audience scope cross-product; trust possession of a returned handle; accept a step-up challenge as approval.

**Finite scope.** Three principals, two delegation edges, two audiences, two sibling objects, two grant epochs, one returned job/resource handle and one disconnected recipient. Synthetic tokens and in-memory resource counters only; no real credentials or crypto-system selection.

**Positive controls.** Allowed narrow read completes; an authorized local bounded operation finishes while offline under its explicit permit; a valid returned handle works before withdrawal; historical receipt remains readable after current authority expires.

**Negative controls.** Prefix-confused sibling object, added verb under old semantic version, different tenant at the same host, handle copied to another parent goal, revoked ancestor with retained child token, stale step-up and new action based on an old receipt.

**Evidence/oracle.** An independent set-based authority model specifies exact admitted requests and original ceiling. Record both translations, recipient policy/freshness, actual fake effect count and returned-handle lineage. Distinguish withdrawal of one proof path from policy withdrawing all task authority.

**Stop.** Every baseline defect is demonstrably reachable; treatment rejects it without rejecting positive controls. Unknown recipient freshness follows the selected explicit policy. Stop on ambiguous policy instead of selecting it inside the fixture.

**Owner inputs/dependencies.** Offline completion scope, revocation target and allowed freshness exposure; G-07 must be reconciled. Extends FU03's authority vectors and SECURITY's existing grant fields, not a new constitution.

**Landing.** Proposed `experiments/v3/harness-composition-contracts/attenuation/` with paired documentation. Production credential work remains separately gated.

### R06 Compaction arbitration at observable boundaries

**Origin:** Context memo E3. **Depends on:** R02 and R03; one shared epoch and ownership oracle with R08.

**Shared implementation boundary.** Use the same canonical epoch and ownership predicates and trace IDs as R08. Keep compaction fidelity and source-event translation as separate assertions over that shared trace.

**Hypothesis.** One canonical epoch transition can remain linearizable through native compaction, appended input, revocation, cancellation and crash, but the guarantee depends on actual upstream interception/observation capability.

**Workload.** Eight synthetic race families, each interrupted at five declared boundaries: before proposal capture; after candidate creation; after validation; after canonical epoch commit; and before adapter resume acknowledgment. Families include two simultaneous compactors, a new Owner message, revocation, tool result arrival, duplicate callback, missing callback, failed transform, and source/retention change. Use two admitted actor identities and a finite two-successor epoch bound; no claimed unbounded proof.

**Baselines/treatments.** B0 serialized stop-the-world fresh-session reconstruction; T1 pre-compaction intercept and candidate admission; T2 observed native rewrite followed by reconcile/hold; T3 opaque upstream with no reliable notification. Compare native-only and fake-upstream interfaces using the same current-authority and capsule validator. T3 is a capability-discovery negative profile and may be unqualified, not silently upgraded by assumption.

**Ablations.** Remove expected-parent compare-and-swap; accept latest-arriving candidate; ignore newly appended tail; validate only before compaction; allow upstream callbacks to update the canonical pointer; omit duplicate-callback identity; retry forever after nonshrinking compaction. A historical bug report is unnecessary as an oracle: each defect has an independent finite property and a valid positive trace.

**Measurements.** Canonical successor commits/parent; lost newly appended events; stale proposals admitted; effect dispatches after invalidation; callbacks paired with terminal outcomes; valid continuations/case; hold duration and recoverable progress; retries and nonshrinking transforms. Model-use counters remain zero for this proposed fake-route structural stage.

**Pass/fail/stop.** Unconditional safety is at most one admitted successor per parent; all-invalid proposals or a revoked parent may correctly yield zero. Eventual admission of one successor is a separate progress property, required only after quiescence when at least one proposal remains valid and admissible, the writer and required dependencies are available, and the experiment's declared fair-delivery/scheduling assumptions hold. The predecessor remains available under retention policy until its replacement is accepted; no lost tail, stale authority or unauthorized effect; duplicates do not create a second transition. Declared positive progress cases must resume under those assumptions. A route without the needed stop/reconciliation boundary remains unqualified for that guarantee. Reject any policy which labels an internal unobservable rewrite validated. Any infinite retry/nonshrinking loop is a failure; the experiment fixes finite attempts in its manifest. Canonical replay agreement alone cannot prove the external upstream honored the fence.

**Evidence bundle.** Event-order traces, route capability stubs and uncertainty states, captured pre/post projection digests, candidate/parent IDs, refusal dispositions, omitted-notification counterexamples, retry accounting and reviewer witness. Later real qualification must pin the upstream binary/interface, actual hooks and no-fallback proof.

**Owner decision / landing.** Decide acceptable functionality for observable-only routes and whether a missing capability blocks a declared workflow; do not reopen one-governor authority. Proposed `experiments/v3/context-arbitration/`, reusing patterns from `typed-consultation` and `generation-authority`; specification under `docs/v3/construction/context-arbitration/`. The common canonical writer remains the sole durable owner; no competing context database is introduced.

### R07 Dependency safe reuse with fresh authority

**Origin:** Context memo E4. **Depends on:** R02 and typed evidence and transform identities.

**Hypothesis.** Immediate-input/output traces plus fresh admission envelopes can avoid redundant work safely, while root-input-only caching and semantic-similarity reuse fail on stale/intermediate dependencies.

**Workload.** A small synthetic dependency DAG with raw source → deterministic extraction → model-produced summary fixture → evidence view → rendered route context. A fixed mutation manifest covers same-content/new authority; revocation; privacy change; changed candidate; tool/schema/environment changes; unchanged extraction after an irrelevant source edit; changed intermediate summary under identical source bytes; hidden filesystem input; conflicting output identity; deleted dependency; and same bytes in two private projects. The admitted manifest must enumerate the individual cases explicitly before execution. Model-produced outputs are literal alternate fixtures, not live calls.

**Baselines/treatments.** B0 rebuild every derived view; B1 invalidate all goal artifacts on any revision; T immediate dependency trace validation with exact output equality; deliberately unsound negative comparator: root-byte digest only. Compare cold restore with missing memo metadata against reconstruction from the retained derivation ledger.

**Ablations.** Omit transform/tool/profile identity, immediate-output digest, project scope, or current-admission envelope. Disable output-equality early cutoff to quantify its separate benefit. Do not use semantic similarity as equality.

**Measurements.** Stale/unauthorized reuse events; false invalidations; transform count; bytes reused versus reread; dependency checks; compile/validation CPU milliseconds; memo/trace bytes; wall time at fixed I/O profile; rejection reasons. Report evidence-byte hit, rendered-context reuse, provider cache hit and subscription debit separately.

**Pass/fail/stop.** Zero stale or cross-scope admitted reuse; every fresh envelope revalidates current scope; valid unchanged deterministic outputs can be reused without rerunning downstream transforms; unknown dependencies conservatively rebuild/hold. A hit-rate gain is rejected if its validation overhead erases the Owner's minimum worthwhile benefit. One unsafe hit kills the candidate. If complete dependencies cannot be captured for a transform, narrow its cacheability claim rather than pretending source hashes suffice.

**Evidence bundle.** Dependency graph, literal outputs, scoped identities, mutation corpus, full-rebuild comparison, invalidation explanations, measured resources and independent accepted/refused oracle. The new envelope must cite the prior immutable bytes without rewriting their historical provenance.

**Owner decision / landing.** Approve which transforms are reusable and evidence-age rules for non-authority facts. No selection of Salsa, Rust, CAS implementation or storage engine follows. Proposed `experiments/v3/context-invalidation/` and `docs/v3/construction/context-invalidation/`; integrate later with the FU-02 artifact closure, M1C evidence references, and CONTEXT's existing dependency-trace proposal.

### R08 Joined ownership under Stop and reconnect

**Origin:** Composition memo HC-03. **Depends on:** R01, R03, R05, R06 and reconciled candidate FU03 and FU05 interfaces.

**Shared implementation boundary.** Consume R06's epoch and ownership oracle; do not fork its state machine. This packet adds source-event interpretation, responsibility handover, and accounting assertions.

**Hypothesis.** Explicit ownership transfer and source-to-fact translation preserve cumulative budgets and permit independent continuation when nested loops emit conflicting lifecycle signals.

**Baseline.** One generic `cancelled/completed` session status, source cumulative cost and latest summary. **Treatment.** Owner vector, logical-operation/attempt/round/segment mapping and one governor transition. **Ablations.** Let both loops retry; let both compactors advance; reset parent budget on source reset; allow old incarnation events to update current work.

**Finite scope.** Two logical operations, at most two attempts/rounds per operation, two meter segments, two context candidates and bounded authority epochs inherited from the reconciled FU03 model. One lost response and one reconnect. Use literal event scripts; no model or upstream runtime.

**Positive controls.** One allowed compaction wins without losing intent references; late authenticated same-operation reconciliation settles the original reservation; unrelated admitted read-only work progresses while another effect is uncertain; a current grant permits a reconstructed upstream-only continuation.

**Negative controls.** ACP's immediate presentation cancellation releases effect hold; interrupt ACK proves process death; `/clear` renews cumulative allowance; unknown crash usage becomes zero; old context candidate overwrites current authority; a new wire request ID creates a second effect reservation or bypasses one.

**Evidence/oracle.** Independent operation and reservation ledgers, immutable raw source stream, canonical event cut, context-candidate digests and explicit owner handovers. Compare exact conservation and current-authority predicates with frozen M1A/M1C controls through the typed bridge. Required artifacts remain rehydratable; semantic summary quality is outside this experiment.

**Stop.** The complete bounded trace family and all ablations are classified; no inference of external settlement from lifecycle-only evidence; productive witness succeeds. Missing SM-01 materialization leaves physical snapshot claims blocked rather than simulated into PASS.

**Owner inputs/dependencies.** Retry/compaction ownership boundary and applicable Stop mode. Consumes FU03, existing shared-reservation/effect experiments and FU05 candidate delivery epochs; G-27 semantic quality remains separate.

**Landing.** Proposed `experiments/v3/harness-composition-contracts/ownership/` and trace crosswalks to existing experiment families.

### R09 Causal work coverage beyond local processes

**Origin:** Composition memo HC-04. **Depends on:** R03, R05, R08; exact FU04 and FU05 evidence for physical qualification.

**Hypothesis.** A route contract can honestly distinguish full local scope termination, remote cancellation request, and remaining external work while still supporting valid bounded-session completion.

**Baseline.** Parent process exit or empty Job/cgroup implies the upstream task stopped. **Treatment.** A bounded work-boundary graph: local managed process scope; callback/host operation; admitted remote service operation; source observation and enforcing endpoint at each edge. **Ablations.** Omit callback-created work; omit a remote edge; let a returning old executor renew its grant; collapse all outcomes into one terminal state.

**Finite scope.** One upstream session, one local child scope, one callback and one fake remote job; two node incarnations; one partition, one reconnect and one Stop per trace. First stage is pure evidence composition. Later native qualification consumes exact FU04 results; it does not rerun or silently replace that platform suite.

**Positive controls.** Local-only artifact work finishes and is accepted under its envelope; a declared remote job completes and returns authenticated matching evidence; local resources are safely reclaimed while unrelated remote uncertainty remains separately held; reconnect queries history without relaunching.

**Negative controls.** Remote job survives local termination but UI says all effects stopped; missing process notification becomes known exit; callback acquires an unadmitted service handle; revoked old incarnation starts a new remote job; a new terminal view launches work.

**Evidence/oracle.** Independently controlled fake remote-effect counter and operation record; exact FU04 observation tuple; declared causal-edge inventory and completeness boundary. A complete local process census is never used as the remote oracle. Unknown causal capture remains unknown.

**Stop.** Each graph edge's owner and disposition is independently reconstructable and all useful-positive traces pass; actual platform or remote enforcement gaps remain blocked. No production node enrollment, service launch, sandbox selection or live host effects are included in this packet.

**Owner inputs/dependencies.** Allowed external delegation boundary, offline local completion and truthful Stop wording. Consumes FU04 profile-qualified facts and FU05 receipts; informs G-15/17/18/19 rather than claiming those gaps closed.

**Landing.** Proposed `experiments/v3/harness-composition-contracts/work-boundaries/`, with per-route qualification overlays under the matching construction documentation.

### R10 Reversible masking folding and selective access

**Origin:** Context memo E2. **Depends on:** R01, R02 and R04-qualified evaluator; later model and route admission.

**Hypothesis.** For observation-heavy tasks, deterministic reversible masking is noninferior in actionable continuation and cheaper in total work; learned/summarized policies earn their complexity only on named density/phase strata.

**Workload.** Thirty-two synthetic episodes crossing four information-demand patterns (one old fact; multi-hop decision; temporal correction; dense aggregation), two irrelevant-output levels, two phase-boundary patterns, and two historical-source availability states. Seed exact exceptions and negative evidence early/middle/late. Use fixed checkpoint cuts after 0, 1, 4 and 16 transformations. These are controlled scenarios, not 128 independent user tasks.

**Baselines/treatments.** B0 full retained history within route capacity; B1 deterministic masking with recent tail and handles; T1 structured summary plus handles; T2 multi-scale phase folding plus handles; T3 read-only selective access with no recursive inference. Hold the exact control projection, evidence store, model/settings, prompt budget and tool affordances constant. Give every treatment the same admitted context capacity, with no silent raw-history truncation or extra raw-baseline budget. Report a matched within-capacity comparison where all treatments fit separately from a labeled over-capacity/capability stratum; in the latter, raw overflow remains an explicit unavailable/incomplete outcome in the availability and demand-coverage denominator rather than being discarded or recoded as a semantic-quality score. Neither stratum establishes a pure harness quality gain from unequal model context limits. If a trained folding model is available under later authorization, evaluate it as a separate model-policy block against its matched base model, never attribute the combined gain entirely to the harness.

**Ablations.** Mask without hydration; hydrate raw atoms versus prior summaries; recursive summaries versus rebuilding from original atoms; fixed window versus phase boundaries; relevance-only retrieval versus type/time/authority-filtered retrieval; selective access without and, only later if admitted, with declared sub-model calls. Keep an oracle-evidence treatment as a diagnostic upper bound and label its privileged information.

**Measurements.** Correct next action and final task result; missed exception/contradiction; unnecessary rediscovery and repeated explanations; raw-atom recall including all required evidence; hydrated bytes/tokens and overlapping re-reads; compaction/folding output tokens; all summarizer calls; rejected candidates; cumulative workflow tokens, local CPU milliseconds, peak RSS bytes; time to first *valid useful* post-restore action and end-to-end completion. Count frozen-trace cost replay separately from closed-loop behavior, because policies change later trajectories.

**Pass/fail/stop.** R02 hard floors first. For a later model-assisted comparison, Owner preregisters noninferiority margin and minimum worthwhile latency/consumption improvement per task family; no margin is inferred from public papers. At the finite budget, an interval crossing both useful benefit and material harm is inconclusive. Drop a policy on a hard-floor failure, unsupported route role, or budget exhaustion. If masking ties the richer policy inside the chosen practical margins, prefer the simpler mechanism for that stratum; this is an experiment decision rule, not a universal product default.

**Contamination controls.** Split by underlying scenario/template, not paraphrase; fixture authors and blind scorers do not tune candidate prompts; training/folding examples never contain held-out source facts or action oracles. Public benchmark tasks serve only as secondary regressions. Do not let the tool index the answer key. Pair runs by scenario and checkpoint; clustered uncertainty must not treat turns/cycles as independent samples.

**Evidence bundle.** Frozen episodes and splits, exact transformations/renderings, retained-source manifest, hydration traces, role-specific usage, blinded grades with disagreement adjudication, failures and trajectory lengths, analysis script specification and all exclusions.

**Owner decision / landing.** Approve model/route eligibility and budget only for the later semantic stage; choose quality margins and complexity tolerance. Proposed `experiments/v3/context-reversible/` and `docs/v3/construction/context-reversible/`. Feed findings into CONTEXT/PERFORMANCE-PLAN only after independent acceptance. No training or vector-store choice is implied.

### R11 Cold restore quality and complete workflow economics

**Origin:** Context memo E5. **Depends on:** R02, R06, R07, R08, R09 and eligible R10 mechanism.

**Shared evidence boundary.** R11 and R13 reuse one checkpoint, fault, and evidence-accounting manifest where applicable. First-valid-action and downstream-use endpoints remain distinct; shared restores do not create independent replicate tasks.

**Hypothesis.** A retained canonical cut plus layered evidence can recover useful authorized work across native/upstream session loss without material task-quality regression, and any efficiency benefit survives compaction, hydration, failed attempts, repair and no-future-work accounting.

**Workload.** Twelve representative synthetic checkpoints drawn from the preceding families. At each, remove one of four components: provider session only; derived indexes/summaries; a required artifact; or current authority access. Cross native-only and upstream-only fake-route modes first. Every mode has either a correct next action or an explicitly correct hold. Include a third combined-mode seam as a separate release prerequisite rather than inferring it from the two modes. No hidden chain of thought is an input or required recovery artifact.

**Baselines/treatments.** B0 full raw reconstruction; B1 validated exact capsule plus reversible masking; T best eligible R10 mechanism. Preserve same-role route eligibility and source evidence. In later authorized real-route trials, separately compare same-route continuation, fresh-session reconstruction and cross-route reconstruction. Session-fresh is not certified provider-cache-cold. Label cache state documented disabled, observed reuse/write, or unknown; include any deliberate priming in cost.

**Ablations.** Evidence locator removed; only summary retained; decision disposition removed; recovery reservation not preserved; role catalog omitted; pending external effect incorrectly treated as failed; no-future-work immediately after compaction. Inject deletion before hydration and partial snapshot closure. An unavailable artifact should test honest refusal rather than artificial task success.

**Measurements.** Correct first useful action/hold; completed-task quality; correct decision/approval provenance; repeated Owner instructions; unjustified effect retries; time from loss to valid useful action (milliseconds/seconds); total time to independently accepted completion; total model input/output/cache read/write and reasoning counters where exposed; per-role compaction/verification/retrieval/repair calls; local CPU/RSS/disk/network; human review and correction minutes. Report aggregate numerator and accepted-outcome denominator, retaining failed/censored attempts. Subscription debit or money is unknown unless an actual route receipt supplies it; API token prices are not a substitute.

**Pass/fail/stop.** R02/R06/R07 hard floors; no fabricated recovery of absent evidence; adapter-free status/replay remains available without inference. Before any upstream-only semantic trial, remove undeclared model/API routes and show every required model role resolves through approved upstream paths. If not, fail qualification rather than silently activating a native compactor. Owner sets semantic noninferiority, recovery latency and total-consumption margins. Stop a failed safety candidate immediately; stop at the admitted finite budget with inconclusive evidence if margins are unresolved. No refresh/keepalive policy can count unused future work as a realized benefit.

**Evidence bundle.** Consistent snapshot manifest and artifact closure; source/candidate/schema/authority cut; role-route map; missing-component fault record; cold-state classification and raw available counters; all restore/hydration/repair traces; blinded task scores; current eligibility proofs; resource distributions; independent review. Native/upstream results stay separate until each is qualified.

**Owner decision / landing.** Decide admitted route pairs, quality/RTO/consumption margins, restore/deletion conflict policy, and observable accounting required per route. Proposed `experiments/v3/context-cold-restore/` and `docs/v3/construction/context-cold-restore/`; connect to FU-02 coherent backup cut, FU-03 commit/refusal evidence, `experiments/v3/recovery-ledger-20260914/`, PRODUCT OR-030/034 and G-27. This is not authorization to run on a personal subscription or real project.

### R12 Route complete workflow economics and availability

**Origin:** Evaluation memo EVAL-03. **Depends on:** Qualified native loop and upstream adapters; R01, R04 and composition qualification.

**Decision and hypothesis.** When does orchestration buy useful quality, continuity, or responsiveness after all verification, retries, support roles, and review are counted? Hypothesis: a configuration can improve the declared objective on a task stratum without outsourcing hidden work or selecting away unavailable tasks.

**Prerequisites.** Qualified minimal native loop and at least two materially different upstream adapters; R01 accounting; R04-qualified task/evaluator subset; explicit all-role route inventory. Fake routes can validate instrumentation but cannot answer model-quality or subscription questions.

**Competitors.** Attribution pairs: direct upstream A versus orchestrated A, and direct B versus orchestrated B, holding exact model/engine/tool capabilities fixed where interfaces allow. Deployment candidates: native-only, independently useful upstream-only, combined. The direct harness may lack platform features; retain that declared limitation. It cannot substitute for a mandatory release configuration.

**Bounded workload.** A disjoint 12-task feasibility pilot, then at most 24 fresh tasks across four workflow strata with three trials per eligible treatment as an exploratory cap. Cover bug fix, interrupted refactor, research-to-tested-change, and multi-step collaborative clarification. Randomize paired order within task and interleave blocks across at least two admission windows. Do not claim power for a small binary difference; a confirmatory size requires the existing blinded simulation rule.

**Ablations.** Orchestration versus direct; support-role helpers disabled where the workflow remains valid; verifier fixed; warm continuity versus clean restart; opaque versus qualified accounting shown only as data-quality strata, not deliberately weaker product behavior. Select one interaction hypothesis, such as compaction × handoff; do not run every component factorial or repeat the full FHAR ladder.

**Leakage controls.** Fresh independent tasks plus a separately reported qualified public benchmark subset; clean per-trial worktree/session/memory; no cross-arm patch access; locked tool permissions and retrieval corpus. Same-source variants stay in the same split. Disable undeclared model connections in upstream-only; log declared route for every planner, compactor, reviewer, and recovery analyst. Keep engine/model drift as a new epoch, not pooled noise.

**Observables.** First-review acceptance, verified closure by deadline, downstream repair, responsiveness, human active/waiting time, whole-cohort resource totals, cost per verified closure, coverage of offered demand, route unavailability, hidden fallback attempts, admission delays, review backlog. Report strict matched-capability effect separately from full deployment tradeoff.

**Shared-pool control.** Treatments in the same subscription/capacity pool can interfere through depletion and throttling. Either serialize matched crossover blocks with measured starting conditions or treat the resource window as an additional cluster and explicitly estimate contention as part of deployment. Do not assume capacity reservations establish experimental independence. Two admission windows provide exploratory crossover coverage, not enough independent window clusters for reliable cluster-based uncertainty. Depletion and carryover must either be controlled with matched, directly observed starting conditions or explicitly included in the deployment treatment. A nominal waiting period is not proof that capacity or caches reset. If starting capacity cannot be matched, retain the economic comparison as descriptive/inconclusive for causal attribution. A missing exact debit leaves that dimension unavailable; it does not license token-to-subscription conversion.

**Falsifiers and gate.** Apparent gain disappearing after failed-task/review cost, a hidden native helper, an omitted capability, unequal unauthorized budget, or a win confined to the mutually available easy subset rejects the claimed interpretation. A hard-floor violation rejects the configuration regardless of averages. A non-dominated tradeoff stays an Owner choice.

**Stop.** Finish the preregistered pilot and finite exploratory cap or stop on safety, invalid evaluator, exhausted budget, or frozen precision/futility rule. If meaningful confidence is impossible within cap, conclude inconclusive and state the next decision-relevant sample requirement. No favorable outcome-selected rerun.

**Retained evidence.** Exact routes/configs, all-role call tree, task and trial census, raw counter windows and unallocated totals, admission conditions, candidate artifacts, blind reviews, matched effect intervals, Pareto report and all unsupported cells.

**Owner decisions.** Admitted routes and accounts, per-arm resource envelope, allowed human assistance, declared primary responsiveness measure, practical margins, trial deadline, reuse horizon, and whether a heterogeneous capability advantage warrants its cost. No technology/model winner selected in this report.

**Proposed landing paths.** `experiments/v3/workflow-route-economics/`, `docs/v3/construction/workflow-route-economics/`; consumes DS-11/G-22 and DS-26/G-25, extends EXP-FHAR-01/07/08 evidence rather than replacing it.

### R13 Long horizon recovery through downstream use

**Origin:** Evaluation memo EVAL-05. **Depends on:** R01, R04, R11 and accepted FU store, OS and broker evidence.

**Shared evidence boundary.** R11 and R13 reuse one checkpoint, fault, and evidence-accounting manifest where applicable. First-valid-action and downstream-use endpoints remain distinct; shared restores do not create independent replicate tasks.

**Decision and hypothesis.** Does durable continuation reduce lost work without silently losing intent, authority, evidence, or future usability? Hypothesis: a recovered workflow reaches the same legitimate downstream outcome at lower total recovery/review cost than restart, while preserving explicit uncertainty.

**Prerequisites.** Accepted FU store/OS/broker facts for the chosen fault profiles; working context/route/recovery slice; R01 and qualified end-state oracles. A simulated restart is not physical power-loss evidence. This packet evaluates task consequences of already qualified recovery primitives.

**Competitors.** A: fresh restart from original task and approved source. B: same-route checkpoint continuation. C: checkpointed cross-route continuation where supported. D: declared human-assisted reconstruction under a fixed intervention script and time allowance. Also retain an uninterrupted control. No illegal no-verifier/no-authority baseline.

**Bounded workload.** Twelve multi-stage synthetic/public task graphs in three families: interrupted refactor with dependent feature; evidence-backed technical change with superseded requirement; plugin/tool workflow with late receipt and explicit revocation. Each graph has three predetermined cut points, but use a balanced fractional allocation of cuts/treatments rather than all combinations. Cap the packet at 48 complete trajectories, plus independent downstream verification. Count graph families/tasks, not 48 independent source problems. A later 10–12-hour soak remains the existing acceptance requirement; this packet does not replace it.

**Fault schedule.** Cut after useful work before durable acknowledgment; after compaction before clarification adoption; or after external fixture acceptance before receipt. Pair no-fault and fault trajectories on identical exogenous events. Add one second interruption to the selected repeated-recovery subset. Unknown effects remain unknown until an independent fixture oracle resolves them; do not reward blind replay.

**Ablations.** Structured capsule versus minimal lawful checkpoint; same versus different route; exact accepted directive retained versus a deliberately corrupted synthetic capsule that must refuse; cumulative recovery allowance versus a deliberately reset-per-restart defective ledger in an inert fixture. Hold the underlying durability mechanism fixed for the behavioral comparison.

**Leakage controls.** Future subtasks and late requirement changes are sealed until their scheduled reveal. Recovery branches cannot inspect uninterrupted answers. Test authors see the task contract, not generated patches. Preserve a separate clone for the downstream consumer; candidate authors cannot alter its checks. Match the assistance script; informal human rescue is an intervention to count, not a successful autonomous run.

**Observables.** Original-intent and current-authority retention; final behavior; executable/history/newest-work/resumability as separate states; time and consumption to verified closure; duplicated work/effects; latent regression at the next subtask; human reconstruction time; cumulative recovery allowance; unresolved reservations; stop compliance. Time since process start is not the main endpoint.

**Falsifiers and gate.** A continuation that initially passes but breaks the sealed dependent task; stale directive adoption; ambiguous effect retried; allowance reset on restart; hidden support-model use; or favorable comparison obtained by giving continuation a free prefix. Valid refusal after an unresolvable effect is safety-preserving but not successful productive closure. A path needing an unavailable capability remains an unsupported cell.

**Stop.** Fixed 48-trajectory cap and completion of each admitted downstream check, or hard-floor/budget/invalid-oracle stop. Set a finite downstream-use window before execution. At its end publish unresolved cases explicitly; retain later defects as amendments, without keeping a trial open indefinitely.

**Retained evidence.** Pre-cut/post-cut snapshots, exact fault timing, task/authority/config/capsule epochs, full attempt and resource ancestry, downstream verifier artifacts, interventions, unresolved effects, continuation/restart cost accounting and all failed prefixes.

**Owner decisions.** Which native/upstream/combined routes enter this packet; approved fault profiles and consequences; recovery allowance fraction and unit; intervention budget; task difficulty and downstream-use window. Ten percent is not silently adopted as the recovery cap.

**Proposed landing paths.** `experiments/v3/workflow-recovery-evaluation/`, `docs/v3/construction/workflow-recovery-evaluation/`; feeds G-24/G-27, OR-030/032/034, and the interrupted-refactor/platform acceptance scenario. It does not redo FU-02/FU-04/FU-05.

### R14 Online adaptation versus frozen generalization

**Origin:** Evaluation memo EVAL-04. **Depends on:** R01, R12 and qualified feedback; live exploration separately admitted.

**Decision and hypothesis.** Do routing/context-policy updates learn transferable value, or only exploit repeated benchmark exposure? Hypothesis: a bounded learner improves on future tasks under an unchanged authority filter, with performance and cost attributable to information available before each decision.

**Research basis.** Adaptive holdout reuse can itself cause overfitting; Dwork et al. give methods with explicit guarantees under their setting, not permission to repeatedly inspect an ordinary test set. RouteLLM is useful evidence that preference-trained routing can be studied, but prompt-level model routing is not full agent-workflow recovery or subscription accounting. Off-policy methods such as doubly robust evaluation require defensible behavior-policy/overlap conditions; logged outcomes from a deterministic route cannot reveal outcomes of a route never tried. [Dwork et al., v2](https://arxiv.org/abs/1506.02629v2), [RouteLLM](https://arxiv.org/abs/2406.18665v4), [Dudík et al., v2](https://arxiv.org/abs/1103.4601v2)

**Prerequisites.** R01, admitted telemetry, fixed authority/privacy/verification filters, and R12 task outcomes or a clearly synthetic offline replay. Offline logs can validate update timing; they cannot prove unseen counterfactual performance.

**Competitors.** A: fixed interpretable task-class routing rule. B: frozen learned policy trained only on discovery data. C: bounded online policy updated from prior eligible finalized results. D: hindsight oracle only as a labeled unattainable diagnostic upper bound, never a deployable competitor. Keep allowed routes and verifier floors identical.

**Bounded workload.** One chronological arrival stream of **60 fresh tasks in three blocks of 20**, with two task-family shifts and one announced route-version/capacity shift; no task repeats across blocks. Use a separate, already frozen discovery corpus for initialization. If live trials are authorized, randomize task assignment among A/B/C within admissible task/window strata, with 20 assignments per policy in total. Maintain isolated per-policy state: each policy receives only the permitted finalized feedback from its own assigned tasks, with no common post-initialization feedback pool. A stays rule-based, B stays frozen, and only C updates. Commit arrival times, label delays, assignment schedule constraints, and update checkpoints before starting. This creates one jointly randomized learning history, not 60 independent learner replications.

After the stream, freeze all three final policies and evaluate **12 separately sealed fresh audit tasks under each policy once**, producing 36 audit trajectories and actual task-matched audit contrasts. The total cap is therefore **96 executed trajectories: 60 learning-stream trajectories plus 36 audit trajectories**. Audit results never update any policy. D is calculated only as an explicitly hindsight-selected diagnostic on these 12 fully observed audit tasks; it is unavailable where alternative outcomes were not observed. Discovery-data construction and any repeat learning streams require separate admitted budgets; they are not hidden inside this cap. An offline-only version may check timing and bookkeeping but must report replay/counterfactual limitations.

**Ablations.** No update; update on verification-only versus premature self-reported success; no provider drift feature; unavailable treated explicitly versus an intentionally defective zero-coded implementation; frozen versus reset memory after family change. Defective variants run only on inert/synthetic safety fixtures, not against live authority boundaries.

**Leakage controls.** Prequential order: commit action and policy version before observing that task's result; update only after the permitted label becomes available. Separate discovery, update stream, and sealed final audit set. Ordinary within-task reasoning/retry is allowed if predefined; cross-task prompt/routing/evaluator changes are the adaptation treatment. Do not tune the judge while assessing the learner. Once final-audit results influence design, retire that bank to regression/discovery and obtain a new final bank.

**Observables.** Time-ordered verified closure and costs on the assigned stream; task-matched contrasts only on the 12 frozen-policy audit tasks; regret only where counterfactuals are actually identified; calibration of routing predictions on resolved eligible tasks; unsupported-action rate; policy-change rate; adaptation lag; drift recovery; delayed-label exposure; hard-floor violations. The adaptive learner’s later state depends on earlier assignments and outcomes, so the complete learning history is the dependent experimental unit for claims about the learning procedure. With one such history, adaptation findings are descriptive/conditional; treating the 60 arrivals as iid treatment replicates is invalid. The matched audit can compare the particular final policy snapshots on those tasks but cannot establish the reliability of the learning procedure across histories. Independent repeated streams, separately initialized and randomized under a new preregistration, would be needed for that question. Log assignment/action propensities only for genuinely randomized supported decisions; never fabricate them after the fact.

**Falsifiers and gate.** Gain vanishes on fresh families or final audit; updates use future labels; production filters are weakened; missing feedback is treated as success; or off-policy estimates rely on zero-overlap actions. Each defeats the corresponding claim. If labels arrive too late for meaningful adaptation in the bounded run, conclude that the experiment did not identify online value. Compare learner cost, including exploration and retraining, with the fixed baseline.

**Stop.** End after the fixed third block and the 36 sealed-audit trajectories, subject to the total 96-trajectory and separately admitted resource/time ceilings, or immediately on authority/leakage violation. If a provider epoch changes outside the planned shift, preserve observations, close that epoch, and require a new admission rather than silently continue. No perpetual learner, automatic production promotion, or new periodic monitoring cadence follows.

**Retained evidence.** Time-indexed policy snapshots, immutable update-input manifest, delayed-label queue, exposure ledger, assignment/propensity receipts, overlap diagnostics, all replay assumptions, frozen audit results and known drift events.

**Owner decisions.** Whether any live exploration is allowed; maximum exploration loss/resource use; permitted update frequency; feedback categories; deployment promotion margin; reset/rollback authority. Until decided, C is an offline/synthetic research object only.

**Proposed landing paths.** `experiments/v3/adaptation-evaluation/`, `docs/v3/construction/adaptation-evaluation/`; feeds DS-11/DS-26 and the existing route-learning decision seam, without adding a standing autonomous executive.

## 8 Use results to narrow decisions

### What would reverse the architectural recommendations

**Reverse masking as the preferred comparator** for a named workload if qualified folding or selective access preserves the hard floors and produces a practically meaningful advantage in accepted outcomes, recovery latency, or whole-workflow resources. Keep the within-capacity and over-capacity strata separate. A trained folding model's improvement is a model-policy result; it does not establish a generic wrapper improvement. If a simple mechanism ties within Lucas's practical margins, use that evidence to simplify the qualified stratum rather than install complexity speculatively.

**Reverse dependency-aware reuse** for a transform if dependency completeness cannot be established, validation approaches the cost of rebuilding, or stale/scope-crossing reuse occurs. Restrict its cacheability claim or rebuild. Conversely, actual output-equality evidence can justify retaining downstream artifacts even when an irrelevant source edit changes root bytes. Neither outcome changes the need for current authority at use.

**Favor per-effect mediation** where a consequential target, freshness, or revocation promise requires an actual resource-boundary check and a session envelope cannot supply it. **Favor bounded sessions** where their independently enforced envelope permits useful work and per-effect translation loses required functionality or imposes unnecessary cost. If neither can enforce the task's promise, the cell stays unsupported or unknown. A shared contract succeeds only if it makes this distinction easier to decide.

**Reverse the added evaluator machinery** when a simpler existing recorder reconstructs every task, attempt, cost, and amendment under the same faults, or when an additional oracle/reviewer arm adds no practically useful conditional detection at the admitted effort. Preserve mandatory verification floors. A shared wrong specification surviving several branded reviewers is evidence against treating brand diversity as semantic independence, not evidence that one new oracle is universally sufficient.

**Defer adaptive routing** when labels arrive too late, allowed alternatives have no overlap, route drift invalidates comparison, or fixed policies already match the useful frontier at lower total complexity. One 60-arrival learning history is descriptive evidence about that history. The 12-task matched audit evaluates frozen final policy snapshots; it does not establish the repeatability of the learning procedure. Live exploration, repeated streams, or promotion needs a new bounded decision and authority.

**Reject apparent recovery gains** that disappear after full prefix costs, human reconstruction, missing evidence, unresolved operations, or sealed downstream regressions are counted. A correct hold may establish safety while the productive task remains incomplete. Keep those two outcomes visible. If continuation loses to restart in a stratum, preserve the accepted recovery capability and improve its mechanism; do not waive the release requirement.

### Owner inputs that remain genuinely open

Before admitting a packet, Lucas needs to decide only the choices it consumes:

- For R01 and R04, recorder overhead, total reviewer/human effort, qualified adjudicator, acceptable false-block tradeoff, retention/redaction, and what unavailable monetary attribution prevents claiming
- For R02 and R07, which evidence gaps are hard holds versus refreshable, which transforms can be reused, and age/applicability rules for non-authority facts
- For R03, R05, R08 and R09, acceptable workflow transformations, per-effect versus session boundaries, offline completion, revocation-freshness exposure, Stop behavior, retry ownership, and acceptable opaque-accounting guarantees
- For R10 through R13, eligible routes/accounts, semantic noninferiority and practical benefit margins, fault profiles, deadlines, human intervention budget, reuse horizon, recovery allowance units, and finite downstream-use window
- For R14, whether live exploration is allowed, its resource/loss ceiling, permitted feedback/update timing, and promotion/reset/rollback authority

Do not ask again whether native-only, upstream-only, and combined workflows are required, which ten controls already exist, whether Hermes resumes repository control, or whether frozen M1 bytes may be casually changed. G-06 availability and G-07 Stop/PAUSE choices remain explicit unresolved dependencies where relevant. No consensus, automatic failover, universal compaction policy, language, database, sandbox, vector store, or training method is selected by this report.

### A small evidence record that earns its place

Use the existing claim, gate-evidence, and decision structures. A construction-changing claim needs its exact scope, source/version, competing explanation, required local observable, disqualifier, evidence class, next disposition, and revalidation trigger. Keep a field only if it changes a decision or helps reconstruct one. There is no need for a second decision log, a new review cadence, or backfilled historical probabilities.

Promote a claim from source-checked to locally mapped, then locally observed, then independently accepted for the exact candidate and scope. Defaults or consequential architecture choices still require the existing Owner authority. A document checker establishes structure. A fixture establishes modeled behavior. A finite model establishes its declared bounded property. A physical profile establishes only its measured behavior. None may silently stand in for the next evidence class.

Stop literature collection when credible primary evidence and a discriminating local observation suffice, unless a material contradiction remains. The next useful result should close a decision, expose a counterexample, or identify an irreducible unknown. Another general survey with the same sources has low value.

## Appendix A Experiment crosswalk

The global identifiers are stable within this report. Memo identifiers are retained for traceability; they are not extra experiments.

| Global ID | Original memo ID | Topic |
|---|---|---|
| R01 | Evaluation EVAL-01 | Denominator and recorder metrology |
| R02 | Context E1 | Actionable control and decision provenance |
| R03 | Composition HC-01 | Semantic mapping and workflow closure |
| R04 | Evaluation EVAL-02 | Oracle custody and common-mode defects |
| R05 | Composition HC-02 | Two-hop attenuation and returned authority |
| R06 | Context E3 | Compaction arbitration |
| R07 | Context E4 | Dependency-safe reuse |
| R08 | Composition HC-03 | Joined lifecycle and accounting ownership |
| R09 | Composition HC-04 | Causal-work versus local-process coverage |
| R10 | Context E2 | Reversible masking, folding and selective access |
| R11 | Context E5 | Cold restore and complete-workflow economics |
| R12 | Evaluation EVAL-03 | Route-complete economics and availability |
| R13 | Evaluation EVAL-05 | Recovery through downstream use |
| R14 | Evaluation EVAL-04 | Online adaptation and frozen audit |

Audit LP-0 through LP-6 retain their existing meanings: authority/evidence reconciliation; model/vector bridge; native OS primitives; canonical writer; runtime comparison; broker chaos; one inert composed seam. These are predecessor or parallel construction packets, not renumbered R experiments. R02/R03/R06/R08/R09 supply sharper assertions and counterexamples for the composed seam; R01/R04 supply measurement and oracle controls. The FU reports remain FU01 through FU05.

## Appendix B Evidence scope and source limitations

### What is established and what is proposed

The repository basis is the pinned snapshot shown on the cover. It supplies observed source shapes and records of earlier experiments; historical run outcomes remain repository-reported unless a later local packet independently reproduces them. This report contains no newly passed target tests, model calls, performance measurements, platform qualifications, route eligibility/entitlement checks, physical fault trials, or production changes. All benefits, quality margins, economic wins, and integrated correctness claims in the experiment program remain unmeasured.

Public sources were inspected on 2 October 2026. Versioned papers and commit-pinned source files identify precise editions. Official documentation and main/latest branches are dated observations and may change. Before real qualification, archive the relevant source text/schema and pin the actual engine, adapter, interface, binary, configuration, and platform. A source publication or retrieval date does not establish the user's installed version.

### Primary source families and limits

**Context methods.** The report uses the pinned Complexity Trap v3, AgentFold v1, and RLMs v1 comparisons for mechanisms and counterexamples, without importing their measured gains into Recursion. AgentFold is a trained model-policy design. MemGPT already establishes prior art for tiered external memory; a portable, authority-aware continuation contract is a desired contribution, not proven novelty. LongMemEval offers information-extraction, temporal/update, and abstention categories; its implementation has a model-based QA evaluator and distinguishes retrieval from generation. It is a secondary rubric, not a tool-effect or authority-recovery oracle. [MemGPT v2](https://arxiv.org/abs/2310.08560v2), [LongMemEval v2](https://arxiv.org/abs/2410.10813v2), [LongMemEval implementation](https://github.com/xiaowu0162/LongMemEval)

**Composition theory and protocols.** ACP, MCP, A2A, Codex, Claude, OpenCode, Pi, WIT, and provider API pages are interface observations, not installed-product certification. Beta or experimental features retain those limits. Lange and Yoshida's bounded safety/exhaustivity analysis motivates lifecycle and progress checks under explicit assumptions; it does not prove Recursion's crash, network, authority, or adversarial model. Macaroons, OAuth RFCs, Miller's limited indexed figure, and UCAN's release candidate are conceptual comparators, not selected security mechanisms. [Lange and Yoshida v2](https://arxiv.org/html/1901.09606v2)

**Evaluation and economics.** The SWE-Bench Pro audit and pinned SWE-bench/Tau/Inspect sources motivate task/scorer/recorder qualification, not universal benchmark rejection. Public agent, infrastructure, and judge studies transfer concerns and methods, not local effect sizes. Tau's pass^k reliability differs from best-of-k pass@k; selecting a successful artifact requires a real charged selection policy. METR's v4 note is an author-list correction, not a fresh experiment or current model ranking. [Tau-bench paper](https://arxiv.org/abs/2406.12045)

**Adaptation.** Dwork et al. establish why adaptive holdout reuse needs explicit controls. RouteLLM studies preference-trained prompt routing; it does not establish full agent-workflow economics. Doubly robust policy evaluation requires defensible behavior-policy and overlap conditions; deterministic logs cannot identify unobserved alternative-route outcomes. This program claims no formal generalization guarantee for its proposed sealed bank and no counterfactual label that was not observed or identified. [Dwork et al. v2](https://arxiv.org/abs/1506.02629v2), [RouteLLM v4](https://arxiv.org/abs/2406.18665v4), [Dudík et al. v2](https://arxiv.org/abs/1103.4601v2)

### Practical completion criterion

The immediate research succeeds when a bounded local packet can answer a real choice with reconstructable evidence: the task and attempt population is intact, the oracle survives independent challenge, useful positive behavior progresses, known adverse behavior is rejected, uncertainty is explicit, and the result is tied to the exact candidate. Broader implementation and release decisions follow only after their own prerequisites and Owner disposition.
