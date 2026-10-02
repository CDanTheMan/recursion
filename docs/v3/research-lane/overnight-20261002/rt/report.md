# R T Multimodal I O and attachment contracts

Decision-ready research candidate, 2 October 2026. Repository baseline `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. All acceptance handoffs are **UNEXECUTED**. No route, parser, OCR/ASR engine, renderer, model, provider, account or target was exercised. This report proposes an extension to shared contracts; it does not adopt a schema, select a component or qualify a route.

## Decision summary

Use one provenance-bearing artifact family for original media, extracted metadata, decoded representations and every derivative. Compile an explicitly bounded view for each authorized recipient and route. Preserve the source even when a derivative is useful, subject to source-specific retention rights; when preservation is forbidden or unavailable, disclose the continuity limit rather than inventing a rehydration guarantee. A transcript is not the audio; a rendered page is not the document; a supported upload is not evidence that the route preserved its meaning.

The strongest candidate is a typed media extension to the proposed R-Q Artifact contract, with R-P provenance and influence fields reused, exact-payload egress binding, conservative capability resolution, explicit loss records and DS-26 accounting. The real alternative is bounded raw-file pass-through to a qualified upstream profile, retaining the required local provenance, loss, authority, rights and accounting manifest without eagerly creating local decoded derivatives. The candidate is falsified if it cannot preserve approved task evidence with acceptable resource and review burden, if an untracked transform or recipient escapes mediation, or if the qualified raw-pass-through baseline preserves equivalent semantics with lower burden. Passing the proposed contract fixtures would establish only the bounded predicates, not media accuracy, isolation, route eligibility or a continuity advantage.

TUI attachment inspection comes first: a stable text record, authorized source location and explicit derived-description status must work before optional previews. GUI later consumes the same backend projections and commands. D019's comprehensive opt-in scope remains accepted; the conflict between older initial-release GUI exclusions and its first-release opt-in wording is not silently resolved here. Construction order is not permission to remove a capability.

## Evidence and ownership

**SD** means source-documented in a named standard, official page or committed contract. **LO** means locally observed static text/hash/artifact QA only. **I** means an original inference/design candidate. **U** means unknown, unavailable or unmeasured. All prescriptions below are I unless explicitly traced to an accepted requirement. Source-derived factual summaries occur once in the public evidence section; later sections apply them to Recursion rather than adding vendor guarantees.

**LO, bounded static inspection:** the current repository has planning, integrity and execution schema families. The execution schema includes evidence and plugin-artifact bindings. Searches of `scripts`, `schemas` and historical `experiments/v3/interface-probes` for attachment, multimodal, image-URL and audio terms produced no attachment-pipeline implementation witness. This is a bounded search observation, not proof that every file lacks related behavior. The lane brief explicitly says this pipeline, media accounting and provider/render probes are unimplemented/unmeasured. Existing historical interface and FU03/FU04 records are neither erased nor promoted into media qualification. No repository script was executed.

The current governance, ANCHOR, D017–D033, active goal, PRODUCT, INTERFACE-STRATEGY, PLUGINS-AND-EDITIONS, CONTEXT, ROUTE-CAPABILITIES, TELEMETRY, relevant ARCHITECTURE sections, research index, architecture/harness coverage, GAPS, domain-D synthesis and DS-26 were inspected. The stale architecture assignment of multimodal to R-Q is superseded by the actual R-T brief. Hermes has no executive authority. G06/G07/G11 Owner decisions are closed; implementation evidence remains open. The accepted platform floors and WSL development-only status are inherited, not newly decided.

| Contract | Design responsibility and canonical ownership |
|---|---|
| Artifact identity, persistence, retrieval, retention, deletion | R-Q proposes the shared artifact model; existing canonical kernel/writer remains the sole state authority. R-T adds media fields and references, never a second media store authority |
| Source trust and influence | R-P envelope and current canonical authority objects. A caption, filename, OCR instruction or purported signature cannot mint a grant |
| Parsing and execution isolation | R-U boundary; R-T specifies the required media operation and output contract, not an isolation product |
| Route, entitlement and helper selection | Maintained RouteCapabilityDescriptor and ordinary admission; R-F technical facts, R-E launch boundary and R-H rights/terms remain separate |
| Context compaction and budgets | Existing context governor per route epoch; DS-26 attribution and settlement ledgers. No media-specific compaction executive or spend ledger |
| Terminal and GUI | R-K rendering/liveness contract, R-L command/query semantics, R-N later GUI. Views are disposable projections; neither owns runtime lifetime |

Sibling reports are proposed cross-lane contracts pending independent integration review, not ratified schemas. Common harness and MCP facts are linked through [shared evidence navigation](../shared-evidence/source-facts.md), not repeated here. Output rights remain an explicit dependency on [R-H H11](../rh/report.md), and provenance on [R-P](../rp/report.md). The proposed ownership mapping in `artifact-contract.json` must be reconciled with R-Q before implementation.

## Public evidence anchors

Retrieved 2026-10-02. Exact page versions, dynamic-page limits and retrieval status are in `source-register.json`. No public page body is packaged; no excerpt digest is represented as a whole-page hash. These examples are deliberately non-exhaustive, and none supplies subscription entitlement or installed-harness capability.

| Source | Bounded documented fact and its implication |
|---|---|
| <a id="rt-s01-facts"></a>S01 [OpenAI image inputs](https://developers.openai.com/api/docs/guides/images-vision) | The retrieved API guide lists PNG/JPEG/WebP/nonanimated GIF; 512 MB request payload and 1,500-image limits coexist with model/detail-specific patch and context bounds. Detail levels and preprocessing vary. A single generic image-size flag cannot describe this interface |
| <a id="rt-s02-facts"></a>S02 [OpenAI file inputs](https://developers.openai.com/api/docs/guides/file-inputs) | Responses handles PDFs as text plus page images, non-PDF documents as text, and spreadsheets through a separate augmentation flow. Embedded non-PDF charts/images are omitted; spreadsheet processing covers up to 1,000 rows per sheet with generated summary/header material. Each file must be below 50 MB and combined files at most 50 MB. Chat Completions has a different file-type surface |
| <a id="rt-s03-facts"></a>S03 [Claude vision](https://platform.claude.com/docs/en/build-with-claude/vision) | Retrieved limits vary by model/context and hosting platform. Image count, encoded byte size, dimensions and many-image limits interact. Animations use only the first frame. Resizing behavior differs for ordinary images and particular tool-result images. Descriptor scope must include content placement and hosting interface |
| <a id="rt-s04-facts"></a>S04 [Claude PDF](https://platform.claude.com/docs/en/build-with-claude/pdf-support) | PDF processing combines page images and extracted text, with request/page/context limits. The documented older-model Bedrock Converse profile requires citations for visual processing and otherwise uses text-only extraction. Endpoint and configuration can therefore change document semantics |
| <a id="rt-s05-facts"></a>S05 [Gemini video](https://ai.google.dev/gemini-api/docs/video-understanding) | The retrieved guide distinguishes static 1-FPS sampling from model-specific agentic timeline inspection. Static and agentic accounting differ; the page warns that fast action may lose detail under sampling. Its efficiency claims are vendor claims, not Recursion results |
| <a id="rt-s06-facts"></a>S06 [Gemini audio](https://ai.google.dev/gemini-api/docs/audio) | The retrieved audio guide documents audio-format support, duration/token treatment and conversion of multiple channels to one. Audio understanding includes more than speech transcription. This is an API profile, not Gemini CLI qualification |
| <a id="rt-s07-facts"></a>S07 [Gemini documents](https://ai.google.dev/gemini-api/docs/document-processing) | PDF byte/page/context and resolution constraints coexist. The guide identifies model-generation-specific native-text inclusion and image-modality reporting. File extension alone cannot determine context or billing quantity |
| <a id="rt-s08-facts"></a>S08 [Gemini Files](https://ai.google.dev/gemini-api/docs/files) | Uploaded files are documented as retained for 48 hours and not downloadable through that API; generated files have a different download path. That object lifecycle is not a universal assertion about service backups, abuse logs or all data retention |
| <a id="rt-s09-facts"></a>S09 [Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html) | hOCR/TSV examples retain page/block/line/word structure, boxes and confidence fields. These are representational affordances, not calibrated correctness probabilities or a selected OCR engine |
| <a id="rt-s10-facts"></a>S10 [Whisper model card v20250625](https://raw.githubusercontent.com/openai/whisper/v20250625/model-card.md) | Its authors distinguish speech recognition from translation, describe uneven language/accent performance and possible text absent from the audio, and call for domain-specific evaluation. Local execution does not imply faithful transcription |
| <a id="rt-s11-facts"></a>S11 [CIPA Exif 3.0 overview](https://www.cipa.jp/std/documents/e/Exif3.0-Overview_E.pdf) | The December 2023 overview identifies capture time/location, device/software and owner/editor metadata, plus annotation and original-preservation-image features. It is a historical feature reference, not a claim that 3.0 is the newest standard |
| <a id="rt-s12-facts"></a>S12 [OWASP file upload guidance](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) | OWASP recommends layered validation, bounded uploads and isolated storage/inspection, and warns about spoofed media types, parser exploits and decompression bombs. Such controls motivate a boundary; they do not certify a parser |
| <a id="rt-s13-facts"></a>S13 [Media Fragments 1.0](https://www.w3.org/TR/2012/REC-media-frags-20120925/) | The Recommendation supplies temporal/spatial addressing concepts. A fragment is a selector, not proof that the bytes at a mutable URL are unchanged or that a client can render them |
| <a id="rt-s14-facts"></a>S14 [ISO BMFF byte-stream note](https://www.w3.org/TR/2024/NOTE-mse-byte-stream-format-isobmff-20240723/) | The 2024 W3C Group Note separates codec/profile signaling, initialization segments, media segments and random-access points, allowing codec subsets. It concerns MSE byte streams, not every MP4 implementation or a universal media decoder |
| <a id="rt-s15-facts"></a>S15 [WebVTT draft](https://www.w3.org/TR/2026/CRD-webvtt1-20260520/) | The May 2026 Candidate Recommendation Draft describes timed text cues and their presentation. A cue format is useful prior art for transcript alignment, not a transcript-accuracy guarantee |
| <a id="rt-s16-facts"></a>S16 [WAI complex images](https://www.w3.org/WAI/tutorials/images/complex/) | Complex images may require a short identifying alternative and a longer description conveying essential information. A short caption alone need not carry chart values or relationships |
| <a id="rt-s17-facts"></a>S17 [WAI audio and video](https://www.w3.org/WAI/media/av/) | WAI distinguishes captions, transcripts, visual descriptions and accessible media players. Speech text alone can omit important non-speech sound and visual content |
| <a id="rt-s18-facts"></a>S18 [kitty graphics protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/) | The protocol supports direct and local file/shared-memory transfer, chunking, queries and image placement. Its local-transfer and error rules address file-access concerns. Protocol support requires an exact terminal/path profile; a remote terminal need not share the sender's filesystem |
| <a id="rt-s19-facts"></a>S19 [iTerm2 images](https://iterm2.com/documentation-images.html) | Its OSC 1337 image/file protocol distinguishes inline display from download; multipart support and tmux handling are version-specific. This is a comparison precedent, not a Windows/Linux support finding |
| <a id="rt-s20-facts"></a>S20 [PROV-DM](https://www.w3.org/TR/2013/REC-prov-dm-20130430/) | Shared factual home: [R-Q E01](../rq/report.md#e01). R-T uses its derivation vocabulary without treating provenance as truth, authorization or a complete-input guarantee |
| <a id="rt-s21-facts"></a>S21 [OpenAI audio workflows](https://developers.openai.com/api/docs/guides/audio) | The guide separates bounded transcription, generated speech, live transcription, multimodal chat and realtime/conversational paths. Shared transport does not make their session semantics interchangeable |
| <a id="rt-s22-facts"></a>S22 [OpenAI image output](https://developers.openai.com/api/docs/guides/image-generation) | The retrieved guide documents encoded image outputs and format/quality choices, and acknowledges text-placement and consistency limits. Output generation is a distinct capability from image input |
| <a id="rt-s23-facts"></a>S23 [Library of Congress PDF A3](https://www.loc.gov/preservation/digital/formats/fdd/fdd000360.shtml) | Its format description explains that PDF/A-3 can contain associated files of other formats. Even an archival-sounding container label does not justify recursively opening every embedded object |

<a id="r-t-q01"></a>
## Q01 Unified artifacts and representations

**I, RT-R01.** Support the accepted modality families as opt-in capabilities: still images/screenshots; vector/raster diagrams; audio; video including separate audio/subtitle tracks; PDFs; office documents; structured files such as CSV, JSON and spreadsheets. A family requirement is not universal codec, format-version or route support. Unsupported encrypted, malformed, oversized or opaque members remain identifiable attachments with a typed blocker when retention is authorized, not fabricated extracted text.

Extend one proposed shared Artifact record with an immutable media facet. R-Q's proposed internal ArtifactRef has four required fields: `object_type`, `id`, `version`, `content_digest`; the enclosing Q ContentEnvelope binds `project_and_audience` and `privacy_domain_id`. Q's `project_id` belongs to MemoryProjection and is not silently inherited into that envelope. This reference is internal to that trust domain; an external projection uses a newly authorized audience-scoped `opaque_handle`. This is a cross-lane design candidate, not an adopted schema. Required bindings are schema version; authorized opaque artifact reference and revision; project/privacy domain; digest algorithm and byte digest scoped inside that domain; byte length and completeness; declared versus validated media type; source origin/authenticity evidence or unknown; claimed capture time separately from ingestion time and clock uncertainty; producer operation/attempt; R-P trust class; privacy classification/allowed readers/purposes; rights and retention reference; and source-location/derivation links. Original bytes, metadata, decoded samples/pixels, OCR, ASR, translated text, embedding, summary, thumbnail, caption and generated output have different `representation_kind` values and identities.

The attachment is a user-visible association with a task/context, not a second content object. A filename is untrusted display metadata, never a storage path or source authority. A screenshot's clock, visible user name and source URL are claims unless independently captured by an admitted operation. An original can be authentic bytes while its claims remain false. Each derived claim records evidence class and verification status independently from the pipeline's successful completion.

R-P field names remain `parent_units`, `transform_identity_version_config`, `observed_input_set`, `coverage_and_loss`, `authority_carried_none` and separately resolved canonical references. The influence set conservatively includes all visible inputs to a model transform; model-generated citations cannot narrow it. Readers intersect, privacy/retention constraints propagate, and a transform cannot declassify itself. Raw digests, filenames, size patterns and stable equality signals are not exported across privacy domains. Externally exposed handles are audience-scoped and authorized. RT-F01/RT-F12 test round-trip and authority preservation; byte identity alone proves neither factual truth nor permission.


### Shared field map and extension ownership

The exact proposed P→Q→T map is [field-map.json](field-map.json), revision RT-field-map-2; it enumerates every media/selector/transform/loss/route/payload/counter/receipt field, its origin, single proposed design owner and validation. All mutable canonical metadata remains owned by the existing fenced writer. This is an unratified logical map, not a new wire schema.

| Mapping | Actual shared base or explicit extension | Single proposed design owner and validation |
|---|---|---|
| P common source/trust/influence names → Q ContentEnvelope.required_names → T base | Reuse Q's exact 18 required names, including project_and_audience and privacy_domain_id | R-Q shared-base design; exact revision and scope required; no inferred project_id alias |
| P raw_digest → Q unit_ref.content_digest; P span_or_time_locator → Q source_locator | Explicit normalization aliases; original sources remain parent_units | R-Q shared normalization; equal byte/domain or selector meaning required, contradictory aliases reject |
| P retrieval_operation, retrieval_time, source_authenticity_evidence, output_digest, disposition, canonical_refs_resolved_separately | Explicit carried P extensions, absent from Q base; output_digest is a checked produced-unit digest alias | R-P provenance design; resolve canonical receipts; no trust or authority promotion |
| Q MemoryProjection.allowed_purposes → T purpose projection | Explicit T extension, not inherited Q ContentEnvelope field | R-T media-policy projection; intersect current source rights/purposes; required unknown denies protected processing |
| P media_type → T declared/validated types; Q source_locator and coverage_and_loss → T typed selectors/loss manifest | T split/extension; declared type is not validated type; duplicate selector/loss views reference the same record | R-T media design; inconsistent type, selector, loss or source revision rejects |
| All other media_facets and transform/loss/route/payload/counter/partial-transfer data fields | T additions enumerated individually in field-map.json; not claimed as Q base | R-T design; bind existing authority/operation/accounting owners, preserve unknowns and reject inconsistent projections |

RT-F01 pins the exact P/Q/map revisions and checks missing scope, undeclared aliases and contradictory digest/locator/loss/purpose values with an independently authored expected envelope. It never silently chooses one conflicting alias.

<a id="r-t-q02"></a>
## Q02 Normalization without native support assumptions

**I, RT-R02.** The compiler first identifies the task-relevant information and the permitted loss envelope, then compares feasible representations. It never begins by assuming a provider accepts the raw media.

| Family | Candidate path and retained mapping | Real competing path and rejecting observation |
|---|---|---|
| Image and screenshot | Preserve original; produce bounded orientation/color-aware decoded view, crop or downscale only as admitted derivatives. Store original and output dimensions, orientation transform, region and overlap | Pass original bytes to a capable route. Reject the derivative when a required label, color relationship, fine mark or surrounding context is lost |
| Diagram | Preserve vector/source if available plus inert raster/text/relationship projections; no scripts or external references executed | Route-native image inspection or manually supplied textual structure. Reject extraction when connector direction, group membership or notation changes |
| Audio | Preserve channel/timeline identity; derive transcript with segment offsets, language and uncertainties; non-speech observations separate | Approved raw-audio route or user transcript. Reject ASR-only compilation for a task requiring tone, overlap, speaker separation or sound events |
| Video | Preserve track/time-base manifest; derive explicitly sampled frames, audio/transcript and coverage intervals, not a fictitious full-video view | Approved native video route or bounded manual clip review. Reject sampled context if a task-critical event lies between samples or sync changes |
| PDF and office | Produce structured blocks, tables and page/render maps alongside a source reference; embedded objects get separate entries and disposition | Route-native document processing or manual extraction. Reject flattening when footnotes, revisions, formulas, charts or reading order matter |
| Structured data | Preserve encoding, schema, rows/cells, types, formulas and extraction bounds; do not execute macros/formulas/links during ingestion | Text-only excerpt. Reject truncation or display-value-only projection for a task requiring unseen rows, formula logic or exact types |

Chunk boundaries are explicitly mapped to the original, with declared overlap and deduplication. No recommendation selects a codec, engine or parser. Loss tolerance is task-specific; when no authorized representation meets it, refusal is useful correctness, not silent degradation. Local description can itself invoke a model and is not automatically cheap, deterministic or offline.

<a id="r-t-q03"></a>
## Q03 Structured documents and citation locations

**I, RT-R02/RT-R03.** A document graph contains immutable source nodes, ordered sections/paragraphs, tables with row/column/cell spans and header relations, footnotes, figures/captions, formulas, and separate hidden/revised/comment content when policy admits it. Every node references the source digest/revision and a typed locator. Preserve both physical zero-based page index and displayed page label; do not confuse Roman-number front matter with document index. Office files may have no stable pages until rendered: cite part/paragraph/table/cell or slide/sheet/range, then bind any page projection to the renderer/configuration/fonts/pagination revision. No live rendering was performed.

A location can include byte span plus encoding; text span plus extraction revision; page/crop rectangle with units, origin, rotation and coordinate transform; spreadsheet cell/range plus sheet identity; audio track, rational time base and start/end; or video presentation timestamp/frame index plus variable-frame-rate mapping. Source order and reading order are separate. Store unsupported/missing nodes explicitly. A crop locator alone cannot reconstruct pixels unless the source and transformation still exist.

The [S09](#rt-s09-facts), [S13](#rt-s13-facts) and [S15](#rt-s15-facts) premises motivate representational choices, but Recursion’s canonical location object is not any one format. The [S23 premise](#rt-s23-facts) motivates nested-object enumeration without auto-opening. A displayed citation resolves through the authorized artifact service and verifies revision/digest before revealing content; a model citation is a proposed locator until checked. RT-F01/RT-F03/RT-F13 reject wrong-page, swapped-track, altered-layout and truncated-table citations.

<a id="r-t-q04"></a>
## Q04 Unsupported attachments and explicit degradation

**I, RT-R04.** Treat `unsupported`, `unknown`, `stale`, `incompatible` and `currently_unavailable` separately. Resolve the accepted four incompatibility responses through the existing configuration semantics: state incompatibility, recommend combinations, no action, or notify and recommend. A no-action receipt is deterministic and causes no transform, upload, helper, reroute or repair. The canonical refusal receipt is not a stored attachment.

If policy permits an alternative, show exact omitted/derived information, receiving route, helper dependencies, resource reservation and residual uncertainty before admission. Options are refuse/defer; use an already authorized local derivative; or request/perform a specifically authorized alternative route. Existing approval may cover a bounded alternative, but a new recipient, scope, billing class or loss beyond the accepted envelope requires new authority. Recommendations never activate themselves. A single empty text part is not success for a rejected video. RT-F02/RT-F05/RT-F14 require both successful allowed compilation and explicit disallowed cases.

<a id="r-t-q05"></a>
## Q05 Versioned media capability descriptors

**I, RT-R04.** Add a media capability facet to the existing RouteCapabilityDescriptor. Bind it to provider, endpoint/API, hosting platform, harness/interface/build, model revision, account/plan class, route epoch and effective settings. Declare each direction and placement separately: input versus output, user message versus tool result, streaming versus bounded request, upload-object versus inline bytes versus provider-fetched URL, local viewer versus model context. A filename or model catalog entry supplies none of these by itself.

For each cell record supported/unsupported/unknown; media/container and codec/profile; encoded and decoded limits; per-item/per-request count, dimensions/pixels/patches/pages/duration/channels/frames; context accounting unit and estimator version; provider counters and missing-counter behavior; preprocessing including sampling/downscale/text extraction; output forms; citation/offset behavior; streaming/cancel/delete/expiry semantics; discovery method, source/version, timestamp, expiry and conflicting observation. Keep documented bound, local observed bound and effective conservative bound separately. A Files upload maximum does not override a model's smaller document input limit.

The API examples in S01–S08 demonstrate why broad modality booleans are insufficient. They are not imported into Codex, Claude Code, Gemini CLI, Cursor or other harness descriptors without exact adapter evidence. The rest of the required harness ecosystem remains media-profile **unknown** here; its technical inventory is in R-F. Codex App Server stays first qualification priority, not already qualified. Maintainer signatures authenticate updates, not runtime behavior or entitlement. Descriptor resolution remains zero-model.

<a id="r-t-q06"></a>
## Q06 Semantic loss is a first class result

**I, RT-R03.** Every derivation records input/output identities, actual observed inputs, transform build/model/configuration, source region/time coverage, output completeness, omissions, uncertainties and a machine-readable loss vector. `no_transform` is meaningful for unchanged bytes; `lossless` must name the preserved property, such as byte reversibility, never universal semantic preservation. A syntactically valid record can still contain wrong text.

Loss dimensions include spatial detail, color/alpha/orientation; layout/reading order/table/formula relationships; temporal coverage/sync/channel separation; spoken words, non-speech events, prosody and speaker attribution; translation/language; numerical precision; provenance/citation coverage; and selection/summarization omissions. Each is `preserved`, `changed`, `omitted`, `unknown` or `not_applicable`, with reason, measurable coverage when known, and independent review reference. Do not invent a global loss percentage or convert confidence into accuracy.

A transcript may reverse a negation; downscaling may erase a decimal; a sample can miss a short event; a summary can omit a contradiction; an embedding can expose source information while being non-invertible in the ordinary workflow. Provider-internal preprocessing may be partly documented and actual per-item behavior unknown. The compiled context and UI show the relevant limitations, not just the final text. Loss composes conservatively through chains: a summary of OCR does not regain the source's authority or resolution. RT-F03 uses a deliberately wrong but well-formed transcript to ensure lineage validation is not reported as semantic verification.

<a id="r-t-q07"></a>
## Q07 Capability conflict resolution

**I, RT-R04.** Resolve conflicts by intersecting accepted types/placements and taking the stricter known limits only where units and semantics are comparable. A known 8-MiB decoded bound cannot be min-combined with an 8-MB encoded bound; both constraints apply. Conflicting preprocessing or accounting meanings are a blocker, not a numeric minimum. Unknown required support prevents admission unless a separately admitted path removes that requirement.

Retain both evidence records, quarantine the affected descriptor cell/epoch, record a typed reason and notify the responsible executive through existing policy. Recompile only under a new inspected descriptor/configuration revision. A runtime 413 or validation error may follow an already attempted upload; it is not retroactively `attempted=false`. No widening based on a lucky larger request. Retries use the same logical operation's owner/reservation and recheck current authorization. RT-F02 tests narrowing, incomparable units, changed endpoint and observed failure after partial dispatch.

<a id="r-t-q08"></a>
## Q08 Entitlement quota and cost comparisons

**I, RT-R05.** Compare exact route profiles, not vendor labels: principal/plan class without secrets, native capacity pool, execution interface/build, model/settings, host, media workload and observation window. Report documented eligibility, actual authorization, technical capability, conformance and financial settlement as independent fields. A route can accept pixels while its quota debit remains unknown.

The output is a quantity vector and a rights/eligibility matrix: API charges, subscription-native debits, bytes, host work, helper calls, latency and human corrections retain their own units. Public API price or token formula does not establish a subscription debit. A local OCR route competes on full-workflow cost and quality, including download/setup if separately authorized, compute, misses/retries, verification and corrections. No account was inspected, no eligibility established, and no comparative savings measured. D031 forbids inferring vendor intent from unequal limits or performance. RT-F07 validates honest nulls and duplicate reconciliation; a future paired experiment is required for any benefit claim.

<a id="r-t-q09"></a>
## Q09 Local processing versus route calls

**I, RT-R06.** Use an eligible local pipeline when raw-media egress is forbidden and local processing is authorized; when offline operation is a hard requirement; or when preregistered quality/resource evidence favors it. The first two are feasibility decisions, not claims of performance superiority. A local neural OCR/ASR/description/embedding engine remains inference with an explicit route, model/license/dependency identity, activation grant and resource budget. It must not fetch weights, invoke a cloud fallback or transmit telemetry merely because it is called local.

| Reason | Competing option | Decisive falsifier of the preference |
|---|---|---|
| Privacy | Authorized raw/derived upload to an eligible route, or no processing | Local process opens an unapproved network/credential/path surface, or its output disclosure exceeds the admitted scope |
| Offline | User-supplied transcript/description, or defer until online | Any needed weight, codec, language pack, license check or helper is unavailable offline or causes network access |
| Cost | Approved route-native handling | Matched accepted-quality workflow costs more in its predeclared native units, or required counters cannot bound the reservation |
| Latency/responsiveness | Approved route or deferred batch | Tail completion/Stop responsiveness fails the adopted profile, including contention with foreground work |
| Reproducibility | Pinned deterministic extraction/manual transcription | Identical input/environment/config produces different output outside the declared tolerance, or dependencies were not recorded |

Local is not inherently deterministic; parallel numeric execution, language detection and model sampling can vary. S09 and S10 support available representations and known failure modes, not an engine choice. RT-F04 tests routing and accounting with synthetic outputs; it does not execute OCR/ASR or measure accuracy. A later separately authorized quality corpus must include scripts/languages, noise, accents, tables, small text and task-critical errors, with independently prepared truth and abstention cases.

<a id="r-t-q10"></a>
## Q10 Metadata privacy retention and deletion

**I, RT-R07.** Raw media, extracted metadata, transcripts, embeddings, thumbnails and descriptions inherit the strictest applicable source privacy and purpose limits. They are individually addressable derivations in the same artifact graph, not harmless cache byproducts. Metadata inspection itself is parsing and requires the admitted boundary. Quarantine by default; extract only needed fields into a classified sidecar. Strip unnecessary metadata from an outbound derivative only through an admitted transform; preserve the original when allowed, and label exactly what was removed.

The [S11 premise](#rt-s11-facts) informs the metadata threat analysis. Removing EXIF alone does not remove visible text, faces, voices, geolocation clues, captions, filenames or embedded objects. Avoid storing a full filesystem path as origin when an authorized source handle suffices. Treat preview caches, clipboard copies, export files, terminal scrollback, decoder temporary files, logs and node spools as copies under R-Q's inventory. Do not cross-project deduplicate private media by raw digest.

Retention combines source/output-specific rights, user policy and deletion constraints; a derivative does not gain longer retention merely because it is shorter. R-H H11 distinguishes original model output, third-party/grounded material, personal data, notices and accidental secrets. Possession of JSON or pixels does not grant re-display, re-summarization, cross-route replay, training or export rights. Where exact rights are unknown, block the affected reuse rather than choose a universal TTL. The [S08 lifecycle premise](#rt-s08-facts) cannot establish that every provider copy is gone.

Deletion traverses descendants, indexes, previews and known copies with tombstone/receipt state; blocked rights-preservation conflicts are explicit. Offline/lost nodes remain pending/unknown, and prior provider or viewer disclosure cannot be undone by local deletion. Reconnection must honor current tombstones before exposure. A minimal authorized audit receipt may remain without content, subject to its own retention rule. RT-F13 tests the graph and residual disclosures; it cannot prove physical erasure on unreachable storage.

<a id="r-t-q11"></a>
## Q11 Exact payload compilation and egress authority

**I, RT-R08.** Compile after source-scope filtering and transformation admission. The compiled payload manifest binds the logical operation, attempt, task/GoalSpec revision, current grant/authority and privacy revision, pause fence, route descriptor/configuration epochs, recipient principal/service/endpoint, purpose, every representation's digest/length/order, text/context contributors, relevant headers/filenames/URLs, transport encoding and reserved budget. The exact content payload is immutable between approval and dispatch. Credentials remain outside this manifest and R-T's readable domain under R-E; do not hash secrets into telemetry.

For multipart/base64 upload, bind both logical content and final serialized body or a verifiable streaming chunk manifest. Base64 size is a wire quantity, not the original byte size or image token count. The boundary verifies actual file handles/bytes and recipient immediately before sending, preventing path replacement after inspection. Revalidate at resumptions and each admitted stream segment. Changed bytes, recipient, redirect, policy, rights or required capability produce a new decision; no approved thumbnail silently becomes its raw original.

A provider-fetched URL exposes the URL and authorizes a remote fetch with its own destination, retention and mutable-content uncertainties. Prefer an authorized immutable byte payload when exact-byte authority is required; if the route only fetches mutable URLs and no binding can be proven, that profile cannot satisfy this contract. Presigned URLs are sensitive bearer capabilities and must not enter ordinary logs. A route reference to previously uploaded content still requires current recipient/reuse authorization and expiry checks.

A raw upload can be blocked while a specifically approved redacted derivative is permitted; that is a new bounded artifact and decision, not automatic declassification. Failed preflight emits `attempted=false`; partial transmission emits its actual uncertainty. RT-F05 tests same-source/different-recipient, source swap, redirect, raw/thumbnail confusion and revoked grants. No egress was attempted here.

<a id="r-t-q12"></a>
## Q12 Parsing containment and fail closed behavior

**I, RT-R09.** Require R-U's qualified isolation profile before any complex decode, metadata extraction, archive traversal or rendering. Pass a scoped immutable input handle and bounded output directory, not ambient project/home access. No network, credentials, macros, script evaluation, external entities, embedded-object execution, automatic font/codec download or shell-open action. Bound compressed bytes, decoded bytes, dimensions, pixels, tracks, frames, pages, nesting, expansion ratio, CPU, wall time, memory and output count independently. A trusted parser name is not a boundary.

Treat declared MIME, magic checks and parse agreement as separate evidence. Polyglot/ambiguous types, unsupported encryption and incomplete streams do not earn a guessed parse. External references are enumerated as inert metadata with withheld targets; fetching them is a separate operation. An antivirus/CDR service is itself an optional recipient/transform and cannot be invoked under a supposedly offline path. S12 supplies threat motivation, not proof of containment.

On timeout, limit, malformed structure, sandbox loss or parser crash: fence further stages; record stage/reason and partial work; retain/quarantine or erase source and partials according to rights; publish no partial derivative as complete; do not silently retry in-process or upload it elsewhere. Bounded partial extraction can be a separately admitted artifact only if policy explicitly permits its missing coverage. Stop and the writer remain usable. RT-F06 uses synthetic parser-error events and limit metadata; actual hostile parser execution requires a separate disposable, approved sandbox campaign. This report contains no exploit file.

<a id="r-t-q13"></a>
## Q13 Context and resource quantities

**I, RT-R05.** Track an explicit counter tuple: value or null; unit; availability/reason; scope; measurement/estimator source/version; observed time/window; cumulative or delta semantics; confidence/uncertainty when justified. Zero is permitted only with positive evidence of zero activity, or a statically impossible admitted action with the reason stated. Absence of an adapter event is unknown.

| Representation | Admission/context dimensions, retained separately |
|---|---|
| Original bytes and metadata | Source bytes, encoded wire bytes, metadata bytes/field count, stored-copy bytes, complete/incomplete length |
| Image or page image | Width/height, decoded pixels/bytes, image count, route-specific tiles/patches/tokens and detail mode; original and sent dimensions |
| Audio | Duration, sample rate/unit, channels, samples/decoded bytes, encoded bytes, transcript text tokens and route audio tokens where reported |
| Video | Duration/time base, track count, decoded versus selected frames, sampled timestamps/coverage, pixels per selected frame, audio quantities and route counters |
| Document/structured file | Pages/blocks/rows/cells, extracted text tokens, embedded image quantities, omitted ranges, rendered bytes and generated summaries |
| Derived description/embedding/output | Text tokens or vector dimensions/bytes plus every producing call; generated image/audio/file quantities and validation work |

No universal token conversion is assumed. A prompt can contain text plus image representations of the same page; physical uniqueness does not imply billing deduplication. Hard request limits and task resource budgets are different constraints. For unknown spend/quota bounds, strict-cap admission refuses unless a qualified conservative bound is available. Any approved uncertainty policy used within that strict profile must itself furnish a justified finite upper bound within the same cap; approval cannot turn an unknown bound into a hard-cap guarantee. Otherwise only a separately admitted non-strict profile could proceed, explicitly without that guarantee and without silently weakening any required task cap. An unknown infinite spend remains unauthorized. RT-F07 includes explicit zero, null, estimated, cumulative and conflicting units.

<a id="r-t-q14"></a>
## Q14 Compaction caching and rehydration

**I, RT-R10.** Keep exact active instructions, grants, task/gates, pending interactions, source/derivation references, material loss/uncertainty and unresolved effects in the non-droppable capsule. A preview, duplicate decoded representation or redundant OCR text may leave hot context if its absence fits the task and it is lawfully rehydratable; the canonical source and its validity obligations do not disappear by summarization. The single context governor commits the new epoch; helpers propose artifacts only.

Rehydrate through current audience/project authorization before lookup/content exposure. Validate source identity/digest/revision, retained availability, expiry/tombstone, rights, transform dependency/configuration, recipient and route capability, and current budgets. Mutable URL, local path or provider file ID is not a durable content identity. If a source was legally deleted, lost or expired, mark unavailable and stop/replan rather than fabricate a recovered copy. Reprocessing a permitted retained original is a new admitted transform with new accounting, not a free cache hit.

Separate source bytes, decoded cache, derived semantic artifacts, compiled route payload and provider/session cache. A cache key includes policy/context/transform versions but does not itself enforce authorization. Raw cross-domain hash matching is forbidden. Reuse avoids a call only when an independent receipt establishes it; provider cache savings remain route-specific unknowns here. RT-F13 combines compaction, source mutation, changed rights, lost node and route switch. Passing reference integrity does not establish semantic continuity or improvement over direct harness use.

<a id="r-t-q15"></a>
## Q15 Accounting without a media side channel

**I, RT-R05/RT-R06.** Extend DS-26's attribution/quantity ledger and financial/capacity settlement ledger, not a new media bill. Every ingest, decode, OCR/ASR, description, embedding, summarization, upload, generation, preview, retrieval, validation, retry and cleanup attempt binds the parent operation/task/role/reservation, host, route/model/interface where used and actual outputs. The production operation and its recovery allowance remain separately attributable within the existing normal/recovery scheme; these are not competing canonical ledgers.

Quantity evidence records source bytes, transmitted bytes, local CPU/GPU time and memory high water where observable, model/provider counters, and output units. The settlement side records actual charges or native subscription debits with evidence and unresolved cells. Local compute is not assigned money without an approved rate card. Retries have real cost even if output is discarded. Native harness helpers must be counted explicitly or marked unavailable under R-F's exact accounting caveats; upstream-only workflows cannot acquire an invisible native API or OCR-model helper.

Reconcile finalized deltas or qualified cumulative totals by request/attempt/epoch. Never sum repeated cumulative events, count included media tokens twice as both total and subset, or subtract a reservation as if it were a refund. A partial upload with unknown remote processing keeps the possible charge unresolved; cancelled is not free. RT-F07/RT-F08 replay evidence, inject late settlement, cross an epoch and preserve unknowns. Full-workflow comparison includes human review and residual uncertainty, not only the main answer's token total.

<a id="r-t-q16"></a>
## Q16 Stop and partial media operations

**I, RT-R11.** Reuse D022: **Aggressive** fences further selected-agent dispatch immediately and requests forceful interruption without waiting, with descendants shown separately; **Full** covers the selected agent and owned children, decoder/uploader/render workers, shells, monitors and relaunchers; **Lazy** closes admission and stops at a named observable boundary with deadline and configured escalation. `checkpoint`, `interrupt` and `drain` are mechanisms, not extra Stop modes. A socket close or decoder exit cannot establish remote cancellation or deletion.

For decode, the checkpoint is the last committed complete output unit and precise source coverage; an incomplete chunk stays partial. For upload, distinguish bytes offered by the application, locally accepted by transport, remotely acknowledged/durable if evidenced, complete-object receipt, model-processing receipt and financial settlement. Do not report the local socket's byte count as exact remote disclosure. Record a known minimum and bounded maximum when justified; otherwise the remote amount is unknown. Encrypted wire bytes, retransmissions and content bytes are separate counters.

A streaming source cannot have its final digest before it exists. Authorize a source, recipient, permitted transformation, maximum bytes/duration, time window and segment boundaries; bind each completed segment, cumulative chain and final completeness marker. If policy demands approval of all exact bytes before exposure, streaming is incompatible and buffering or refusal is required. A checkpoint does not permit a revoked upload to resume. The adapter's existing owner controls reconciliation and retries, with no automatic new effect after a lost acknowledgement.

Media buffers and worker queues are bounded and separate from control/writer capacity. Preview backpressure cannot delay admission fences indefinitely. Unknown remote chunks/worker state survive crash, detach, route switch and recovery; no reopening occurs solely because a UI reconnects. RT-F08/RT-F11 test these traces under all three modes. Physical response time and remote enforcement remain unmeasured until profile-specific local tests.

<a id="r-t-q17"></a>
## Q17 Terminal rich media and accessibility

**I, RT-R12/RT-R13.** The stable text record is always available; optional previews are replaceable projections. Compare four implementations rather than choosing a terminal protocol.

| View option | Appropriate use and required bound | Limit and competitor |
|---|---|---|
| Negotiated inline image protocol | Exact terminal/multiplexer/remote-hop profile, bounded payload/placement, inert renderer-generated controls and explicit preview activation | Use [S18](#rt-s18-facts) and [S19](#rt-s19-facts) for source semantics. Unknown support falls back; compare text/open reference |
| Half-block or character approximation | Bounded cells and redraw, textual legend, known color/width policy, explicit lossy-preview label | Dense charts, low contrast and screen readers can fail; compare source viewer or description |
| Text description and structured data | Short label plus available long description/transcript/table; provenance, coverage and uncertainty retained | A generated description can be wrong; compare source inspection rather than hiding the missing semantics |
| Explicit open in viewer | Audience-authorized revision-bound handle and size/type warning; approved inert viewer profile or an explicit separate effect | Local path may not exist on the client or may reveal private paths; compare deferred authorized retrieval |

Escape/control sequences found in filenames, extracted text, SVG, captions or model output remain inert. Only the trusted renderer emits its negotiated control grammar; untrusted payloads cannot request file reads, clipboard changes, downloads, hyperlinks or command execution. A file-transfer capability must not be mistaken for a preview capability. The terminal or external viewer may itself decode the preview outside the original parser sandbox. Treat that renderer as an additional qualified boundary and disclosure recipient; a sanitized/re-encoded derivative reduces selected content features but does not prove the terminal has no parser vulnerability. If that boundary cannot meet the required profile, use inert text and defer opening. No autoplay audio/video, blinking progress or motion by default. Reduced-motion uses stable progress text and still frames; high contrast includes textual labels and patterns, never color alone. Plain text exposes source/location, status, loss, budget and available actions without ANSI dependence.

Keyboard navigation reaches attachment details, source/caption toggle and Stop with stable focus. Screen readers get a concise semantic announcement, not per-frame/per-token chatter; long descriptions remain navigable. Character art does not count as an accessible text alternative. R-K owns terminal/AT qualification; R-N owns later GUI accessibility. Windows/Linux floor compliance is not inferred from a macOS terminal example. RT-F09/RT-F11 require incomplete-preview recovery, resize/multiplexer mismatch, output flood and accessible linear inspection; unknown terminal/AT combinations remain unqualified.

<a id="r-t-q18"></a>
## Q18 Generated output artifacts

**I, RT-R14.** Output capabilities are separately declared for raster images, diagrams/source graphs/vector assets, audio, documents and structured deliverables, with video treated as a separate optional output capability if provided. A route supporting an input modality need not generate it. Deterministic exporters and model generation are different producing operations. Preserve generating prompt/input artifact references, actual influence set, operation/attempt, route/model or exporter build/config, source dependencies, output digest/version, resource/cost evidence, rights/notices and verification status.

Generated source diagrams, raster previews and exported PDFs are distinct linked artifacts; a pretty render does not validate the underlying graph or factual claims. Audio carries transcript/voice attribution and synthetic-generation disclosure when required by policy/rights. Documents retain editable source versus export links and any partial validation. Generated content starts as a candidate, never source-observed evidence merely because it is an attachment. Store quality/factual checks separately from decode/render success. A failed generation, refused output or partial stream is an outcome, not a blank successful artifact.

Use [S21](#rt-s21-facts) and [S22](#rt-s22-facts) for output-interface premises; no vendor is selected. Receiving bytes does not authorize publication or cross-provider reuse. R-H output-category restrictions, third-party source obligations and privacy constrain every export and caption. RT-F10 checks versioning, prohibited reuse, generated-status labels and helper accounting; it does not establish originality, legal ownership or artifact truth.

<a id="r-t-q19"></a>
## Q19 Descriptions captions and nonvisual consumption

**I, RT-R13.** Attach short alt text, long description, captions and/or descriptive transcript as separate language-tagged derivatives with source locators and author/method. User-supplied wording, extracted labels and model descriptions are distinguishable. A task-relevant chart description should expose the values/relationships needed for the task when known, with a structured table if available; otherwise mark the information unavailable rather than guessing. WAI guidance motivates separating these functions [S16,S17].

Descriptions inherit source privacy, readers, rights and expiry. They can reveal more than a small preview, so low bandwidth is not a privacy classification. A helper-generated description has its own authorized route and budget, never a hidden call on opening a view. If no description exists and no transform is enabled, show a metadata-only placeholder and ask for a supplied description or explicitly admitted derivation through normal workflow. The description's coverage/loss and review state appear adjacent to it. Alt text cannot satisfy a task requiring exact source detail without verification. RT-F09/RT-F10 use deliberately misleading captions and meaningful non-speech events to test this distinction.

<a id="r-t-q20"></a>
## Q20 Fallback and complete canonical records

**I, RT-R12.** Use a stable placeholder containing authorized artifact handle, revision, declared/validated type, available size/duration/page count, source/derived/generated status, completeness, description availability, material loss and reason preview is absent. Fields disallowed to that audience are omitted without leaking the hidden item's identity/size. The placeholder is a projection of already retained canonical facts, not a substitute for them.

An authorized local client may resolve a local path; a remote or low-trust client gets an audience-scoped artifact handle, not a server path or bearer upload URL. Deferred open performs current authorization and viewer capability checks. No automatic shell launch, browser navigation, download, thumbnail creation or model description follows attach/reconnect. Canonical records keep the source/derivation/receipt graph even when a viewport drops disposable render updates. If retention rights forbid source retention, the canonical record honestly preserves only permitted metadata and the unrecoverable state; completeness of the record does not mean completeness of retained media.

GUI later adds page/region/timeline navigation over exactly these IDs and operations. Dragging a file into a view is an ingestion proposal, not approval to upload it. RT-F09/RT-F13 compare plain text, unavailable renderer and later-GUI projection at the same authorized source cut. Equivalent displayed IDs do not prove equivalent pixel fidelity.

<a id="r-t-q21"></a>
## Q21 Recommendation competitors and decisive falsifiers

All recommendations are conditional candidates. Their exact mappings also appear in `recommendations.json`.

| ID | Candidate and real competing option | Decisive falsifier | A pass would not prove |
|---|---|---|---|
| RT-R01 | Shared artifact/derivation graph versus qualified raw pass-through with the same mandatory provenance/loss/rights manifest | Any transform loses a source/recipient/authority binding, or same bytes cross domains through equality lookup; F01/F12 | Truth, rights or universal portability |
| RT-R02 | Task-sensitive structured normalization versus raw route-native handling/manual extraction | Required event/cell/layout relation omitted or wrong source location; F01/F03 | Best extraction engine or general accuracy |
| RT-R03 | Per-dimension loss vector versus task-specific structured loss checklist attached to a summary | Loss/unknown omitted, confidence treated as proof, or a descendant upgrades trust; F03/F12 | Quantified semantic fidelity |
| RT-R04 | Maintained descriptors versus fresh authorized deterministic capability discovery before each admission, both fail-closed | Conflict widens dispatch, hidden fallback occurs, or refusal claims no effect after upload; F02/F14 | Account entitlement or all route coverage |
| RT-R05 | Separate attribution/settlement projections versus one tagged evidence relation with independently typed quantity and settlement views | Null becomes zero, helper vanishes, cumulative receipt doubles cost or reservation becomes refund; F07/F08 | Savings or monetary precision |
| RT-R06 | Explicit eligible local OCR/ASR where justified versus approved route processing/manual text | Local path egresses, lacks offline dependency or loses matched-quality cost/latency comparison; F04/F15 | Local accuracy, determinism or lower cost |
| RT-R07 | Graph-propagated retention/rights versus per-artifact rights registry with complete copy inventory and query-time revocation checks | Thumbnail/embedding survives forbidden reuse, revoked source rehydrates, offline deletion claimed complete; F13 | Remote physical erasure or legal clearance |
| RT-R08 | Locally materialized exact payload versus immutable provider-file reference with independently evidenced content identity and current recipient authorization | Swapped bytes, redirect, raw-for-thumbnail or revoked-recipient upload proceeds; F05/F08 | Prevention of prior disclosure or all side channels |
| RT-R09 | Per-job isolated parse workers versus a bounded mature parser inside a separately qualified reusable sandboxed media service | Boundary unavailable yet parse occurs, parser network/exec escapes or partial output becomes complete; F06/F11 | Exploit resistance without actual qualification |
| RT-R10 | Reference-preserving compaction versus retained full raw context plus the same control capsule and rights checks | Missing/deleted evidence silently recreated or stale rights reused; F13 | Task-quality continuity or cache savings |
| RT-R11 | Segmented media receipts versus bounded monolithic job with separate responsive control and honest partial-settlement receipts | Stop blocks behind media, post-fence segment starts, or transport exit claims rollback; F08/F11 | Bounded real-host latency or remote rollback |
| RT-R12 | Text-first projection plus opt-in previews versus preview-first activated viewer with equivalent accessible text and control path | Canonical record lost, untrusted escape executes, rendering corrupts controls or view owns work; F09/F11 | Universal terminal/GUI accessibility |
| RT-R13 | Attributed short/long/timed descriptions versus user-authored accessible transcripts/descriptions plus authorized source inspection | Missing essential nonvisual information is labeled complete, or preview opening launches hidden inference; F09/F10/F14 | Caption accuracy or all disability needs |
| RT-R14 | Separate generated candidates/versioned exports versus immutable export bundle with shared operation provenance and equivalent candidate/rights labels | Generated output becomes verified evidence by receipt, rights bypassed or production cost omitted; F10 | Originality, ownership or publication permission |

Unbounded decoding, silently dropped media, untracked helpers, unlabeled summaries, path-only approval and output-as-verified are deliberately invalid negative controls, not competitors. Every real competitor retains the fixed authority/privacy/loss/accounting/Stop invariants. A route-native or manual alternative is not automatically admissible; it must satisfy the same authority/privacy/budget floors. If all alternatives fail, the correct result is a precise blocker. Thresholds for fidelity, latency, accuracy and resource burden require adoption before experiments, not retrospective tuning.

<a id="r-t-q22"></a>
## Q22 Provider free fixture predicates

The full `local-test-handoffs.json` and readable `UNEXECUTED-local-test-handoffs.md` specify inputs, prerequisites, independent oracle, steps, exact pass/fail, evidence, stopping conditions and non-proofs. **All are UNEXECUTED.** They describe synthetic objects, events and inert stubs; no real media was decoded and no malicious payload was constructed. No verified media-pipeline entrypoint exists, so no runnable target command is invented.

| Fixture | Exact contract predicate |
|---|---|
| RT-F01 Ingestion and provenance round-trip | Authorized synthetic original and each derivative retain identity, source locator and all inherited bindings; forbidden/missing fields reject; accepted round-trip equals independently prepared expected records |
| RT-F02 Capability conflict | Effective support never exceeds comparable intersected bounds; incomparable/required-unknown fields block; no recipient/billing fallback; post-dispatch error remains attempted |
| RT-F03 Transcription and transform loss | Every changed/omitted/unknown dimension and original source interval survives chaining; incorrect known transcript remains unverified; missing loss or wrong locator rejects |
| RT-F04 Local OCR ASR route | Enabled, admitted stub yields attributed derivative and quantities; missing model/dependency/permission blocks; zero provider/network helper calls; no actual OCR/ASR execution |
| RT-F05 Privacy-blocked egress | Allowed derivative to exact recipient passes; raw/changed bytes, wrong recipient, redirect or stale grant causes zero dispatch; approval never broadens on retry |
| RT-F06 Hostile-document parse failure | Injected parser failure/limit/boundary-loss returns typed failed/quarantined state; no complete derivative, network, exec or unbounded allocation; control remains serviceable |
| RT-F07 Unavailable-counter accounting | Missing counter remains null with reason; explicit zero remains zero; cumulative duplicate replay does not change totals; estimates and settlement retain different provenance |
| RT-F08 Long-upload Stop | Trace at every chosen boundary preserves offered/acknowledged/unknown delivery and unsettled charges; no post-fence new segment; restart never blindly retries ambiguous dispatch |
| RT-F09 Terminal fallback | Unsupported/failed renderer yields exact accessible placeholder and source/loss references; raw control bytes remain inert; canonical source cut is unchanged; no hidden preview/model work |
| RT-F10 Generated output and descriptions | Output/caption versions, influence, rights and cost retain candidate status; source-only and generated descriptions differ; forbidden redisplay/export is denied |
| RT-F11 Writer Stop and recovery liveness | Saturated/incomplete media and stalled view cannot consume reserved control path; adopted local fence deadline met or explicit failure; canonical events/recovery contain no fabricated completion |
| RT-F12 Attachment authority laundering | Command-looking image/OCR/transcript/metadata/summary never creates a grant, accepted instruction or approval; independent authorized control still succeeds |
| RT-F13 Retention compaction and prior disclosure | Deleted/revoked/expired source never rehydrates; descendants/copies are accounted; offline/prior external copies remain unresolved; permitted reference-only capsule survives route change |
| RT-F14 Disabled-path inertness soak | Each independent probe first detects an admitted harmless synthetic event and the same observer is reset/baselined; missing/blind probe is UNKNOWN/BLOCKED. Qualified disabled interval then requires no decode/model/upload/network/media write or optional import/start; metadata discovery and ordinary controls remain separate |
| RT-F15 Container and coordinate compatibility | Unsupported codec/profile or unbounded expansion rejects before complex decode; tracked page/time/crop transformations preserve expected selectors; no MIME-only portability claim |
| RT-F16 End-to-end continuity trace | Authorized synthetic task moves native→upstream→native with compaction/fork/node-loss events, preserving evidence/loss/authority/accounting, and completes its literal gate without provider calls |

F01–F16 exercise permitted positive cases and negative cases; blanket refusal cannot pass. Tests of stub policy outcomes do not test parser exploit resistance or physical runtime liveness. F11/F14 require independent side-effect monitors on a separately admitted local candidate before anyone can claim execution evidence.

<a id="r-t-q23"></a>
## Q23 What the fixtures can establish

**I, RT-R01/RT-R05/RT-R09/RT-R11/RT-R12.** Attachments carry `authority_carried_none`. F12's oracle compares the canonical grant/directive/approval sets before and after hostile-looking content travels through ingestion, OCR, transcript, summary, embedding retrieval and view rendering. The expected difference is only attributable content/operation records. A separately authenticated permitted control is the positive control; a model's compliance is not the oracle.

F14 instruments optional-code imports, process creation, decoder/model entry, upload/network attempts, write/retention paths and every other declared side-effect channel while disabled, not just a self-reported zero counter. Before accepting that interval, each independent probe must detect its own expected event from a separately admitted enabled synthetic control or harmless mutant through the observed path. Controls use inert local/stub events only, never real provider/model inference, credentials or external effects. Retain per-probe expected/detected receipts, then reset/baseline the same observer identity/configuration before the disabled interval. A missing, blind, failed or unbaselined probe yields UNKNOWN/BLOCKED, never zero. The ordinary-control positive workload proves usability separately and cannot substitute for sensitivity. A minimal refusal/control receipt and bounded installed-manifest discovery are allowed metadata work; no media bytes, thumbnails, derived content or media-store object is persisted. If a frontend copied a dropped file before checking the switch, inertness fails. The upstream sender may already possess a file, but Recursion must not claim that its own disabled ingestion path stored nothing while its spool did.

F07 uses independent arithmetic and evidence IDs to distinguish known zero, unknown, estimate and actual settlement. F08/F11 place the Stop at each transfer/write boundary, leave acknowledgements missing, replay a crash and block a view; an independent event-order oracle checks fences and completeness. Schema validation cannot prove scheduling responsiveness, and a modeled trace cannot prove OS isolation. F16 assesses the task's literal answer and source locations with a hidden independently prepared key; a kept digest graph alone is not productive continuity.

Source trust and factual correctness remain distinct. A well-formed, faithfully attributed OCR error is still an error. A successful fixed fixture gives evidence only for its candidate/pin/profile/inputs/fault assumptions, never all media or future builds.

<a id="r-t-q24"></a>
## Q24 Evidence status unknowns and non proofs

**SD:** official pages document the bounded API and representation facts in the evidence section; committed governance supplies accepted requirements. **LO:** this session inspected static repository/public text, recorded input hashes and checked the authored packet's structure. **I:** artifact, transform, loss, capability, egress, Stop and fixture contracts are design proposals. **U:** every implementation/conformance/quality/performance/security/entitlement result. A public standard or vendor claim does not fill a Recursion measurement cell.

No measured accuracy, cost, latency, fidelity, bandwidth, accessibility or resource advantage is established. No complete provider/modality/codec/language coverage, route qualification, subscription entitlement, legal clearance, complete sandbox containment, end-to-end cancellation, remote deletion, universally portable preview, or advantage over strong direct-harness baselines is established. No component, language, store, framework, media codec, OCR/ASR engine, renderer, terminal protocol, sandbox product or vendor is selected. No accepted Owner decision is reopened.

Concrete next blockers are: adopt the shared Artifact/media extension with R-P/R-Q ownership; select a separately authorized implementation candidate and exact supported-format/OS/terminal profile; provide independent boundary/side-effect instrumentation; freeze task fidelity and Stop/resource thresholds; resolve route/output-specific rights under R-H; and execute independently reviewed F01–F16 before any qualification claim. Exact route media behavior, helper visibility, account entitlement and native quota units remain unknown until separately admitted evidence exists. The public API table cannot substitute for that work.

## Completion gate review

Research coverage is complete at proposal level; runtime qualification is not. `coverage.json` preserves all 24 exact question texts and all nine exact gate bullets with locators, status and evidence limits. Gate 9 is supported only by the bounded authored-packet privacy scan and unchanged named protected-input hashes in `artifact-qa.json`; this is not a repository-wide secrets certification or an inspection of credentials. Delivery files were created in the assigned output directory; no source repository edits were made. No real private media, authentication data or account/host identifier was ingested. Independent review remains pending.
