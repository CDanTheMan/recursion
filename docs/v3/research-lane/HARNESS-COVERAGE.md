---
title: Harness coverage matrix (anti-drift)
status: research-coverage-not-qualification
last-updated: 2026-10-01
---

# Harness coverage matrix

One row per harness/product named across the repository. A cell is `documented`
(source-documented with a path), `partial`, `unknown`, or `not applicable`. **A documented capability
is not a qualified one.** No harness was installed, logged in or run for this file.

## Legend

- `SRC-V3-NNN` — row in `SOURCE-REGISTER.md`.
- `RCAP` — `ROUTE-CAPABILITIES.md`; `RM` — `REFERENCE-MATRIX.md`; `FH` — `FRONTIER-HARNESS-EVIDENCE.md`.
- `ST§4`/`ST§5` — `research-lane/scope-reframe-20261002/raw/01-current-strategy/Recursion_Interface_and_Product_Strategy.md`.
- `RB§3` — `research-lane/dot-ra-rd-20261002/raw/R-B/report.md`; `RC` — `.../raw/R-C/report.md`; `RD` — `.../raw/R-D/report.md`.
- `RI` — `prompts/dot-research-20261002b/R-I-grok-build-source-study.md`.

## Coverage matrix

| Harness/product | Route/interface documented | Source-code study | UI/TUI flow | Plugin/extension model | Delegation surface | Legal/terms (R-C) | Quota/accounting (R-D) | Overall status |
|---|---|---|---|---|---|---|---|---|
| Codex / ChatGPT-OAuth | documented (SRC-V3-052,107,144,252) | documented (SRC-V3-052,252,273) | partial (ST§4) | documented (SRC-V3-052,109) | documented (RB§3.1) | documented (RC O1–O5) | documented (RD§1) | documented, uninstalled; D-023 first |
| Claude Code | documented (SRC-V3-044,139–150,220–221,224) | partial (SRC-V3-044; proprietary) | partial (ST§4) | documented (SRC-V3-044) | documented (RB§3.2) | documented (RC C1–C6) | documented (RD§1) | documented; internals closed |
| Cursor first-party | documented (SRC-V3-046,121–124,151–152,205,268) | partial (SRC-V3-152,268) | partial (ST§4) | partial (SRC-V3-151) | documented (RB§3.3) | documented (RC U1–U6) | partial (RD) | documented, uninstalled |
| Cursor third-party | documented (SRC-V3-153,268) | documented (SRC-V3-268) | not applicable (headless) | unknown (SRC-V3-268) | documented (RB§3.3) | documented (SRC-V3-268) | unknown | documented adapter; distribution open |
| Gemini / Google CLI | documented (SRC-V3-043,053,115,159–160,225) | documented (SRC-V3-053,215–217) | partial (ST§4) | documented (SRC-V3-053,159) | documented (RB§3.4) | documented (RC G1–G9) | documented (RD) | documented; Plan Mode trap |
| Grok Build | documented (SRC-V3-125,161,204,208) | documented (SRC-V3-208–214,222,267); RI issued | documented (SRC-V3-125; ST§4) | documented (SRC-V3-208–209) | documented (RB§3.5); wire partial | documented (RC X1–X5) | documented (SRC-V3-267) | Apache-2.0, source-documented |
| Hermes Agent | documented (SRC-V3-045,120,154–157,244) | documented (SRC-V3-244,269,274–275) | documented (ST§4) | documented (SRC-V3-045) | documented (RB§3.6) | documented (RC H1–H3) | partial (SRC-V3-274) | documented; executive role retired, D-017 |
| OpenCode v1 | documented (SRC-V3-042,054,117,169–171,200) | documented (SRC-V3-054,218–223,238,271) | partial (SRC-V3-117; ST§4) | documented (SRC-V3-042,171,238) | documented (RB§3.7) | documented (RC P1–P3) | partial (RD) | documented v1.18.x |
| OpenCode v2 | partial (ST§4) | unknown (no pin) | partial (ST§4) | documented (ST§4; SRC-V3-200) | partial (ST§4; prompt_async) | partial (RC; no v2 pin) | unknown | generation split; do not mix |
| Antigravity | documented (SRC-V3-165–168,201) | partial (SRC-V3-201) | documented (ST§4) | documented (SRC-V3-201) | documented (RB§3.8) | documented (RC A1–A5) | partial (ST§4) | local/managed separated |
| Pi | documented (SRC-V3-041,059,195) | documented (SRC-V3-041,059,251) | partial (SRC-V3-195; ST§5) | documented (SRC-V3-041) | documented (RB§3.9) | documented (RC I1) | documented (SRC-V3-251) | experimental durable; no sandbox |
| Meta Muse Code | documented (SRC-V3-126,163–164; ST§4) | documented (ST§4 msp schema) | documented (ST§4) | unknown | partial (ST§4) | unknown (not in RC nine) | unknown | referent resolved; embedding open |
| DeepSeek Harness / Cordis | documented (SRC-V3-040,118,158,183) | documented (SRC-V3-040,118) | partial (ST§4) | documented (SRC-V3-118,183) | documented (ST§4) | partial (RC appendix) | partial (ST§4) | developer preview |
| T3 Code | documented (SRC-V3-039,119,229) | documented (SRC-V3-039,119,229) | documented (ST§5) | unknown | unknown (not in RB nine) | documented (SRC-V3-039; RM) | partial (ST§5) | operator-interface baseline, not routed |
| Goose | documented (SRC-V3-058; ST§5) | documented (SRC-V3-058) | documented (ST§5) | documented (ST§5) | partial (ST§5) | partial (RC appendix) | unknown | composition precedent |
| Aider | documented (SRC-V3-057; ST§5) | documented (SRC-V3-057) | partial (ST§5) | unknown | unknown | documented (SRC-V3-057) | unknown | Git-first baseline |
| mini-SWE-agent | documented (SRC-V3-101; ST§5) | documented (SRC-V3-101) | not applicable | unknown | unknown | documented (SRC-V3-101) | partial (ST§5) | minimal baseline / contradictory evidence |
| OpenHands | documented (SRC-V3-055; ST§5) | documented (SRC-V3-055) | partial (ST§5) | unknown | documented (SRC-V3-055; ST§5) | documented (SRC-V3-055) | unknown | durability prior art |
| Devin | partial (construction/external-rdt-20260914/README.md) | not applicable (proprietary) | unknown | unknown | partial (construction campaign) | unknown | partial (external-rdt README) | contributor tool, no adapter research |
| Cline | partial (FH corpus) | partial (sampled/excluded) | unknown | unknown | unknown | unknown | unknown | sampled, then excluded |
| Command Code | unknown (PRODUCT.md name only) | unknown | unknown | unknown | unknown | unknown | unknown | name-only |
| Grok Bot | documented (SRC-V3-194; ST§5) | unknown (cloud) | documented (ST§5) | unknown | partial (ST§5) | unknown (not in RC nine) | unknown | UX reference, distinct from Grok Build |
| SWE-agent | documented (SRC-V3-056) | documented (SRC-V3-056) | not applicable | unknown | unknown | documented (SRC-V3-056) | unknown | benchmark-loop reference |
| Continue / Roo Code | partial (FH corpus) | partial (sampled/excluded) | unknown | unknown | unknown | unknown | unknown | IDE-presentation overlap, excluded |
| BYOK | documented (RCAP; RM) | not applicable | not applicable | unknown | partial (RCAP) | partial (RC provider terms) | unknown | native-loop category, unbuilt |
| ChatGPT sign-in (SiWC) | documented (ST§4; RC O5) | unknown | partial (ST§4) | unknown | partial (ST§4) | partial (RC O1–O5) | unknown | candidate, restricted preview |
| Perplexity | unknown (PRODUCT.md comparator) | unknown | unknown | unknown | unknown | unknown | unknown | prospective research-quality comparator only |

