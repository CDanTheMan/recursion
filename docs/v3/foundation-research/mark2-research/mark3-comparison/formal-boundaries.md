# Comparison specification for the two formal boundaries

2026-09-07. Preregistered design, not a formal model or proof. OR-036 is accepted. The first
construction candidate is the smallest aggregate plus an independently checked bounded broker
refinement; the broker-inclusive comparison is required. No M1 schema or contract is edited.

## Common state and observation boundary

Use the immutable M1A planning, M1B execution and M1C integrity contracts and literal regression
vectors. The model adapter must explicitly bind these six existing obligations:

1. Join M1A `effect_observation_record` to authenticated supplemental intent/attempt evidence
   before constructing M1C `EffectIntent`/`EffectTraceInput`. The observation contains digests
   and optional provider-operation/receipt digests, not the original idempotency key, target,
   payload digest, complete admission or ordered attempts required by M1C. Never invert a digest
   or equate effect_key with a provider operation ID. Bind the original key/target/payload and
   packet/goal/plan digests to their actual issuer and attempt ordering; reject an absent,
   contradictory or unauthenticated join. Do not fill unknown outcomes with success or silently
   add fields to M1. The exact seams are M1A-WIRE-PROFILE.md's effect-observation record and
   M1C-WIRE-PROFILE.md's EffectIntent/EffectTraceInput.
2. Keep lease epoch, writer fence, process/daemon epoch and admission/PAUSE epoch distinct.
   Record each issuer, monotonic domain, consumer and rejected stale transition. Configuration
   authority epochs and provider-session generations map to their own typed namespace; equal
   integer values do not make epochs interchangeable.
3. Authenticate the single writer and require atomic append/projection under its current fence.
   A hash chain alone is not authorization. OR-015's common-writer migration blocker remains;
   passing an M1C fabric-only check does not resolve it.
4. Model `current-immediate` as the only operative PAUSE policy. Close new admission immediately.
   Existing M1A validation classifies record-effect-observation as PAUSE-sensitive and returns
   E-PAUSED; preserve that refusal. Existing M1C pure trace classification may inspect already
   retained evidence, but it does not authorize a new runtime writer during PAUSE. A future
   adapter needs an explicit evidence-retention/classification mapping; if it cannot preserve
   the immutable boundary, record the construction blocker separately. Do not claim a runtime
   bridge or the common-writer migration is solved. Future policy names authorize no transitions.
5. Treat provider nonresponse, partition, partial process termination and late/reordered receipts
   as environmental inputs. Timeout, cancellation and disconnect preserve uncertainty; no blind
   repeat of an ambiguous external effect.
6. Preserve bounded broker flow and replay: a detected gap requires RESET before further EVENT,
   slow views cannot block canonical append or Owner control, and reconnect cannot relaunch work.

The shared visible alphabet includes admitted/rejected command, accepted GoalSpec digest,
canonical event with cursor, dispatch intent, cancellation request and scope, observed process
state, effect settled/unknown, reservation change, consultation response/adoption, configuration
fence, checkpoint/fork lineage and per-host update state. Presentation pixels, provider-private
reasoning and wall-clock speed are not semantic observations.

Distinguish canonical admission fence from recipient-installed fence, in-flight permit and
installation acknowledgment. Stop accepted locally is not atomic with remote installation.
Once installed, the recipient rejects earlier epochs; before then an offline recipient may
still act on a previously admitted permit, and the exposure remains visible. Similarly separate
requested, validated, staged and effective configuration; transport ACK is not effective state.
For consultations retain logical identity, reply-delivery generation, adoption lease and
borrowed-operation ownership. Shared-pool accounting is serialized across goals, not per goal.
CMP-021 through CMP-027, CMP-033.

## Bounds and identical environments

