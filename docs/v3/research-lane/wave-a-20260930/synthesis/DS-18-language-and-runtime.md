# DS-18 — language and runtime (synthesis)

## Provenance

Synthesis of the Deep Research report at `raw/ds-3-DS-18-language-runtime.md`, answering the handoff `DS-18 —
Implementation language and runtime selection`. Evidence freeze is 2026-09-30; the report's upstream claims
rest on the report's sources, not on any Recursion rerun. The raw file carries status
`research-evidence-not-a-decision` and is not independently verified.

## The question

Not "which language is best," but Owner decision support for a hard-to-reverse foundational choice, split into
three questions:

1. Which candidates demonstrably satisfy the language-independent hard floors?
2. Among floor-passers, what are the real resource/operational trade-offs on coordinator-small?
3. Does any hybrid topology earn its extra ABI and packaging complexity?

The report splits the decision: the privileged pure kernel and canonical writer are dominated by determinism,
race freedom, stable refusals and dependency closure; the daemon, broker and adapters are where cancellation,
OS seams, FFI and long-running tail latency dominate.

## Key findings

- **No selection.** There is no product-default language. Evidence is insufficient and DS-18 reserves the
  choice to the Owner. The verdict is "no-selection now," not "choose Rust," "choose Go" or "stay with
  Python."
- **Primary experiment `EXP-FHAR-10`** remains the CPython / Rust / Go triad. Exact pins at freeze: **CPython
  3.13.15** (GIL and free-threaded builds as *separate* arms), **Rust 1.98.1**, **Go 1.27.1**. An optional
  Python **3.14.7** regular/free-threaded sensitivity arm may be added only by explicit amendment, never as a
  silent replacement. Python 3.13 free-threading is experimental; 3.14 moved it to supported phase II. Rust
  1.98.1 corrected a 1.98.0 miscompilation, which the report uses to argue for exact compiler pins.
- **Hard-floor-first order.** `EXP-FHAR-10` is conformance then resource comparison. Freeze
  toolchain/host/deps/flags; run canonical-byte conformance, replay and refusal stability,
  race/lease/PAUSE/crash faults, offline build and SBOM closure; any failure rejects the candidate. Only
  floor-passers get latency/CPU/RSS/FFI/cold-start/soak measurements. No weighted composite score: speed
  cannot compensate a correctness failure.
- **Determinism hazards.** RFC 8785 canonicalization must be explicit: deterministic property sorting,
  duplicate-key rejection *before* a parser collapses an object into a map, finite IEEE-754 numbers, `-0` →
  `0`, rejection of NaN/Infinity, no Unicode normalization. No candidate may rely on ordinary map/dictionary
  traversal, default JSON serialization, ambient hashing, RNG, wall clock or exception text. Python hash
  randomization, Rust randomized `HashMap` and unspecified Go map order all forbid container-derived ordering;
  refusals must be protocol-owned `{code, schema_epoch, field/path, stable_detail_enum}`.
- **Concurrency/cancellation limits.** No reviewed runtime provides PauseSafety by itself. Go `context`
  cancellation is cooperative; Python `Task.cancel()` can be delayed or suppressed; Tokio `spawn_blocking`
  work cannot necessarily be aborted after starting; JDK 27 structured concurrency is preview and
  uninterruptible subtasks may delay scope close. PauseSafety must be an admission/effect-fencing invariant,
  with an explicit canonical-writer primitive in every language.
- **Memory/tail latency are `unknown`.** p99/p999 latency, RSS level and slope, FFI cost, artifact size, cold
  start, dependency-closure size and 24/7 behavior are unmeasured for every candidate on the 2-vCPU/4-GiB
  profile. Go's concurrent GC has assist/scheduling and brief stop-the-world transitions plus a *soft* memory
  limit; CPython has `pymalloc` arenas and cyclic GC; a non-tracing runtime does not by itself prove bounded
  RSS.
- **Packaging.** Rust Cargo supports vendor/`--locked`/`--offline`/`--frozen`; Go supports module checksums
  and vendoring; Python has a standardized lock-file format, but its Windows/Linux wheel/sdist closure is
  dependency-specific. None of these facts proves bit-reproducible Recursion artifacts; a clean-host,
  network-off release drill must test that.
