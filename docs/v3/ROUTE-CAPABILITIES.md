---
title: Recursion v3 provider-route capability matrix
status: reconstructed-current-observation
last-updated: 2026-09-03
---

# Recursion v3 provider-route capability matrix

This matrix records campaign observations, not entitlement, price, privacy, cache, subscription
debit or future availability. Model, provider, engine, account, capacity pool, credential
reference and host remain separate. Unknown never means free, unlimited or private-data eligible.

## Reconstruction campaign routes

| Requested route | Observation on 2026-09-03 | Campaign use | Unknown/limit |
|---|---|---|---|
| native Codex `gpt-5.6-luna`, `xhigh` | eight explicit workers accepted in two waves of four | R1-R17 reconstruction; planning lifecycle; DAG; source; lean adversary | dispatch is not completion, quality, contractual entitlement, cache or billing evidence |
| native Codex `gpt-5.6-terra`, `xhigh` | two targeted workers admitted after discovery | authority/lifecycle and final exact-document adjudication | same GPT-5.6 family as Sol/Luna; not cross-family independence |
| Contributor external family | not used | none; no packet or verdict | lead could not establish both an already approved current non-metered route and exact privacy/model mapping without forbidden account/configuration action |
| Grok external family | not used | none; no packet or verdict | exact approved non-metered route and known effort mapping unavailable without forbidden changes; no alias/substitute guessed |

The exact historical Muse packet/response described by older consolidated prose is not preserved
in the active repository. Its verdict is therefore unrecovered and not used as evidence. No new
external-family packet exists to reproduce. No paid fallback was enabled and no account/provider
configuration was inspected or changed.

## Admission observations

Before wave 1: 32 logical processors; 33.17 GiB free of 63.12 GiB memory; 650.72 GiB free disk;
418 processes/two visible Codex processes; usage surface 20% used in the visible 10,080-minute
window. Between waves: host response 2.6 seconds; 32.84 GiB free memory; 650.63 GiB free disk;
427 processes/one visible Codex process; usage surface still 20%. The localized CPU counter was
unavailable at the second check and was not guessed.

These point samples justified four-at-a-time admission only. They are not sustained machine or
provider capacity, model-token denominator, entitlement, billing, efficiency, concurrency default
or performance evidence. No returned account identifier was retained. Exact receipts are in
[AUTONOMOUS-PLANNING-CAMPAIGN.md](AUTONOMOUS-PLANNING-CAMPAIGN.md).

## Cache and route-capability precision

Official API documents opened 2026-09-03 establish only their own interfaces:

- [OpenAI API prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)
  exposes model-dependent automatic/explicit prefix caching, `prompt_cache_key`, breakpoints,
  retention controls and cached/write-token counters. The key influences routing but does not
  pin a machine or guarantee a hit. [OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction)
  exposes stateful compaction configuration and an opaque compaction item; neither is canonical
  Recursion evidence.
- [Anthropic API prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  exposes automatic/explicit breakpoints, up to four explicit breakpoints, a 20-block lookback,
  five-minute/one-hour TTL choices and cache read/write counters, with platform-specific isolation.
- [Gemini API context caching](https://ai.google.dev/gemini-api/docs/generate-content/caching)
  distinguishes implicit and explicit cached content, TTL/expiry/delete controls and cached-token
  metadata. Conflicting official savings wording means cost benefit remains unknown until measured.

These are not uniform or portable. They do not establish Codex OAuth CLI cache behavior,
subscription debit, account-window attribution or cross-provider cache reuse. A future
`RouteCapabilityDescriptor` records explicit supported/unsupported/unknown fields, exact endpoint,
model/account class, source/retrieval date and expiry. Revalidate on provider, endpoint, model,
SDK/CLI, account/policy or contradictory-observation change.

## Eligibility states

| State | Meaning | Required behavior |
|---|---|---|
| `verified-current` | exact behavior observed and applicable policy source fresh | eligible only inside current GoalSpec/privacy/budget/policy |
| `documented` | official source describes an interface but this exact route was not observed | require local admitted observation before work |
| `observed-uncertain` | response observed while billing/privacy/cache/control remains unclear | keep unknown fields and fail closed |
| `stale` | expiry or relevant component/policy changed | revalidate before autonomous selection |
| `unavailable` | required route/auth/control/authorized pool absent | block/defer that lane; never silently substitute or enable spend |

A model listing supplies name/capability documentation only. A successful dispatch supplies one
behavior observation only. Neither supplies billing, privacy, entitlement, stable capacity or
cache-portability authority.
