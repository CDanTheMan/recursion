# Primary-source research — 2026-09-08

Read-only worker source_protocol_research inspected the predecessor and primary sources;
root independently opened the etcd guarantee, Raft and RFC pages before construction
admission. No installation or live service trial. These sources inform constructions and
do not prove Recursion's protocol or select production architecture.

[etcd API guarantees](https://etcd.io/docs/v3.7/learning/api_guarantees/) describe atomic
operations, total-order revisions and delayed watch delivery. Inference for this model:
capture an authority revision covering registration and append, then validate it at
publication. The model supplies the atomicity premise; it does not deploy etcd.

[Raft extended paper, section8](https://raft.github.io/raft.pdf) describes client serial
numbers and retained responses to prevent duplicate application after a lost reply.
The model separately constructs stronger caller/full-body conflict semantics. Intact
retained state and atomic state/receipt commits remain abstract assumptions.

[RFC9162, section2.1](https://www.rfc-editor.org/rfc/rfc9162.html#section-2.1.2) distinguishes
inclusion and append consistency. These cannot show that an outside intent or attempt
was ever registered. Exact captured registry and ordinal coverage must be constructed.

[Chandy-Lamport](https://lamport.azurewebsites.net/pubs/chandy.pdf), reviewed by the worker,
includes channel state and ordered-channel premises in distributed snapshot reasoning.
A consistent distributed snapshot does not directly establish a current single-source
append boundary. No distributed snapshot protocol is implemented here.

The worker identified a source-specific constraint in p_literal.py: original attempt
mapping comes from AttemptStarted records. Registering another attempt while the record
head remains unchanged must therefore block attestation and current reconciliation.
This is local source inspection, not a fact inferred from the external papers.

Bounded alternatives: optimistic captured revision with pending registration; the same
protocol with atomic registration/start. The latter eliminates one pending interval while
preserving uncertainty. A sealed-window alternative was considered but not selected for
construction; it adds close/open and progress obligations without resolving physical
source truth. This is a bounded comparison, not product language/store/framework choice.

Meaningful counterexamples are preregistered: omitted middle/tail ordinal despite current
head, delayed collection, concurrent registration, append before publication, same-version
append/fork, foreign mapping/body/caller, lost reply and duplicate request, source restart,
PAUSE and stale reconciliation retaining A6. Source truth outside admitted transitions,
physical recovery/reclamation and full original comparison remain explicitly unproved.

[Microsoft job-object documentation](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
documents default subprocess membership, job termination and kill-on-close. The new wrapper
uses an anonymous job assigned before resuming its suspended child, covering frozen gate
grandchildren without editing historical scripts. The [extended limit structure](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)
defines committed-memory limits and accounting. These controls do not establish a general
network/filesystem sandbox; actual local containment probes are separately retained.
