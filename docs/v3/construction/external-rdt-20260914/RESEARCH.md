# Kernel research triage — 2026-09-14

Lead synthesis of the external SWE-2 report, independently checked against source df158fe. The original report and tool evidence remain in the campaign attempt. Its source-access gate passed, but its roughly1,000-word prose exceeded the900-word packet limit; the original is not accepted. This shorter derived note preserves useful findings and corrections. It is not a new Owner decision or formal proof.

| Area | Current evidence and bounded next question |
|---|---|
| Admission | ARCHITECTURE and ACCEPTANCE require policy/GoalSpec/grant/route bindings, fence and PAUSE/revocation epochs. Existing finite subsystem results do not close the full corpus. A next probe can inject one stale epoch or digest into an explicitly bounded composition and compare both representations. |
| Reservations | The shared-reservation specification models conservation and unknown-effect holds. Retention across an integrated broker RESET/replay path remains a separate obligation. A proposed composition must retain the reservation and forbid dependent dispatch until reconciliation. |
| Replay | The replay dossier records115 local cases and435 helper processes, with a synthetic trust anchor and named cuts. That is historical evidence, not a fresh rerun or power-loss guarantee. Reader pins, publisher death and reclamation need an explicit concurrent model. |
| Wire | The frozen M1B oracle specifies credit, ACK, cursor units and gap/RESET behavior. The new tests add literal controls against that single-stream oracle. A two-stream experiment needs a separate composition; feeding two streams into the present oracle only tests its stream-mismatch refusal. |
| Recovery | OR-032 fixes the relative-allowance interpretation. The arithmetic prototype tests exact rational examples only. ARCHITECTURE additionally specifies integer-quantum flooring, committed plus outstanding reservations, unknown accounting and retention across restart/reset. Those ledger obligations remain unimplemented by this prototype. |
| Integration | OR-036 accepts the smallest aggregate plus separately checked broker direction while requiring the inclusive comparison. Remaining adequacy/comparison work does not reopen that accepted direction. The complete six-obligation/27-row corpus, physical recovery and common-writer migration remain unproved. |

The independent tests are supplemental evidence, not full scientific acceptance. Prior experiment counts are attributed to frozen documentation rather than claimed as newly measured. No language, store, framework, provider or autonomy policy is selected here.

Source slices: [architecture](../../ARCHITECTURE.md), [state](../../STATE.md), [acceptance](../../ACCEPTANCE.md), [decisions](../../DECISION-REGISTER.md), [wire profile](../../M1B-WIRE-PROFILE.md), [reservation specification](../shared-reservations-20260908/specification.md), and [replay dossier](../replay-store-evidence-20260907/dossier.md).
