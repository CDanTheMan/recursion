# Prospective method decisions — 2026-09-09

Two independent read-only packets proposed the obligation audit and periodic workload
comparison. The initial scheduling proof used the last-offer tick T directly. Root
identified that arbitrary H6 opportunities can remain after an early final offer;
the reviewer confirmed S=max(6,T), actual periodic suffix start, is the correct bound
origin for the stated useful-operation proof. The superseded T justification is
retained here and is not used to admit or judge any model result.

The initial audit wording called trace22 itself unselected-unrun. Direct source reading
showed that conflated two fields. Its original row status is constructed-unrun; the
original extension policy is unselected-unrun. The baseline construction separately
says not-selected-unrun, and the later shared-reservations overlay selects a bounded
one-transfer extension with partial support. The reviewer confirmed this correction;
the machine overlay copies all original rows and each later overlay verbatim.

The11 inspected registries comprise one baseline /traces registry and ten /slice_traces
overlays. The prospective18-supported/9-without-positive-entry count concerns those ten
slice overlays, not all possible evidence in the repository. Proposed Q responsibility
links are labeled inferences; the original question dependency arrays remain unchanged.

Budget2 is a threshold before permitting resealing, analogous to the existing one
policy. It does not block further append service if a collector opportunity has not
arrived. A currently empty backlog permits an earlier capture; a new offer before C
can change that decision. Initial/refill budget2, dynamic backlog checking, seals and
unchanged-count idling are explicit premises. Two/drain read dominance is tested only
at joint completed endpoints. Partial read counts do not establish a winner.

The first admission at9ead065 retained268657788 bytes of raw source snapshots,
exceeding the268435456-byte artifact limit before any model process was created.
That failed run remains intact, with receipt SHA-256 f1cbe9e1d82424aebf2bbf1f01acb7bb2e5df3160642b6118670c6d059e72bc6.
New snapshots use deterministic lossless gzip (mtime0). Working and Git blob hashes
continue to bind original uncompressed source bytes; snapshot_codec identifies how
to restore them. This changes storage, not source content, model limits or evidence
claims. The failed receipt is never treated as an accepted run.
