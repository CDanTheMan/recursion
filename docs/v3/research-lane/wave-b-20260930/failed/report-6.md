# Deep Research Topic Selection

## Assumptions

The substantive research topic has not yet been specified. I will therefore **not invent a subject and produce a potentially irrelevant literature review**.

There is one uploaded document, **“DS-08 — Private canary methodology,”** which defines a research-only methodology for `CANARY-01`, including alias-only handling, test/fixture write boundaries, private-route eligibility, independent reruns, failure injection, disclosure controls, stop conditions, and proof that no canary execution occurred. It explicitly states that merely reading the document does **not** invoke the canary or authorize provider calls, writes, commits, deployment, publication, or other effects. fileciteturn0file0

## Likely Research Topics

| Choice | Research topic | What the report would focus on |
|---|---|---|
| **A** | **DS-08 private canary methodology** | A source-pinned analysis of how to design the proposed `CANARY-01` characterization methodology without executing it: alias-only references, machine-checkable test/fixture boundaries, independent clean reruns, baselines, failure injection, disclosure controls, stop conditions, and limits on what one canary can establish. This most directly matches the uploaded document. fileciteturn0file0 |
| **B** | **Software migration canaries and verification pipelines** | A broader literature and industry review of canary validation for software migrations: deterministic characterization tests, differential testing, regression baselines, hermetic/reproducible execution, fault injection, clean-room reruns, and evidence needed before broader migration. |
| **C** | **Privacy-preserving evaluation of proprietary software systems** | Methods for evaluating private code or business rules while minimizing disclosure: pseudonymous/alias-only artifacts, information-flow boundaries, secret scanning, provenance, controlled execution environments, data minimization, and auditable non-disclosure guarantees. |
| **D** | **Reproducible and trustworthy software verification** | Research on hermetic builds/tests, deterministic inputs and outputs, independent replication, mutation/fault testing, non-tautological oracles, provenance, supply-chain integrity, and what constitutes persuasive verification evidence. |
| **E** | **AI-agent governance for repository-changing workflows** | How autonomous or semi-autonomous coding agents should be constrained: least privilege, protected paths, write allowlists, approval gates, commit/push separation, provider and credential controls, stop conditions, and machine-verifiable audit trails. |

## Research Framework

Whichever topic is selected, I will prioritize **primary and official sources, original academic papers, standards, and authoritative technical documentation**, emphasizing roughly **2021–2026** while using older foundational work where necessary.

The resulting report will contain an executive summary; explicit assumptions; detailed analytical synthesis; evidence-comparison tables; recent developments; competing approaches and trade-offs; recommendations with decisive falsifiers where applicable; limitations and unresolved questions; and inline source citations. Quantitative evidence will be charted where useful, while process or relationship structure will use diagrams where they materially improve understanding.

For **Choice A**, I will preserve the uploaded document's stated boundary: the work would be **research and specification only**. It would not execute `CANARY-01`, invoke a private route, create a candidate commit, touch production code, publish, push, merge, or expose any real canary identity, path, content, transcript, or digest. fileciteturn0file0

## Selection

Reply with **A, B, C, D, or E**. If no additional constraints are provided, **A** is the strongest interpretation because it is directly grounded in the uploaded research brief.