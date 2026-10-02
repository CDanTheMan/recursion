# R G local conformance and port cost handoffs

## Status and admission boundary

**Every handoff in this file is UNEXECUTED.** This is a detailed research deliverable, not authorization to run a parser, test, host, plugin, installer, model, provider, remote service or credential flow. No executable adapter or test runner is included. The language-independent examples are inert fixture descriptions.

Parent goal: `goal-recursion-v3-harness-orchestrator`. Source baseline: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. R-A contract is the current-branch committed proposal, not a ratified schema. D-019 comprehensive/opt-in scope and D-033 unproved port-economy hypothesis remain intact.

Before any future run, the Owner must admit the exact candidate implementation, allowed paths, disposable environment, immutable source/artifact pins, finite budget, stop conditions and independent verifier. Separate data-only checks, synthetic semantic simulations and real-host enforcement qualification. A successful lower level cannot be reported as a higher-level pass. A fresh permission is needed for any host/plugin/install action absent from that future admission.

No live credentials, user files, provider endpoints or externally routable destinations enter fixtures. Use public synthetic data, inert logical handles, fake credential sentinels and a deterministic clock. Any attempt to call a provider, fetch/install a dependency, authenticate or send externally stops the run. If a host cannot initialize under those conditions, classify that profile as unsupported for provider-free testing rather than turning on a service.

## Evidence levels

| Level | Permitted only after future admission | What a pass can mean | What it cannot mean |
|---|---|---|---|
| L0 source inventory | Read exact package/schema/license bytes, without imports or execution | Pin correspondence and a complete inert input inventory | Runtime equivalence or legal clearance |
| L1 data-only translation | Parse synthetic descriptors and produce deterministic records | Correct declared mapping and rejection behavior | Arbitrary plugin behavior, inertness after actual loading |
| L2 semantic simulation | Exercise pure candidate reducers/codecs against independently authored traces | Bounded canonical behavior over fixture alphabet | Real host containment, real credential separation |
| L3 exact-host provider-free qualification | Separately approved target host with synthetic plugins and calibrated no-network/no-provider observers | Named host/OS/version behavior under observed fixture conditions | Universal ecosystem support, live service entitlement, model performance |

These levels do not select a runtime, framework, sandbox or host implementation. A future packet must name its exact implementation and justify that choice separately.

## Frozen corpus and counting units

The primary planned corpus is 8 semantic fixtures × 6 ecosystem profiles = 48 assignment units. The profiles are Cordis, OpenCode V1, OpenCode V2 server with explicitly separate optional CLI realization, Goose external MCP configuration, MCP 2026-07-28, and VS Code. Eight legacy MCP 2025-11-25 assignments are a separate compatibility stratum. They must not inflate the number of independently portable ecosystems. Additional Agent Plugins/OpenAI/Cursor package differences are targeted subcases of F05/F08, not extra successful plugins.

Every assignment begins with its canonical scenario specification, source-shaped descriptor, required/optional contribution map and frozen expected result. Unsupported profiles remain in the 48-assignment denominator. The unknown native/port cost of an unsupported case is not assigned zero.

One fixture may have many assertions or retries. Report those counts for coverage but do not use them as independent statistical samples. Multiple hosts realized from one shared core also form a cluster.

## Synthetic semantic fixtures

### F01 Pure typed transform

Input: `{"text":"alpha","mode":"upper"}`. Allowed alphabet: ASCII a–z, length 0–32. Expected output: `{"text":"ALPHA","changes":5}`. Empty string produces `{"text":"","changes":0}`. Non-ASCII or length 33 fails input validation before dispatch. Optional description metadata must not change canonical output.

Required semantics: exact input/output schema; deterministic output; pure effect class; stable contribution identity; no provider/network/process/file access; explicit completion versus acceptance. The values 32 and 33 are fixture boundaries, not product defaults.