Retain the original E-FHAR2-101 core: one aggregate/task/effect/timer/verifier; two workers,
goal epochs, plan revisions and attempts; three lease epochs; at most twenty events and bounded
queues. Do not silently replace these bounds with the larger Mark 2 proposal. Run an additional
cross-area configuration with two assistants, two tasks, two hosts, queue capacity two, two
configuration epochs, one unresolved effect and one update candidate. Specify both in the run
record and compare each boundary under exactly the same configuration. The core and cross-area
profiles are standalone: cross-area does not inherit the core single-aggregate cardinality. Two
goals mean two aggregates, while one shared pool has its own serialized owner. A smaller debugging run
is reported separately and cannot replace the required corpus.

The cross-area configuration has two goals sharing one pool, each with a separately identified
writer, and one serialized pool-reservation owner. Bound one outstanding permit per host and
two recipient fence epochs; include one retired completion record and one stale request. The
optional conserved-rights comparator adds two holders and one transfer in flight; it cannot
replace the serialized baseline. Pool reset and process restart do not reset aggregate budget. Three preference revision
identities R1/R2/R3 coexist with two authority/configuration epochs; do not collapse the
coalescing trace by giving it only two revision identities. Remaining byte/credit, descendant,
message multiplicity, retry, cursor and budget domains are explicitly unresolved in the JSON
specification. Both resolved model configurations must bind them identically before checking.
For each applicable fault schedule require a reachable positive trigger and a discriminating
guard-removal witness. The valid-join positive control uses the missing/contradictory-join
negative partner for sensitivity; it does not require a mutant to fail on the same valid input.
A too-small bound that makes an applicable trigger unreachable is incomplete coverage, not a pass.

Define byte/event credit bounds, control-reserve capacity, cursor wrap abstraction, retry count,
process descendants and message multiplicity explicitly. Enumerate no-fault, one crash/restart,
partition and unresponsive recipient schedules. Use identity symmetry only after checking that
it preserves Owner, lease-holder, observer and stale-worker distinctions. Report reductions,
reachable states, transitions, depth, runtime and peak memory; none is measured in this round.

Safety has no eventual-delivery assumption. Conditional liveness assumes weak fairness for
continuously enabled local kernel/broker actions and a named bounded operation boundary for
Lazy Stop, with deadline expiry yielding a visible hold rather than assumed completion. Do not assume Owner response, provider response, network recovery or an external
effect's termination. Under permanent failure require a visible hold/unknown state and no
unauthorized progress. If strong fairness, a retry bound or recovery assumption is added, give
the exact property that needs it and apply it to both alternatives. Finite exploration does
not prove unbounded liveness or wall-clock responsiveness.

## Split aggregate plus refinement

Aggregate state contains authority, canonical events/projections, accepted intents, epochs,
effect uncertainty, parent reservations, waiters and required abstract delivery/control states.
The broker model contains bounded per-client queues/credit, replay floor and cursor, input and
resize leases, process ownership/liveness, request delivery and relaunch fences.

The recipient environment contains installed fences, operation-record status (absent,
in-progress, completed, retired, unknown), process birth/containment facts and external effects.
Keep these environmental facts identical in both boundaries; moving broker state inward must
not make the external environment cooperative. The shared machine-readable documentation
contract is [comparison-contract.json](comparison-contract.json); it is not executable modeling
code and its validator does not explore state space.

The coupling relation `R(A,B)` must make every broker action either a matching aggregate action
or a stutter that preserves visible state. Candidate mapping:

| Broker fact | Aggregate observation / obligation |
|---|---|
| Enqueued render delta, ACK or credit change | Stutter only if no control/durable fact is lost and resource bounds hold |
| Committed event projected to a view | Same canonical event identity/cursor; duplicate delivery cannot duplicate transition |
| Cursor below replay floor | Gap detected; RESET must precede next EVENT; no effect outcome inferred |
| Process launch/exit/kill request | Matching owned attempt and epoch; exit is an observation, not remote effect success |
| Input or resize lease transfer | Current holder and epoch fence; stale input rejected |
| Control reserve exhaustion | Visible blocked/overload result with admission safety; never silently delayed Owner Stop |
| Timer or supervisor wakeup | Propose revalidated dispatch; stale authority/relaunch fence blocks launch |
| Lost remote receipt | Preserve same operation ID and unresolved reservation; no blind retry |
| Recipient installs fence / old permit arrives | Match visible installation or rejection; prior local Stop alone cannot stand in for this fact |
| Receiver completion record queried / retired | Match known result or explicit stale/unknown; record retirement cannot authorize reexecution |
| Two goals reserve from shared pool | One serialized pool transition, or separately proved conserved-rights transition |
| Reply generation expires / delayed answer arrives | No obsolete continuation or stale adoption; retained evidence is explicitly distinguished from lost data |

