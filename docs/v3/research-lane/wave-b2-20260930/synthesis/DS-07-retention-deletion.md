# DS-07 — privacy-preserving retention and deletion (synthesis)

## Provenance

- Raw: `raw/ds-DS-07-retention-deletion.md`.
- Handoff: `DS-07 — privacy-preserving retention and deletion` research directive supplied to the run.
- Session: Wave B Deep Research (self-contained handoff, run 2); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved from the report: **SD** = source-documented; **M** = inferred/modelled from source-documented facts; **Measured** = reproduced on a pinned target (the report contains **none**); **U** = unknown/unverified. All claims are attributed to "the report's sources"; no new facts or URLs are added.
- Scope: read-only. The report states it performed no encryption, deletion, KMS operation, deployment, repository mutation, provider configuration, spending or publication, and included no real keys, raw artifacts, content digests, credentials or private identities.
- Source base: the report cites NIST SP 800-88 Rev. 2 (Sept. 2025), the NIST SP 800-57-derived key-destruction definition, NIST FIPS 186-5, RFC 9052 (COSE), RFC 9162 (Certificate Transparency v2), Google Cloud KMS, AWS KMS/CloudHSM and Azure Key Vault documentation, the Harnik/Pinkas/Shulman-Peleg deduplication side-channel research, DupLESS (USENIX Security 2013), and GDPR Article 17.

## The question

How should Recursion v3 make raw-artifact retention and deletion an evidence-backed, auditable process rather than an optimistic workflow outcome? The report treats the ratified direction — scoped encryption with expiry, deletion of blobs and applicable keys, propagation through replicas/caches/backups/provider copies/disconnected spools, and a minimal signed non-sensitive tombstone preserving durable lineage — and the Owner-selected defaults (30 days successful raw sessions, 90 days failed/disputed, policy-governed durable metadata, explicit pinning) as inputs, not decisions to reopen.

## Key findings

