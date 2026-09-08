# Shared composition evidence — 2026-09-08

Parent: `goal-recursion-v2-execution-fabric`. Canonical dispositions are in
ARCHITECTURE, EXECUTION-FABRIC and TERMINAL-RUNTIME; this packet holds their method
and reproducible evidence. It advances the formal-comparison stage after PR101.
It does not complete that stage or release the common-writer migration blocker.

The accepted model compares15 declared environments, including a free-interleaving
core, across two independent concrete representations. Both close49,742 states
and290,954 edges in aggregate across those environments. Counts include identical
states occurring in different environments; they are not unique global-product
counts. The third relation checks complete postconditions, enabledness, ownership
footprints and invariants on every edge. Exact state/edge correspondence adds an
implementation cross-check. Twenty-five inclusive-reducer guard mutations expose
reachable violations; five checker calibrations include a present-but-no-op Stop.
These are modeled results, not measured runtime performance or integration support.

| Candidate | Concrete mapping | Disposition and limit |
| --- | --- | --- |
| Authority aggregate plus broker refinement | Authority record owns selected generation, writer term/serial, admission, evidence inventory and lifetime accounting. Broker record owns its queue, reader pin, copied snapshot, gap/credit and installed view. Publication/evidence append immutable presentation facts; reclamation checks the broker pin. | Retain as preferred modular candidate. Cross-component predicates are explicit contracts, not independent unsynchronized writes. No state-space or latency reduction has been proved. |
| Inclusive record | One complete state owns the same obligations; a separate reducer updates it directly. | Retain as coverage reference and fallback when the broker refinement cannot preserve an aggregate obligation. It has the same normalized graph here, not a demonstrated complexity disadvantage. |

The finite equivalence relation pairs the authority and broker records with their
complete flattened inclusive record. No authority-relevant state is discarded.
The independent relation checks broker-only transitions as well as authority
changes; it does not claim a general abstraction theorem for an arbitrary broker.

The consequential results are:

- A snapshot is a view of a particular historical evidence cut. Installing an
  earlier successful cut preserves a newer unresolved effect-attempt start and
  canonical quarantine. Literal status, unsettled IDs and settlement hold differ:
  `later-start-only` remains `succeeded` with a hold; conflicting receipts can
  require a hold with no pending IDs. An external-effect reservation is a separate,
  currently uncomposed obligation.
- A reader can pin G1 while G2 is published and the invocation is released. A
  refused reclamation, explicit copy/wait, later reclamation and installation of
  the independent copied snapshot occur in one ordered witness. Copy completion
  alone cannot release the reader's pin.
- Same-term writer replacement needs a serial distinction even with unchanged
  parent/target. A separate boot change invalidates the term. The isolated denial
  witnesses have a staged candidate and open admission, so another failed guard
  cannot explain rejection. Publication survives restart before acknowledgment;
  a literal lost-reply transport is not represented.
- Stop applies from a saturated queue. An old permit can still execute after
  local Stop and before recipient fence installation; installation then prevents
  that execution. Local process death, old transport ACK and provider quota reset
  cannot settle another attempt or erase lifetime compute.
- Internal recovery requires a detected gap, clears old EVENT credit on emission,
  blocks delivery while installation is pending, and preserves newer broker-owned
  entries. One ordered witness retains a prequeued newer entry through installation,
  then delivers it after fresh credit. Emission interrupted by broker restart does
  not advance installed content. M1B receiver pending deliveries are a different
  queue; full wire/byte-credit/ACK/handshake correspondence remains unproved.

Reuse the frozen M1A/M1C fixtures, strict schema paths and evidence adapter as
validation references. Adapt the generation-reader and internal recovery contracts.
The two reducers, finite schedule explorer and independent obligation relation are
new local experiment code, not a selected product framework. No upstream code or
new dependency was imported. Existing repository licensing and frozen dependency
context apply; this campaign makes no new distribution or provider-terms judgment.

The literal controls are locally executed fixture evidence: seven explicit
status/pending/hold/permission mappings and the predecessor's actual M1A PAUSE,
duplicate and quarantine controls. They establish neither production evidence
authenticity/completeness nor a graph-to-runtime integration proof. No external
provider, model inference, login, service, deployment or paid experiment runs in
the model. Included capacity was checked; reset credits remain untouched.

Independent review changed the method before acceptance. Run01's state-only
witnesses did not establish all required event orders; run02 still lacked recovery
credit/trigger correspondence and an explicit queued-future delivery path. Their
complete sources/results remain externally retained. Run03 established the revised
semantic result; the final discovery rerun also records the exact installed
jsonschema version in prospective admission. None of those earlier runs is silently
promoted to final-candidate validation.

The remaining boundary is explicit: two goals reserving six units each from ten;
separate uncertain-effect reservations; typed goal/lease/issuer namespaces;
complete original core/cross profile cardinalities; full M1B wire mapping; process
containment at birth; remote relocation/record retirement; consultation, adoption
and configuration closure. Finite witness paths do not prove fairness or eventual
delivery of every retained entry. All27 original trace rows and six obligations
remain in coverage.json, with partial support or no new coverage.

No consequential new Owner direction is needed. Keep the approved aggregate plus
explicit broker refinement, compare the inclusive fallback, and continue the
bounded requests in next-probes.md before formal freeze, language comparison and
storage comparison.
