# Recursion counsel questions for installed CLI orchestration

**R-H research return · 2026-10-02 UTC · evidence and questions only**

This packet extends the committed R-C licensing packet with the exact D-030 operating mode: a local orchestrator calls the user's installed, user-authenticated harness, consumes its structured output, and asks that harness to perform native delegation. It examines the legal questions created by that arrangement without deciding them. **This is legal-risk research, not legal advice. No route is cleared, no practice is condemned, and G-32 remains open.**

The useful result is a configuration-specific question set, rather than a route-wide yes or no. Could counsel distinguish **credential custody, initiation of use, output processing, subscription allocation and distribution** as separate questions? A technical absence of credential custody does not itself answer the other four questions. That is a proposed analytical separation for counsel, not a legal finding.

## 1 Authority and research result

### 1.1 Which facts and decisions are fixed

The authoritative project snapshot is commit **73d70505b8c266fbb08d820d304ebd2e68ac7f1b**. This research read CONTROL_PLANE, ANCHOR, D-017 through D-033, the active v3 goal, the R-H brief, the current R-A–R-D synthesis and reconciliation, the R-C report/checklist/source registers, relevant R-A/R-B/R-D contract and accounting sections, and GAPS/DS-33. Their private contents were not sent in public searches.

- D-017 and D-032 establish the v3-only product and active parent goal. Hermes is an optional integration, not an executive authority
- D-019's comprehensive build with opt-in delivery stands. This packet does not propose a smaller release contract
- D-021 and D-029 establish the intended no-credential-intermediation posture and the operator-provisioned trusted launch boundary. The stronger non-access property is unqualified until separately evidenced
- D-022 supplies **Aggressive / Full / Lazy**, plus **checkpoint / interrupt / drain**. A killed PID or closed socket is not external rollback
- D-023's Codex-first qualification sequence stands; it is neither current qualification nor service authorization
- D-026's Apache-2.0 direction stands. This packet does not choose a different project license or claim the release artifact already implements it
- D-027 authorizes preparing a packet. Lucas engages counsel; there is no engagement, spend, legal commitment or external sharing here
- D-030 accepts harness-native driving and fan-out subject to counsel. It is not permission for this research to invoke a target
- D-031 excludes vendor-sabotage positioning. Neither lower token counts nor a licensing comparison establishes vendor intent
- D-028 platform floors and D-033's unmeasured porting hypothesis remain unchanged

Some older entry-point wording still refers to a Hermes constitution or a v2 goal. Under CONTROL_PLANE precedence, those are historical source drift, not alternative current authority. No source file was edited.

### 1.2 What should counsel resolve first

