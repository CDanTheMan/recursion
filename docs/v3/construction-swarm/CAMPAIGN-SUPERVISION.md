# Campaign supervision — 2026-09-11

Lucas authorized capacity above100 and asked that Grok oversee working agents
instead of terminating them at an arbitrary short cutoff. Native plan version3
implements this prospectively. Version2 preserves its prior behavior.

With an explicit `--campaign` policy, prepare defaults the worker duration to
28,800seconds and caps the work window at the policy's immutable campaign end
minus its closeout reserve. There is no inferred inactivity cutoff. The actual
worker duration remains capped by that work window. Four machine-wide command
slots, 60second command sandboxes, existing cgroups, output limits, one native
worker pool, and nonrefundable unknown reservations remain enforced.

Version3 admits at most200 reserved worker slots, subtracting all earlier native
and Windows holds. This is an authorized capacity bound, not a claim that200 live
clients have been qualified by this campaign. The prior live qualification
observed77 concurrent; this campaign's earlier wave observed65. Resource headroom
still determines useful admission. No quota reset or paid route is enabled.

Workers check owner stop paths and fresh named quota windows. Reset identities,
the binding minimum, and the quota reserve are fixed in the admitted policy.
A shared observation bounds quota-file checks to approximately once per second;
worker STOP, command cancellation and the absolute worker window remain enforced.

`foundry_coordinator --live-revision N` reads the hash-checked ledger plan and
requires its external plan file to match. It uses a separate supervision lock,
so it can observe running workers. Each immutable revision/batch is a separately
charged call on the explicit selected route. Up to20 workers enter each batch.
The snapshot includes the task objective, elapsed-time observation, last completed
tool receipts and bounded untrusted excerpts. Activity is not scientific progress.
Unknown tool cleanup cannot advance. Partial files remain incomplete observations.

Grok returns evidence-bound `continue`, `inspect`, or `stop_for_review` advice.
It cannot accept research, modify workers, renew policy, launch descendants or
publish. Astra inspects the evidence and performs authorized follow-up actions.
Terminal synthesis retains its existing contract. No background scheduler is added.

Independent Astra source review found no remaining deployment-blocking defect
after correcting plan binding, reset identities, v3 defaults and live uncertainty.
The native regression completed68 tests:67 passed and one Windows-only test was
skipped. Ruff passed. Evidence is retained at
`/var/lib/recursion-foundry/campaigns/research-20260911-155142/framework-v3-qualification`.
These are framework checks, not the inherited scientific acceptance gates.

Freeze the reviewed package into a new native directory; never replace a package
beneath active clients. The first substantive v3 wave must retain actual live
supervision, transport, model-identity and cleanup evidence before claiming those
paths demonstrated with providers.