Source shapes to provide as inert data: Cordis tool definition with output schema; V1 tool/hook map; V2 ID/setup-registration description; Goose extension/config plus MCP descriptor; current MCP tools/list/result transcript; VS Code manifest command/tool plus implementation-binding description. The source descriptions must say where static information is unavailable rather than fake a source manifest.

### F02 Logical resource read and staged artifact

Logical source `goal://fixture-A/input` contains exactly the five UTF-8 bytes `alpha`. Grant permits reading that handle and proposing an artifact at `goal://fixture-A/output`; it permits no filesystem path discovery or external write. Expected result contains uppercase bytes and their digest, with write state `proposed`, not published.

Variants: wrong goal; same basename under a different root; symlink/junction/reparse escape; case collision; path alias; network-shaped URI; expired grant; resource version change between resolve and dispatch. Required outcome is refusal or explicit stale-resource revalidation before a new effect. Do not let `../`, wildcard interpretation or transport URL matching stand in for semantic containment.

### F03 Ordered interceptors and final authorization

Source declares three stages: annotate the candidate, policy guard, execute. A countervariant short-circuits before `next`; another modifies the resource after a preliminary permission check. Independent oracle expects an ordered trace `candidate → transformed-candidate → final-admission → effect → result` only when the final candidate is permitted. Denied path has no effect entry.

The target cannot replace a required blocking hook with an after-event notification. Cordis around-middleware and monotonic post-waterfall guards, V1 before hooks and V2 domain hooks have separate source profile definitions. Include callback order permutation, duplicate registration, reentrant request, thrown callback and asynchronous late callback. Pure event observers receive only their allowed fields.

### F04 Optional presentation and required approval UI

Variant A: required F01 tool plus optional panel showing its result. A host without the panel records `partial`, one explicit optional `HOST_UI_UNAVAILABLE` loss and preserved tool output. Variant B: that panel is the sole required approval interaction before a synthetic write. Without an equivalent approved approval binding, import is incompatible and no effect is attempted.

No automatic conversion of a required approval to a log line, natural-language prompt, toast or pre-granted “allow.” Output evidence must identify which rendering/interaction binding produced a response and the exact pending interaction/effect it covers.

### F05 Dependency resolution and inert disabled state

Input describes one required service, one optional service, a disabled installation, a dynamic config expression, an unresolved environment reference and a source auto-install setting. Expected L1 output is an inventory with typed blockers, zero effective grants and no activation. No code must be evaluated to fill missing fields.

L3 variants, only under later admission: absent versus installed-disabled; 0/10/100 disabled descriptions; configuration reload; package cache hit/miss; source `enabled=true`; default-enabled marketplace metadata; wildcard re-enable; dependency cycle; duplicate IDs. The no-effect requirement covers module evaluation, subprocess, network, install, credential lookup and provider use. Disk/CPU enumeration cost is measured separately, not called zero.

### F06 Authority and privacy adversaries

Finite oracle universe: principals A/B; goals A/B; resources input/output/forbidden; operations read/propose/publish; labels public/private; recipients none/allowed/forbidden; budgets 0/1/2 synthetic units; epochs 1/2. Construct all explicitly assigned positive/negative relations before candidate implementation. Cardinalities are fixture choices only.

Variants: grant injection in manifest/extensions; sibling-grant union; dependency implies permission; forged source identity; imported allow overrides canonical deny; transform changes destination; private data under public output; env/header credential sentinel; redirect to forbidden origin; source timeout treated as unlimited budget; reservation double refund; child depth exceeded; source-enabled inherited as activation.

Expected outcome is intersection with every applicable boundary and a typed refusal at the first unfulfilled required condition, with no new effect. Unknown bound/label/enforcement is represented as unknown and refused. Security false negatives are disqualifying even if the overall failure rate is low.

### F07 Output and evidence fidelity

Canonical successful result is a structured F01 output plus a source-boundary record. Variants include missing output schema, altered result bytes, extra content block, resource link with unrelated authority, synthetic image/audio metadata, tool error inside successful RPC, forged verifier field, source completion mislabeled accepted, unknown accounting and redacted evidence.