## Biggest gaps

1. **Quota/accounting values (R-D).** Every counter is a candidate surface with no measured value,
   helper coverage, cache debit or subscription attribution. Run `RD§3` (U1–U12, Q1–Q5) per route
   before any efficiency claim.
2. **Real delegation semantics beyond nine routes (RB§3, R-F).** T3, Goose, Aider, mini-SWE-agent,
   Devin, Cline, Command Code and Grok Bot have no submit/steer/interrupt/resume/observe map;
   extend the R-B map.
3. **Plugin/extension model unstudied (R-G).** T3, Aider, OpenHands, mini-SWE-agent, Muse Code and
   Grok Bot have no extension-model record; importability and porting savings stay unmeasured.
4. **UI/TUI flow thin (R-J).** Almost every row is `partial`; only Grok Build, Hermes and the
   T3/Goose/OpenHands baselines document an interaction flow. Thinnest column.
5. **Legal terms outside the R-C nine (R-C/R-H).** Muse Code, Grok Bot, Devin, Cline, Command Code,
   T3, Goose, Aider, mini-SWE-agent, OpenHands and BYOK have no route terms record; G-32 stays open.
6. **Proprietary internals (R-I/R-G).** Claude Code, Cursor first-party, Devin, Grok Bot and
   OpenCode v2 lack an open source study; Claude Code and Cursor remain interface-only.
7. **Trusted-launch/credential boundary (R-E).** Cross-cutting and unevidenced for all rows; the
   strong non-intermediation claim is architecture, not a tested property.

**Packet mapping:** 1,2 → R-D/R-F; 3 → R-G; 4 → R-J
(`R-J-multi-agent-terminal-communication.md`); 5 → R-C/R-H; 6 → R-I/R-G; 7 → R-E.

## Limits

No harness was installed, logged in, probed or run; no credentials, provider call, spend or counsel
contact occurred, and no file outside this one changed. These cells record document coverage only.
Nothing here is qualification, entitlement, security clearance, legal advice or acceptance;
`documented` means a source says it, never that Recursion can use it. Revalidate every `SRC-V3`
cell against its stated expiry before relying on it.
