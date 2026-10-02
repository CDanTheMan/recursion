# Recursion route terms and licensing questions for counsel

R-C public evidence packet | Retrieved 2 October 2026 | Legal-risk research, not legal advice

## Purpose and decision boundary

What route-specific conditions, agreements and distribution controls would qualified counsel require before Recursion ships or claims support for the configurations below? This packet supplies public evidence and questions, not a lawful/unlawful finding, an infringement opinion, a clearance statement or a decision closing G-32.

Supplied project decisions remain fixed: D-021 prefers delegation to user-authenticated local tools; D-026 chooses Apache-2.0 for Recursion's own release; D-027 authorizes this counsel-ready research with no spending or legal engagement. They are project directions, not legal findings. Recursion is its own harness and a harness orchestrator. Hermes is one potential delegated harness, not Recursion's executive control plane. No assumption that credential intermediation is the only relevant contractual restriction is adopted.

The nine mandatory routes are Claude Code, Codex/ChatGPT, Cursor, Gemini/Google CLI, Grok Build, Hermes, OpenCode, Antigravity and Pi. Component examples are separately scoped. No additional service route is silently selected. No counsel was contacted, no account was accessed, no credential was collected, no model request was made, and no upstream code was executed.

## How to use the evidence

Every source excerpt in the register is classified source-documented, meaning that the stated public text was retrieved, not that it governs a particular deployment. Unknown means the public record reviewed does not settle the point. A technical authentication surface is evidence of implementation, not permission. A source-code license is evidence about the identified source, not an entitlement to a hosted service, a branded binary, an extension marketplace or a logo.

All public retrievals occurred on 2026-10-02 UTC. Effective, last-updated and commit dates are recorded as different fields; an undated page is not assigned an invented effective date. Terms pages remain mutable even when their displayed date is unchanged. License copies have immutable commit links and SHA-256 hashes in the evidence manifest. A moving documentation URL is a retrieval-dated public observation, not an immutable version pin.

Revalidation triggers used in every evidence row:

- T: a terms/AUP revision, incorporation change, jurisdiction, tier, contracting entity, private order/MSA, account owner, billing or audience change
- D: a documentation, client/auth-flow, API, token-custody, endpoint, deployment or commercial-hosting change; also every T trigger
- R: a source commit, package/release, binary build, dependency, vendored asset, notices or redistribution channel change
- M: a brand guideline, logo, product name, marketing copy, prominence, endorsement implication, recipient or distribution change

Could counsel require a release-time recheck and retain a dated approved configuration for each route, rather than accepting a timeless route-level yes/no? No polling, account inspection or release implementation is commissioned by this packet.

## Questions 1 to 4 by route

### Claude Code

Evidence anchors: C1 to C6; immutable source license below. C1 distinguishes an unmodified Claude Code binary authenticated by its end user from third-party developers offering Claude login in their own apps or collecting/intermediating session credentials. The page describes own-user direct billing, preservation of built-in authentication choices and conditions for preinstallation or execution in another product. It assigns consumer versus commercial terms by plan. C5 describes a non-interactive CLI; C2 contains an automated-access exception tied to API keys or explicit permission. C3 addresses downstream products and service resale separately. C4 extends AUP coverage to authorized passthrough users.

Questions for counsel:

- For an owner-operated local Recursion process invoking the installed unmodified CLI, how do C1's hosting/product conditions and C2's automation language apply to the exact plan and jurisdiction? Does unattended repetition change that answer?
- Which acts count as collecting, storing, routing or intermediating credentials or usage: inheriting an environment, launching an authenticated process, forwarding its output, accepting a setup token, managing remote machines, or operating a multi-user service? Which precise boundary does C1 document and which remains unknown?
- If Recursion charges for orchestration while the user pays Anthropic directly, what contract, billing separation and representations are required? Could optional installation, bundling or disabling a login choice change applicability?
- Which principal and agreement apply to subscription OAuth, API-key and cloud-provider modes? Can counsel reconcile plan-specific terms with the actual installed version and any negotiated agreement?

Public-record distinction: explicit in C1 for specified own-user/unmodified-binary versus third-party-credential cases; exact Recursion implementation remains unknown. Service resale, quota and AUP review remain separate questions.

### Codex and ChatGPT

Evidence anchors: O1 to O6. O3 states a local/open-source continuation position and a different commercial/hosted position for App Server authentication. It separately documents API-key storage, Codex-managed ChatGPT OAuth and experimental externally supplied ChatGPT tokens. O2 addresses API integration into customer applications, account resale, single-end-user accounts, API-key transfer and usage-limit avoidance. O1 has individual-account and programmatic-extraction language. O5 describes a distinct registered sign-in route for eligible plan usage.

Questions for counsel:

- Is the specified Recursion edition a local or open-source application, a commercial service, a hosted service, or more than one? Does O3's App Server statement attach to authentication only, to runtime invocation or to both?
- How do the product-specific statements relate to O1, O2, incorporated service terms and a user's exact plan? What evidence would establish continued local use or a required Sign in with ChatGPT registration without presuming eligibility?
- If the parent merely speaks JSON-RPC to a local already-authenticated child and never reads OAuth tokens, what obligations remain? Would external-token mode, refresh callbacks or a hosted relay materially change the analysis?
- Can a registered sign-in integration, direct API integration and subscription-backed CLI be treated as separate routes with separate identities, billing and quotas? What changes would require provider confirmation?

Public-record distinction: O3 documents distinct auth custodians and local/open-source versus commercial/hosted scope. It does not establish a universal installed-CLI exception or approve the proposed Recursion distribution. Unknown: exact tier, contract hierarchy, edition classification and registered integration eligibility.

### Cursor

Evidence anchors: U1 to U6. U3 distinguishes browser login with local credential storage from a user API key recommended for automation. U4 describes headless scripts. U2 includes broad non-human-access, resale, copying, rate-limit, usage-metering and account-provisioning language and applies model-provider AUPs too. U1 points organizational MSA users to their MSA and retains service rights.

Questions for counsel:

- How should the apparently broader AUP automation language be reconciled with the officially documented CLI/headless/API-key workflows for the specific paid tier and MSA?
- Does an already-authenticated CLI driven through a local process differ contractually from Recursion handling the Cursor API key or browser credential? The reviewed text does not expressly resolve that distinction; what written clarification, if any, is needed?
- What user identity, account responsibility, fee allocation and concurrency limits follow a delegated run? Does a user API key represent a Cursor account entitlement rather than a third-party model API entitlement?
- What distribution or paid-wrapper acts would implicate the separate copying, redistribution, resale and competitive-service language, including use of an upstream model through Cursor?

