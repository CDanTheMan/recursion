2026-09-10 — conditional pre-stage correspondence

Source inspection only. No imports, symbolic enumeration or new model execution. Candidate 9798b38a780d4849e604ba5a461b2266f19392d7 remains unchanged. schedule_design returned this argument at 2026-09-10T20:44:10Z; root retains it as a conditional source argument, pending independent review, not a checked all-order invariant.

Paths below are relative to the candidate worktree. S denotes experiments/v3/cut-source-overnight/, A denotes S/batch-06/, Q denotes experiments/v3/cut-publication/.

The sufficient induction premise is typed equality of source authority fields and adapter journal, equal guard inputs from the Q portion, and original reachable data shapes. A/a_domain.py:25–27 overlays the journal source incarnation when constructing guard inputs. A/a_inclusive.py:8–19 and A/a_split.py:8–19 preserve the Q core and invocation list for nondelegated calls.

| Clause | Source correspondence under those premises |
|---|---|
| Registration | S/s_inclusive.py:14–20, A/guard_a.py:15–21 and A/guard_b.py:13–19 have the same completeness, scope and conflict precedence. Successful initial registration changes registration and source_revision. |
| Ordinary attempts | S/s_inclusive.py:21–34, A/guard_a.py:22–35 and A/guard_b.py:20–36 have the same registration/pause/duplicate/gap order and pair construction. Success appends one pair and increments revision; refusal preserves the journal. Atomic branches are outside this profile. |
| Setup appends | S/s_inclusive.py:36–53, A/guard_a.py:37–54 and A/guard_b.py:38–59 construct the same request, body, incarnation, index and receipt. Matching success gives identical append_log, append_receipts, append_reply and revision. |
| Capture and collection | S/s_inclusive.py:55–62, A/guard_a.py:56–63 and A/guard_b.py:61–70 construct the same five-tuple collection, clear collected on opening, and insert the same sorted index/raw pair. Neither changes revision or registration. |
| Refused attestation | S/s_inclusive.py:63–68, A/guard_a.py:64–69 and A/guard_b.py:71–76 use missing capture/cut, freshness, inventory, registry precedence. Given packet06's conditional refusal conclusion and equal inputs, the exact refusal agrees. The adapters do not invoke Q or change attestation. |
| Restart | Q/q_inclusive.py:7–13, Q/q_split.py:7–11,88 and A/a_inclusive.py:10–16, A/a_split.py:10–18 advance the source and adapter journal generations identically under the journal-equality premise. Equality of the adapter's actual Q-core generation additionally requires the delegated-Q coupling premise; the overlaid guard view does not establish it. Captured generation stays unchanged. |

The reachable-shape qualification is necessary. Guard B uses a last-entry dictionary lookup for append receipts, whereas S/guard A use the first match. The original setup has distinct append-0/1/2 requests and the core has no append (S/s_domain.py:43–58,63–71,147–149), so they agree here. Capture requires the collect-open five-tuple; attempt maps require uniquely constructed keys. This is not equality on arbitrary malformed states.

Remaining proof obligations:

1. Whole compared-state agreement requires a delegated-Q coupling invariant. Initial journal equality follows from S/s_domain.py:12–21 and A/a_domain.py:21–23. Successful setup/delivery hypotheses alone do not establish each intermediate Q field or response. Fixed setup and delivery calls must preserve S-projection/Q-core correspondence despite different completion masks. Local core branches preserve that correspondence once established; restart is directly mask-independent. Live-generation equality with empty source_name is sufficient for the relevant comparison field (S/batch-05/semantic.py:103–106); no incarnation pair may be fabricated.
2. Whole response/invocation agreement requires prefix-level delegated-call justification. Local clauses above establish exact visible decisions and append replies with no Q invocation. Responses use the adapter's outer decision, not its potentially older core decision (A/adapter_traces.py:23–25). The Q subprofile retains potential calls, including refused attestation; its mask must contain only actual calls (A/a_domain.py:15–19, A/a_audit.py:17–34). Auditing supplied histories does not prove all orders.
3. Typed trace preservation remains separate: literal occurrences, original dependencies, patches, full-state hashes, and both completion masks require the trace construction/restoration invariant (A/adapter_traces.py:54–75). Case-specific identity proofs remove only the staged difference (S/batch-07/identity.py:39–64).

No reachable counterexample was established by this inspection. The result is a conditional pre-stage journal/local-response lemma. It does not establish accepted comparison over all 40,320 orders, a stronger reduction, source truth, Q1–Q6, composition, fairness or recovery.
