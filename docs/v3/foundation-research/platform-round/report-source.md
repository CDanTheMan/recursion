# Frontier integration findings for the platform research round

2026-09-06. Audience: Owner and research integrator. Scope: current public interface evidence
plus the inspected Recursion baseline; no live engine probes or performance measurements.
The complete platform contract remains the research target. These findings identify useful
integration seams and the evidence needed to turn them into supported routes.

The evidence supports keeping both pipelines and treating rich interfaces/extensions as first-class
adapter candidates. It does not establish uniform feature parity or a universal subscription
access mechanism. [The machine-readable matrix](integration.json) contains 12 candidate rows
and 120 feature dispositions, including a generic native design and T3 as a composition precedent.
Each named upstream remains a candidate until exact-version tests and eligibility review pass.

| Integration | Verified source mechanism | Consequential next check |
|---|---|---|
| Codex | [App Server](https://learn.chatgpt.com/docs/app-server) supplies typed turn controls and experimental dynamic tools | Bind installed protocol/build, approvals and compaction to all ten Recursion semantics |
| Claude Code binary | [CLI reference](https://code.claude.com/docs/en/cli-reference) includes structured bidirectional input/output, input acknowledgment and permission-tool support | Test the binary plus supported hooks/plugins as one composition; a one-shot wrapper is insufficient evidence of a limit |
| Claude Agent SDK | [SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) supplies the vendor's loop as a library | Keep it classified as upstream execution; prove callback/session behavior and intended product authentication separately |
| Cursor | [ACP](https://cursor.com/docs/cli/acp) supplies structured sessions and question/plan/task extensions | Probe active steering, forks and compaction rather than assume all ACP implementations match |
| OpenCode | [Server](https://dev.opencode.ai/docs/server/) and [plugins](https://dev.opencode.ai/docs/plugins/) expose session controls and compaction customization | Certify hook/server combination, startup effects and experimental behavior |
| Gemini CLI | [CLI](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/cli-reference.md) and [extensions](https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/reference.md) document structured headless mode, experimental ACP and extension manifests | Pin actual protocol/build and inspect missing control methods; Google login, API and Vertex are separate routes |
| Hermes Agent | [Programmatic integration](https://github.com/nousresearch/hermes-agent/blob/main/website/docs/developer-guide/programmatic-integration.md) documents RPC and HTTP/SSE interaction controls | Compare exact interfaces and descendant accounting; this optional product is distinct from Recursion's current Hermes executive |
| Grok Build / xAI | [Headless/ACP](https://docs.x.ai/build/cli/headless-scripting) and [CLI reference](https://docs.x.ai/build/cli/reference) expose sessions, forks, plugins and inspection | Separate Build, Grok Bot and direct API; test import/continuation semantics and current plan eligibility |
| Muse Code | [Meta launch](https://research.meta.ai/blog/introducing-muse-code-and-muse-spark-1-2) describes persistent agents, event-log recovery and bundled skills; [September update](https://research.meta.ai/blog/introducing-muse-spark-1-3) identifies current model availability | External control protocol and terms remain unresolved; developer product page was rate-limited and a bounded retry failed |
| DeepSeek Harness | [Product description](https://deepseek.com/harness/en/) and [official repository](https://github.com/deepseek-ai/deepseek-harness) expose a configurable plugin architecture and shared session-log operations | Compare component reuse with adapter integration; developer preview means version/breaking-change risk must be measured |
| T3 Code | [Official repository](https://github.com/pingdotgg/t3code) demonstrates a multi-harness control-surface approach | Inspect adapters as prior art; its graphical product and subscription claims do not establish Recursion compatibility |
| Native Recursion | Owner-required direct model-and-tool loop behind the shared runtime contract | Split into concrete eligible provider/endpoint/account routes and test independently; a generic row is not executable |

Anthropic illustrates why technical access, billing and distribution must be separate.
Its [current billing notice](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
pauses the previously announced SDK credit changes. Its
[product/credential conditions](https://code.claude.com/docs/en/legal-and-compliance) separately
govern unmodified binary hosting, user-owned authentication and credential intermediation.
The billing notice cannot establish blanket product-login permission. Conversely,
[OpenCode Go](https://opencode.ai/docs/go/) explicitly contemplates similar coding agents with
request-identification requirements; it should not be assumed exclusive to the OpenCode UI.

The most useful architecture experiments extend the existing M1 contracts, configuration resolver,
capsule/evidence model and placement/recovery primitives: role closure in an upstream-only workflow,
capability-preserving plugin compositions, executable compatibility records, configuration rehearsal
and deterministic failure simulation. Their comparisons and rejection rules are in
[architecture-roadmap.md](architecture-roadmap.md) and [trials.json](trials.json).

This source pass is complete as preparation, with named gaps. Immutable build pins, route-specific
usage/distribution decisions, exact effect mediation, realistic control latency, quota attribution
and cross-machine continuation remain for the next admitted probes. Mutable documentation and
vendor performance claims do not establish observed behavior. No current configuration, authentication
or runtime was changed.