SDK profile question: U5 and U6 separately document local-loop and Cursor-hosted execution, user/service-account API-key authentication, and corresponding user/team billing. TypeScript also describes SDK-managed browser provisioning and storage of a user key, plus embedding bundles. Stored-key reuse is distinct from supplying an explicit key argument or environment variable on every later call. How do CLI delegation, SDK local runtime, SDK cloud runtime and REST cloud agents differ under U1/U2, SDK package licenses, consent and distribution terms? Who owns and stores the key, who authorizes its provisioning, and does Recursion hold it or merely drive a separately authenticated CLI? No SDK or account operation was performed.

Public-record distinction: technical auth methods are source-documented; third-party local-driving exception and credential-intermediation boundary remain unknown. Headless documentation is not used to override the AUP.

### Gemini and Google CLI

Evidence anchors: G1 to G9. G1 separates Google-account Code Assist, Gemini Developer API and Vertex AI authentication and specifies different terms by service/edition. It directly discusses third-party access to the service behind the CLI using CLI OAuth. G7 describes programmatic headless operation. G3 addresses documented API means, client identity, developer credential confidentiality, API sublicensing and quotas. G4 distinguishes paid/unpaid and regional use; G5 and G6 address Cloud restrictions.

Questions for counsel:

- Does G1 distinguish Recursion invoking the installed Gemini CLI from Recursion directly accessing Code Assist using the CLI's token, and which parts of that distinction are explicit versus still unknown?
- Which agreement controls Google-account individual, AI Pro/Ultra, Code Assist Standard/Enterprise, Gemini API paid/unpaid and Vertex-backed runs? Could organizational entitlement override a personal subscription assumption?
- Which identity is presented by the actual CLI or API client, and would altering client IDs, headers, token paths or refresh ownership violate applicable identity requirements?
- How should retries, quota fallback and account selection be constrained under G3/G5, without treating ordinary efficient scheduling as proven circumvention or as automatically acceptable?

Public-record distinction: direct third-party service/OAuth access is expressly addressed; installed-CLI orchestration is not expressly resolved in the reviewed legal text. API-key routes require their own terms and cannot be inferred from the CLI source license.

### Grok Build

Evidence anchors: X1 to X5 and E2. X5 documents browser OIDC, device code, external auth-provider commands and API keys, with mode-dependent principal and credential precedence. X4 demonstrates headless/ACP auth using cached login or an API key. X2 describes API-integrated bundled services and permitted users; X3 includes unauthorized automation, service resale/distribution and rate-limit language. X1 and X2 are separate consumer and business instruments, branded SpaceXAI on retrieval.

Questions for counsel:

- Which instrument and order form govern the user's Grok Build entitlement? Does the documented automation make this particular third-party local driver an authorized means under X3, or is additional evidence required?
- Does the answer differ for the user's cached local session, direct API key, corporate IdP, external token broker or remotely hosted CLI? No general local-driving versus credential-custody carve-out was identified in X1 to X3.
- What is the boundary between X2's API-integrated bundled service and bare resale of access? Are ordinary paid orchestration, multi-tenant dispatch and direct end-user billing treated differently?
- How do team identity, key identity, quota ownership and upstream source/binary differences affect the route record?

Public-record distinction: technical auth surfaces are explicit; the specific legal boundary between local invocation and credential intermediation is unknown. Apache-2.0 source evidence does not answer service access or trademark questions.

### Hermes

Evidence anchors: H1 to H3. H2 documents three external-driving protocols. H3 documents a local API bearer credential distinct from the downstream provider credential; it is required even on loopback. H1's platform scope includes Portal/inference services and contains individual login, connected-account, quota, automation, redistribution and plugin clauses. Its automatic-request exception references programs made available by Nous. The local Hermes source license is separate.

Questions for counsel:

- Is the proposed path local Hermes plus a direct third-party provider, Nous Portal, Hermes Cloud or a connected-account integration? Which H1 provisions apply to each, if any?
- Does driving a Nous-provided local process fit the H1 automation exception, and does adding an external orchestrator change that? Would passing only a local API bearer differ from reading or relaying a provider OAuth token?
- Who authenticates, pays and accepts each upstream provider's terms? Can the provider consent to Nous's particular integration be assumed to extend to Recursion, or must it be separately evidenced?
- What obligations attach to reselling hosted access, quota rotation, redistributed plugins and Nous branding under the relevant scope?

Public-record distinction: local caller authentication versus provider authentication is technically documented; general legal permission for orchestration or inherited upstream entitlement is unknown. No executive-control role for Hermes is assumed.

### OpenCode

Evidence anchors: P1 to P3. P1 expressly distinguishes non-hosted open-source software from website, inference and hosted services. For the latter it addresses internal use, programmatic extraction, bulk-account circumvention, account transfer and third-party model access rights. P2 documents provider credentials stored locally; P3 documents a server interface. None of those technical facts establishes a provider's authorization to reuse a subscription.

Questions for counsel:

- Is the route a local MIT-licensed OpenCode build using a user's direct provider entitlement, OpenCode Zen/Go inference, a hosted offering, or a combination? Which P1 scope governs each layer?
- Does local server/CLI delegation leave model credential custody wholly with OpenCode? What evidence must show that Recursion does not read or relay those credentials, and would that distinction alter the contract analysis?
- How do P1's hosted-service restrictions apply to an orchestrator forwarding outputs, running unattended or offering a paid integration? Is there a separate agreement qualifying them?
- Which provider identity and upstream terms apply for each selected provider/auth mode? What is the required separation of local software licensing, OpenCode service entitlement and upstream model policy?

Public-record distinction: non-hosted software versus hosted/inference services is expressly documented; legal treatment of installed-client driving versus credential intermediation remains provider- and configuration-specific and unknown here.

### Antigravity

Evidence anchors: A1 to A5 plus applicable Google sources. A1 section 6 addresses third-party tools accessing the service, with an OAuth example. Its opening excludes specified enterprise/Workspace/API-key arrangements in favor of administrator-accepted terms. A2 documents headless cached credentials. A3 documents a Gemini API-key mode that does not establish an account session. A1 also points selected third-party models to their terms.