- **WASM.** WASI 0.3 is a stronger component/plugin substrate with native async and the Component Model. It is
  better evidence for the `E-FHAR2-105` plugin-isolation lane than for putting the privileged kernel inside a
  Wasm runtime. The host engine (e.g. a Wasmtime build) is part of the trusted base and must itself be pinned;
  per-boundary cost is unknown.
- **Hybrid topology.** Python kernel + Rust hotspots (PyO3), Rust embedding Python, Go + cgo, and a
  WASM-sandboxed plugin tier each add a pin, ABI, packaging and failure surface. A hybrid is rejected unless
  it shows a measured advantage a simpler single-runtime or process-isolated topology cannot obtain.

## Recommendation and falsifier

Preserve the explicit **no-selection** result and make `EXP-FHAR-10` the decision-producing artifact. Pass
every hard floor first; among passers, select only when one option shows a practically meaningful,
reproducible advantage on named resource/operational dimensions without a compensating packaging, FFI, support
or supply-chain regression; otherwise retain no-selection and gather the missing evidence.

Decisive falsifiers: non-identical admitted event/refusal bytes across valid reruns or Windows/Linux; a replay
yielding a different state/projection digest or permitting blind effect re-execution; concurrent admission
violating canonical sequence, idempotence, lease fencing, authority narrowing or expected-state semantics; a
PAUSE/epoch race letting stale work commit an unauthorized effect; core-only release not reconstructable
offline or SBOM/provenance inputs unaccounted. Per-candidate: Rust if its safe abstractions still force a
large `unsafe`/FFI surface; Go if GC/RSS/tail or cgo seams violate accepted envelopes; CPython if
GIL/free-threaded, extension closure, RSS/tail or packaging make the core materially less robust; any hybrid
if it shows no measured benefit over a simpler topology; the WASM plugin layer if the Component Model cannot
express the capability/denial lifecycle or boundary cost defeats the isolation benefit.

**No recommended experiment was run in producing the report, and no language is selected.**

## What this does not prove

It does not prove Rust will win; that Go's GC is too expensive; that Python is too slow; that Zig lacks the
necessary ecosystem closure; that a JVM is too large; that JavaScript runtimes are nondeterministic; or that
Wasm should or should not host plugins. Raw historical CVE totals are a poor ranking metric without exposure
normalization, and the real library closure (SQLite binding, JCS, crypto, PTY/ConPTY, MCP, HTTP) is
unselected, so per-candidate CVE totals remain `unknown`. "Current stable" means upstream release status at
freeze, not that a binary passed Recursion's frozen-host acceptance. Exact per-call FFI costs and all
Recursion p99/p999/RSS figures remain unmeasured.

## Open Owner decisions

- Is one implementation language across kernel, daemon and broker a goal, or may a second runtime be accepted
  when independently justified?
- Is CPython 3.13 required long-term, or may 3.14.7 be promoted after a sensitivity comparison?
- What minimum supported Windows versions must the broker target?
- Must the core be a single executable, or is a signed self-contained install closure acceptable?
- Is a preview runtime API ever acceptable inside the privileged base?
- Is Wasm's first evaluation specifically a plugin-isolation lane rather than a kernel lane?
- What evidence threshold converts a resource difference into a practical decision?
- What is the acceptable dependency-security policy (upgrade cadence, severity tolerance, native dependency
  rules)?

## Relevance to later waves

The language/runtime choice shapes later canonical-state, plugin/route, node-fabric, optimization and soak
milestones. Its outputs feed: canonical-byte and replay suites for conformance work; the `E-FHAR2-105`
plugin-isolation probe and the zero-cost-disabled test; `ReleaseId`/`E-FHAR2-108` build-provenance and SPDX
SBOM evidence; and version-pinned integration (for example a specific MCP protocol version rather than
"supports MCP"). Until `EXP-FHAR-10` runs and is independently verified, later waves must treat every
candidate as viable and no runtime as chosen.