- **Completion is derived, never asserted (M).** The report's decisive invariant: no component may emit `verified-complete` while any enumerated recoverable copy is present, any expected copy class is unaccounted for, any applicable key recovery path is unresolved, or any unresolved copy lacks a recorded, evidence-backed expiry boundary.
- **Cryptographic erasure is defense in depth (SD).** NIST SP 800-88 Rev. 2 accommodates logical/cloud storage, gives CE a larger role, and emphasizes verification/validation, but the report reads it as warning that CE cannot be trusted as disposal of backed-up or escrowed copies unless all target keys are accounted for. Key destruction is defined more strongly still: removing all traces so a key cannot be recovered physically or electronically.
- **Provider states are provider-specific abstractions (SD).** Google Cloud KMS can report a version `DESTROYED` while key material may remain for up to 45 days from scheduled destruction; AWS says KMS-backed CloudHSM material deletion is best effort and does not delete CloudHSM backups; an Azure Key Vault restored backup is independent of the original and unaffected by purging the original. A provider state name is evidence to translate, not `verified-complete`.
- **Unexpired backups are visible states (M).** A recoverable backup that cannot yet be purged produces `expiry-bound` with a source-pinned boundary, not completion; an expired boundary that is overrun must move to `blocked`/`partial` with the violated boundary preserved, never silently extended.
- **Disconnected copies fail closed (M).** An offline spool or node stays unresolved until it provides acceptable evidence after reconnection or is covered by a separately justified, non-bypassable destruction/expiry mechanism; mere silence is not evidence, and an expired spool must not upload expired material on reconnect.
- **Key scope cannot silently cross incompatible fates (M).** If two artifacts under one key can have different expiry, pin or legal-hold outcomes, cryptographic erasure of one cannot be claimed while that shared key remains required by the other. The report's invariant: a shared key is permissible only where sharing its cryptographic deletion fate is also permissible.
- **Identity, address, encryption and dedup must be separate (M).** The report separates `artifact_id`, `storage_address`, `key_scope_id` and `deletion_request_id`; a global plaintext digest should not serve as all four because cross-user deduplication and message-locked/convergent encryption create membership/equality and known-content guessing exposure.
- **Evidence-oriented state machine (M).** `requested → local-content-deleted → key-destroyed → propagation-pending → verified-complete | partial | blocked | legal-hold | expiry-bound`, derived from a copy ledger and key ledger rather than local success. `retention-held` is proposed as a distinct state (or a typed `blocked` reason) so a pin is not confused with a legal hold.
- **Copy ledger is closed (M).** Active store, CAS replicas, caches, backups, provider-side copies and disconnected spools/node each need minimum evidence; an omitted class is not an empty class. Key backups and restored copies are first-class members of the ledger rather than one indivisible "KMS."
- **Boundary records are auditable facts (M).** Backup/provider-residual boundaries keep copy class, policy version, latest possible containing snapshot, expiry time, calculation basis, evidence reference, observation freshness and a post-boundary verification status.
- **Tombstone is minimal and non-sensitive (M).** The signed tombstone asserts what policy-governed event was asserted, by whom, when and with what disposition, using opaque non-content-derived IDs. It excludes raw content, global plaintext/ciphertext digests, paths, exact size by default, and key/account identifiers; a signature and an append-only Merkle log prove integrity/inclusion, not physical deletion.
- **Leakage is explicit (SD/M).** Deduplication hit/miss, deterministic ciphertext, exact size, exact timing, copy topology and access patterns can leak membership or activity; the report prefers scope-local, opaque identifiers and treats padding/ORAM-like techniques as threat-modelled choices.
- **Legal hold and pin are different authorities (SD/M).** A legal hold is a blocking authority state with separate compliance implications (the report cites GDPR Article 17's exceptions); a pin is an expected policy state. Hold/pin precedence must be checked before each irreversible operation via a policy generation, and a stale worker must abort.
- **Required negative fixtures (M).** The report lists tests that use only synthetic content and keys: cross-project equality oracle, shared-key blast radius, known-content CAS probe, convergent-encryption dictionary, backup key resurrection, provider residual window, cache resurrection, disconnected spool reconnect, lost disconnected node, backup-boundary overrun, legal-hold race, pin race, tombstone equality leak, fake negative key test and audit-log-only proof.
- **Generic physical-destruction proof is unavailable (U).** The report states no vendor-independent way to prove physical destruction of key material on an arbitrary disconnected OS node is established by the reviewed public standards, and keeps `unknown` distinct from zero recoverable copies.
- **NIST bounds, but does not replace, provider evidence (M).** The report says NIST grounds the sanitization objective, CE discipline and validation emphasis, yet cannot tell Recursion whether an undocumented provider replica or escrowed key copy exists; that remains a provider-specific copy-inventory question.

## Recommendation and falsifier

The report recommends **standardizing the deletion evidence contract, not a single key granularity**. The contract requires a closed per-request copy inventory; explicit per-copy predicates and evidence references; a key-recovery inventory separate from blob copies; a strict distinction among `partial`, `blocked`, `expiry-bound` and `verified-complete`; a policy-generation guard for pin/legal-hold races; scope separation among lineage identity, storage address, key identity and deletion-request identity; a minimal signed tombstone generated from the derived terminal state; and an independent review step before accepting completion.

It pairs three decisions with competing options and falsifiers:

1. Govern key scope by the invariant that a key must not span artifacts whose required cryptographic deletion fates can diverge unless the product explicitly accepts that individual cryptographic erasure waits for scope closure. Competing option: per-artifact keys. Falsifier: a product requirement that one artifact receive a completed cryptographic-erasure claim before a live sibling in the same scope loses decryptability — then the shared scope is logically incompatible and must escalate, not weaken the claim.
2. Disallow cross-deletion-scope deduplication for raw private artifacts unless an explicit exception passes the equality-oracle, reference-isolation and deletion-truthfulness fixtures. Competing option: global content-addressed dedup with deterministic/message-locked encryption. Falsifier: measured constraints make scoped/no-global dedup infeasible and a reviewed scheme meets the privacy and deletion predicates.
3. Make `verified-complete` a read-only derived state no adapter, worker, storage engine or KMS wrapper can set directly. Competing option: the orchestrating worker marks completion after its calls succeed. Falsifier: only if every recoverable copy and key path is controlled synchronously with no independent backup, provider, cache or disconnected lifecycle — conditions the lane's copy classes rule out.

## What this does not prove

- No single key granularity, epoch length, provider or storage engine is selected; nothing is encrypted, deleted, provisioned or measured.
- Cryptographic erasure is not shown to prove every copy disappeared, that surviving ciphertext is gone, or that an escrowed/exported/restored key cannot re-enable it.
- A provider attestation is the strongest available evidence for provider-held infrastructure but remains an assurance boundary, not direct physical observation.
- No dollar budget is derived; artifact volume, object size, KMS pricing, backup volume, request rate and recovery objectives are unspecified, so the cost comparison is qualitative.
- Platform-keystore assurance, epoch economics, traffic-analysis requirements and provider-evidence normalization remain open research questions requiring concrete adapters and measurements.
- Legal-hold and jurisdictional decisions remain with the Owner and counsel; the GDPR citation is a design justification, not legal advice.

## Open Owner decisions

- Is `expiry-bound` explicitly a non-complete, user-visible outcome?
- What deletion claim is promised at artifact level when a shared project/class key remains live?
- What maximum coupling window is acceptable for shared keys?
- May private raw artifacts ever participate in cross-project/global deduplication?
- Is the signed tombstone strictly internal/audit-scoped or intended for external export?
- What authority can create/release a pin versus a legal hold?
- What evidence tier is sufficient for provider-held copies?
- When is a permanently lost disconnected node considered irrecoverable rather than indefinitely `blocked`?
- Must every boundary receive a post-expiry verification event before completion?
- What independent reviewer role accepts `verified-complete` evidence?

## Relevance to later waves

This lane supplies the copy ledger, key ledger, state machine and tombstone schema that any retention/deletion implementation must satisfy. Later waves should build the negative fixtures first and treat `verified-complete` as a read-only derived state that an independent verifier must accept, with provider adapters preserving each provider's distinct deletion and audit semantics rather than collapsing them into a boolean. The report's framing — absence of evidence stays absence of evidence, an expiry boundary is not completion before it passes, a signed statement is not deletion, and inaccessibility is not destruction — is the acceptance posture later implementations should inherit.