Questions for counsel:

- Does section 6 reach orchestration of the installed unmodified CLI, direct service access with Antigravity OAuth, both, or a narrower configuration? Its breadth must be reconciled with A2, not resolved merely by the existence of headless mode.
- Which personal, enterprise, Workspace, Gemini Enterprise-key or Gemini API-key instrument applies to the exact edition? Are the two named API-key products distinct for this purpose?
- Which principal, billing account and underlying provider receive a delegated run? Do custom endpoints, copied caches, remote hosting or alternative models alter the terms stack?
- What binary redistribution and asset permissions would apply to optional installation, preinstallation, wrapping and logo display? Public blanket bundling permission remains unknown.

Additional profile question: A4 distinguishes its local Python SDK from the managed cloud agent API and documents Gemini-key or Google Cloud credential modes; A5 describes the managed Antigravity agent through the Gemini Interactions API. How should counsel separately classify cached CLI, CLI API-key, local SDK, Vertex-authenticated SDK and managed Interactions profiles, including preview terms, data location, package licenses and billing identity? These profiles are not interchangeable solely because they share the Antigravity name.

Public-record distinction: technical session versus API-key operation is explicit; no installed-CLI legal exception was identified. The enterprise carve-out requires the actual administrator agreement, not an assumed consumer answer.

### Pi

Evidence anchors: I1 and pinned MIT source license. I1 documents print, JSON, RPC and SDK use and connecting a subscription or API key. A separate generally applicable hosted Pi-service terms/AUP instrument, subscription resale rule or Pi-specific credential-intermediation policy was not established in the reviewed primary sources.

Questions for counsel:

- Which exact Pi build, provider plugin, model endpoint and authentication mechanism form the proposed route, and whose terms apply beyond Pi's source license?
- Does the chosen provider authorize this installed-client use, the plugin's login mechanism and any delegated traffic? A Pi login feature alone is not evidence of provider permission.
- Which provider identity, token owner and account entitlement are presented? Does invoking Pi locally differ from a hosted Pi service or extracting provider tokens, and what public/private evidence closes that unknown?
- What source, binary, extension and name/logo permissions attach to the actual package? What notice and dependency evidence would accompany redistribution?

Public-record distinction: automation surfaces are documented; service, resale, quota and credential rules depend on the selected upstream and remain unknown until specified. Absence of a located Pi-specific policy is not absence of restrictions.

## Question 5 distribution and trademark evidence matrix

Each source-license label below is a quotation from the identified license title or text, not an opinion about all assets in a distribution. Dates and exact pinned URLs appear in the license register. Every row expires on R and M changes, and on T changes if a service is involved.

| Route | Source and binary question | Trademark and attribution question | Bundled assets or notices question |
|---|---|---|---|
| Claude Code | Pinned repository says all rights reserved and links commercial terms. How do C1's unmodified-binary conditions apply to an optional installer or packaged copy? | How do C1's plain-text interoperability description and B1's approval conditions apply to proposed naming and logos? | Which released binary notices, licenses and install terms apply beyond the public repository file? |
| Codex/ChatGPT | Pinned Codex source is Apache-2.0. Which compiled CLI assets match that tree, and which ChatGPT app/service elements are separate? | Which proposed words, icons and product names fit B2? Does a service-auth flow create additional branding requirements? | Which NOTICE files, vendored crates, platform binaries and installer assets must travel with the exact artifact? |
| Cursor | U1 retains service rights; public blanket source/binary redistribution grant is unknown. What downloadable-software agreement controls the exact build? | B3 supplies design assets; what permission covers a connector icon, compatibility prose or product title? | Which Code OSS, Electron, extension and proprietary assets are included and separately licensed? |
| Gemini CLI | Pinned CLI source is Apache-2.0. How should an official npm package, rebuild and external Google service be separated? | How do B4 and the relevant product/API attribution rules apply to prose and logos? | What notices and dependency licenses belong to the actual release and optional extensions? |
| Grok Build | Pinned first-party source is Apache-2.0. Which official binary contents and release terms differ from the source tree? | How does B5 constrain app titles, names, mark prominence and modified builds? | E2 identifies upstream ports, UI themes and vendored material. Which notices and file-specific licenses survive packaging? |
| Hermes | Pinned source is MIT. Which desktop/CLI package and plugin assets are independently covered, and when does H1 apply? | What does H1 section 12.1 require for Nous materials? Separate local-Hermes mark policy remains unknown. | Which third-party skills, browser components, plugins and provider adapters need separate inventories? |
| OpenCode | Pinned source is MIT. How does P1's non-hosted scope separate a local rebuild from Zen/Go and hosted services? | B6 exposes assets; what license or authorization covers reuse beyond descriptive interoperability prose? | Which v1/v2 packages, desktop assets and plugins are included; does a copied plugin retain its own license? |
| Antigravity | Public blanket source or binary redistribution license is unknown. What official download terms and third-party notices apply? | B7 is a press-assets page. Does the intended product UI or promotion fall within that scope, and what Google approvals apply? | Which Code OSS-derived, proprietary and third-party model components can be redistributed in the proposed package? |
| Pi | Pinned source is MIT. Which published package files and optional extensions fall under it? | Separate project name/logo reuse policy is unknown. What jurisdiction-specific trademark review is needed? | Which extension packages, dependencies and copied provider adapters require their own licenses and attribution? |

## Question 6 candidate Apache obligations for counsel

With D-026 fixed, can counsel map these public text anchors to the actual artifact rather than infer requirements from a project-level license badge?

1. Under L1 sections 3 and 4, what patent-grant scope, patent-litigation termination condition, license-copy delivery, modification marking, source-notice retention and relevant NOTICE reproduction apply to the exact copied or modified material? Does the package inventory identify all applicable notices?
2. Under L1 section 6 and each B source, what use of upstream names is required for attribution, permitted for description, or separately subject to trademark permission? Should logos be reviewed independently from textual credits?
3. Under L2, which retained MIT notices belong to the included source or substantial portions, and how should they appear in binary distributions? What asset-specific license exceptions are present?
4. How should individual plugin licenses, documentation licenses, fonts, icons, themes, models, sample data and generated assets be recorded and distributed? Is each item copied, linked, fetched after opt-in or entirely user-supplied?
5. What SBOM/provenance evidence should accompany the release: package identity/version, immutable upstream URL, hash, declared/concluded license, file exceptions, dependencies, notices, build origin and redistribution channel? L5 offers a standard vocabulary; it is not evidence that an SBOM is universally mandated or that a complete license analysis has occurred.
6. Which customer, procurement, jurisdictional or sector requirements add SBOM, security, export, privacy or attribution duties beyond the source licenses? Those facts are not supplied here and remain counsel inputs.

