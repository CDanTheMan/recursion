# M1B semantic coverage audit

Source: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b` · 2026-10-02 UTC

## Result

**No additional sound implementation defect was established.** Two small, source-grounded test additions remain useful: exercise RESIZE's own lease/idempotency branch, and exercise a multibyte character split across EVENT payloads. A third lead, independently exceeding the pending-byte queue bound, is **already reached by later literal-oracle calibration** and is not a new repository-wide coverage gap. One minor fixture-table status discrepancy should be reconciled when documentation is next edited.

Nothing was executed against the target: no target script, import, test, model checker, process probe, provider/model/harness call, account, credentials, live host or installation. Only source text, JSON data and hashes were read; separate research artifacts were written. All supplied expected outcomes and hypothetical source mutations are UNEXECUTED. No repository or frozen packet was changed.

The accepted D-018–D-033 decisions remain closed. In particular, the old frozen `current-immediate` M1B field is historical contract coverage, not a reversal of D-022's present Aggressive/Full/Lazy product vocabulary. Native platform, failover, entitlement, runtime and release claims remain subject to their separate gates.

## Exact boundary and visible path

`docs/v3/M1B-EXECUTION-CONTRACTS.md:11–28,145–150` declares pure, test-only, in-memory requirements behavior. M1B does not launch/observe real processes, execute plugins, persist state or admit effects. Its absence of those actions is intentional. `scripts/tests/v3/execution/static.test.py:14,30–31` even requires no production execution directory.

The frozen conformance path is:

1. `scripts/tests/v3/execution/conformance.test.py:38–46` loads literal fixture bytes using the strict decoder, validates the bundle, calls `reference_oracle.decide`, validates the returned decision, then compares it to literal expected bytes
2. `scripts/tests/v3/execution/schema.test.py:64–82,131–143,172–189` supplies strict JSON, canonical/bounded base64 and extended schema validation
3. `scripts/tests/v3/execution/reference_oracle.py:657–674` dispatches the six fixture arms; broker inputs reach `replay_broker:471–654`
4. The supplemental `experiments/v3/external-20260914/broker_wire_tests.py:2–14,116–142` directly calls the oracle and compares hand-authored decisions. It explicitly does **not** perform JSON-schema validation or implement a live protocol

Consequently, an arbitrary unvalidated dict reaching a direct helper is not evidence that the composed frozen decoder/schema/oracle gate accepts it. Likewise, a copied work counter or constructed disabled-zero trace is not an independently observed runtime result. The existing integration handoff already requires real observers and snapshot-installation/control evidence; this report does not repeat those as new findings.

## SC-01: flow dimensions — attribution clarification, not a new gap

**Contract and guard.** `docs/v3/M1B-WIRE-PROFILE.md:254–268` separately bounds credit consumption and pending queues. `reference_oracle.py:608–614` checks/debits byte and event credit; `615–620` separately checks pending bytes and event count. ACK releases pending entries at `622–635`; it does not replenish credit. Per-message CREDIT caps are in `schemas/control-plane/v3/execution/materialize.py:651`, and grants are additive at `reference_oracle.py:523–527`.

**Initial lead, then disconfirmation.** F-M1B-022 supplies four credit bytes and a four-byte queue but an eight-byte payload, so both byte failures share `credit-exhausted`. The frozen adversarial test at `adversarial.test.py:452–475` independently exceeds queue *event count*, while ordinary exhaustion cases often exhaust both credit dimensions. This masks attribution within those legacy cases. It does not mean the repository lacks an independent byte-queue discriminator.

**Existing later path reaches the same target predicate.** `experiments/v3/flow-recovery-integration/experiment.py:11–18` loads and calls this exact M1B oracle; `30–41` enumerates every sequence of one through four messages from its fixed alphabet at queue bounds `(1,1)` and `(2,2)`, comparing complete decisions with the separate compact audit. `domain.py:4,18–25` encodes event costs 1,2,1,2 and credit grants of 1 or 2 bytes with one event credit.

One enumerated four-message witness is CREDIT(1 byte,1 event), CREDIT(2 bytes,1 event), EVENT(cursor 1,payload 1 byte), EVENT(cursor 2,payload 2 bytes), queue limits 2 bytes/2 events. Immediately before the last event, credit is 2 bytes/1 event: sufficient. After it, pending is 3 bytes/2 events: **only pending bytes exceed their limit**. This reaches `reference_oracle.py:617`, rather than merely exercising a separate preventive model. Removing only that byte-queue term changes the literal decision and would disagree with the compact audit's separate byte sum at `audit.py:50`. This is static path deduction, not a newly run mutation result.

The later `ignore_byte_credit` / `ignore_queue_bytes` mutations at `experiment.py:81–84` instead target the separate models. Keep those sensitivity results distinct from the literal-oracle calibration. The retained evidence record describes a conditional finite integration result, not full formal freeze; the run's raw result is referenced by hash but is not present at the assumed `results.json` path in this snapshot.

**Reusable data only.** `synthetic-inputs.json` retains FLOW-CONTROL and four single-scalar variants: credit bytes, credit events, queue bytes, queue events are each reduced from 2 to 1 for two one-byte events. Each negative has just one insufficient dimension and otherwise-valid credit/cursor/identity state. Baseline expects `accepted`; each negative expects `refused`, only `credit-exhausted`, final cursor 2, `requires_reset=true`.

**Rival / future use / non-proof.** A compact audit comparison and a small literal known-answer regression are both conforming evidence methods. Prefer reusing the existing calibration and explicitly attributing its coverage; do not commission duplicate work merely because the frozen fixture is narrower. The portable matrix can qualify a future independent implementation. It proves neither physical memory bounds nor slow-view isolation or Stop progress.

## SC-02: RESIZE's semantic branch needs a direct discriminating pair

**Exact claim and current coverage.** `M1B-EXECUTION-CONTRACTS.md:121–123` requires independent current input/resize leases and idempotency. `M1B-WIRE-PROFILE.md:247–262` gives the arms and same-command conflict rule. `M1B-FIXTURE-ORACLES.md:50` names stale input **or resize**; F-M1B-021 contains only INPUT. `schema.test.py:405–419` validates a RESIZE's shape, but does not replay it. The frozen semantic and supplemental broker suites contain no RESIZE replay case.

There **is** a later RESIZE literal: `experiments/v3/formal-comparison/calibrations.py:100–107`. It deliberately follows an unrecovered replay gap, so `reference_oracle.py:520–522` rejects it before reaching the command/lease branch. This is real coverage of the replay-gap fence for RESIZE, not coverage of RESIZE's own lease choice or command handling. The companion domain's RESIZE token alone is not a semantic lease test.

**Visible path.** Valid RESIZE schema → `decide` broker arm → matching daemon/stream/client → no replay gap → command cache `529–535` → process epoch `536–537` → distinct resize lease/current resize lease `538–543` → final decision. The present source appears to enforce the intended rule.

**Isolated synthetic tests.** The saved RESIZE-CONTROL has process/daemon epoch 2, input lease `lease:input:2`, resize lease `lease:resize:2`, valid dimensions and a matching RESIZE. It expects `accepted`, cursor 0, no reasons, zero counters. Separate one-field mutations change only the submitted resize lease to the valid *input* lease, only the process epoch to 1, or only current resize lease to null. They expect, respectively, sole reasons `stale-lease`, `stale-process-epoch`, `passive-client-input` and `refused`.

Identical RESIZE replay expects acceptance; changing only the repeated `columns` to 81 expects `duplicate-command-conflict`. A valid INPUT plus valid RESIZE with distinct IDs is accepted; changing only RESIZE's ID to the prior INPUT ID is a conflict. The latter pins the current shared command-ID domain rather than inventing a new per-arm namespace.

**Hypothetical isolated source mutations.** Narrow `if kind in {"INPUT", "RESIZE"}` at `reference_oracle.py:528` to INPUT only; or change only the RESIZE `current_field` selection at `539` to the input lease; or key the command cache by `(kind, command_id)` instead of command ID. A separately authorized later test must show the correct positive control and each appropriate negative distinguish the intended change. None of these edits or tests occurred here.

**Conforming rival / non-proof.** A unified command reducer and separate typed INPUT/RESIZE handlers are both acceptable if they preserve independent leases, epochs and shared idempotency identity. This addition qualifies pure classification only. Accepted identical replay is consistent with a no-op; without side-effect state it cannot prove a runtime did not apply resize twice, preserve process lifetime, or safely revoke a live lease.

## SC-03: F-M1B-023 does not actually split a multibyte payload

**Exact mismatch.** `M1B-FIXTURE-ORACLES.md:52` requires “Fragmented multibyte output.” The actual F-M1B-023 has one CREDIT and one EVENT containing complete snowman bytes E2 98 83 (`4piD`), cursor 3. Its constructor is `materialize_fixtures.py:434–440`. `adversarial.test.py:425–430` changes that one complete EVENT's cursor; the supplemental test at `broker_wire_tests.py:171–190` likewise uses complete encoded characters. These establish byte counting, not split-codepoint coverage.

**Visible path and controls.** Base64 payload validation at `schema.test.py:131–143` bounds bytes; it does not require each payload independently decode as a complete UTF-8 string. `reference_oracle.py:594–603` counts decoded bytes. The saved UTF8-WHOLE-CONTROL has three byte credits and two event credits, ensuring segmentation alone does not introduce a credit failure. The split treatment emits E2 (`4g==`) at byte cursor 1, then 98 83 (`mIM=`) at cursor 3. Both whole and split expect `accepted`, final cursor 3, unit `utf8-byte`, no reasons. Changing only the second split cursor from 3 to 2 expects `refused` with only `utf8-byte-cursor-mismatch`; the present oracle's final cursor is the supplied 2, not the correct expected 3.

**Decisive future test and source mutation.** A proposed per-EVENT strict UTF-8 decode before byte counting would accept the existing complete character but reject the valid split representation. The new split positive control must detect that regression, while the wrong-cursor negative must still refuse. No such mutation was installed or run.

**Conforming rival / non-proof.** A byte-oriented broker and a renderer with incremental UTF-8 decoding are compatible with these wire semantics. M1B does not implement terminal decoding, UTF-8 reassembly, JSON transport framing or a physical partial-frame buffer. This test must not require those features or claim to prove them. It is a small pure byte-cursor coverage extension, not evidence of a present decoding defect.

## SC-04: minor F-M1B-024 status-table discrepancy

`M1B-FIXTURE-ORACLES.md:53` lists `accepted`; the actual F-M1B-024 is a ProcessFixtureBundle whose expected status is `admitted`. `M1B-WIRE-PROFILE.md:224–226` and `materialize.py:610–619` allow only `admitted`/`blocked` for that decision; `reference_oracle.py:468,667–671` returns the process decision. The actual fixture therefore conforms to its typed wire arm.

A future documentation consistency check should compare table statuses against each fixture's actual arm. The unchanged fixture is the valid control; changing only `/expected/status` to `accepted` should fail schema validation. Rival interpretation: the table used “accepted” colloquially for acceptance of the fixture, rather than the exact status. Because its heading says “Expected status,” reconcile the wording in a reviewed documentation edit; do not weaken the schema or alter effect semantics to match it. This is documentary drift, not an effect-safety defect.

## Enforced checks and retained negative findings

- **Credit/ACK/reset:** Explicit credit, cumulative debit, independent pending accounting, ACK-ahead/backward refusal, exact stream/client binding, zero-cursor unit binding, reset rollback/unexpected-reset refusal and permanent replay-gap continuation are implemented. Ordinary flow exhaustion does not impose the replay-gap continuation rule. Missing-credit refusal remains permanent even after reset. `requires_reset` is historical recovery-needed state, including accepted-reset, not an instruction to reset again. Existing later mappings explicitly preserve these distinctions
- **Sequence/framing:** Closed schema union, protocol version, dimensions, canonical base64, raw JSON bounds, duplicate/invalid lexical values and exact byte/event progression have real guards. Supplemental direct oracle calls do not replace the structural gate. Negotiation, rollover, authentic snapshot materialization and ACK-release ownership remain the known G-05 work, not fresh findings here
- **Policy/epochs:** `reference_oracle.py:303–321,393–440` checks plugin grant/artifact/dependency-lock/GoalSpec/policy bindings, lifecycle state/sub-epochs, revocation and reload fences. Immutable input `pause_epoch` or opaque M1A digests do not authenticate an external current authority source. No such live source is claimed by this pure surface
- **Process/control lifetime:** `reference_oracle.py:443–468` blocks missing/unknown required capability support and host/platform mismatches. Attach-created-work counters are checked at `501–502`, not measured. No detach/Stop wire arm or OS lifetime implementation should be invented to make the frozen corpus look more complete
- **Disabled behavior:** `reference_oracle.py:385–390` constructs exact zero activity, and schema constants reject nonzero fields. This is declarative conformance, not a live inertness observation. The existing IT-11 observer-sensitivity gate remains necessary
- **Effect uncertainty:** `materialize.py:621–638` fixes `effect_conclusion=not-evaluated` and enforces terminated/partial shapes; schema/oracle additionally bind termination to its requirement ID. `adversarial.test.py:386–396` rejects success attribution and a wrong requirement. No supplied current-process-epoch authority exists for a separate receipt-epoch comparison; that absent production join is not claimed as implemented
- **Historical real dissent:** The campaign records rejected candidates and repaired false greens in PlanRevisions 3–5, including replay-gap/CREDIT/EVENT/RESET masking. The terminal receipt says the repaired candidate and immediate-reset positive control were independently rechecked. These are repository-recorded historical observations, not fresh executions. The supplemental review records 13 tests and five guard/arithmetic mutation detections, while explicitly withholding runtime acceptance

## Bounded next step

Preserve existing later coverage and add only the two small RESIZE and split-payload control groups when a local test session is separately admitted. Reconcile the one status-table wording during a reviewed doc edit. Before any runtime qualification, use the existing integration handoff's independent observers, physical control/lifetime and authenticated snapshot/effect obligations. No new Owner choice, production threshold, transport extension, store/runtime selection or release claim follows from this audit.

Companions: [minimal matrix](coverage-matrix.json), [designed synthetic inputs](synthetic-inputs.json), [source-byte pins](source-pins.json). Source paths above are repository-relative; research-reference pins are explicitly relative to this artifact directory.
