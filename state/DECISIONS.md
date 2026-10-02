# Decision log

Every decision gets a falsifier — the specific thing that, if observed, means this was wrong.
Without it, review is hindsight.

**Review cadence:** first of the month. Pull decisions ≥60 days old, check whether the
falsifier fired, mark `HELD` / `FAILED` / `UNCLEAR`. Do not edit the original entry.

---

## D-017 — Recursion v3 is greenfield; v1/v2 are retired, not migrated
Date: 2026-09-28 · Status: OPEN

**Options considered:** A) migrate v2 aggregate-by-aggregate into v3 (the original
`CURRENT-AND-MIGRATION` / OR-019 strangler) / B) keep both versions side by side / C) treat v3 as
a brand-new harness that inherits nothing from v1/v2 and retire the old control plane.

**Chose:** C.

**Because:** v3 is a from-scratch provider-neutral agent harness (its own client, execution
kernel, context/compaction engine and node fabric). The v1/v2 Hermes-based control plane
contributed no dependency to it, and version coexistence caused the drift that blocked
contributors. The complete prior tree is preserved at tag `pre-v3-clean-cut-20260928`.

**Consequence:** the pre-v3 decision log (D-001 through D-016) and the v2 migration framing in
`docs/v3/CURRENT-AND-MIGRATION.md` are historical lineage only and authorize no current work.
`CONTROL_PLANE.md` and `ANCHOR.md` were rewritten for a single-product repository under Lucas
alone, with coding agents as bounded executors and no standing executive.

**Falsifier:** if v3 turns out to require v2 state, schema or a migration path to function, this
was wrong.

**Review:** 2026-12-01

---

## D-018 — Thesis: Recursion is a native harness *and* a unifying wrapper; no ecosystem lock-in
Date: 2026-10-02 · Status: ACCEPTED

**Options considered:** A) keep the 2026-09-07 "not another … provider router" framing / B)
reposition Recursion as both a first-class native harness and a first-class wrapper over the
wider harness ecosystem, whose purpose is to remove lock-in and cut quota/usage burn, shipped as
a community, open-source product.

**Chose:** B.

**Because:** users should be able to use the models and subscriptions they already prefer across
many harnesses; much of that surface is reachable by adapter/porting rather than greenfield work;
and a community/open-source posture is the growth vector.

**Consequence:** `PRODUCT.md` and `ANCHOR.md` are reframed; the "provider router" non-goal is
reworded to "not a naive router"; the compatibility inventory expands with plugin-supported
harnesses. The claim that vendors deliberately unoptimize quota is recorded as a **hypothesis
requiring a falsifiable experiment**, never as fact. Release or publication of any
credential-reliant route stays counsel-gated (G-32).

**Falsifier:** honest measurement shows Recursion cannot reduce quota/usage burden, or cannot
integrate routes without violating provider terms.

**Review:** 2026-12-01

## D-019 — Release model: build comprehensively, ship lean, install opt-in (Dot Option B rejected)
Date: 2026-10-02 · Status: ACCEPTED

**Options considered:** A) lean default with all accepted capabilities available through
supported components/profiles / B) a smaller initial release with revised launch gates and named
deferrals (the Dot's recommendation).

**Chose:** A. The Dot's Option B is rejected as the release model.

**Because:** a 2-developer project needs the full capability and plugin surface at first release
to be adopted; a large fraction of that surface is port/optimize work ported from existing plugin
ecosystems, not new invention; and deferrals shrink the product without meaningfully shrinking
the engineering.

**Consequence:** the comprehensive contract in OR-021…OR-025 stands; every capability is built and
ships as an opt-in plugin/profile, not default. The Dot's seven proposed deferrals (seven-name
launch gate, remote nodes, coordination topologies, universal plugin adaptation, six-mode
updates, GUI, adaptive compaction/research) become *built, opt-in, not default* unless separately
removed.

**Falsifier:** delivery evidence shows the comprehensive surface cannot reach a usable first
release, or that porting leverage is far lower than assumed.