## Question 7 competing distribution postures

These are cases for comparison, not selected product defaults. For each, what would disprove the intended legal boundary?

| Candidate case | Competing case | Counsel question and decisive disconfirming evidence | What it does not resolve |
|---|---|---|---|
| Ship only Recursion adapters and require separate user installation | Preinstall the unmodified upstream client | Does no redistribution occur in the actual package/install chain? A packaged executable, copied asset or mirror download would disconfirm that premise. | Hosted-service automation, entitlement, naming and contractual use restrictions |
| Bundle an upstream source rebuild with notices | Call the user's vendor-distributed executable | Which file/build licenses govern the rebuild? A file-specific exception, proprietary dependency or incomplete source/binary mapping would defeat a blanket root-license assumption. | Provider access or brand permission |
| Provide a purely local single-user orchestrator | Offer managed remote or multi-tenant execution | Does any server receive user tokens or provide pooled service access? A relay, central refresh owner or shared account would disconfirm the local-only premise. | Local mode's own terms or exact commercial classification |
| Charge for orchestration with direct user-provider billing | Charge for an integrated service through a specific provider contract | What service is sold and who owns the account? Invoices, entitlements or token flow inconsistent with the stated separation would disconfirm it. | Resale definitions, taxes, contract hierarchy or consumer obligations |
| Name interoperability in plain text | Display vendor marks/logos or co-brand | Does the copy merely identify an integration? A feature/product name, dominant logo or endorsement implication would disconfirm that characterization. | Jurisdiction-specific nominative use or vendor-specific approval |
| Publish the plugin contract and original examples without third-party code | Ship ports, SDK code or curated plugin bundles | Can provenance show original authorship? Copied interface text, schemas, examples, icons or implementation files would defeat the no-third-party-material premise. | Patent, contributor title, interoperability or service permissions |

Public examples for these questions: C1 discusses hosted/preinstalled unmodified binaries; O3 distinguishes authentication use cases; P1 separates non-hosted source from services; E2 separates first-party and vendored materials; V1 to V3 separate editor source, branded product and extension acquisition. They illustrate different published postures and are not legal precedents clearing Recursion.

## Questions 8 and 9 Recursion licensing posture

D-026's Apache-2.0 choice for Recursion remains the project direction. The following alternatives concern contribution process, optional components, interfaces, documentation or trademark policy; they do not reselect Recursion's own license.

- Contribution provenance: Would Apache inbound-equals-outbound treatment with documented sign-off be adequate, or is an individual/corporate CLA needed? Compare L1 section 5, L3 and L4. What employer authority, patents, AI-assisted contribution records and third-party attribution must be checked? A missing rightsholder authorization would disconfirm an assumption that a contributor's click-through or sign-off alone establishes title.
- DCO versus CLA: Would DCO 1.1 certification plus retained provenance records meet the project's goals, or should a tailored CLA grant additional rights? Neither example establishes that the submitter actually owns every contribution; neither chooses a future relicensing policy. What data-retention notice is appropriate for public sign-offs?
- SDK and interface publication: Should original SDK code, schemas and examples also be Apache-2.0, or should separable specification text and documentation have distinct SPDX-identified licenses? What exact files, patents and generated bindings would each cover? Discovery of copied third-party material or an upstream specification license would disconfirm a universal original-authorship assumption.
- Independently authored plugins: Would permissive plugin licensing, file-level MPL-2.0, GPL-3.0-only or AGPL-3.0-only be appropriate for separate optional plugins? L6 to L8 are text anchors for counsel. What constitutes a combined or derivative work, what source-delivery or network-interaction provision would apply, and can the proposed boundary preserve D-026? Merely communicating over an interface does not resolve these questions.
- Trademark posture: Should Recursion publish a separate project-name/logo policy, or initially rely on case-by-case permissions and descriptive-name guidance? What searches, classes, territories and ownership evidence are needed before adopting or registering the name? An existing conflicting mark or a contributor-owned logo would disconfirm an unreviewed name/asset assumption.
- Notices and compatible permissive components: What review shows compatibility for each exact Apache, MIT or other component, including patent conditions and third-party notices? Should notices be assembled centrally, component-locally or both? A missing license, mixed-license subtree or binary-only asset would defeat a root-license-only process.

No alternative establishes service access, trademark clearance, patent freedom, contributor title, enforceability or compatibility merely because its SPDX identifier is known.

## Component and extension appendix

These are distribution questions prompted by portability research, not additional mandatory service-route approvals.

- VS Code and extensions: V1 expressly separates the MIT source repository from Microsoft's branded product and each extension's own license. V3 addresses in-scope products, acquisition through supported interfaces and publisher-specific terms; V2 provides explanatory context. Would a port use independently licensed source, a Marketplace-acquired VSIX, an official branded build, Code OSS or a third-party registry package? Which of those exact artifacts may Recursion redistribute or execute outside the listed product family? Technical API compatibility does not answer this.
- DeepSeek Harness and Cordis: The pinned root LICENSE is MIT; E1 points to separate dependency notices. Which vendored Cordis files, upstream commits, notices and trademarks are actually copied into a port? Does the preview API's instability affect provenance maintenance? No blanket inference is made about every vendored file or the DeepSeek hosted API.
- Goose and MCP: The pinned Goose root is Apache-2.0. The retrieved MCP LICENSE describes a transition: new code/specification contributions under Apache-2.0, non-specification documentation under CC-BY-4.0, and earlier unconsented contributions retaining MIT. Which actual files and SDK versions are reused? How does counsel document mixed provenance rather than assign one license to the entire protocol ecosystem?
- OpenCode v1 and v2: Which exact source revision, npm package, generated SDK and plugin artifact is being ported? Is a current dev-root license sufficient for a historical v1 artifact or a separately published v2 package? What release manifests and per-file terms would close the gap?
- Provider plugin surfaces: E3 describes an interoperability specification. What licenses cover the actual schema, examples and implementations? What independent marketplace submission, security, privacy, model-access and branding conditions apply for an OpenAI, Anthropic or Cursor plugin? Publishing a portable plugin format does not establish permission to republish another author's plugin.

