---
title: Recursion v3 provider-route capability matrix
status: evidence-reconciled
last-updated: 2026-09-03
---

# Recursion v3 provider-route capability matrix

This matrix records route observations, not promises of entitlement, price, privacy, or
future availability. `Model`, `provider`, `engine`, `account`, `capacity pool`, `credential
reference`, and `host` remain separate objects. Unknown never means free, unlimited, or
safe for private data.

## Campaign preflight

| Requested route | Local result on 2026-09-03 | What was established | What remains unknown | Campaign use |
|---|---|---|---|---|
| Native Codex `gpt-5.6-luna`, `xhigh`, default tier | Accepted by the native subagent interface | Exact model/effort dispatch is supported by the current app surface; `fast` was not requested | Contractual entitlement, reset capacity, future availability, and server-cache controls | Enabled for three bounded repository/review lanes |
| OpenCode Go `opencode-go/muse-spark-1.3-contributor` | Catalog present; public-only no-tool probe and research/review turns succeeded with OpenCode 1.18.25 | Exact installed identifier can produce responses on the current route | Stable entitlement, reset capacity, contractual billing, and future availability | Enabled only for public sources and synthetic briefs |
| Codex CLI custom-provider `grok-4.5`, `xhigh`, default tier | Failed closed with Codex CLI 0.149.0 | Current ChatGPT route does not support the model; no configured custom provider semantics were found | Authentication, non-metered authority, and whether `xhigh` maps meaningfully to xAI | Omitted; no Grok alias or alternate provider substituted |
| Codex spawned-agent concurrency | Codex CLI 0.149.0 accepted `agents.max_concurrent_threads_per_session=10`; official docs identify the field | The setting caps concurrently open spawned-agent threads and excludes the primary; `agents.max_threads` is a legacy alias | A client/app/server may enforce a lower effective ceiling, and syntax acceptance does not prove ten simultaneous routes have quota or machine headroom | Selected as the next campaign ceiling only; use bounded waves if effective capacity is lower |

The OpenCode probe reported a provider-calculated usage/cost field. That field is not proof
of a charge, a flat-subscription entitlement, or free metered usage. No paid fallback was
enabled. The Grok probe was a deliberately invalid capability check and completed without
using a supported model route.

## Primary capability sources

| Route fact | Source opened 2026-09-03 | Adjudication |
|---|---|---|
| Native subagents accept explicit model and reasoning overrides; concurrency is configured separately | [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) | Supports the local preflight shape, not account entitlement or remaining quota |
| `gpt-5.6-luna` is a named OpenAI model and `xhigh` is a documented capability | [OpenAI model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna) | API documentation does not prove this app's subscription terms; local dispatch supplies the behavioral observation |
| OpenCode Go names `muse-spark-1.3-contributor` and warns that Contributor prompts/completions may train future models and are not ZDR | [OpenCode Go](https://dev.opencode.ai/docs/go/) | Confirms the public/synthetic-only boundary; terms and limits are volatile |
| Grok 4.5 exists in xAI documentation | [Model page](https://docs.x.ai/developers/models/grok-4.5) and [vendor announcement](https://x.ai/news/grok-4-5) | Existence does not supply a configured Codex custom-provider route or meaningful `xhigh` mapping |
| Codex supports a per-session spawned-agent cap excluding the primary | [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) | Supports the selected profile shape; it does not bypass lower service/client limits or establish quota entitlement |

The Contributor lane received only purpose-written claims and public URLs. It did not receive
the v3 drafts, archived transcript, private repositories, infrastructure details, owner
identity, credentials, environment values, authentication output or local paths.

## Eligibility states

| State | Meaning | Required runtime behavior |
|---|---|---|
| `verified-current` | Exact route behavior was directly observed and its policy source is fresh | May be eligible only inside the existing GoalSpec and privacy/budget envelope |
| `documented` | Official source describes the capability, but this installation was not probed | Require local admission probe before first real work |
| `observed-uncertain` | A response was observed but billing, privacy, cache, or control semantics remain unclear | Preserve unknown fields; fail closed across the uncertain boundary |
| `stale` | Evidence is beyond its route-specific expiry or a relevant component changed | Revalidate before autonomous selection |
| `unavailable` | Required model, provider, auth, control, or authorized pool is absent | Stop only that lane; never silently substitute |

## Revalidation triggers

Revalidate after a CLI/app/model/provider update, descriptor change, authentication-profile
change, contradictory runtime observation, or the time limit recorded in the claim ledger.
A model listing is route-name evidence only. A successful prompt is behavior evidence only.
Neither proves subscription coverage, stable capacity, privacy terms, or cache portability.