1. **Does the precise caller qualify differently from a third-party credential or usage intermediary?** Claude product guidance explicitly separates certain unmodified, end-user-authenticated binary cases from third-party credential/routing cases; Gemini and Antigravity use different wording about third-party access. Can that difference be applied to the actual process diagram rather than generalized across vendors? Evidence: S01, S16, S34; H01–H04 below
2. **Is the relevant edition local/open-source, commercial, hosted, or several of these?** Use the [canonical applicability note](#codex-app-server-legal-facts). Which facts determine the classification of a paid local app, a freely distributed client with paid support, and an operator-managed remote node? Evidence: S08; H05
3. **What reconciles a documented automation interface with broader contractual restrictions?** Compare the [headless facts](../rf/report.md#cursor-headless-facts), [auth facts](../rf/report.md#cursor-auth-facts) and S12 AUP wording. Does the exact agreement supply an exception or require written clarification? Evidence: S11–S14; H06
4. **Does harness-native fan-out remain within the particular account's permitted use?** Which concurrency, duration, human-presence, request, pool, retry and billing conditions apply? A harness feature is a technical capability, not an answer to those questions. Evidence: S02, S07, S12, S18, S20, S23, S28, S30; H07–H10
5. **What may the output consumer retain or redisplay?** Does the JSON contain ordinary model output, third-party content, grounded results, notices, secrets or personal data, and do they need different handling? Evidence: S21, S27; H11

### 1.3 Evidence classes and limits

**Source-documented** means a public primary source or committed project document says the stated thing. **Locally observed** here means only reading the supplied snapshot or checking the generated packet, not running the product. **Inferred** identifies proposed factual decomposition, review priority, schema or handoff design. **Unknown** means the researched public record or supplied facts do not answer applicability; it never means permitted, forbidden, unrestricted or zero.

No target CLI, harness, model, provider API, account, credential, live host, benchmark, test suite, installer or provider configuration was used. No Work, Codex or cloud task was created. Ordinary public-document retrieval is the only external research performed. Target behavior, billing, isolation, availability and stop semantics remain unmeasured.

The public appendix contains 38 dated primary sources and short checked excerpts. Live documents are pinned by URL, retrieval date and section/version, not a claim of permanent immutability. A source's displayed date inherited from R-C is explicitly identified as inherited where the current excerpt did not re-display it. The immutable Pi README is a commit pin; R-C's separate root-license pins retain their inherited status.

## 2 The factual operating mode for counsel

### 2.1 Which boundary is actually under review

Could counsel review the following bounded scenario, with each premise marked **intended and unverified**, rather than assume it describes a running build?

1. The operator installs and authenticates the vendor's unmodified CLI through the vendor's own flow outside Recursion's readable domain
2. Recursion submits a scoped task to an operator-provisioned launch boundary, which starts the approved executable and invocation profile
3. The CLI selects its own auth mode and performs provider requests under the user or organization's entitlement
4. Recursion consumes authorized structured results and correlated control events, not an exported provider token or a provider HTTP proxy
5. The CLI's own delegation features create children. Each child remains bound to the reviewed identity, scope, limits and topology
6. A single Recursion UI displays connection status and opens the vendor-owned setup surface. Whether any key-entry widget, credential reference or local broker secret belongs in that UI is an explicit review question, not a resolved implication of the phrase one place to connect
7. Work remains local to the reviewed user and machine topology unless an independently reviewed remote profile says otherwise

Could the evidence distinguish a **provider credential** from a **local IPC capability/bearer**? A local bearer may still be a powerful credential even if it cannot independently call a model provider. Could a generic response stream accidentally carry credentials from a tool result, log or authentication error? D-029 needs an actual boundary argument; the word local and a promise not to read a file do not establish non-access.

For this packet, **owns the JSON stream** means operational control of transport and parsing. Could counsel confirm that wording should not imply ownership of all intellectual property, personal data, notices or third-party material within it?

### 2.2 Which facts must not be collapsed into one route name

| Profile axis | Precise question for counsel and technical reviewer |
|---|---|
| Contract | Which entity, territory, user category, plan, effective terms, order form and incorporated policy govern? |
| Auth | Does the harness use subscription OAuth, a provider API key, a service account, enterprise OIDC, cloud IAM or externally supplied tokens? Who refreshes it? |
| Caller | Is Recursion a single-user local caller, a paid local product, an organizational service or a hosted multi-tenant operator? |
| Interface | Is the actual interface installed CLI exec, App Server, ACP, local HTTP, in-process SDK or hosted API? |
| Invocation | Which flags, environment names, config sources, hooks, plugins and defaults can change auth, endpoint or billing? |
| Work | Is this one human-directed task, many independent jobs, native subagents, long-lived scheduled activity, team use or resale? |
| Output | Which content and metadata categories are retained, transformed, replayed to another provider or displayed publicly? |
| Package | Does the release contain only original adapters, copied SDK/protocol code, bundled executables, installer scripts, cached downloads, logos or other vendor assets? |
| Evidence | Which source revision and reviewed artifact prove each factual assertion? Which assertions remain unknown? |

This decomposition is **inferred research structure**. Competing option: independently complete case dossiers with the same variant coverage versus normalized profile decomposition. Negative control: one approval per vendor name. Comparative falsifier: the normalized sheet omits a required predicate or exceeds the adopted review/error burden relative to complete dossiers. Original scope-granularity falsifier: counsel confirms in writing that a route-wide instrument covers every materially different listed profile with identical conditions. Non-proof: the decomposition itself neither creates compliance nor proves any implemented boundary.

## 3 Per route operating mode evidence and questions

This section addresses **R-H.Q01–Q05**. Every route has separate cells for installed driving/output, credential distinction, fan-out/subscription routing, identity/accounting and conditions. The cited source IDs point to the quoted evidence appendix, URLs, retrieval date and expiry codes. Each cell's applicability is **unknown** unless counsel resolves it. All rows expire under **T and D**; any package or branding inference also expires under **R or M**.

<a id="claude-legal-facts"></a>
### 3.1 Claude Code

**SD — RM-S24/S03 source version:** Commercial Terms retrieved 2026-10-02 display effective June 17, 2025. Sections A.1, D.4 and F are the service-use, competing-product/reverse-engineering and intellectual-property anchors for counsel. No applicability is settled here.

| Issue | Public record and exact question |
|---|---|
| Installed caller and JSON | **Source-documented premise:** [R-F print profile](../rf/report.md#claude-headless-facts), S04. Which exact invocation constitutes the reviewed local caller, and does embedding it in a product invoke S01's offering conditions? |
| Credential versus usage intermediation | **Source-documented distinction:** S01 separately discusses the unmodified binary's end-user sign-in, third-party login/token custody, and usage routed on another user's behalf. Does the intended launch boundary satisfy the relevant factual distinction, and can usage intermediation exist without token custody? |
| Native fan-out | S01 describes ordinary individual subscription usage; S02 has automation language with exceptions, and S03 addresses resale. Which native children, concurrency and unattended duration fit the applicable exception? **Unknown:** a generally applicable numeric concurrency or high-volume entitlement for this profile |
| One connection UI | May the UI merely hand the user to Anthropic's flow and display status? Would embedded Claude login, setup-token handling, API-key entry or a hidden relay change the answer? |
| Identity and accounting | Auth premise: [R-F print profile](../rf/report.md#claude-headless-facts). S05 ties metering to sign-in. Which principal and plan actually fund every child? Can the record differentiate client estimates, cumulative conversation totals and native allowance debits? |
| Conditions and notices | Does the review require preserving every built-in auth choice, keeping the binary unmodified, direct end-user billing, accurate plain-text compatibility wording and commercial terms for the offering? S01/S03 are evidence anchors. **Unknown:** a universal powered-by requirement for the proposed local adapter |

**Profile-specific addition beyond R-C:** review the [invocation/auth facts](../rf/report.md#claude-headless-facts) and [accounting facts](../rf/report.md#claude-accounting-facts) together. Could changed defaults trigger renewed review despite an unchanged command? Which evidence, rather than an overlapping estimate, could support a subscription-efficiency statement?

**Competing characterization:** a user's own locally invoked binary versus a developer's service routing usage. **Decisive falsifier of the caller premise:** Recursion receives/refreshes a subscription token, modifies the executable, suppresses an auth option, pays/resells the end user's usage, or counsel identifies a required-route restriction on the exact driver. **Non-proof:** absence of these facts alone does not establish permitted automation or unlimited fan-out.

### 3.2 Codex and ChatGPT

<a id="codex-app-server-legal-facts"></a>
**D — canonical applicability note:** S08 distinguishes local/open-source continuation from commercial/hosted authentication use. See Appendix B’s quotation and [R-F’s technical profile](../rf/report.md#codex-app-server-facts); actual applicability remains unknown.

| Issue | Public record and exact question |
|---|---|
| Installed caller and output | S09 is the exec evidence; [R-F §1.2](../rf/report.md#codex-app-server-facts) is the App Server evidence. Are these distinct contractual profiles, even when both run locally and produce structured events? |
| Credential boundary | Use the [canonical auth-mode inventory](../rf/report.md#codex-app-server-facts). Would excluding all auth mutation/token endpoints preserve the reviewed caller facts? **Unknown:** a universal installed-tool exception under every plan |
| Local versus hosted | Under the [canonical applicability note](#codex-app-server-legal-facts), how should a new project, paid distribution/support and managed remote machines be classified? Is the relevant scope authentication, execution topology or the offering? |
| Native fan-out and limits | S07 addresses account sharing, resale and usage-limit avoidance; S10 describes shared allowances and plan-dependent billing. Does a native child remain the same authorized End User, and where are duration/concurrency limits specified? **Unknown:** a universal number of subscription-funded children |
| One connection UI | Could the UI expose only Codex-owned setup/status? Would externally supplied ChatGPT tokens or registered Sign in with ChatGPT be a different approval case? No registration or integration eligibility is assumed |
| Identity and accounting | Use the [canonical auth inventory](../rf/report.md#codex-app-server-facts). S10 separates allowance/credit plans from token-based Enterprise billing. Which native meter and account scope fund each attempt? Does a displayed plan or token count prove an actual subscription debit? |
| Conditions and notices | What incorporated terms, registration, user disclosure, API-only alternative or branding conditions attach to the exact distribution? S06–S10 and S38 are evidence anchors; no blanket powered-by requirement is established |

**Competing characterization:** alternative applicability categories in the [canonical note](#codex-app-server-legal-facts); installed exec versus registered sign-in integration. **Falsifier:** counsel classifies a required configuration outside the applicable product-specific language, or the implementation relies on external token lifecycle ownership. **Non-proof:** Apache-licensed client source and a documented JSON-RPC surface do not answer service authentication, account sharing or redistribution of unrelated app assets. D-023 remains the sequence decision, not a legal result.

### 3.3 Cursor

| Issue | Public record and exact question |
|---|---|
| Installed caller and JSON | Technical premise: [R-F §1.5](../rf/report.md#cursor-headless-facts), S14. What reconciles that interface with S12's broader automation wording under the applicable S11 agreement/MSA? |
| Credential boundary | Auth premise: [R-F §3](../rf/report.md#cursor-auth-facts), S13. **Unknown:** an express contractual distinction between a third-party caller of an authenticated CLI and a third party holding that key. Does the answer depend on whether the caller is a personal script or distributed product? |
| Fan-out and routing | S12 addresses automation, rate limits and subscription/billing/metering manipulation. Which official automation and native-subagent behaviors are contemplated? **Unknown:** a general local CLI concurrency cap or unrestricted fan-out allowance |
| One connection UI | Does vendor-owned browser setup differ from Recursion requesting, storing or supplying a Cursor user key? Is a Cursor account API key different from a model-provider BYOK key for contract and accounting purposes? |
| Identity and accounting | S15 describes separate usage pools and subagents using a different model than the visible parent. Does that apply to the exact CLI build and tier, and must each child carry its actual model/pool rather than inherit the parent picker? |
| Conditions and notices | What does the actual MSA add or supersede? S11 also makes benchmark publication conditional on reproducibility information. What release, attribution and evaluation-report constraints attach? **Unknown:** general binary redistribution or powered-by permission/requirement |

**Competing characterization:** officially documented automation under a user key versus access captured by the AUP's broader wording. **Falsifier:** the governing instrument or written clarification excludes this third-party driver, or the implementation manipulates metering/account workflows. **Non-proof:** obeying technical rate limits does not itself reconcile the automation wording. A general usage help page is not proof of actual CLI billing; no account was inspected.

### 3.4 Gemini and Google CLI

| Issue | Public record and exact question |
|---|---|
| Installed caller and JSON | Technical premise: [R-F §1.6](../rf/report.md#gemini-headless-facts), S17. Does invoking that client differ from directly accessing its service using another tool, the scenario addressed by S16? |
| Credential boundary | S16 explicitly addresses direct third-party service access and the example of CLI OAuth. **Unknown:** whether the exact caller-of-installed-CLI arrangement falls on the same side of that language. Which fact would determine directness: endpoint caller, token owner, process control or product purpose? |
| Fan-out and subscription routing | S18 publishes per-user daily request figures for Code Assist Standard/Enterprise and separate pay-as-you-go modes; S19/S20 address API/Cloud limits and avoidance. Do native subagents aggregate under the same user's allowance, and what separate concurrency/rate rules apply? **Unknown:** this user's allowance, applicable parallel-session count and every child's actual routing |
| One connection UI | Could the UI open Google's own sign-in without copying CLI OAuth? Would altered client identity or fallback across accounts/projects create a different case under S19/S20? |
| Identity and accounting | S16 separates Google-account Code Assist, Gemini Developer API and Vertex, including enterprise precedence when entitlements overlap. Which identity and agreement is actually active, rather than inferred from a visible personal subscription? |
| Conditions and output | Do API-client identity, branding, privacy and grounded-output conditions attach? S21 introduces feature-specific Search/Maps treatment; S22's automated-access clause includes a machine-readable-instruction qualifier, not a blanket statement about all scripts. **Unknown:** required notice/powered-by treatment for this exact profile |

**Competing characterization:** the user operates the documented CLI through a local frontend versus third-party software directly accesses the backing service. **Falsifier:** the adapter presents the CLI's OAuth independently, masks client identity, changes the backing endpoint, or counsel says the installed caller is covered by the relevant restriction. **Non-proof:** the Apache CLI license, JSON mode and published daily request numbers do not authorize a service-access method or make quota circumvention acceptable. A subscription-funded route and an API-key fallback cannot be booked to the same assumed allowance.

### 3.5 Grok Build

<a id="grok-enterprise-facts"></a>
**D — canonical enterprise auth facts:** S26 lists browser OIDC, device code, external auth-provider command and API key. Credential precedence is per model; direct API and session inference paths differ. Which actual principal and payer fund a child remains unknown; the quoted inventory count appears only in Appendix B.

| Issue | Public record and exact question |
|---|---|
| Installed caller and JSON | Technical premise: [R-F §1.7](../rf/report.md#grok-headless-facts), S25. Does the exact driver qualify as an authorized automation means under S23? |
| Credential boundary | Use the [canonical enterprise auth inventory](#grok-enterprise-facts). **Unknown:** a general legal carve-out for a caller without custody. Would using an external token-producing command make Recursion an auth lifecycle participant? |
| Fan-out and routing | S23 addresses unauthorized automation, resale and rate-limit circumvention. S24 separates permitted users and API-integrated bundled services. Which instrument governs native parallel work on a subscription? **Unknown:** a route-wide simultaneous-session entitlement and numeric subscription fan-out cap |
| One connection UI | Can Grok own sign-in completely while Recursion displays only state? Which flow is selected if several credential sources coexist? |
| Identity and accounting | Use the [canonical precedence/routing facts](#grok-enterprise-facts). Which source wins for each child and who is charged? Is the visible session identity sufficient to determine that? |
| Conditions and notices | Does a paid orchestration product constitute a bundled service, another customer's permitted-user use, or something requiring a separate agreement? S27 has AI-generated disclosure language. What output/branding notice applies, if any? |

**Competing characterization:** an own-user local client versus an API-integrated service supplying access to end users. **Falsifier:** the actual account/payer, token broker, endpoint, distribution or billing flow differs from the stated local session case, or counsel finds a required driver unauthorized. **Non-proof:** documented ACP support and an upstream source license do not determine the correct contract, resale classification, commercial indemnity or quota entitlement. The current pages use SpaceXAI branding; that observation alone does not establish the contracting party for an existing account.

### 3.6 Hermes

| Issue | Public record and exact question |
|---|---|
| Installed caller | Technical premise: [R-F §1.8](../rf/report.md#hermes-integration-facts), S29. Does the reviewed profile invoke only local Hermes, or also Nous Portal/inference/another hosted service? |
| Credential boundary | R-C/R-B separately describe local caller authentication and downstream provider credentials. **Unknown:** whether the chosen bearer or transport is isolated from provider material and whether Nous service terms apply to the purely local software case |
| Fan-out and routing | S28 distinguishes individual login credentials, authorized users and automatic requests through a Nous-provided program; it also addresses multiple-account capacity and rate-limit avoidance. Does a third-party driver of Hermes satisfy the program exception when a covered Nous service is used? What upstream-provider terms also apply? |
| One connection UI | Is the connection a local protocol capability, a Nous account or a selected third-party provider entitlement? Which party's flow and consent does the UI present? |
| Identity and accounting | What selected provider, endpoint, auth owner, account and payer sit behind each native child? **Unknown:** a universal Hermes subscription, fan-out cap or meter that can replace provider-specific records |
| Conditions and notices | Which software-license notices apply to included material, and which Portal/Nous clauses apply only if the covered service is actually used? What separate provider and brand obligations remain? |

**Competing characterization:** local open-source execution using the operator's separately authorized provider versus a Nous service/connected-account integration. **Falsifier:** the factual endpoint or hosted service changes the governing stack, the caller receives provider credentials, or counsel finds the automatic-request exception does not reach this driver. **Non-proof:** external protocols and local software licensing do not carry a universal upstream subscription entitlement. The local API bearer is not to be called credential-free merely because it is not a model-provider key.

### 3.7 OpenCode

| Issue | Public record and exact question |
|---|---|
| Installed caller and output | Technical premise: [R-F §1.9](../rf/report.md#opencode-server-facts), S32. S30 expressly distinguishes non-hosted open-source software from website/inference/hosted offerings. Which layer is the actual route? |
| Credential boundary | S31 documents provider-auth storage; server-control auth is covered in [R-F §1.9](../rf/report.md#opencode-server-facts), S32. **Unknown:** a provider-independent legal distinction between calling the installed server and holding downstream credentials. Can the launch boundary exclude auth mutation endpoints as well as file access? |
| Fan-out and routing | For its covered services S30 addresses internal use, programmatic extraction, excessive load and bulk-account limit avoidance. How do these clauses apply to Zen/Go/hosted inference versus the non-hosted software carve-out? **Unknown:** a universal native fan-out or subscription quota for arbitrary upstreams |
| One connection UI | Does OpenCode itself own provider setup, with Recursion only opening that surface? Would calling an auth-setting API be a different posture from using a preconfigured tool? |
| Identity and accounting | Is the billed principal an upstream BYOK account, OpenCode inference entitlement, organizational account or local model with no external provider request? Can this be evidenced without reading secret values? |
| Conditions and notices | What actual third-party model rights, file-level software notices, service conditions and brand permissions apply? **Unknown:** a universal powered-by condition or entitlement inherited from the root source license |

**Competing characterization:** non-hosted software interoperability versus use of a separately contracted inference/hosted service. **Falsifier:** a model endpoint resolves to a covered hosted service although the profile says local-only, or a copied auth key/proxy substitutes for the installed client. **Non-proof:** the express software/service distinction is not clearance of every upstream provider route, copied plugin, binary asset or output-use policy.

### 3.8 Antigravity

<a id="antigravity-auth-facts"></a>
**D — canonical auth facts:** S36 distinguishes cached account-session/keyring authentication from direct Gemini API-key operation using environment credentials. Logout does not clear API-key operation. Whether actual billing follows the presumed subscription is unknown; a Gemini API key must not be equated with a Gemini Enterprise key. S34's enterprise carve-out requires the actual administrator agreement.

| Issue | Public record and exact question |
|---|---|
| Installed caller and JSON | Technical premise: [R-F §1.10](../rf/report.md#antigravity-headless-facts), S35. How does counsel reconcile that technical interface with section 6 of S34 about third-party tools accessing the service? |
| Credential boundary | S34's third-party-access wording and OAuth example do not expressly resolve the intended installed caller. **Unknown:** a local-launch exception. Does lack of token custody affect the analysis if the caller still initiates service use? |
| Fan-out and routing | S34 addresses autonomous agents and user supervision, not a general unlimited-fan-out allowance. Which Google/enterprise or selected-model conditions define rates, concurrency and subscription routing? **Unknown:** the applicable session cap, headless fan-out entitlement and exact backing-model stack |
| One connection UI | Can the user authenticate only in the vendor CLI/keyring while Recursion sees status? Which data would an API-key UI transmit and to whom? |
| Identity and accounting | Use the [canonical auth note](#antigravity-auth-facts). Which exact agreement and billing record establish the actual profile, including any enterprise exception? |
| Conditions and notices | Which downloaded-software, third-party-model, agent-supervision and output obligations apply? Are any branding/binary rights separately granted? **Unknown:** a general redistribution grant, local caller exemption or powered-by rule |

**Competing characterization:** documented headless operation by the user's own client versus third-party software accessing the service; consumer additional terms versus an administrator's enterprise agreement. **Falsifier:** counsel says section 6 covers the exact required driver, or the actual profile does not fall within a claimed enterprise carve-out. **Non-proof:** headless documentation does not override terms. The [canonical logout caveat](#antigravity-auth-facts) prevents treating UI disconnect as universal revocation.

### 3.9 Pi

| Issue | Public record and exact question |
|---|---|
| Installed caller and output | The immutable S33 README documents print/JSON/RPC/SDK automation. Which exact binary, plugin and provider configuration implements the route? |
| Credential boundary | S33 describes connecting a subscription or API key. **Unknown:** a Pi-specific service instrument that establishes a general installed-client versus credential-custody boundary. What chosen provider terms govern that login and subsequent traffic? |
| Fan-out and routing | **Unknown:** a Pi-specific subscription resale rule, numeric concurrency entitlement or universal provider fan-out policy in the reviewed source. Which upstream terms and exact extension mechanism must counsel examine? Absence of a found Pi rule is not absence of restrictions |
| One connection UI | Does Pi own setup and refresh, and is Recursion excluded from the provider store and any auth-related RPC/SDK calls? Does a third-party provider plugin have its own terms? |
| Identity and accounting | Which provider subscription/key/account is active for the parent and each child? **Unknown:** a common Pi subscription debit or universal metering unit |
| Conditions and notices | S33 identifies its source license as MIT. Which complete license text, package file exceptions, dependency notices, extension rights and project-mark permissions apply to the actual distributed artifact? |

**Competing characterization:** a local extensible tool using a separately authorized provider versus an integrated service or plugin reusing a provider subscription in an unreviewed way. **Falsifier:** the selected provider disallows the auth/driver configuration, or actual extension code introduces credential custody or a different endpoint. **Non-proof:** Pi's automation support and source-license label cannot establish a provider's permission. The pinned root LICENSE fetch failed in this research; the R-C manifest's license pin is inherited, not newly verified.

### 3.10 Other operator named routes

No additional operator-named route was supplied to this task. The row is therefore **not applicable for roster expansion**, not a blanket approval for future routes. Would counsel require the same identity, contract, automation, credential, output and distribution sheet before any new route could inherit a reviewed posture? No automatic inheritance is proposed.

## 4 Distribution posture questions

This section addresses **R-H.Q06–Q07**. It does not rank legal risk conclusively or select a shipping model. Would counsel compare exposure categories separately, with D-026's Apache-2.0 direction and D-019's opt-in release contract fixed?

| Candidate posture and open question | Competing option | Decisive falsifier of the stated premise | What it does not resolve |
|---|---|---|---|
| **P01 Adapter-only:** If only original adapters ship and users independently install clients, which reproduction/distribution issues are absent from that artifact? | Bundle an upstream executable or source rebuild under identified terms | Release/installer/cache contains a vendor executable, copied asset, SDK or implementation despite claiming none | Service automation, contract classification, upstream auth, patent and trademark questions |
| **P02 No bundled binaries:** Does requiring an existing unmodified client avoid a particular binary-redistribution question, and does an optional installer create a new one? | Vendor-directed opt-in download or packaged client | A mirror, image, embedded archive, installer redistribution or modified launch package changes the reviewed supply chain | Download terms, installation consent, runtime restrictions, dependencies or users' separate contracts |
| **P03 No credential custody:** Does the proven D-029 boundary alter counsel's view of credential or usage intermediation? | A separately contracted explicit API/registered integration where credential handling is approved | Token/key, refresh control, readable auth store, environment inheritance, logs or remote relay contradict the claimed separation | Initiation of service use, account sharing, output handling, native delegation or actual legal classification |
| **P04 Descriptive interoperability prose:** Which plain-text mentions accurately identify compatible tools without implying endorsement? | Vendor logos/co-branding or a vendor name in the feature title | Naming prominence, assets or wording imply partnership or approval; a mark is used beyond the reviewed purpose | Jurisdiction-specific trademark analysis, exact vendor guidance and required notices |
| **P05 Original plugin contract only:** Which file-level authorship and patent review is needed for an early interface publication without third-party code? | Ship copied SDKs, protocol schemas, examples or curated ports with their own licensing evidence | A supposedly original schema/example/interface text is copied, or a dependency/asset enters the package | Patent freedom, contributor title, compatibility, service access or existing third-party specification obligations |
| **P06 User-provider direct billing:** What distinguishes charging for orchestration/support from selling pooled provider access? | A provider-contracted integrated service with separately reviewed billing/entitlements | Invoices, quotas, shared accounts or control rights show Recursion pays/resells usage or assigns users to another user's entitlement | Resale definitions, API-client duties, consumer obligations or commercial/hosted classification |
| **P07 Separate profile evidence:** Should each opt-in route require a configuration-specific counsel disposition before activation/release claims? | Rely on a generic disclaimer or the upstream license badge | A supposedly reviewed profile differs in auth, topology, audience, package, contract or feature set | Technical qualification, every user's contract, future terms changes or closure of unrelated gates |

**Evidence anchors:** S01 gives product-specific binary/auth/naming conditions; the [S08 applicability note](#codex-app-server-legal-facts) supplies its own scope; S30 gives a software/service distinction; S37 separately addresses source/object redistribution, notices, contribution and trademark topics; S38 addresses endorsement and branding. These are comparison inputs, not precedents that clear Recursion.

Could counsel prioritize **bundled proprietary executables/assets, altered binaries/auth methods, pooled subscription access, central refresh/custody, and endorsement-like naming** for explicit review because they introduce additional disputed facts? The competing posture is a factual adapter-only/user-installed/own-user case. The falsifier of the narrower factual claim is finding one of those additional acts in the release or service. The non-proof is that fewer factual acts do not automatically imply a legally safe release.

No public-distribution decision is executed. Proposed defaults, activation consequences or release-blocking conditions remain for the existing Owner/counsel process, not an implicit reopening of D-019 or D-026.

## 5 Precise question set for qualified counsel

This section addresses **R-H.Q08**. **H01–H18** are legal handoff questions; they are distinct from the twelve numbered research questions **R-H.Q01–Q12**. The evidence appendix for each is the cited S rows, which include the short quote, URL, retrieval date and expiry trigger. The factual sheet below is intentionally blank on private account facts.

| ID | Answerable counsel question | Evidence appendix and expiry | Missing factual evidence and expected response |
|---|---|---|---|
| H01 | For each reviewed profile, does calling the unmodified installed CLI without receiving provider secrets fall within any prohibited credential intermediation, usage intermediation or third-party access concept? Which exact provision and fact decide that? | S01/S02/S08/S16/S34; T,D | Redacted process diagram, account/credential owner, endpoints, bytes crossing boundaries; a per-profile answer with conditions or named unresolved facts |
| H02 | Does command/RPC control, auth status display, an inherited environment, a local bearer, a setup handoff or refresh ownership change that classification individually? | S08/S13/S26/S31/S32/S36; T,D | Separate variant for each act, not a merged catch-all; identify which variants remain outside the intended no-custody profile |
| H03 | Does the phrase one place to connect keys/subscriptions accurately describe a launcher/status UI, and which credential-entry, sign-in, storage or registration acts would need a different contract or permission? | S01/S08/S13/S16/S26/S33/S36; T,D | UI wireframes with actor and destination for every field; required disclosures and any provider permission evidence |
| H04 | In Gemini and Antigravity, does third-party access language cover an installed unmodified CLI caller, direct OAuth reuse, or both? What changes under enterprise/Workspace/admin terms? | S16–S22/S34–S36; T,D | Exact auth mode, entitlement overlap, accepted admin terms, topology, endpoint and client identity; do not infer an exception from documentation alone |
| H05 | For Codex App Server, how does the [documented applicability distinction](#codex-app-server-legal-facts) affect a new Apache project, paid local distribution/support and remotely operated user machines? What separate registration, if any, would change the result? | S06–S10; T,D | Entity/pricing/topology/history of integration and applicable agreement; opinion limited to stated edition, not every use of the Codex name |
| H06 | For Cursor, what authoritative reconciliation applies between AUP automation wording and headless/API-key instructions? Do an MSA or written product permission change it? | S11–S14; T,D | Accepted MSA/order/policy versions, headless flags, credential owner and use purpose; exact supporting hierarchy/permission or unresolved blocker |
| H07 | What workload, concurrency, simultaneous-session, user-presence and duration limits apply to native fan-out under each subscription/profile, including nested children and native background work? | S01/S02/S07/S12/S18/S23/S28/S30; T,D | Quantified intended load envelope, native delegation mechanism, identity of beneficiary and operator; numeric limits or explicitly qualitative limits, never an assumed unlimited value |
| H08 | When does retry, task splitting, cross-harness fallback, multi-node continuation or account selection become limit avoidance or account sharing under the governing text? Is ordinary scheduling within an account distinguishable from multiplying its entitlement? | S07/S12/S19/S20/S23/S28/S30; T,D | Routing/backoff/fallback/state-transition description and aggregate meters; conditional answer for each behavior, not a generic efficiency blessing |
| H09 | What distinguishes own-user subscription use from resale, pooled access, permitted-user delegation or an API bundled service when Recursion charges for software or support? | S01/S03/S07/S24/S28/S30; T,D | Product prices, invoices, payer, tenancy, customer agreements and who can initiate work; classify the specific arrangement |
| H10 | Which principal, entitlement and agreement fund every parent/child attempt, and which evidence may support a statement that the user's subscription was debited? How should key/API/enterprise exceptions be disclosed? | S04/S05/S08–S10/S13/S15/S16/S18/S26/S31/S36; T,D | Per-attempt auth-mode attestation without secrets; meter scope/unit/window, payer, authoritative billing record or unknown; no invented conversion from tokens to quota |
| H11 | Does parsing, storing, summarizing, replaying to another harness/provider or displaying the output require different rights or notices for model output, third-party grounded material, personal data and accidental secrets? | S06/S21/S27/S30; T,D | Content-category inventory, retention/replay purposes, destinations and access; special treatment for Search/Maps results if actually present |
| H12 | What legal significance, if any, should be attached to Aggressive/Full/Lazy Stop and checkpoint/interrupt/drain, given that process interruption is not external rollback or credential revocation? | D-022; S04/S36; T,D | Reviewed state/effect semantics and later independent evidence; specify required revocation/notification timing without assuming implementation success |
| H13 | Under what conditions could original adapters and a plugin contract ship under the accepted Apache posture while calling user-installed clients? Which exact notices and file-level obligations attach? | S01/S30/S33/S37 plus inherited R-C license manifest; R,T | Release file manifest, source pins, dependency licenses, copied-versus-original map; no badge-only compatibility conclusion |
| H14 | How do optional download, mirroring, preinstallation, wrappers around vendor binaries, containers and modified builds change the distribution analysis? | S01/S11/S30/S37; R,T | Complete distribution/installer chain and vendor agreement for exact artifact; compare P01/P02 variants |
| H15 | Which plain-text references, logos, names, powered-by statements, notices or endorsement disclaimers may or must appear for each route and output feature? | S01/S21/S27/S37/S38 and R-C brand register; M,T,R | Actual screens, README and marketing drafts, territory/audience and asset provenance; explicit unknowns where public sources do not answer |
| H16 | What contribution-title, patent, CLA/DCO and third-party import process implements the accepted Apache choice for original code, interfaces, SDK examples and optional plugins? | S37 and inherited R-C Q09–Q10; R | Author/rightsholder records, employer authority, copied source inventory, proposed contribution text; no new project-license selection |
| H17 | Which contract version, entity, territorial variant, admin agreement, policy precedence and user category govern each profile, and which fact/document changes require re-review? | All terms sources; T,D,R,M | Private contracts and jurisdiction/tier facts supplied through Lucas's chosen secure counsel channel; a dated applicability matrix |
| H18 | What configuration-bound counsel response, independent factual verification and Owner acceptance would be sufficient for the G-32 decision, and what unresolved item prevents closure? | R-C Q12; H01–H17; all expiry triggers | Written response, reviewed artifact IDs and conditions, exact unknowns, re-review triggers, independent verification and explicit Owner disposition |

### 5.1 Evidence sheet for each counsel answer

Could each response attach the following facts, with **unknown** allowed only where the resulting restriction/blocker is explicit?

- Route and profile ID; executable/package version and hash; source commit; interface and invocation flags
- Operator, beneficiary, account holder, contracting entity, payer and jurisdiction as distinct roles
- Terms/policy/order/admin-agreement versions and counsel's explanation of precedence
- Auth mode, credential/refresh owner, store boundary, local bearer and provider endpoint, using abstract labels rather than secret values
- One-place connection UI flow; prompts/status/output/control data crossing the launch boundary
- Native delegation mechanism, depth/width/duration envelope, user-presence assumptions and aggregate usage scope
- Account sharing, routing, retries, fallback, continuation, interruption and restart behavior
- Output categories, onward destinations, retention/reuse purposes and required notices
- Distribution manifest, copied materials, third-party licenses, installer/mirror behavior, naming/branding sample
- Source evidence IDs, factual verification evidence, counsel conditions, unresolved facts, reviewer, date and re-review trigger

**Competing option:** independently complete case dossiers and indexed narrative answers under the same profile/question coverage. **Negative control:** a generic yes/no email about the vendor. **Comparative falsifier:** the normalized sheet omits a required predicate or exceeds the adopted review/error burden relative to complete dossiers. **Original scope-granularity falsifier:** counsel provides a governing instrument that directly and unambiguously settles every listed variant without additional implementation facts. **Non-proof:** a completed sheet is neither an opinion nor evidence that a future build follows it.

## 6 How this extends R C

This section addresses **R-H.Q09**. R-C already covers the nine routes, service/source/binary/trademark separation, Apache obligations, distribution options and its twelve counsel checklist questions. R-H does not relabel those answered legal questions: R-C contains a question packet, not legal answers.

| R-C item retained | R-H addition for the accepted operating mode |
|---|---|
| Q01 contract and jurisdiction | H17 binds each answer to an invocation profile, not merely a vendor name; geographical variants and administrator agreements remain missing facts |
| Q02 credential/usage intermediation | H01–H03 separate token non-custody, causal initiation of use, process control, local IPC credentials, one-place setup UI and unexpected secret-bearing output |
| Q03 headless/scheduled/remote use | H04–H07 distinguish ordinary installed driving, nested native fan-out and product-specific local/commercial/hosted conditions |
| Q04 identity and auth modes | H10 treats per-child credential precedence, API fallback and subscription accounting as factual predicates; Claude bare-mode default changes and Antigravity key-mode logout are explicit change triggers |
| Q05 resale/account sharing | H09 compares charging for orchestration/support with pooled access, account sharing and API bundled services without deciding the classification |
| Q06 rate/quota avoidance | H07/H08 add total load, native children, continuation and cross-node/cross-harness aggregate limits; no multiplication of entitlement is assumed |
| Q07 binary/source distribution | H13/H14 bind adapter-only and no-binary claims to the complete installer/image/cache chain, not just the main repository |
| Q08 trademarks | H15 separates plain-text compatibility, feature/product naming, logos, AI notices and content-specific grounding notices |
| Q09 contribution/IP | H16 carries this forward unchanged as an unresolved counsel/Owner implementation question |
| Q10 plugin contract/SDK | H13/H16 add original-versus-copied schemas/examples and source-package boundaries; no license reopening |
| Q11 privacy/security/sector | H11 adds structured stream contents, retention, summary, cross-provider replay and third-party grounded output; no assertion any sensitive feature is enabled |
| Q12 G-32 acceptance | H12/H18 add D-022 stop vocabulary, revocation evidence, profile changes and a concrete response/acceptance record |

**All R-C legal applicability questions remain open until counsel answers them.** R-A's graph/grant and disabled-path proposals, R-B's launch/isolation and continuity proposals, and R-D's accounting/preregistration are technical evidence inputs; they neither replace counsel nor become adopted contracts through this report. R-E/R-F can later supply boundary and mechanics evidence; none is treated as already run.

## 7 What must precede a G 32 closure decision

This section addresses **R-H.Q10**. Under the accepted project authority, G-32 remains open until counsel returns and the Owner makes the required disposition. The following is an **inferred proposed sufficiency checklist for that review**, not a new gate definition or a closure declaration.

1. **Scope identified:** Does counsel have the actual entity, territories, tiers, customer/consumer roles, accepted agreements and required-route roster?
2. **Caller facts bounded:** Has each route's response addressed installed unmodified invocation, output consumption, absence of credential custody and any distinct usage-intermediation concept?
3. **Fan-out addressed:** Does the response cover harness-native children, aggregate identity, simultaneous sessions, request rates, duration, retries/fallback and subscription allocation, including unknown limits?
4. **Connection UI addressed:** Are launcher/status behavior, sign-in ownership, optional key entry and any local broker credentials individually classified?
5. **Distribution and content addressed:** Does counsel cover original adapters, binaries/assets/installers, licenses/notices, contract/SDK publication, branding and output retention/replay?
6. **Conditions made verifiable:** Are required conditions mapped to exact executable/profile/artifact versions and observable checks, with unknowns neither hidden nor treated as passes?
7. **Independent factual evidence available:** Has a reviewer other than an implementer verified the stated technical boundaries, disabled paths, secret non-access, package contents and revocation semantics under separately authorized work?
8. **Written response retained:** Is the opinion dated, scope-limited, linked to the reviewed facts and explicit about unresolved matters and change triggers?
9. **Owner acceptance recorded:** Has Lucas accepted the disposition under the project decision process, without this research silently reducing D-019's required surface or changing D-026?

If counsel finds a D-030 falsifier on a required route, the packet returns that exact finding to Lucas. It does not reinterpret the accepted decision, substitute another required route, drop a release capability or decide that a disclaimer cures the issue.

**Competing approach:** Owner-approved predicate-dependency adjudication retaining the same counsel, factual verification and required-scope gates. **Negative control:** close G-32 after collecting public terms and obtaining one broad counsel response. **Falsifier of that approach's sufficiency:** an uncovered auth/topology/audience/distribution variant, unmet condition, contradictory governing instrument or unverified factual premise in the release. **Non-proof of this checklist:** document completeness, an opinion and technical qualification are different evidence classes; none guarantees all future users' circumstances.

## 8 Competing interpretations for counsel

This section addresses **R-H.Q11**. These are hypotheses to test against the governing texts and facts, not assertions of law.

| Competing readings | Precise unresolved question | Evidence that could distinguish them | Non-proof |
|---|---|---|---|
| Own-user caller of an installed tool vs credentialed intermediary | Does provider-secret custody control the result, or can control of initiation/routing be sufficient? | S01/S16/S34, exact token/process/request flow, written provider/counsel interpretation | A process boundary alone does not define a contractual term |
| Own-user native fan-out vs account sharing/access resale | Do many agents act for one authorized user or make the account available to other users/beneficiaries? | S07/S24/S28/S30, beneficiary identity, tenancy, billing and initiation rights | Child count alone is not a legal classification |
| Documented automation vs broad automated-access restriction | Does the specific product documentation create or evidence the required exception under the governing agreement? | S02/S11–S14/S23/S25 and actual MSA/hierarchy | A working script does not establish an exception |
| Local/open-source distribution vs commercial/hosted service | What facts classify a paid local app, support business or user's remote node? | S08 and actual deployment/contracts | Open source is not synonymous with noncommercial or nonhosted |
| Separate adapter vs redistribution of vendor material | What is actually copied, linked, installed, cached or embedded? | Release manifest, S01/S30/S37, file-level sources and notices | A separate repository/process does not answer all copyright/patent questions |
| Efficient scheduling vs quota-circumvention mechanism | Does the routing reduce redundant work within a reviewed entitlement or simulate multiple entitlements/accounts? | S07/S12/S19/S20/S23/S28/S30 plus routing and aggregate accounting | Lower usage, staying below a rate or lack of enforcement is not clearance |
| Transport control vs ownership/reuse of output | Do extracted JSON fields include content with separate retention/display constraints? | S21/S27, output-category and retention/replay inventory | Possession and parsing do not settle rights, privacy or attribution |

Each reading competes with the other in its row. The decisive falsifier of a proposed factual characterization is a verified artifact/flow or a counsel interpretation of the governing instrument inconsistent with that characterization. The packet does not choose the reading that is most favorable to the product.

## 9 Stop revocation and honest accounting

### 9.1 D 022 vocabulary without invented guarantees

Could counsel assess termination, user control and revocation using the accepted labels **Aggressive / Full / Lazy Stop**, plus **checkpoint**, **interrupt** and **drain**, while requiring an implementation-specific mapping for each?

- For **Aggressive Stop**, what admission/effect authority is withdrawn, which already dispatched effects may continue, and what must be reconciled?
- For **Full Stop**, what scope of running/queued work and descendants is covered, and what terminal evidence distinguishes stopped, failed and unknown work?
- For **Lazy Stop**, which bounded work may finish, what new admissions are blocked, and can any child or native background activity outlive the requested boundary?
- For **checkpoint**, which state is saved and which external effects remain unsettled?
- For **interrupt**, what upstream acknowledgement exists and what does it fail to establish about in-flight provider requests, billing or third-party actions?
- For **drain**, which already admitted work may settle and what finite scope/time policy controls it?

These questions do not assign new semantics to accepted terms. The operator/technical team must supply the current formal/broker mapping. Could counsel distinguish an orchestration stop from CLI logout, provider token revocation, account suspension and deletion of retained outputs? The [Claude control facts](../rf/report.md#claude-headless-facts) and [Antigravity auth note](#antigravity-auth-facts) supply concrete source cases for this distinction. No signal, logout, token revocation or stop test was performed.

**Competing posture:** linked receipt timeline versus per-stage Stop vector, preserving the same scopes, uncertainty and credential-revocation distinctions. **Negative control:** claim a killed process proves revocation. **Negative-control falsifier:** an issued request/effect settles later, a credential still authenticates or an admitted child continues. **Candidate falsifier:** a required stage or unresolved outcome is omitted or misclassified against an independently fixed receipt oracle. **Non-proof:** even correctly mapped stops do not establish service permission or external rollback.

### 9.2 What would support an accounting statement

Could the future factual record bind **attempt → parent/child lineage → exact profile → effective auth principal → payer/entitlement → native meter** without storing bearer secrets? R-B/R-D already propose missing values as null, not zero; all helper, retry, failed, interrupted and recovery attempts remain visible. This packet carries that discipline into H10, not a new implementation decision.

Could counsel and the evaluator distinguish these statements: a provider request was initiated; a CLI reported tokens; a client estimated dollars; a shared allowance decreased; and an invoice charged a party? Which actual evidence supports each? A native child counter or cumulative conversation total cannot silently stand in for a per-attempt subscription debit.

**Competing record:** retained aggregate-native reconciliation with identical coverage, units and null unknowns versus event-level ledger. **Negative control:** a parent model name plus one cost total. **Negative-control falsifier:** a native child uses another auth/model/pool, a resumed total includes prior work, the plan bills in dollars rather than credits, or a key fallback occurs. **Candidate falsifier:** the complete ledger loses or double-counts an identity/native-unit boundary against independent retained records. **Non-proof:** a complete ledger still does not establish savings, lawful use, zero unreported costs or provider intent. A terms/rate-limit review does not authorize API fallback, on-demand spend, quota resets or account changes.

## 10 Keeping the packet evidence and questions only

This section addresses **R-H.Q12**.

Could reviewers apply these boundaries before sending the packet to counsel or quoting it publicly?

- Keep direct source statements attributed to their issuer and bounded by page/version/section
- State the proposed operating facts as intended/unverified until independent technical evidence exists
- Mark legal applicability, account entitlement, exact terms hierarchy and missing limits as unknown
- Ask counsel to resolve apparent documentation/terms tensions; do not let technical documentation silently override an agreement or vice versa
- Do not label any route lawful, unlawful, compliant, safe, cleared, infringing or unrestricted based on this research
- Do not turn D-030's accepted subject-to-counsel posture into a permission for target invocation
- Do not reinterpret no credential custody as no credentials anywhere in the trusted system, or output control as ownership of its contents
- Do not copy private contracts, account identifiers, infrastructure details or credential values into a public research brief
- Do not claim a public source/license, a model's opinion, no enforcement, a working demo or an implementer's PASS closes G-32
- Preserve accepted license, release scope, vendor sequence, platform floors and product positioning; propose no final language/store/framework/vendor choice

**Competing approach:** indexed case narratives versus normalized disposition matrix, both retaining every material profile, source, blocker and uncertainty. **Negative control:** a short green/red route chart. **Negative-control falsifier:** the same named route changes disposition with auth, contract, topology, user, workload or artifact. **Candidate falsifier:** a material profile yields a missing or wrong disposition under an independently fixed case oracle. **Non-proof:** cautious phrasing alone cannot fix unsupported facts; the source and missing-input references remain essential.

## 11 Actionable unexecuted handoffs

Every action below is a proposed next step under a separate appropriate admission. **None was executed.** Lucas retains counsel contact/spend and product decisions. No live provider, target harness or system changes are authorized by this table.

| Handoff | Owner and concrete deliverable | Acceptance evidence to request | Competitor, falsifier and non-proof |
|---|---|---|---|
| L01 Counsel fact intake | Lucas supplies one completed profile sheet per required configuration, plus actual accepted agreements securely | Every H01–H18 relevant fact has a value or named blocker; no secret values in the sheet | Competitor: independently complete case dossiers versus normalized profile matrix, with identical material variants and unknowns. Negative control: one vendor-level summary. Falsifier: a material variant is omitted. Non-proof: factual intake is not advice |
| L02 Written counsel response | Lucas engages qualified counsel through his chosen channel; response to H01–H18 and R-C Q01–Q12 | Dated configuration-specific answers, governing instruments, conditions, unknowns and re-review triggers | Competitor: scoped narrative counsel opinion with complete question/profile index versus structured answers, with identical scope and unresolved conditions. Negative control: informal general reassurance. Falsifier: required profile/question remains uncovered. Non-proof: opinion is not a technical test or Owner acceptance |
| T01 Source refresh | A separately authorized document reviewer refreshes dynamic sources when counsel/release review occurs | URL/version/territory and excerpts reconciled; material changes escalated; historical evidence retained | Competitor: independently re-captured source set versus version-refresh diff, with identical freshness and retained history. Negative control: timeless saved links. Falsifier: terms/doc changes invalidate a quoted premise. Non-proof: fresh text is not applicability |
| T02 Launch boundary evidence | Future authorized R-E/local qualification work supplies a redacted process/data-flow and credential isolation record | Exact platform/executable profile, trust assumptions, positive/negative boundary evidence and independent review; no secrets in outputs | Competitor: model/refinement evidence plus the same independent implementation observations versus observed boundary corpus, under the same threat model. Negative control: policy promise alone. Falsifier: Recursion can read or cause export of provider secrets. Non-proof: technical separation is not a contractual exception |
| T03 Fan-out and meter specification | Future authorized R-F/R-D work specifies child limits, accounting scopes, retries and auth/billing changes without running them here | Every native child profile and meter is covered or explicitly unknown; all fallback routes separately admitted | Competitor: retained aggregate reconciliation versus event-level native-unit ledger, with identical all-child coverage and unknowns. Negative control: parent-only totals. Falsifier: undiscovered helpers/changed identity/cumulative double count. Non-proof: a specification is not executed evidence or savings |
| T04 Stop and revocation specification | Future broker/formal reviewer maps D-022 vocabulary to the exact profile and external-effect reconciliation | Each stop primitive identifies admission scope, descendants, in-flight outcome, evidence and credential/logout distinction | Competitor: linked receipt timeline versus per-stage Stop vector, with identical scope, unknowns and external-effect distinctions. Negative control: cancel equals rollback. Falsifier: effects or credentials persist beyond the asserted bound. Non-proof: source behavior is not local qualification |
| T05 Release contents and notices | Future release reviewer inventories exact source/binary/assets/installers and copied contract/SDK material | File-level provenance, licenses/NOTICE, build hashes, distribution paths and independent comparison with counsel-reviewed manifest | Competitor: independently rebuilt bill of materials versus file manifest, with identical rights/notices/provenance checks. Negative control: root-license badge. Falsifier: unreviewed file/asset/installer enters artifact. Non-proof: inventory is not license compatibility or trademark clearance |
| L03 G-32 disposition | Lucas reviews counsel answer plus factual evidence and records the decision under existing governance | Required scope covered, conditions independently checked, unresolved items explicit and release claims bounded | Competitor: Owner-approved predicate-dependency adjudication versus checklist, with identical counsel and independent factual requirements. Negative control: research self-approval. Falsifier: any unmet condition or required-route blocker. Non-proof: closure does not authorize later changed profiles automatically |

## Appendix A Coverage and completion record

### Numbered research questions

| ID | Brief question subject | Report answer | Status and next resolver |
|---|---|---|---|
| R-H.Q01 | Per-route public terms for installed CLI, stdout, no custody and connection UI | Sections 2–3, Appendix B | Evidence supplied for all nine; applicability unknown → H01/H03/H17 |
| R-H.Q02 | Installed caller versus credential intermediary distinction | Sections 3.1–3.9 and 8 | Source distinctions/absence explicit per route → H01/H02/H04–H06 |
| R-H.Q03 | High-volume native fan-out restrictions | Route fan-out rows; 5 H07–H09 | Quoted restrictions or explicit unknowns; exact load/limits → H07/H08 |
| R-H.Q04 | Identity and subscription accounting | Route identity rows; 9.2 | Source auth modes and unknown actual principal/debit → H10 |
| R-H.Q05 | Conditions, attribution, API-only/headless/client requirements | Route conditions rows; H11/H15 | Product conditions identified; no universal notice/permission inferred → counsel |
| R-H.Q06 | Adapter-only, no binaries/custody, prose/contract posture | Section 4 P01–P07 | Compared open questions, no choice → H13–H16 |
| R-H.Q07 | Risk-raising distribution choices and competitors | Section 4 | Factual exposures compared, not a legal risk verdict → H09/H14/H15 |
| R-H.Q08 | Precise counsel questions plus evidence appendix | Section 5 H01–H18; Appendix B | Complete handoff structure; private facts and counsel answers pending |
| R-H.Q09 | R-C extension and remaining questions | Section 6 | Explicit twelve-item crosswalk; all legal applicability questions remain |
| R-H.Q10 | G-32 closure prerequisites | Section 7 | Proposed review sufficiency under existing authority; G-32 open |
| R-H.Q11 | Competing legal interpretations | Section 8 | Hypotheses/questions plus distinguishing evidence, no selection |
| R-H.Q12 | Evidence/questions-only safeguards | Section 10 | Boundaries explicit; independent review pending |

### Completion gate bullets

| Gate | Exact requirement or stable short name | Disposition |
|---|---|---|
| R-H.CG01 | Every named route has an operating-mode evidence row with quoted public sources and retrieval dates, or an explicit unknown | Sections 3.1–3.9 plus Appendix B; nine routes; Q01 coverage |
| R-H.CG02 | Driving-an-installed-CLI versus credential-intermediation distinction stated per route from public evidence only | Each route credential row distinguishes source wording from unknown applicability |
| R-H.CG03 | Fan-out and subscription-routing terms quoted per route, unknown where absent | Route fan-out rows point to quote appendix; Pi and provider-dependent gaps explicit |
| R-H.CG04 | Distribution posture as separate open questions, not a decision | Section 4 P01–P07 |
| R-H.CG05 | Conclusion-shaped statements reframed as counsel questions; no legal conclusion | Sections 3–10 distinguish source facts, questions and proposed structures; independent review still required |
| R-H.CG06 | Extends R-C and states what must be true to close G-32 | Sections 6–7; G-32 explicitly remains open |
| R-H.CG07 | Stop/revocation uses D-022 vocabulary | Section 9.1; no invented semantics or rollback claim |
| R-H.CG08 | Each proposed posture names competitor and unresolved limits | Section 4 and each route; handoff table includes falsifiers/non-proofs |
| R-H.CG09 | Protected paths untouched; privacy and secret scan clean | Read-only input hashes retained; artifact-only structural/privacy checks recorded in QA.json; no credentials used; independent verification pending |

This is a **research-complete self-check**, not independent acceptance. A clean artifact scan cannot prove no secret exists in all possible upstream output. The separate coverage JSON repeats exact question text and completion-gate text for machine-readable review, with section references and next resolver for each unknown.

## Appendix B Public evidence register

All quotations below are source-documented public text retrieved on **2026-10-02 UTC**. Applicability to an actual configuration remains **unknown**. Vertical bars separate short excerpts from the same source; they do not join adjacent sentences. Excerpts are deliberately short and must be read in their linked context. Live pages are dated snapshots, not immutable legal instruments; no full-page archival hash is claimed. An excerpt digest in the JSON register is not a page digest.

| ID | Quoted public evidence | Source version and section | Expiry |
|---|---|---|---|
| S01 | “The Claude Code binary must not be modified.”; “developers may not collect, store, or intermediate Claude.ai credentials or session tokens”; “ordinary, individual usage” | [Claude Code legal and compliance](https://code.claude.com/docs/en/legal-and-compliance) · Undated live page · Offering Claude Code; authentication; acceptable use | T,D,M |
| S02 | “automated or non-human means”; “or where we otherwise explicitly permit it”; “or resell the Services” | [Anthropic consumer terms](https://www.anthropic.com/legal/consumer-terms) · Effective 2025-10-08; retrieved EEA/Switzerland consumer variant · Section 3 | T |
| S03 | “resell the Services except as expressly approved by Anthropic” | [Anthropic commercial terms](https://www.anthropic.com/legal/commercial-terms) · Effective date inherited from R-C: 2025-06-17; restrictions freshly rechecked · D.3–D.5 | T |
| S04 | “bare mode doesn’t use your subscription login”; “client-side estimates”; “earlier runs’ spend included” | [Run Claude Code programmatically](https://code.claude.com/docs/en/headless) · Undated live page; observed 2026-10-02 · Start faster with bare mode; Pipe data; Stop a run | D |
| S05 | “How you signed in determines how usage is metered.” | [Models usage and limits in Claude Code](https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code) · Page displayed Updated over a week ago; absolute revision unknown · How usage is metered | T,D |
| S06 | “Automatically or programmatically extract data or Output”; “You may not share your account credentials” | [OpenAI Terms of Use](https://openai.com/policies/terms-of-use/) · Effective 2026-01-01 · Registration and access; Using our Services | T |
| S07 | “violate or circumvent Usage Limits or otherwise configure the Services to avoid Usage Limits” | [OpenAI Services Agreement](https://openai.com/policies/services-agreement/) · Updated 2025-12-01; effective 2026-01-01 · Sections 2.2 and 3.1–3.3 | T |
| S08 | “App-server authentication has never been permitted for commercial or hosted services.”; “local or open-source application” | [Codex App Server](https://learn.chatgpt.com/docs/app-server) · Undated live page · Auth endpoints; Authentication modes | T,D |
| S09 | “codex exec”; “reuses saved CLI authentication by default.” | [Codex non interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) · Undated live page · Authenticate in automation | T,D |
| S10 | “Model usage counts toward your normal Codex usage limits and applicable credits or billing.” | [Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan) · Live help page; absolute update date not captured · Usage limits by plan; Why usage can run out | T,D |
| S11 | “There are no implied licenses in these Terms” | [Cursor Terms of Service](https://cursor.com/terms-of-service) · Updated 2026-09-03 · Opening MSA clause; 1.5; 5.1 | T |
| S12 | “Accessing the Service through automated or non-human means, whether through a bot, script, or otherwise”; “circumventing any rate limits” | [Cursor Acceptable Use Policy](https://cursor.com/acceptable-use-policy) · Updated 2026-08-11 · Scope; Comply with the law | T |
| S13 | “For automation, scripts, or CI environments, use API key authentication” | [Cursor CLI authentication](https://cursor.com/docs/cli/reference/authentication) · Undated live page · Browser authentication; API key authentication | T,D |
| S14 | “Use Cursor CLI in scripts and automation workflows” | [Cursor headless CLI](https://cursor.com/docs/cli/headless) · Undated live page · Introduction; Output formats | T,D |
| S15 | “Subagents can also run a named third-party model while the picker still shows Auto, Grok, or Composer.” | [Cursor usage and limits](https://prod.cursor.com/help/models-and-usage/usage-limits) · Undated live page · Usage pools; Can Auto usage draw from Other Models | T,D |
| S16 | “Directly accessing the services powering Gemini CLI”; “using third-party software, tools, or services” | [Gemini CLI license terms and privacy](https://geminicli.com/docs/resources/tos-privacy/) · R-C records update 2026-04-10; relevant text rechecked · Introduction; Supported authentication methods | T,D |
| S17 | “Headless mode provides a programmatic interface to Gemini CLI” | [Gemini CLI headless mode reference](https://geminicli.com/docs/cli/headless/) · Updated 2026-03-10 · Introduction; Output formats | T,D |
| S18 | “1500 maximum model requests / user / day”; “2000 maximum model requests / user / day” | [Gemini CLI quotas and pricing](https://geminicli.com/docs/resources/quota-and-pricing/) · Updated 2026-06-18 · Through your organization; Pay as you go | T,D |
| S19 | “You will not misrepresent or mask either your identity or your API Client's identity”; “will not attempt to circumvent” | [Google APIs Terms of Service](https://developers.google.com/terms) · R-C records last modified 2021-11-09; relevant clauses rechecked · 2(c) Permitted Access; 2(d) API Limitations | T |
| S20 | “to circumvent Service-specific usage limits or quotas” | [Google Cloud Platform Terms](https://cloud.google.com/terms) · R-C records modified 2026-09-02; section 3.3 rechecked · 3.3 Restrictions | T |
| S21 | “will only display the Grounded Results with the associated Search Suggestion(s) to the end user who submitted the prompt” | [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms) · R-C records effective 2026-03-23; relevant clauses rechecked · Use Restrictions; Grounding with Google Search and Maps | T,D |
| S22 | “in violation of the machine-readable instructions on our web pages” | [Google universal Terms of Service](https://policies.google.com/terms) · R-C records effective 2026-07-30 US variant; relevant clause rechecked · Do not abuse our services | T |
| S23 | “Accessing the Services through unauthorized automated or non-human means”; “circumventing any rate limits” | [SpaceXAI Acceptable Use Policy](https://x.ai/legal/acceptable-use-policy) · Effective 2026-08-14 · Comply with the law | T |
| S24 | “Customer may only provide End Users with access to the Services as part of a Bundled Service.” | [SpaceXAI Enterprise Terms](https://x.ai/legal/terms-of-service-enterprise) · R-C records updated 2026-08-14; actual effective date order dependent · 1.1 Access and Use; 1.2 Permitted Users | T |
| S25 | “already authenticated locally, or XAI_API_KEY is set” | [Grok Build Headless and Scripting](https://docs.x.ai/build/cli/headless-scripting) · R-C records updated 2026-06-10; ACP text rechecked · ACP; Output formats | T,D |
| S26 | “Grok Build supports four session authentication methods” | [Grok Build enterprise deployments](https://docs.x.ai/build/enterprise) · Undated live page · Authentication | T,D |
| S27 | “you may be required to apply”; “a disclosure stating that the content was generated or altered by artificial intelligence” | [SpaceXAI Consumer Terms](https://x.ai/legal/terms-of-service) · Updated 2026-09-11 · Scope; AI Generated Disclosures | T |
| S28 | “Login Credentials must not be used by multiple persons.”; “unless such program has been made available by Nous Research” | [Nous Portal Terms](https://portal.nousresearch.com/terms) · R-C records last update 2026-09-28; scoped clauses freshly rechecked · Definitions; 5.2; 10.1–10.2 | T |
| S29 | “Hermes ships three protocols for driving the agent from external programs” | [Hermes programmatic integration](https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration/) · Undated live page read 2026-10-02 about 06:24 UTC · Protocol table; TUI gateway | T,D |
| S30 | “automatically or programmatically extracts data or Output”; “only use the Services for your own internal use” | [OpenCode Terms of Use](https://opencode.ai/legal/terms-of-service) · Effective 2026-08-15 · Opening scope; restrictions; Third Party Models | T |
| S31 | “they are stored in ~/.local/share/opencode/auth.json” | [OpenCode providers](https://opencode.ai/docs/providers/) · Undated live page · Credentials; Base URL | T,D |
| S32 | “Use the opencode server to interact with opencode programmatically.” | [OpenCode server](https://opencode.ai/docs/server/) · Undated live page · Authentication; How it works | T,D |
| S33 | “automate it in print, JSON, or RPC mode”; “connect a subscription or API key” | [Pi coding agent README](https://github.com/earendil-works/pi/blob/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/packages/coding-agent/README.md) · Commit 7fbbd5f4a1d982bb02d63472dde0774fa639f99b · Introduction; Getting started; License | T,R |
| S34 | “Using third party software, tools, or services to access the Service” | [Google Antigravity Additional Terms](https://antigravity.google/terms) · No effective date displayed · Opening enterprise carve out; sections 4, 6, 8 | T,D |
| S35 | “Headless mode uses your cached credentials.” | [Antigravity headless mode](https://antigravity.google/docs/cli/headless/) · Undated live page · Overview; Authentication note | T,D |
| S36 | “the CLI never establishes an account session”; “/logout has no effect” | [Antigravity installation and auth](https://antigravity.google/docs/cli/install/) · Undated live page · Using a Gemini API key; Managing your session | T,D |
| S37 | “This License does not grant permission to use the trade names” | [Apache License Version 2](https://www.apache.org/licenses/LICENSE-2.0) · Version 2.0 January 2004 · Sections 3–6 | R,M |
| S38 | “Misrepresent your relationship with OpenAI, imply endorsement, or confuse users about sponsorship.” | [OpenAI Design Guidelines](https://openai.com/brand/) · Undated live guidelines · How to use our Logos | M |

### Expiry trigger definitions

- **T**: Governing terms, policy, interpretation, effective version, entity, jurisdiction, age/audience, tier, order form/MSA, admin agreement, account holder, payer or commercial model changes; recheck before any release decision.
- **D**: Executable/version/hash, invocation flags, auth mode or precedence, credential/refresh owner, endpoint, transport, client ID, output categories, fan-out profile, platform or local/remote/hosted topology changes; includes all T triggers.
- **R**: Source/package/release, file-level license, dependency, copied schema/example, binary/asset, installer/mirror, notice or distribution channel changes.
- **M**: Product or feature name, logo/asset, marketing claim, compatibility wording, presentation/prominence, audience, territory or brand guideline changes.

### Source limits and qualifications

- **S02**: This geographical variant is not assumed to govern Lucas or any future user.
- **S04**: Exact invocation and binary release must be pinned before future use. These words are not observed target behavior.
- **S06**: Separate EEA/UK/Switzerland terms linked; the governing variant is unknown.
- **S08**: Original developers.openai.com/codex/app-server route redirects to this official page. Auth-mode facts: [R-F §1.2](../rf/report.md#codex-app-server-facts).
- **S09**: Retrieved through official developers.openai.com/codex/noninteractive redirect; no invocation performed.
- **S15**: The precise CLI/account coverage of this general usage page remains a profile question; no target account read.
- **S18**: First excerpt is Code Assist Standard; second Enterprise. They are not an unlimited-fan-out grant or evidence of this user's limits.
- **S22**: Qualifier retained: the automated-access wording is not quoted as a universal ban on all automation.
- **S28**: Scope of Portal/service terms over a solely local Hermes build is unknown; not presumed.
- **S29**: Public technical documentation successfully read on the stated retrieval date; not an upstream entitlement grant.
- **S31**: Generic documented path, never read locally; no credential value collected.
- **S33**: README retrieved successfully at immutable commit. A root LICENSE retrieval separately failed; its inherited R-C pin is not described as freshly verified.

Comparison interpretation: these evidence-review alternatives are architectural inferences, not rival legal conclusions. Each must preserve the same complete profile/question coverage, independent factual evidence, governing-instrument scope and Owner/counsel gates. A decisive comparative falsifier is a required material distinction or condition that one representation cannot preserve or independently reconcile while the other can; if both pass, compare reviewer error and maintenance burden on the same bounded cases. Existing falsifiers remain rejection-sensitivity tests, and all non-proofs still apply. No counsel contact or legal determination occurred.