## Question 10 local handoff and G32 closure checklist

Lucas engages qualified counsel. This packet authorizes no outreach, payment, legal engagement, acceptance of terms or change to a provider account. G-32 remains open pending counsel's response and the project's independent acceptance process.

For each item below, can counsel return a written, dated answer that identifies the factual configuration, governing instruments, unresolved assumptions, required conditions and a re-review trigger? A generic statement that a route is acceptable is not a substitute for the requested configuration-specific record.

| ID | Question only counsel can answer | Exact missing inputs and evidence to supply locally |
|---|---|---|
| Q01 | Which jurisdiction, legal entity and contract stack governs each route? | Owner/operator and user jurisdictions; entity; business/consumer role; exact tier; accepted terms versions; order forms/MSAs; admin policies and precedence clauses |
| Q02 | How is local installed-client driving distinguished from credential or usage intermediation? | Per-route process/sequence diagram; credential owner and store; environment inheritance; refresh owner; bytes crossing each boundary; logs/redaction; no real secrets in the diagram |
| Q03 | Which headless, scheduled, unattended, remote and commercial uses are covered? | Exact binary version/hash, command or RPC surface, concurrency, duration, user presence, machine ownership, local/hosted topology and factual load profile |
| Q04 | How do subscription sessions, API keys, enterprise principals and registered integrations differ? | Entitlement proof; account holder and payer; endpoint/model; scopes and client identity; provider registration/private permission if any; upstream terms for selected provider |
| Q05 | What does resale, bundled service or account sharing mean for the proposed commercial model? | Product/pricing description; billing flows; user-provider relationship; contracts; who can invoke a run; tenant/account isolation; whether usage is pooled |
| Q06 | What behavior could constitute quota/rate-limit avoidance under the governing text? | Retry/backoff, fallback and routing policy; account rotation behavior; official limit definitions; admin settings; no assumption that a missing meter means zero |
| Q07 | What may be bundled, downloaded, modified or redistributed? | Exact release file manifest; source commits; binary hashes; dependency lockfiles; installer/mirror behavior; optional versus default assets; per-file LICENSE/NOTICE and change records |
| Q08 | What attribution and trademark treatment is required for each name, logo and asset? | Proposed UI screenshots, README/marketing wording, product/feature names, logo source and license, prominence, target markets and any actual permission letters |
| Q09 | What contribution and IP process implements D-026? | Rights-holder identity; employee/contractor contribution authority; chosen CLA/DCO draft; inbound/outbound policy; AI-assisted provenance; patent concerns; third-party imports |
| Q10 | Which licenses and publication terms attach to the early plugin contract and SDK? | File-by-file interface/specification/SDK/examples/docs boundary; SPDX identifiers; copied versus original content; dependencies; intended optional plugin licenses |
| Q11 | Which privacy, security, export or sector duties apply to delegated data and accounts? | Data categories and subjects; storage/telemetry/processors; destinations/regions; subprocessors; customer contract requirements; restricted-use cases and retention rules |
| Q12 | What exact evidence and acceptance closes G-32, and what changes reopen it? | Dated counsel response mapped to Q01-Q11 and all nine routes; conditions and unknowns; approved artifact/architecture versions; local verification records; independent review and Owner acceptance |

Suggested evidence packet layout for local counsel handoff: the supplied project decisions; this question packet; public-source register; immutable license manifest; a redacted per-route implementation/identity sheet; actual applicable private contracts; release inventory/SBOM; proposed distribution and branding samples; contributor-policy drafts; and the counsel response matrix. Private contracts, account identifiers and credentials belong in the Owner's chosen secure counsel channel, not in a public research query.

A local technical reviewer can later verify factual process boundaries and release contents without declaring legal compliance. What technical tests and documents would counsel require for each answer, and who independently verifies that the shipped build matches the reviewed facts?

## Completion gate record

| Gate | Research status and limitation |
|---|---|
| All ten research questions | Addressed by route sections Q1-Q4, distribution Q5, Apache Q6, competing cases Q7, project posture Q8-Q9 and local handoff Q10 |
| Nine route terms and credential rows | Present with quoted public anchors and retrieval dates; specific unknowns retained |
| Installed CLI versus credential custody | Separately recorded for every route; technical surface never substitutes for legal permission |
| Source versus service versus binary versus trademark | Separate registers and distribution questions; no root-license clearance inference |
| Accepted Apache direction | D-026 preserved; component and contribution alternatives remain questions |
| Competing postures and falsifiers | Included with disconfirming evidence and limits |
| G32 closure | Not closed; requires qualified counsel and independent project acceptance |
| Protected paths and privacy | Only new-packet brief/README and public sources used; no old Recursion checkout or earlier report consulted; no protected project file modified |
| Quotes and final artifact | Short excerpts checked against per-source quotation limits; deterministic scan and full-page DOCX render review recorded separately |

## Public evidence register

All rows: source-documented public text; retrieval date 2026-10-02 UTC. Applicability remains a counsel question. Separate quotation fragments are divided by a semicolon. Trigger codes are defined above.

### Claude Code and OpenAI

