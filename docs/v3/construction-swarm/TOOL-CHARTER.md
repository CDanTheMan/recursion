# Tool-enabled construction pipeline — 2026-09-11

Parent: `goal-recursion-v2-execution-fabric`. Baseline: `3cb7405` (PR122).
Lucas authorizes refining and exercising a 100-worker SWE-2 Max construction
pipeline with Cursor Grok 4.5 non-fast coordinators and the explicit OpenCode Go
Muse Spark 1.3 Contributor alternative. This authoring session may change only
`tools/construction_swarm/**` and `docs/v3/construction-swarm/**`. Lucas merges.

Build repository read/search/write, isolated command execution, and bounded source
retrieval tools. Provider credentials stay with the trusted client. Model tools
must not expose the host checkout, other workers, controller state, credentials,
publisher, or operational control plane. Native recursive delegation stays under
the central dispatch budget. A model can propose changes; verification and human
review remain separate. Coordinator synthesis must preserve worker evidence and
dissent, use the exact selected model, and never silently change provider.

Acceptance: existing Windows/WSL regression gates; strict tool protocol and scope
tests; real WSL read/edit/command and isolation/cleanup probes; 100-job scheduling
with separate tool capacity; actual SWE-2 Max tool-use exports and independent
adversarial review; actual coordinator synthesis of retained worker outputs;
documented useful-work and capacity evidence, limitations, and recovery; commit
and review-branch publication. Do not claim 100 simultaneous builds or an
unattended research campaign from a short transport benchmark. No deployment,
merge, model-setting changes, credential edits, or quota reset use is included.