**Review:** 2026-12-01

## D-020 — Availability contract: automatic node takeover required; core is single-node (closes G-06)
Date: 2026-10-02 · Status: ACCEPTED

**Options considered:** for canonical-state availability after coordinator loss: A) fail-closed,
writer may be temporarily unavailable / B) another enrolled node must take over writing
automatically; and for packaging: core-only vs plugin.

**Chose:** B for availability (user-toggleable, required for long-running autonomous work), with
the shipping **core single-node**. The kernel owns the monotonic fence/epoch and a store/
availability seam; the replicated store + coordinator election ship as a first-party plugin in
the `remote`/`full` editions. Default install compiles in no consensus.

**Because:** auto-takeover can only be a *safe* plugin if fencing is core; otherwise two writers
can commit. This preserves one-writer correctness while giving zero-downtime failover when the
plugin is installed.

**Consequence:** closes G-06. Adds a store/availability seam to the architecture; names
availability backends and node transports as capability plugins; distinguishes multi-node
*execution* (first release, OR-025) from multi-node *canonical-writer failover* (plugin).

**Falsifier:** a plugin cannot implement takeover against the core fence contract, or the seam
forces consensus into the core.

**Review:** 2026-12-01

## D-021 — Delegation over credential intermediation

Date: 2026-10-02 · Status: ACCEPTED

**Chose:** Recursion must not hold, copy or relay provider credentials it was not explicitly
granted; where possible it delegates a request to a user-authenticated local tool/harness rather
than intermediating login. Driving the user's already-authenticated CLI is the preferred route
over capturing OAuth tokens.

**Because:** third-party credential intermediation is the specific thing provider terms restrict;
delegation to an installed authenticated tool is a materially stronger legal and trust position and
is the cross-harness behavior the product is built for.

**Consequence:** an architecture principle, applied per adapter. Still not legal advice:
per-route terms and automation limits remain counsel-gated (G-32 / D-027).

**Falsifier:** a required route only works via credential intermediation and cannot be delegated.

**Review:** 2026-12-01

## D-022 — One pause/stop vocabulary across config, formal model and broker (G-07)

Date: 2026-10-02 · Status: ACCEPTED

**Chose:** adopt three Stop modes — **Aggressive / Full / Lazy** — plus `checkpoint`, `interrupt`
and `drain`, as the single cross-surface vocabulary in configuration, the formal model and the
broker. A source interrupt, socket close or killed PID is not external rollback.

**Because:** three surfaces currently disagree, and pause/stop is the substrate for revocation,
disconnect and admission.

**Consequence:** needs to be reflected in FU-03's model and the broker contract; G-07 closed.

**Falsifier:** the vocabulary cannot be expressed consistently across all three surfaces.

**Review:** 2026-12-01

## D-023 — First qualified upstream profile

Date: 2026-10-02 · Status: ACCEPTED

**Chose:** qualify **Codex App Server** end-to-end first (strongest structured interface:
steering, correlated approvals/questions, resume, compaction, review). All other harnesses ship as
plugins.

**Because:** a first qualified profile forces the adapter contract to be real; Codex exposes the
richest structured surface to qualify against.

**Consequence:** FU-01/FU-05 route work targets Codex first; a second, deliberately different
adapter is prototyped as an architecture stress test, not a launch promise.

**Falsifier:** Codex's stable/experimental split or account terms prevent a trustworthy qualified
profile.

**Review:** 2026-12-01

## D-024 — Frontier claim: productive continuity

Date: 2026-10-02 · Status: ACCEPTED

**Chose:** the headline measurable differentiator is **productive continuity** — a currently
authorized task survives a harness change, compaction, a source fork or a lost machine while
preserving authority, evidence and honest accounting. The six demonstration journeys from the
2026-10-02 strategy are adopted as release acceptance scenarios.

