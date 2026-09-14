# Next parallel work for the external v3 fleet

Start from the final independently reviewed integration commit in C:/r3i, each in its own clean codex/ worktree. Record the full commit as TASK_BASE. Read CONTROL_PLANE, ANCHOR, AGENTS and docs/v3/START-HERE. Preserve the accepted v3 product specifications and existing modules. This new source binding supersedes COMMON's old starting-commit instruction for these successors only; its authority, quality and publication boundaries remain.

The five external Devin/SWE-2 workers build Recursion v3. They are not installed as agents inside the product runtime. Useful bounded research can continue before the continuous service is finished.

## Sol 1: host-lifecycle construction

Execute the draft packet in docs/v3/construction/p2-access-20260914/README.md with the new TASK_BASE. Its complete five-path allowance and test interface already exist. Build the operator-invoked controller/watchdog using fixture children, persisted incarnation, duplicate-controller refusal, stale-PID safety, capped restart and explicit outage state. Preserve read-service fencing versus canonical writer authority. The existing P2 protocol is an unchanged dependency.

Run the new lifecycle unittest gate, existing P1/P2 gates and an additive source/scope check for exactly the packet's five files; obtain independent Astra review. The original integration gate will reject new successor paths by design, so retain its predecessor receipt and define the successor's own composition binding. Draft actual-host qualification instructions without installing startup policy or shutting down the user's host.

## Sol 2: actual foundry observations through the read interface

Implement a read-only foundry observation adapter and explicitly invoked service entry point. Read tools/construction_swarm/foundry.py's report implementation and its actual run-directory schema first. Pin the observed schema and reader dependencies in the new SPEC. Report foundry work/attempt/result evidence honestly; preserve canonical fields as unavailable where foundry cannot establish them. It must never promote a worker return to accepted product output.

Allowed new files:
- tools/construction_swarm/p2_foundry_observation.py
- tools/construction_swarm/test_p2_foundry_observation.py
- docs/v3/construction/p2-foundry-observation-20260914/SPEC.md
- docs/v3/construction/p2-foundry-observation-20260914/PROGRESS.md

Use existing AccessService/serve interfaces without editing P2 or foundry. The entry point must be explicitly invoked and must launch no scheduler/provider/worker. Preserve authentication and project-scoped access. Build manifest-digest-bound artifact views only from actual verified records; absent digests mean unavailable, never generated trust. Handle missing, malformed, partial and concurrently replaced records with bounded reads and explicit uncertainty. Derive cursor behavior from real durable ordering or refuse unsupported replay; never invent a canonical cursor.

NEW gate: python -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_foundry_observation

Required cases: coherent completed and in-flight views, returned versus independently accepted distinction, held/unknown attempt visibility, missing and partially written records, project isolation, stale snapshots, unsupported cursor refusal, correct immutable artifact binding and refusal of missing/tampered digests. Verify input directory bytes are unchanged after each read and no provider/scheduler/mutation path is invoked. Use temporary fixtures; at most 32 MiB, 15 seconds per child, 120 seconds for the focused gate, zero inference. Also rerun P1/P2 and source/scope checks, then independent Astra review. Any existing completed-run smoke is read-only and separately labelled observed or unrun; it grants no service activation or access to another project's records.

## Astra: construct the missing DQ execution controller

The initial delegated-Q and recovery candidates are complete within their inert scopes. The next DQ task is controller/accounting integration and evidence qualification before DQ-16 execution; the next recovery task is a separately specified physical-persistence boundary. Neither is supplied by the fleet's P2 host controller or the product's inert ledger alone.

Build the missing controller integration as an inert candidate. Read the DQ SPEC, its ScientificKernel interface and the actual inherited controller/receipt contracts first. Preserve the original reducers and DQ files. Do not claim that a process timeout or the product recovery ledger supplies inner-call metering, historical charge reconciliation or scientific admission.

Allowed new files:
- experiments/v3/dq-execution-controller-20260914/admission.py
- experiments/v3/dq-execution-controller-20260914/runner.py
- experiments/v3/dq-execution-controller-20260914/test_controller.py
- docs/v3/construction/dq-execution-controller-20260914/SPEC.md
- docs/v3/construction/dq-execution-controller-20260914/plan.json
- docs/v3/construction/dq-execution-controller-20260914/PROGRESS.md

NEW gate: python -X utf8 -B experiments/v3/dq-execution-controller-20260914/test_controller.py

Implement typed, source-bound prerequisite validation and a controller seam with fake reducers. Require exact candidate/plan/controller bindings, independently sourced grant/review/accounting evidence, current resource/account/PAUSE/lock observations and unreconciled-history handling. Specify which existing authority authenticates each fact; self-authored approved flags or missing receipts must never grant execution. Exercise a meaningful valid fake envelope as well as stale-source, forged/missing review, expired deadline, unknown prior charge, double-reservation, failed-attempt charging, inner-call undercount and child-timeout/cleanup controls. Charge construction, checker, auditor and both scientific review reruns additively; preserve uncertainty after incomplete cleanup. A fake envelope can run only fake reducers and cannot reach ScientificKernel imports.

Construction gate budget: zero providers and inherited scientific state visits, at most 1,024 fake scenarios, 15 seconds per owned child, 60 seconds per focused command and 32 MiB artifacts. Commit the SPEC and literal controls before the runner, then coherent implementation slices. Obtain two independent reviews of the exact candidate. Actual historical receipt reconciliation and host observations may remain missing; report each explicitly. Deliver an executable controller candidate and exact remaining admission requirements. DQ-16 may run only after a separately reviewed finite execution grant and actual prerequisite evidence, never by extending this construction packet.

## Path from these lanes to continuous development

P1/P2 still require the real canonical state/acceptance integration and actual Cursor/Codex client qualification. Then P3 adds shared leases, bounded task scheduling and scoped mutation; P4 adds standing-envelope and account/reset handling; P5 preserves context, evidence and independent acceptance; P6 serializes integration and publisher recovery. Real application and host qualification must supply actual evidence, not only fixture tests.

After those gates, use the specified P7 one-worker then five-worker canary, followed by P8's 72-hour soak. Host-awake availability, retained unknown charges, provider backoff and review quality are measured outcomes. An eight-worker comparison follows accepted five-worker evidence and actual headroom. No standing grant, installed startup/watchdog, provider selection or autonomy setting changes through this document.