Expected output preserves independent dimensions: wire/RPC completion; tool outcome; effect settlement; verification acceptance. Optional unavailable content carries a loss only if the workflow explicitly allowed it. If required output or evidence is unavailable, status is unsupported/unverified, never success by text fallback.

### F08 Version drift and interrupted operation

Freeze source/canonical/binding/host/protocol version tuple and previous candidate digests. Change one at a time: V1 source to V2 API; current MCP to legacy; package schema to unrecognized epoch; output schema revision; host SDK callback timing; placeholder syntax; dependency payload; contribution identity. Expected result is exact profile selection or a typed incompatibility, never silent fallback.

Interrupt at admission, dispatch, reply loss, cancellation, reload and late callback. New effects require current epoch; already-admitted effects remain unsettled until evidence resolves them. Current MCP task-handle and MRTR continuations have separate synthetic traces below. All provider helpers remain unavailable.

## Individual handoff records

### RG T00 Pin and profile correspondence

Handoff ID: RG-T00

**Status:** UNEXECUTED · **Level:** L0 · **Questions:** Q01, Q03, Q07, Q10

Inputs: immutable candidate source/package inventory, API schema/document revision, host executable digest and license/notice inventory. Method: map each asserted feature to an exact public source or versioned contract and, later, the artifact being admitted. Record unresolvable mutable-document correspondence as unknown. For proprietary internals, limit the claim to documented interface behavior; do not invent source evidence.

Expected artifact: per-profile identity tuple and explicit unmatched claims. Failure: any row claims an exact supported build from an unversioned documentation page, or inherits an unverified old source pin. Stop before L3 until correspondence needed for the asserted behavior is established.

Competitor: use the latest documentation and any installed host. Falsifier: profile label survives a source/artifact mismatch. Non-proof: source correspondence is not runtime conformance.

### RG T01 Complete static translation and round trip

Handoff ID: RG-T01

**Status:** UNEXECUTED · **Level:** L1 · **Questions:** Q01, Q02, Q04, Q05

Inputs: F01/F05/F08 descriptor variants, exact input bytes, separate golden TranslationRecords. For every source field/contribution, compare direct/mechanical/annotation/none classification, target pointer, rule revision, unknown/loss disposition and candidate digest. Preserve source bytes for recovery.

Oracle: identical candidate for identical bytes/profile; every required source contribution is realized or explicitly blocked; zero effective grants; every declared reversible mapping round-trips under its stated normalization. Fields with noninvertible defaults retain original bytes and `partial/not-invertible` status.

Failure: silent omission, execution to enumerate, unknown as empty, schema fetch, grant creation, nondeterminism, or global reversible label hiding a lossy mapping. Evidence: input/output digests, field checklist and expected/actual diff, not a host success message.

Competitor: native loading to discover behavior. Non-proof: parsing does not establish executable behavior.

### RG T02 Capability graph and binding attenuation

Handoff ID: RG-T02

**Status:** UNEXECUTED · **Level:** L2, then independently L3 · **Questions:** Q02, Q05, Q08, Q12

Inputs: F06 finite grant relations and F02 logical resources. Independently enumerate permitted relation tuples; compare each candidate admission and effect. Exercise grant injection, sibling union, dependency activation and post-transform resource changes.

Oracle: admitted relation is contained in every boundary; budgets use reservation accounting rather than set union. Foreign and translator records never generate `permits` edges. Mutation after check must force revalidation before effect.

Failure: one out-of-bound admitted effect, unknown enforcement accepted, stale grant or source default acting as authorization. L2 pass remains unqualified until L3 observers show target effects obey the same relation.

Competitor: translate upstream allow/deny strings into grants. Non-proof: finite relations do not establish all filesystem alias cases or actual containment.

### RG T03 Semantic phase and cleanup ownership

Handoff ID: RG-T03

**Status:** UNEXECUTED · **Level:** L2/L3 · **Questions:** Q01, Q02, Q04, Q10