| ID and authority | Public evidence excerpt | Source and version | Recheck |
|---|---|---|---|
| C1 · Anthropic product-specific legal guidance | “The Claude Code binary must not be modified.”; “developers may not collect, store, or intermediate Claude.ai credentials or session tokens” | [Claude Code legal and compliance](https://code.claude.com/docs/en/legal-and-compliance); No effective date displayed; Offering Claude Code; authentication | T |
| C2 · Vendor terms or policy | “automated or non-human means”; “or resell the Services” | [Anthropic consumer terms](https://www.anthropic.com/legal/consumer-terms); Effective 2025-10-08; retrieved EEA/Switzerland consumer variant; Sections 2 and 3 | T |
| C3 · Vendor terms or policy | “resell the Services except as expressly approved by Anthropic” | [Anthropic commercial terms](https://www.anthropic.com/legal/commercial-terms); Effective 2025-06-17; A.1; D.2; D.4 | T |
| C4 · Vendor terms or policy | “including via any authorized resellers or passthrough access” | [Anthropic usage policy](https://www.anthropic.com/legal/aup); Effective 2025-09-15; Scope; additional agentic use guidelines | T |
| C5 · Vendor technical documentation only | “To run Claude Code in non-interactive mode” | [Claude Code programmatic mode](https://code.claude.com/docs/en/headless); Undated live documentation; Introduction; Basic usage | D |
| O1 · Vendor terms or policy | “Automatically or programmatically extract data or Output”; “You may not share your account credentials” | [OpenAI Terms of Use](https://openai.com/policies/terms-of-use/); Effective 2026-01-01; separate EEA/UK/Switzerland terms linked; Registration; Using our Services | T |
| O2 · Vendor terms or policy | “buy, sell, or transfer API keys from, to, or with a third party” | [OpenAI Services Agreement](https://openai.com/policies/services-agreement/); Updated 2025-12-01; effective 2026-01-01; 2.2; 3.1 to 3.3 | T |
| O3 · OpenAI product-specific authentication guidance | “App-server authentication has never been permitted for commercial or hosted services.” | [Codex App Server](https://learn.chatgpt.com/docs/app-server); Undated live documentation; redirected from developers.openai.com/codex/app-server; Auth endpoints; Authentication modes | D |
| O4 · Vendor terms or policy | “circumventing our safeguards” | [OpenAI usage policies](https://openai.com/policies/usage-policies/); Effective 2025-10-29; Protect people | T |
| O5 · OpenAI integration documentation; eligibility is not established | “use their ChatGPT plan for eligible AI requests in your app” | [Sign in with ChatGPT](https://developers.openai.com/siwc); Undated live documentation; Introduction; Get started | D |

### Cursor and Google

| ID and authority | Public evidence excerpt | Source and version | Recheck |
|---|---|---|---|
| U1 · Vendor terms or policy | “There are no implied licenses in these Terms” | [Cursor Terms of Service](https://cursor.com/terms-of-service); Last updated 2026-09-03; Intro MSA; 1.7; 3; 5.1 | T |
| U2 · Vendor terms or policy | “Accessing the Service through automated or non-human means, whether through a bot, script, or otherwise” | [Cursor Acceptable Use Policy](https://cursor.com/acceptable-use-policy); Last updated 2026-08-11; Scope; Comply with the law | T |
| U3 · Vendor technical documentation only | “For automation, scripts, or CI environments, use API key authentication” | [Cursor CLI authentication](https://cursor.com/docs/cli/reference/authentication); Undated live documentation; Browser authentication; API key authentication | D |
| U4 · Vendor technical documentation only | “Use Cursor CLI in scripts and automation workflows” | [Cursor headless CLI](https://cursor.com/docs/cli/headless); Undated live documentation; Introduction; How it works | D |
| G1 · Google product-specific legal guidance | “Directly accessing the services powering Gemini CLI”; “using third-party software, tools, or services” | [Gemini CLI terms and privacy](https://geminicli.com/docs/resources/tos-privacy/); Last updated 2026-04-10; Introduction; authentication table | T |
| G2 · Vendor terms or policy | “using automated means to access content from any of our services” | [Google universal terms](https://policies.google.com/terms); Effective 2026-07-30; US country variant; Do not abuse our services; Software | T |
| G3 · Vendor terms or policy | “Developer credentials may not be embedded in open source projects.” | [Google APIs Terms](https://developers.google.com/terms); Last modified 2021-11-09; 2(c)-(e); 4(a)-(b); 6 | T |
| G4 · Vendor terms or policy | “for developers building with Google AI models for professional or business purposes” | [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms); Effective 2026-03-23; Use Restrictions; paid and unpaid services | T |
| G5 · Vendor terms or policy | “to circumvent Service-specific usage limits or quotas” | [Google Cloud terms](https://cloud.google.com/terms); Last modified 2026-09-02; 3.3 Restrictions | T |
| G6 · Vendor terms or policy | “to alter, disable, interfere with or circumvent any aspect of the Services” | [Google Cloud AUP](https://cloud.google.com/terms/aup); Last modified 2026-06-23; All Services | T |
| G7 · Vendor technical documentation only | “Headless mode provides a programmatic interface to Gemini CLI” | [Gemini headless mode](https://geminicli.com/docs/cli/headless/); Last updated 2026-03-10; Introduction; Technical reference | D |

### Grok Hermes OpenCode Pi and Antigravity

| ID and authority | Public evidence excerpt | Source and version | Recheck |
|---|---|---|---|
| X1 · Vendor terms or policy | “If you do not have a valid contract with us, you are prohibited from using our Service.” | [SpaceXAI consumer terms](https://x.ai/legal/terms-of-service); Last updated 2026-09-11; Scope; 2; 3 | T |
| X2 · Vendor terms or policy | “Customer may only provide End Users with access to the Services as part of a Bundled Service.” | [SpaceXAI enterprise terms](https://x.ai/legal/terms-of-service-enterprise); Last updated 2026-08-14; customer effective date depends on purchase/order; 1.1; 1.2; 2 | T |
| X3 · Vendor terms or policy | “Accessing the Services through unauthorized automated or non-human means, whether through a bot, script, or otherwise” | [SpaceXAI acceptable use policy](https://x.ai/legal/acceptable-use-policy); Effective 2026-08-14; Comply with the law | T |
| X4 · Vendor technical documentation only | “Run grok login first, or set XAI_API_KEY.” | [Grok Build headless scripting](https://docs.x.ai/build/cli/headless-scripting); Last updated 2026-06-10; ACP scripting example | D |
| X5 · Vendor technical documentation only | “Grok Build supports four session authentication methods” | [Grok Build enterprise deployments](https://docs.x.ai/build/enterprise); Undated live documentation; Authentication; API key; Restricting login methods | D |
| H1 · Nous Portal/platform service terms; scope of local-only Hermes remains a question | “unless such program has been made available by Nous Research” | [Nous Portal terms](https://portal.nousresearch.com/terms); Last update 2026-09-28; 1; 5.2; 10; 12.1; 13 | T |
| H2 · Nous technical documentation only | “Hermes ships three protocols for driving the agent from external programs” | [Hermes programmatic integration](https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration/); Undated live documentation; Introduction; protocol table | D |
| H3 · Nous technical documentation only | “API_SERVER_KEY is required for every deployment” | [Hermes API server](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/); Undated live documentation; July 2026 breaking-change note; Authentication; Security | D |
| P1 · Vendor terms or policy | “only use the Services for your own internal use”; “automatically or programmatically extracts data or Output” | [OpenCode terms](https://opencode.ai/legal/terms-of-service); Effective 2026-08-15; Opening scope; basics; restrictions; Third Party Models | T |
| P2 · Anomaly technical documentation only; generic public path | “they are stored in ~/.local/share/opencode/auth.json” | [OpenCode providers](https://opencode.ai/docs/providers/); Undated live documentation; Credentials; provider setup | D |
| P3 · Anomaly technical documentation only | “opencode serve” | [OpenCode server](https://opencode.ai/docs/server/); Undated live documentation; Introduction; Authentication | D |
| I1 · Maintainer technical documentation only | “automate it in print, JSON, or RPC mode” | [Pi coding agent README](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md); Moving main observed 2026-10-02; Introduction; Getting started | R |
| A1 · Google product terms; enterprise carve-out must be resolved | “Using third party software, tools, or services to access the Service” | [Antigravity Additional Terms](https://antigravity.google/terms); No effective date displayed; Opening enterprise carve-out; sections 4, 6 and 8 | T |
| A2 · Google technical documentation only | “Headless mode uses your cached credentials.” | [Antigravity headless mode](https://antigravity.google/docs/cli/headless/); Undated live documentation; Headless authentication note | D |
| A3 · Google technical documentation only | “the CLI never establishes an account session” | [Antigravity installation and auth](https://antigravity.google/docs/cli/install/); Undated live documentation; Using a Gemini API key; Managing your session | D |

### Trademark and licensing

| ID and authority | Public evidence excerpt | Source and version | Recheck |
|---|---|---|---|
| B1 · Vendor trademark policy | “only in materials we approve beforehand” | [Anthropic trademark guidelines](https://www.anthropic.com/legal/trademark-guidelines); Effective 2024-08-01; Trademark permission | M |
| B2 · Vendor trademark and brand guidelines | “Misrepresent your relationship with OpenAI, imply endorsement, or confuse users about sponsorship” | [OpenAI brand guidelines](https://openai.com/brand/); Undated live guidelines; Logos; Usage terms | M |
| B3 · Vendor asset page; no general reuse clearance established | “Resources to represent Cursor consistently and accurately.” | [Cursor brand guidelines](https://cursor.com/brand); Undated live guidelines; Brand assets | M |
| B4 · Google brand policy; exact use requires relevant product guidance | No excerpt reproduced; identified text supports the linked counsel question | [Google brand overview](https://partnermarketinghub.withgoogle.com/brands/google/overview/); Undated live guidelines; Brand overview | M |
| B5 · Vendor brand guidelines | “Use our Marks in any app title, domain name” | [SpaceXAI brand guidelines](https://x.ai/legal/brand-guidelines); No effective date displayed; Usage terms; Logos | M |
| B6 · Anomaly asset page; no general reuse clearance established | “Resources and assets to help you work with the OpenCode brand.” | [OpenCode brand page](https://opencode.ai/brand); Undated live page; Brand guidelines | M |
| B7 · Google press asset page; scope outside press unknown | “Press Assets” | [Antigravity press assets](https://antigravity.google/press); Undated live page; Press Assets | M |
| L1 · Canonical license text | “This License does not grant permission to use the trade names” | [Apache License version 2](https://www.apache.org/licenses/LICENSE-2.0); Version 2.0 January 2004; Sections 3 to 6 | R |
| L2 · SPDX authoritative license text registry | “The above copyright notice and this permission notice shall be included” | [MIT license text](https://spdx.org/licenses/MIT.html); SPDX MIT identifier; Notice condition | R |
| L3 · ASF project governance example; not mandatory for Recursion | “Contributor License Agreement” | [Apache contributor agreements](https://www.apache.org/licenses/contributor-agreements.html); Undated current ASF policy; Contributor agreements | R |
| L4 · Canonical DCO text | “I have the right to submit it under the open source license” | [Developer Certificate of Origin](https://developercertificate.org/); Version 1.1; copyright 2004 and 2006; Certification (a)-(d) | R |
| L5 · SPDX standard steward; provenance framework, not legal clearance | No excerpt reproduced; identified text supports the linked counsel question | [SPDX overview](https://spdx.dev/learn/overview/); Undated live overview; Overview | R |
| L6 · SPDX license text; component alternative for counsel | No excerpt reproduced; identified text supports the linked counsel question | [MPL 2 license](https://spdx.org/licenses/MPL-2.0.html); MPL 2.0; Sections 3.1 to 3.3 | R |
| L7 · SPDX license text; plugin alternative for counsel | No excerpt reproduced; identified text supports the linked counsel question | [GPL 3 license](https://spdx.org/licenses/GPL-3.0-only.html); GPL 3.0 only; Sections 5 and 6 | R |
| L8 · SPDX license text; plugin alternative for counsel | No excerpt reproduced; identified text supports the linked counsel question | [AGPL 3 license](https://spdx.org/licenses/AGPL-3.0-only.html); AGPL 3.0 only; Section 13 | R |

### Distribution and component examples

| ID and authority | Public evidence excerpt | Source and version | Recheck |
|---|---|---|---|
| V1 · Microsoft branded-product license; distinct from source license | “share, publish, rent or lease the software” | [VS Code product license](https://code.visualstudio.com/license); No effective date displayed; Opening; 1(c)-(d); 5 | R |
| V2 · Microsoft explanatory documentation | “some extensions”; “use proprietary licenses” | [VS Code FAQ](https://code.visualstudio.com/docs/supporting/FAQ); Undated live FAQ; Licensing; Microsoft extensions outside VS Code | D |
| V3 · Microsoft marketplace contract; separate publisher terms | “Marketplace Offerings are intended for use only with In-Scope Products and Services” | [Visual Studio Marketplace terms](https://aka.ms/vsmarketplace-ToU); Last updated September 2025; PDF pages 1 to 3; sections 1 to 3 | T |
| E1 · Maintainer source and packaging documentation | “Third-party dependencies and their licenses are disclosed” | [DeepSeek Harness README](https://github.com/deepseek-ai/deepseek-harness); Moving master observed 2026-10-02; License; Developer preview | R |
| E2 · Vendor source and packaging documentation | “Third-party and vendored code remains under its original licenses.” | [Grok Build README](https://github.com/xai-org/grok-build); Moving main observed 2026-10-02; License; third-party notices | R |
| E3 · Interoperability specification; not blanket marketplace or package license | No excerpt reproduced; identified text supports the linked counsel question | [Agent Plugins specification](https://agent-plugins.org/specification); Version 1.0.0 stated on page; Specification | R |

### Cursor SDK scope evidence

| ID and authority | Public evidence excerpt | Source and version | Recheck |
|---|---|---|---|
| U5 · Vendor SDK documentation; local/cloud execution is not a service permission finding | “All inference goes through Cursor's hosted models in both modes.” | [Cursor TypeScript SDK](https://cursor.com/docs/sdk/typescript); Undated live documentation; Overview; Authentication; Usage and billing; bundled executables | D |
| U6 · Vendor SDK documentation; key identity and plan remain route-specific | “The SDK accepts user API keys and service account API keys for both local and cloud runs.” | [Cursor Python SDK](https://cursor.com/docs/sdk/python); Undated live documentation; Authentication; Usage and billing; Local persistence | D |

### Antigravity SDK and managed API evidence

| ID and authority | Public evidence excerpt | Source and version | Recheck |
|---|---|---|---|
| A4 · Google technical documentation; separate runtime and auth profile, not access clearance | “The Google Antigravity SDK is a Python SDK” | [Antigravity Python SDK overview](https://antigravity.google/docs/sdk/overview/); Undated live documentation; Overview; Quickstart; Gemini Enterprise | D |
| A5 · Google technical documentation; separate runtime and auth profile, not access clearance | “The Antigravity agent is a general-purpose managed agent on the Gemini API.” | [Gemini API Antigravity agent](https://ai.google.dev/gemini-api/docs/antigravity-agent); Last updated 2026-09-29 UTC; preview identifier September 2026; Introduction; REST example | D |

### Supplemental contract and policy sources

| ID and authority | Public evidence excerpt | Source and version | Recheck |
|---|---|---|---|
| C6 · Vendor supplemental terms or policy; incorporation must be established | “these Service Specific Terms control for the relevant Services.” | [Anthropic Service Specific Terms](https://www.anthropic.com/legal/service-specific-terms); Effective 2026-08-31; Intro precedence; A; D | T |
| O6 · Vendor supplemental terms or policy; incorporation must be established | “may be subject to third party licenses” | [OpenAI Service terms](https://openai.com/policies/service-terms/); Updated 2026-09-29; Intro precedence; 1; 4 | T |
| G8 · Vendor supplemental terms or policy; incorporation must be established | “Circumvention of abuse protections or safety filters” | [Google Generative AI Prohibited Use Policy](https://policies.google.com/terms/generative-ai/use-policy); Last modified 2024-12-17; Scope; 2(c) | T |
| G9 · Vendor supplemental terms or policy; incorporation must be established | “You may not sell or transfer AI credits to another user or account” | [Google One Additional Terms](https://one.google.com/terms-of-service); Last modified 2025-11-11; Our Service; AI Credits | T |

How do C6 and O6 affect precedence, user/admin notices, marketplace-provider agreements and code-output license review? For Google-account AI subscriptions and API-backed routes, which of G8 and G9 are incorporated, and what feature-specific credit or use conditions apply? These are supplemental questions, not assumptions that every policy governs every route.

## Immutable source license register

Public license files were retrieved through unauthenticated GitHub read APIs. No source was built or executed. All retrievals: 2026-10-02. Every row is source-documented for the named file only and reopens on trigger R. Release-binary equivalence and the full dependency inventory are unknown.

| Repository and license evidence | Immutable file and commit date | Counsel scope question |
|---|---|---|
| openai/codex · “Apache License” version 2.0 | [d25c114d494ddb693290b76bf5e5f64ecbdb38fc](https://github.com/openai/codex/blob/d25c114d494ddb693290b76bf5e5f64ecbdb38fc/LICENSE); 2026-10-02T03:31:52Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |
| NousResearch/hermes-agent · “MIT License” | [5bba024d8ddd388f56f354c1f789be825e3d8a3c](https://github.com/NousResearch/hermes-agent/blob/5bba024d8ddd388f56f354c1f789be825e3d8a3c/LICENSE); 2026-10-02T02:25:21Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |
| anomalyco/opencode · “MIT License” | [1ddb0873aee50d209d1a8d7f91b89c5daf692d49](https://github.com/anomalyco/opencode/blob/1ddb0873aee50d209d1a8d7f91b89c5daf692d49/LICENSE); 2026-10-02T03:21:08Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |
| earendil-works/pi · “MIT License” | [7fbbd5f4a1d982bb02d63472dde0774fa639f99b](https://github.com/earendil-works/pi/blob/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/LICENSE); 2026-10-01T20:10:57Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |
| google-gemini/gemini-cli · “Apache License” version 2.0 | [c9096a847193c16e282d7bd20a70fddc57646bbe](https://github.com/google-gemini/gemini-cli/blob/c9096a847193c16e282d7bd20a70fddc57646bbe/LICENSE); 2026-10-01T19:55:51Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |
| anthropics/claude-code · “All rights reserved.” | [52c76441cae91f6891e4712306bffb057ff6fec5](https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/LICENSE.md); 2026-10-01T18:43:08Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |
| xai-org/grok-build · “Apache License” version 2.0 | [2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8](https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/LICENSE); 2026-09-29T16:57:09Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |
| deepseek-ai/deepseek-harness · “MIT License” | [639ed015397290b3745d163aafe02ffee4aa3f84](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/LICENSE); 2026-09-29T09:21:31Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |
| aaif-goose/goose · “Apache License” version 2.0 | [8f4cab5fdb54dfb6a6749b997f4ef560625d1f9c](https://github.com/aaif-goose/goose/blob/8f4cab5fdb54dfb6a6749b997f4ef560625d1f9c/LICENSE); 2026-10-02T02:18:13Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |
| modelcontextprotocol/modelcontextprotocol · Mixed transition statement in LICENSE | [3098fe94caa1b9e0afaaa6d30e040b61d5802471](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/3098fe94caa1b9e0afaaa6d30e040b61d5802471/LICENSE); 2026-10-01T12:55:32Z | Which actual files, binaries and dependencies are covered, and what additional notices or terms apply? |

The companion rc-source-license-manifest.json records full SHA-256 values for every retrieved license, alongside immutable URLs, commit timestamps and retrieval dates. License names in this register are brief identifiers; no longer license text is reproduced in the report.
