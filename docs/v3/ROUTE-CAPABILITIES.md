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
| Native Codex `gpt-5.6-luna`, `xhigh`, default tier | Eight explicit research workers were accepted in two four-worker waves by the native subagent interface | Exact model/effort dispatch is supported by the current app surface; `fast` was not requested | Contractual entitlement, future availability, server-cache controls and how dispatch maps to account-window use | Enabled for the eight bounded discovery lanes; acceptance is not completion or quality evidence |
| Native Codex `gpt-5.6-terra`, `xhigh`, default tier | Current interface and official model documentation expose the exact model and effort; campaign adjudication is admitted only after Luna packets exist | The requested selector is available and official documentation includes `xhigh` | Contractual entitlement, future availability and service-side accounting | Reserved for two targeted same-family adjudication lanes |
| OpenCode Go `opencode-go/muse-spark-1.3-contributor` | Catalog present; a public synthetic no-tool probe returned the requested sentinel with OpenCode 1.18.25 | Exact installed identifier can produce a response on the current route | Stable entitlement, reset capacity, contractual billing, future availability and provider-policy naming drift | Eligible only for public sources and purpose-written synthetic briefs |
| Codex CLI custom-provider `grok-4.5`, `xhigh`, default tier | Omitted after read-only inspection found no configured custom-provider/profile section | No already-configured Codex custom-provider route exists; official xAI API documentation describes metered API use and `low`/`medium`/`high`, not Codex `xhigh` semantics | Whether Lucas later configures an approved non-metered route | Omitted; no prompt, alias, provider, effort or billing substitution |
| Codex spawned-agent concurrency | Effective config has `agents.enabled=true` and `agents.max_concurrent_threads_per_session=10`; ten no-op agents were accepted before the campaign, and eight Luna workers were later admitted | The setting caps concurrently open spawned-agent threads and excludes the primary; the current client accepted the configured ceiling | Simultaneous provider capacity, remaining quota and service throttling remain independent | Ten is the observed/configured ceiling; workers are staged in waves and machine/review headroom can lower admission |

The OpenCode probe result is not proof of a charge, flat-subscription entitlement or free
metered usage. No paid fallback was enabled. The current English OpenCode Go page listed Muse
Spark 1.2 Contributor while the installed catalog and other official OpenCode pages named 1.3;
the exact installed 1.3 route responded, but the documentation mismatch remains visible and
blocks any stronger stability claim. No Grok prompt was sent because the required pre-existing
custom-provider route was absent.

## Current admission observation

The campaign host exposed 32 logical processors, about 34 GiB free memory and about 653 GiB free
disk before research admission. Four Luna workers were admitted, the machine was rechecked, and
then four more were admitted because local memory, disk and process counts remained effectively
unchanged. This is a one-time observation, not a benchmark or edition default. New workers stop
when local responsiveness, memory/disk pressure, provider throttling, remaining synthesis quota
or review debt becomes material.

## Primary capability sources

| Route fact | Source opened 2026-09-03 | Adjudication |
|---|---|---|
| Native subagents accept explicit model and reasoning overrides; concurrency is configured separately | [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) | Supports the local preflight shape, not account entitlement or remaining quota |
| `gpt-5.6-luna` and `gpt-5.6-terra` are named OpenAI models and `xhigh` is a documented capability | [Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and [Terra model page](https://developers.openai.com/api/docs/models/gpt-5.6-terra) | API documentation does not prove this app's subscription terms; local dispatch supplies the behavioral observation |
| OpenCode Contributor routes permit provider training and are not ZDR | [OpenCode Go](https://dev.opencode.ai/docs/go/) and [OpenCode Zen](https://dev.opencode.ai/docs/zen) | Confirms the public/synthetic-only boundary; the pages disagreed on the current Muse minor version, so the installed exact identifier is recorded separately |
| Grok 4.5 exists through a metered xAI API and documents `low`, `medium` and `high` reasoning controls | [Model page](https://docs.x.ai/developers/models/grok-4.5) | Existence does not supply a configured Codex custom-provider route, non-metered authority or meaningful Codex `xhigh` mapping |
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