Inputs: F03 and the source-specific phase/lifecycle definitions. Inject a cancellation before/after each callback, change callback order, trigger short-circuit and run a late completion after unload. Oracle expects exact declared phase, scope, failure and cleanup ordering. Ownership includes child callbacks and resources, not just a disposer being called.

Failure: required guard runs after effect, callback widens destination after final authorization, disposed instance emits a new effect, or drain completes while owned work remains active. Already-dispatched effects must retain `settling/unknown` until resolved.

Competitor: normalize all hooks to before/after notification. Non-proof: deterministic disposal ordering does not roll back an external effect.

### RG T04 Explicit partial import and required losses

Handoff ID: RG-T04

**Status:** UNEXECUTED · **Level:** L1/L2 · **Questions:** Q04, Q06, Q08

Inputs: F04 variants plus unsupported transport/output dependency. Oracle: availability, translation, installation, activation and qualification axes remain separate; required loss blocks admission; optional loss is visible and linked to its permitted scenario policy.

Exercise each existing incompatibility response. `no_action` returns no-effect receipt without import, notification, repair or reroute. Notify/recommend modes may emit only the configured permitted diagnostic and never activate their suggestion.

Failure: global supported boolean conceals missing approval, source capability absence deletes the product requirement, or an incompatible request reports execution attempted. Competitor: silent omission. Non-proof: an explicit loss does not validate an alternative behavior.

### RG T05 Disabled discovery and observer calibration

Handoff ID: RG-T05

**Status:** UNEXECUTED · **Level:** L3 only after separate admission · **Questions:** Q01, Q05, Q06, Q09

Inputs: F05 cases and disposable synthetic plugin artifacts. Calibrate each observer with a permitted positive control attempting module evaluation, process start, install, network, credential lookup and provider dispatch against fail-fast synthetic channels. A missed control invalidates the corresponding absence claim.

Compare absent/disabled/enabled-but-not-activated states and 0/10/100 descriptions. Expected disabled path does not load/import plugin code or trigger any disallowed channel. Record enumeration disk/CPU/memory separately with baseline uncertainty; never equate no effects to no computational cost.

Failure: any forbidden attempt, hidden startup install/telemetry/provider helper, missing calibrated observer, or unobserved state change. Stop rather than installing a monitoring tool without separate authority.

Competitor: inspect only the visible tool list. Non-proof: visibility alone or one quiet trace does not establish inertness for every version.

### RG T06 Version and package mismatch

Handoff ID: RG-T06

**Status:** UNEXECUTED · **Level:** L1/L2, later L3 · **Questions:** Q01, Q03, Q07, Q11

Inputs: F08 V1/V2 descriptors and two package formats. Expected V1-to-V2 config transform never labels V1 implementation compatible; exact API migration obligations remain. For Agent Plugins, test the same inert MCP args with `${PLUGIN_ROOT}`, `${PLUGIN_DATA}` and the documented Cursor-specific variable. Compare canonical resolved logical values in the target-specific profile; do not expand the actual environment.

Failure: a declared common-format path changes behavior silently, a host variable becomes an unrestricted path, or unsupported version is treated as latest. Record missing implementation correspondence separately from a failed fixture.

Competitor: infer compatibility from file names and semver. Non-proof: a successful package transform does not prove plugin behavior across the two products.

### RG T07 Credential and privacy translation

Handoff ID: RG-T07

**Status:** UNEXECUTED · **Level:** L2/L3 · **Questions:** Q02, Q04, Q05, Q12

Inputs: fake secret sentinel, privacy labels, header/body fields and forbidden-origin redirect descriptors. The expected translation contains symbolic credential requirements and provenance only. Any actual secret bytes in canonical manifests, model context, logs or cross-scope cache is a failure.

Include HTTP audience-specific handles, stdio environment requirements, OS-auth-store requests, body-to-header mirroring, environment inheritance and optional source auto-scope selection. Distinguish metadata parsing from credential retrieval. A profile that cannot prevent ambient credential visibility must remain incompatible with a strong non-access claim.