**Because:** multi-agent dashboards, persistence, plugins, worktrees and attention inboxes already
exist elsewhere; only the combined continuity contract is a candidate advance, and it must beat
strong baselines in verified outcomes and human effort.

**Consequence:** evaluation focuses on continuity endpoints, not feature counts.

**Falsifier:** a strong baseline preserves these semantics with equal or less effort.

**Review:** 2026-12-01

## D-025 — Continuing autonomous research is an optional bounded plugin

Date: 2026-10-02 · Status: ACCEPTED

**Chose:** 24/7 autonomous research is an optional, off-by-default, budgeted plugin with explicit
sources, cadence, stopping conditions and promotion authority. It is not a standing executive and
cannot self-activate or self-approve.

**Because:** matches ANCHOR's "no standing autonomous executive" and keeps the lean base idle-free.

**Consequence:** G-27/G-33 style research work stays optional; lean profiles do no idle inference.

**Falsifier:** it cannot be bounded, or it reproduces a standing executive by another name.

**Review:** 2026-12-01

## D-026 — Recursion's own license and public posture

Date: 2026-10-02 · Status: ACCEPTED (license file still to be added)

**Chose:** release as a community, open-source project under **Apache-2.0** (patent grant +
adoption), with the plugin/capability contract published early to attract porters, and a
contribution/CLA posture to be finalized.

**Because:** the growth vector is community adoption and plugin porting; a permissive,
patent-granting license maximizes both.

**Consequence:** add a LICENSE file and a `plugin` contract doc; this is a distribution decision
that still requires counsel (D-027) before any public release claim.

**Falsifier:** counsel identifies an obligation incompatible with Apache-2.0 distribution.

**Review:** 2026-12-01

## D-027 — Counsel engagement authorized (packet only; no spend)

Date: 2026-10-02 · Status: ACCEPTED

**Chose:** authorize preparation of a counsel-ready packet — per-route terms/ToS, third-party
credential-intermediation limits, Recursion's own licensing, distribution and trademark handling.
Lucas engages counsel; no spending or legal commitment is made by an agent.

**Because:** G-32 / DS-33 make licensing a hard release gate, and the anti-lock-in goal is legally
sensitive the moment the repository is public.

**Consequence:** research packet R-C is commissioned; G-32 stays open until counsel returns.

**Falsifier:** n/a (a process decision).

**Review:** 2026-12-01

---

## D-028 — Platform floors (closes G-11)
Date: 2026-10-02 · Status: ACCEPTED

**Chose:**

- **Windows:** minimum **Windows 11 25H2 (build 26200)** for Home/Pro; additionally qualify
  **24H2 (build 26100) Enterprise**. **x64 primary**; Arm64 a separate later case.
- **Linux:** kernel **6.12 LTS** primary, **6.6 LTS** compatibility minimum; **cgroup v2
  required**; ext4.
- **WSL2:** development/test only, never production; WSL2-ext4 and WSL2 `/mnt/c` are distinct
  mandatory cases.
- **Storage:** canonical state on **local NTFS / local ext4 only**; **SMB/NFS out of scope** for
  the first release.
- **"Survives power loss":** application-consistent after an abrupt **VM reset** at the commit
  boundary, verified by replay reproducing identical canonical state. Physical platter
  interruption is out of scope.
- **Filesystems:** NTFS + ext4; ReFS/xfs/btrfs deferred.

**Because:** these are bounded, testable floors; 24H2 Home/Pro reaches end of updates on
2026-10-13; 6.12 LTS is the RHEL 10 / Debian 13 kernel and 6.6 LTS covers Ubuntu 24.04 and WSL.

**Consequence:** closes G-11. FU-04 pins these floors, maps every manifest case to an in-scope /
dev-test / out-of-scope / later disposition, and keeps every profile **Unqualified** until its
traces pass. Destructive traces still require a disposable, Owner-approved target.

**Falsifier:** a required mechanism fails at the stated floor, or replay diverges after an abrupt
VM reset.

**Review:** 2026-12-01
