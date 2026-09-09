# Campaign D: conditional architecture decision dossier — 2026-09-09

Batch 02 supports a narrower design space and a clearer correctness backlog. It does
not establish source validity, full composition or a production architecture choice.
The two-service addition has no measured-objective advantage over drain in the original
finite inventory. The substantive unresolved choice remains one versus drain under an
explicit workload/objective, while source and composition obligations remain separate.

| Question | Supported conclusion | Boundary before using it |
|---|---|---|
| Can collection run forever under finite offers and recurring A/C opportunities? | Retained same-count idling and sealed captures give conditional eventual completion. | No physical-time guarantee or crash/restart theorem. |
| Can declared periodic service give a numeric bound? | Completion by S+len(W)U; exact per-record maxima and witnesses for AC/AAC/ACC. | Unit-action clock, H6 prefix, finite original inventory and stated suffix. |
| Does adding more A opportunities always improve waiting? | The model compares identical prefixes and exposes record-specific tradeoffs; C releases seals. | Period lengths differ, so no physical throughput or probabilistic inference. |
| Is two-service preferable to drain on these metrics? | Drain is no worse on completed reads and matched-record waiting for N<=4; two is identical for N<=3. | No general dominance claim for larger inventories or different objectives. |
| Is one preferable to drain? | Existing completed counterexamples rule out universal read/wait dominance. | An owner-selected objective and workload assumptions are still needed. |
| Do the new results close source or original trace obligations? | No.18 trace IDs have partial slice entries; nine have none in the inspected slice registries. | Full original schedules, authentic originals and explicit composition mappings remain separate requirements. |

A conditional decision within this exact model can eliminate two-service when the only
objectives are completed ordinal reads and matched-record waiting against drain: its
additional budget state buys no advantage. That conclusion does not choose a runtime,
change architecture policy, select a framework/provider or authorize integration.

The next correctness bottleneck is the evidence bridge. A-audit.json preserves Q1-Q6,
their explicit dependency arrays and all six obligations. Q6 cannot be settled by
assuming Q1-Q5. Coverage of collection schedules cannot substitute for attestation,
identity, original-data admission/classification or independent record-position evidence.
Replaying the previously interrupted experiments is outside this batch.

The nine rows without positive slice entries concern selected-actor Stop and relaunch,
ordered preference/revocation, fork/retry allowance lineage, partial activation/rollback,
process-registration crash timing, external-effect relocation/rendezvous, retirement,
changing wire IDs and metering across reset/crash. This is an audit of named registries,
not authorization to activate services or execute those operational scenarios.

The practical owner decisions for later research are which correctness boundary to
resolve next, which arrival/service assumptions represent the intended system, and
which explicit read/wait objective matters. Preserve conditional alternatives until
those decisions and admissible evidence exist. No extra campaign is activated here.

Acceptance evidence is separate from this synthesis: focused A/B/C passed; final review
publication requires both complete 45-item gates and two independent exact-candidate
reviews. Those later receipts belong in the external final-candidate completion record.
