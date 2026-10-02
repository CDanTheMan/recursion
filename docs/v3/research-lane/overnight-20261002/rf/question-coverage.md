# R-F exact question and completion-gate coverage

Source: the exact R-F brief at repository commit 73d70505b8c266fbb08d820d304ebd2e68ac7f1b. All target executions are unrun. Unknown answers identify the next discriminating test instead of treating missing evidence as false.

## R-F.Q01
For each named harness — Codex (exec and app server), Claude Code (`claude -p` and Agent SDK), Cursor (`cursor-agent`), Gemini CLI, Grok Build, Hermes, OpenCode, Antigravity and Pi — what documented headless, exec, CLI or ACP surfaces exist for (a) submitting a request, (b) steering or queuing a running request, (c) interrupt, cancel or stop, (d) resume, fork or rewind, (e) emitting machine-readable stdout/JSON and (f) reporting usage/accounting, and which cells are `unknown` from public sources?
- Answer: report §1.1–1.11
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F17–F19, RF-F25, RF-F32; later exact-binary qualification

## R-F.Q02
Which surfaces emit a documented JSON stream or structured event stream that Recursion can own and parse, and what is the documented schema stability, version negotiation and deprecation policy for each?
- Answer: report §2
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F23–F25, RF-F32

## R-F.Q03
Which surfaces authenticate the user and hold the credential themselves (delegation), versus expecting the caller to supply a token or key (intermediation), and what is the documented boundary per harness?
- Answer: report §3
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F27–F28; later R-E process/network/secret-boundary qualification

## R-F.Q04
What is the precise test for "Recursion is a caller, not a proxy": which process owns the outbound provider connection, which process holds the credential, and what would have to be true for a design to cross into forbidden credential intermediation?
- Answer: report §4
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F27–F28; later R-E qualification

## R-F.Q05
What is the minimal delegation record that names the invoked binary and version, the argument vector class, the inherited environment policy, the working directory and artifact scope, the credential owner, and the evidence class for each field?
- Answer: report §5
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F02–F06, RF-F20–F22, RF-F26

## R-F.Q06
What is the minimal Honest Accounting record for a delegated headless call — attempts, completions, interruptions, excluded helper calls, unknown counters — and how are missing counters recorded as `unknown` rather than zero?
- Answer: report §6
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F07–F11; later R-D native-meter qualification

## R-F.Q07
For an external session (for example a Codex `/goal`) that authorizes headless sub-agent spawns (`codex exec`, `claude -p`, `cursor-agent`, ACP): how is authority propagated to each child, how is it attenuated so a child can never widen the parent goal, and how are capability, budget, egress and privacy bounds inherited or narrowed?
- Answer: report §7
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F02–F04, RF-F20–F22, RF-F29

## R-F.Q08
Who owns usage and accounting for a fan-out — the parent session, the child harness invocation, or the user's subscription — and how is per-child consumption attributed when a harness excludes helper calls from its counters or reports nothing?
- Answer: report §6
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F07–F10, RF-F29; later R-D account-window reconciliation

## R-F.Q09
What is effect settlement for fan-out: at what points are effects committed, how are partial or concurrent effects reconciled, and what makes a duplicate or lost spawn detectable rather than silently double-counted or dropped?
- Answer: report §8
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F05–F06, RF-F12–F13, RF-F26

## R-F.Q10
How do the D-022 vocabulary and Stop modes (Aggressive / Full / Lazy) plus `checkpoint`, `interrupt` and `drain` apply to a live fan-out — how are in-flight children checkpointed, interrupted and drained, and why is a killed child PID not external rollback?
- Answer: report §9
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F14–F19, RF-F24, RF-F31; later D-028 containment

## R-F.Q11
How does fan-out converge or fan-in — result aggregation, conflict resolution, cancellation of redundant children, and bounded parallelism under quota and rate limits — without creating a second canonical authority?
- Answer: report §10
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F01, RF-F13, RF-F22, RF-F24, RF-F29–F31

## R-F.Q12
What competing fan-out designs exist (single sequential delegate, harness-native fan-out, Recursion-orchestrated parallel spawns, queue-only) and what decisive falsifier rejects each?
- Answer: report §11–12
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: All four comparator arms, RF-F01–F32

## R-F.Q13
What is a provider-free experiment design that exercises delegation and fan-out with synthetic fixtures and a stub harness (deterministic stdout/JSON, scripted delays, induced interrupts and failures) to test authority attenuation, accounting attribution, settlement and D-022 stop semantics, with endpoints, confounders, hard floors and stop conditions?
- Answer: report §13; unexecuted-local-test-handoff.md §§1–11
- Disposition: answered; source/design/unknown distinctions retained
- Unknown-resolution handoff: RF-F01–F32; separately admitted implementation and independent rerun

## R-F.G01
Every named harness has a headless/exec surface map with each cell source-documented, inferred or explicitly `unknown`.
- Evidence: §14; §1–3
- Disposition: covered in report

## R-F.G02
The caller-not-proxy test is stated so that ownership of the connection and the credential is unambiguous per harness.
- Evidence: §14; §3–4
- Disposition: covered in report

## R-F.G03
The delegation record and the Honest Accounting record are defined, and unavailable counters are `unknown`, never zero.
- Evidence: §14; §5–6
- Disposition: covered in report

## R-F.G04
The fan-out design states authority propagation and attenuation, usage/accounting ownership, effect settlement, and convergence/fan-in without creating a second canonical authority.
- Evidence: §14; §7–8, §10
- Disposition: covered in report

## R-F.G05
Stop and interrupt semantics use the D-022 vocabulary (Aggressive / Full / Lazy, `checkpoint`, `interrupt`, `drain`), and no killed PID is described as external rollback.
- Evidence: §14; §9
- Disposition: covered in report

## R-F.G06
The experiment is provider-free and deterministic, with a stub harness, endpoints, confounders, hard floors, stop conditions and falsifiers.
- Evidence: §14; §13; unexecuted-local-test-handoff.md
- Disposition: covered in report

## R-F.G07
Every recommendation names a competing option and what it does not prove.
- Evidence: §14; §11–12
- Disposition: covered in report

## R-F.G08
Protected paths are untouched; privacy and secret scan are clean.
- Evidence: §14; artifact-validation.json
- Disposition: static artifact checks; no repository writes; not a live security audit


## Revision clarifications

- Q01/Q02: separate OpenCode v2 global live subscription from experimental durable session.log replay; no cross-generation qualification
- Q04: require exact unmodified upstream C/T support or equivalent protection, direct and induced-flow non-access, and refusal after failed strong preflight; policy-only requires separate admission
- Q06/Q08: preserve raw crash-zero fields but classify invalid consumption as unknown; RF-F11 adds the present-but-invalid zero variant; RF-F08 also tests positive-but-incomplete budget-crossing usage