Check initialization, every transition's preservation of R, invariant implication and liveness
assumption compatibility. Check the composition, not just two isolated invariant reports.
Auxiliary history variables may record facts; prophecy or backward-simulation techniques may be
needed where a state-only forward map cannot express a valid relation. Such augmentation must
preserve behavior after hiding and cannot constrain the environment to remove counterexamples.
Calibrate with an abstract hidden-bit choice made early and a concrete choice made at Reveal:
the same visible behavior need not admit the naive state-only map. Separately test infinite
broker requeue while local Stop processing remains continuously enabled but never executes.
That violates the shared weak-fairness condition; intermittently enabled starvation is a
different assumption. Remote termination may remain unknown. Finite-prefix stuttering must not
hide failure of the continuously enabled local obligation. Abadi/Lamport and Lamport/Merz support methods under stated conditions, not this split's
correctness. CMP-015, CMP-027.

## Broker-inclusive model

Put the same broker state directly beside the aggregate, with the same atomicity boundaries and
environmental nondeterminism. Project its traces through the same visible alphabet. The target
is trace inclusion and preservation of all required obligations under the same assumptions,
not a claim of byte-for-byte state equality. Compare discovered counterexamples by minimized
visible trace and cause, including whether the split requires an unstated coupling assumption.

An inclusive model that accidentally serializes launch, append, Stop or notification delivery
into one atomic action is an invalid comparator. Preserve preemption points around admission,
intent append, send, remote acceptance, local receipt and projection. Local enqueue success
must not be atomic with remote execution. Both models must retain their own internal action
trace alongside the normalized visible trace to make a missing race reviewable.

## Required constructed traces and guard-removal tests

These are unrun test designs, not observed counterexamples. Their presence in a JSON/document
validator does not establish a model result. JSON trace IDs follow table order. Trace 13 is a
positive mapping control, paired with negative trace 14. Trace 21 (serialized shared-pool
conservation) is mandatory. Trace 22 applies only if the conserved-rights extension is explicitly
selected for both boundaries. If it is not selected, report that trace as unrun/not-covered,
without removing any shared obligation or counting optional rights support as established. All
other schedules belong to the mandatory baseline; their resolved core/cross-area profile must
be identical between boundaries. Production adoption of the rights mechanism remains unselected.