Competitor: copy source env/headers into a common launch configuration. Non-proof: fake-sentinel containment does not qualify real credentials or grant legal use rights.

### RG T08 Budget accounting and evidence adoption

Handoff ID: RG-T08

**Status:** UNEXECUTED · **Level:** L2/L3 · **Questions:** Q05, Q09, Q12

Inputs: F06/F07, two child reservations sharing a parent, unknown meter, duplicate settlement, retry and helper attempt. Oracle counts all known resource use exactly once, keeps missing usage null with reason, does not release unresolved reservations merely on cancel, and rejects source claims of independent acceptance.

Failure: oversubscription, double refund, orphaned retry/helper, unknown-as-zero, changed host activates metered route, or successful RPC with tool error becomes goal success. Evidence includes attempt lineage and observation provenance, not only a cost total.

Competitor: total only successful calls. Non-proof: provider-free counters do not measure real subscription burden.

### RG T09 MCP current and legacy era separation

Handoff ID: RG-T09

**Status:** UNEXECUTED · **Level:** L1/L2, later L3 · **Questions:** Q01, Q02, Q07, Q08

Inputs: two inert wire transcripts conforming to the [canonical era facts](../protocol-edges/report.md#era-and-identity). Freeze the admitted era before dispatch; deliberately inject the documented modern-version-error case and test that no unadmitted fallback occurs.

Oracle: self-reported server/client names are descriptive only; authentication binding and protocol capability remain separate. No connection-state assumption supplies missing request capabilities in the modern profile. Legacy features are available only in the legacy profile.

Failure: session abstraction name chooses wire semantics, modern/legacy transcripts get mixed, or any compatibility fallback widens permissions. Competitor: one generic `MCP` boolean. Non-proof: correct transcript normalization does not authenticate a real server.

### RG T10 MCP MRTR and Tasks are separate continuations

Handoff ID: RG-T10

**Status:** UNEXECUTED · **Level:** L2, later L3 · **Questions:** Q04, Q05, Q07, Q08

Inputs: separate synthetic traces using the complete [MRTR](../protocol-edges/report.md#multi-round-trip-requests) and [Tasks](../protocol-edges/report.md#cancellation-and-asynchronous-tasks) fact inventories. Include every enumerated transition and failure case; pin the exact wire revision before execution.

Oracle: apply the [canonical wire rules](../protocol-edges/report.md#multi-round-trip-requests) while holding logical operation/deadline/reservation and effect parameters constant. Treat all returned state as non-authorizing. Route each continuation through its admitted profile; a profile mismatch must fail before another effect.

Cross-scope or changed-parameter continuation is refused. Cancel acknowledgement does not settle the effect. Expired task state preserves unknown outcome/accounting. A completed protocol task carrying a tool error does not produce verified success. Concurrent equal task strings from different verified peers remain distinct.

Failure: duplicate effect, renewed budget/deadline, scope-laundered approval, automatic provider helper, or collapsed status. Competitor: generic SDK-managed retry. Non-proof: bridge bookkeeping cannot guarantee remote idempotence or cooperation.

### RG T11 Reused capability across hosts

Handoff ID: RG-T11

**Status:** UNEXECUTED · **Level:** L2/L3 · **Questions:** Q03, Q07, Q10, Q11

Inputs: F01/F02/F07 shared semantic implementation and separate binding records for at least two meaningfully different profiles. Freeze common asset/source digest and mark any host-specific code and behavior. Native comparators implement identical required behavior and optional-loss policy.

Oracle: same required outputs, admitted relation and evidence for the same canonical input; each host's extra behavior is either inert or explicitly authorized. Per-principal/goal/compartment/revision mutable state cannot leak across bindings. Count total and marginal host costs.

Failure: required semantic divergence, duplicated shared logic hidden as glue, extra ambient authority, shared-state leak or higher accepted total cost than separate native plugins. Competitor: independent native plugins with common tests/docs. Non-proof: two accepted bindings do not imply all harnesses work.

### RG T12 Supply and rights evidence boundary

Handoff ID: RG-T12

**Status:** UNEXECUTED · **Level:** L0/L1 · **Questions:** Q03, Q04, Q10

Inputs: synthetic package inventories with root license, separately licensed dependency, proprietary asset, missing notice, source-only file and Marketplace-acquired payload. Expected output distinguishes source license, dependency closure, asset rights, service terms and distribution provenance.

No legal interpretation is delegated to the translator. Missing rights evidence is a distribution blocker; no imported payload is relabeled Apache-2.0 because Recursion's own work uses that license. Emit a bounded evidence packet for the separate R-H/Owner/counsel process, without contacting anyone.

Failure: root MIT/Apache label clears all dependencies/assets or marketplace access is assumed from code compatibility. Competitor: one license field per ecosystem. Non-proof: a complete inventory does not itself clear use/distribution.

### RG T13 OS resource mapping and failure recovery

Handoff ID: RG-T13

**Status:** UNEXECUTED · **Level:** L3 under separate OS-specific admission · **Questions:** Q02, Q05, Q09, Q10

Inputs: F02/F08 with approved D-028 profiles and disposable synthetic storage. Qualify Windows x64 floors, Linux cgroup/filesystem floors and dev/test-only WSL cases separately; do not use one host's success for another. Canonical store scope remains local NTFS/ext4.

Exercise path case, separators, symlink/junction/reparse aliases, newline/framing, environment/reference handling, lost response, reload and stale epoch. Abrupt reset or destructive checks need fresh disposable-target permission; this handoff does not authorize them.

Oracle: stable logical identity, no alias-based scope escape, no duplicate effect after lost response, preserved unresolved outcome and revision-bound evidence. Competitor: OS-neutral path string substitution. Non-proof: no physical-power-loss or universal filesystem guarantee follows.

### RG T14 Drift and maintenance challenge

Handoff ID: RG-T14

**Status:** UNEXECUTED · **Level:** L1/L2/L3 as separately admitted · **Questions:** Q03, Q07, Q09, Q11, Q12

Inputs: a preregistered synthetic upstream change after initial acceptance: renamed field; changed default; new required callback; output schema change; permission-order change; removed lifecycle hook. The same change burden is applied to port and native comparator where their dependencies require it; disclose if the baseline has no upstream dependency rather than pretending equal maintenance.

Oracle: old acceptance never attaches to new source/profile bytes automatically; dependent realization quarantines or requalifies; newest authorized work is retained; review and repair costs counted. Failure: stale qualification, semantic loss masked by compatibility version, or total cost advantage disappears.

Competitor: update by version range without semantic requalification. Non-proof: one drift challenge does not estimate an ecosystem's future release rate.

### RG T15 Paired total cost and predictive validity

Handoff ID: RG-T15

**Status:** UNEXECUTED · **Level:** experiment accounting only after separately approved construction/qualification · **Questions:** Q03, Q09, Q10, Q11, Q12

Preregister the 48 assignment IDs, fixture clusters, implementer experience, order allocation, independent reviewer, scope, budgets, stop reasons, quality threshold and interval method before work. Use separate implementers or counterbalanced order to limit learning advantage; disclose cross-contamination and experience differences. Do not use an LLM grader as the oracle.

For each assignment, record stage-level active labor, elapsed delay, handwritten/generated/generator LOC, unique APIs, semantic rules, failures, repairs and accepted required scenarios. Keep every assigned case, including no-port and censored attempts. Native and port realize the same behavior and evidence requirements. Shared infrastructure cost is reported both once and amortized at observed scale.

Primary outcomes are critical failures and independently accepted equivalence; cost is meaningful at matched quality. Report raw paired differences, median/IQR, accepted/assigned counts and total incurred cost/accepted count. Zero accepted denominator means undefined. No current hour estimate is supplied; prior feasible effort interval is nonnegative and unbounded above.

Preregister a cluster-aware uncertainty procedure and decision margin before looking at results. Intervals crossing the margin are inconclusive. Any fitted R-A complexity model uses a small frozen feature set and held-out whole fixture families/porters, compared with constant/ecosystem baselines. Too few independent units means descriptive results only. Check critical-failure false negatives explicitly.

Falsifier: port total cost exceeds matched native rewrite, apparent gains depend on dropping failed assignments/rights work/generator costs, or structural predictors fail the simple held-out baseline. Competitor: compare only glue LOC or completed ports. Non-proof: synthetic economy does not demonstrate natural-plugin ecosystem savings.

### RG T16 Eligible ecosystem census

Handoff ID: RG-T16

**Status:** UNEXECUTED · **Level:** L0 read-only research under a separate bounded packet · **Questions:** Q01, Q03, Q10, Q11

Freeze public discovery sources, time window and selection rules. De-duplicate by artifact/source lineage, classify maintained version compatibility, inspect source/license/dependency evidence, and stratify by contribution family and host coupling. Record missing/inaccessible/proprietary cases rather than remove them quietly. Count candidates, inspectable candidates, rights-evidence-complete candidates and later independently accepted ports separately.

Publish counts with dates and confidence/coverage limitations. Do not infer population from stars, downloads, search-result totals or the number of entries in a marketing directory. A source directory is a sampling frame, not a verified universe.

Falsifier: the apparent large reusable population vanishes under compatibility/rights/required-semantics screening, or selection bias makes the useful-port estimate indeterminate. Competitor: rank by directory size. Non-proof: a census does not establish port cost or future adoption.

## Required artifacts from a future admitted run

- Preregistration: source commit, exact candidate/host/profile/OS pins, fixture corpus digest, authorization boundary, budgets, stop condition, oracle/reviewer identities and interval method
- Assignment ledger: 48 primary assignments plus separately marked compatibility/additional strata; every rejected, unsupported and censored item retained
- Translation evidence: immutable source inventories, MappingEntry/LossRecord/ContributionRealization records, expected and actual normalized data
- Canonical trace: stable operation/attempt/effect IDs, current authority epoch, exact output digest, refusal, accounting and settlement observations
- Observer calibration: positive controls and bounded negative traces for every no-effect/containment claim
- Cost ledger: stage labor, raw LOC categories, API/rule counts, conformance failures and repairs, shared-tool allocation, maintenance challenge
- Independent rerun: exact candidate and corpus, disagreements retained, final disposition separate from implementation self-report

No report may collapse UNEXECUTED, unsupported, rejected, unverified and independently accepted into the same status. Missing evidence stays a named blocker.

## Unknown closure map

| Unknown | Concrete closure attempt | If the attempt cannot close it |
|---|---|---|
| Exact mutable-doc to executable correspondence | T00 source/artifact inventory | Remain documentation-only; no exact-host qualification |
| Full static contribution inventory for executable plugins | T01 plus authored sidecar review | Dynamic unresolved contribution blocks required scenario |
| Cleanup and strong containment | T03, T05, T07, T13 | Remain unqualified or policy-only where allowed; no security claim |
| MCP era/Tasks/MRTR behavior for a binding | T09/T10 | Explicit incompatible profile; no generic fallback |
| Cross-host accepted equivalence | T11 | Separate bindings/native implementation or no port |
| Cost and real leverage | T15; T16 for population generalization | No finite savings claim; D-033 remains unproved |
| Rights and acquired assets | T12 evidence plus separate Owner/counsel determination | Distribution blocked; test cannot substitute for rights clearance |
| Interface maintenance stability | T14 and later version-pinned evidence | No stability claim, reevaluate each profile revision |

## Relationship to the protocol boundary supplement

The separate MCP bridge supplement's current/legacy, MRTR, Tasks, retry and settlement distinctions are carried into T09/T10. Its protocol fault fixtures can share synthetic transcripts and independent oracles with this lane, while their cost/acceptance accounting remains explicit. Reusing the fixture description does not count as a second independent runtime observation. The [canonical Tasks facts](../protocol-edges/report.md#cancellation-and-asynchronous-tasks) bound every such case.