| Trace | Required outcome / guard to remove |
|---|---|
| Saturate presentation queue, issue Owner Stop, detach slow view | Stop admission fence remains enabled; removing reserved control path exposes blockage |
| Detect cursor gap, receive fresh EVENT before RESET | Reject delivery ordering; removing gap guard yields an illegal visible trace |
| Append dispatch intent, remote accepts, receipt lost, restart | Same effect unknown and reservation retained; removing ambiguity guard duplicates dispatch |
| Stop selected actor while follow-up queue and relaunch timer exist | Correct scope fenced, queue disposition explicit; remove fence to reveal relaunch |
| Revoke at R2 between preference R1 and R3, coalesce notification | Old epoch rejected; remove independent fence to expose stale authority |
| Consult under goal/lease A, change lease, receive delayed advice | Evidence retained, authoritative adoption denied under stale lease |
| Fork unfinished work, retry, then provider pool resets | Original preserved and parent allowance conserved; remove lineage/reservation guard |
| Update crashes after partial activation while remote node is offline | Per-host unknown/partial state, newest history retained, no unsafe rollback inference |
| Two writer candidates have valid-looking chains but different fences | Only current authenticated writer appends; remove writer fence/authentication |
| PAUSE arrives after plan acceptance but before effect admission/permit issue | New permit denied immediately; already-issued permits follow recipient-fence trace; remove current-immediate check |
| Replace process epoch while old worker returns an output | Evidence quarantined/reconciled; old epoch cannot publish or renew reservation |
| Broker reports drain or process exit while external effect remains pending | Distinct states preserved; remove outcome separation to expose false settlement |
| Valid M1A observation with authenticated complete supplemental intent/attempt join | Positive mapping control yields the same M1C input; no invented fields or digest inversion |
| M1A digests lack original key/target/admission or supplemental bindings contradict | Reject missing/contradictory authenticated join; remove join guard; do not let this case stand in for PAUSE validation |
| Otherwise schema/digest/auth/state/lease-valid record-effect-observation under PAUSE | Literal E-PAUSED and no new event; retained valid evidence can undergo pure M1C classification without runtime write; remove PAUSE guard |
| Same command ID and aggregate, changed payload | Preserve immutable payload-conflict rejection; remove digest comparison to expose false deduplication |
| Local Stop accepted, delayed permit reaches unfenced remote recipient | Report exposed in-flight work; after recipient fence installation reject old permit; remove installed-fence guard |
| Broker crashes between process creation, association and registration | No process or identifiable contained process; compare at-birth containment; remove ownership admission |
| Effect and completion record commit, reply lost, recipient relocates | Query same operation record without reexecuting; remove retry-rendezvous requirement |
| Record retired, stale client retransmits old request | Stale rejection or explicit unknown; remove retirement fence to expose duplicate effect |
| Two goals each reserve six from a pool of ten | At most ten total admitted; remove pool serialization to expose oversubscription |
| Rights transfer interrupted, duplicated or restored from stale snapshot | No duplicated allowance; remove durable conservation guard; offline timeout alone cannot reclaim rights |
| Head retains sole eligible executor while waiting for consultant | Visible blocked dependency or released executor, never hidden deadlock; remove wait-for resource check |
| Stop expires a borrowed consultation while consultant does unrelated work | Fence that operation and delivery generation; preserve unrelated work; remove scope separation |
| MRTR returns new wire IDs with unchanged logical operation repeatedly | Preserve original deadline/round/byte/reservation cap; remove operation-level bound |
| SDK loses notification before ingestion or parser receives unterminated oversized line | Gap/resync or typed unknown; bounded framing and independent control progress; remove ingress guard |
| Reset usage, spend again, crash before aggregate report, resume | Conserve immutable meter segments and unknown remainder; remove reset-boundary accounting |

All common invariants remain: TypeOK; chain/atomic append; idempotence; attenuation; lease,
amendment, PAUSE, retry, cancel, effect and verifier safety; replay/fail-closed/projection parity;
flow bounds; no blind replay. Cross-area additions cannot weaken any original invariant.

## Disposition rule and freeze gate

Classify results as a semantic counterexample, unenforceable mapping assumption, inadequate
auxiliary state/proof technique, or exploration limit. Only the first two directly falsify a
candidate boundary; the others leave it unestablished and require a stronger method or explicit
incomplete result. Never convert a checker timeout into success or a proof-method failure into
an invented product fault.

Fail either candidate on an invariant violation, omitted applicable required trace/field, unjustified
atomicity/fairness assumption, unbounded queue hidden by the bound, vacuous guard mutant or
lost uncertainty. If a broker interleaving violates an aggregate obligation, or an independent
composition check cannot establish R without assumptions the implementation cannot enforce,
move the relevant broker state into the aggregate and rerun both comparisons. Do not discard
the obligation or declare the smaller model adequate because it explores fewer states.

If both cover the same obligations and counterexamples, compare proof maintenance and state
cost before retaining the smaller split. A result under one finite bound is conditional and
must state its limit. Output frozen mapping tables, model/tool/config digests, all commands,
counterexample traces, mutant evidence, assumptions and a language-neutral vector corpus.
Only then request language comparison, followed by complete storage comparison. Interface probe
counterexamples may revise this specification before that freeze; whole-system optimization
research continues alongside the sequence.
