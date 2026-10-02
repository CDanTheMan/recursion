# Recursion iOS and Android design and language research

Separate mobile-platform research packet for Lucas, 2026-10-02.

This extends the corrected capability-composition packet without replacing it. It addresses two independently optimized client apps: an iOS glassmorphic design and a custom Android design, both using Recursion's existing backend semantics.

## Recommendations to evaluate

- **iOS:** Swift and a SwiftUI application shell, with narrowly scoped UIKit integration only where an equivalent, accessible workload demonstrates a benefit. Use system glass for appropriate navigation and controls; keep dense streams, evidence and consequential details readable
- **Android:** Kotlin and Jetpack Compose with a custom design system. Compare a Views-heavy implementation and introduce specialized rendering only when profiling justifies its complexity
- **Shared product:** preserve command meanings, device/current-authority checks, receipt facts, source-cut honesty and all ten controls/three Stops. Share contracts and parity fixtures before assuming shared UI code is necessary

These are advisory starting recommendations, not a claim that native languages automatically win every performance test. Both reports treat modern React Native as a genuine comparator. AI-assisted authoring is evaluated together with review, debugging, accessibility, device coverage and ongoing OS maintenance.

## Reports

1. [iOS design and optimization](ios/report.md): glass treatment, screen/navigation design, SwiftUI/UIKit alternatives, streaming and text behavior, iPhone/iPad adaptation, accessibility, lifecycle, privacy, notifications and bounded measurement handoff
2. [Android design and optimization](android/report.md): custom visual systems, Compose/Views alternatives, navigation and predictive Back, insets/IME, adaptive/foldable windows, accessibility, streams, lifecycle, backup/device identity, notifications and bounded measurement handoff

Each report includes competing designs, falsifiers, non-proofs, current primary sources and local prototype/test work for later sessions. OS/build/API availability, minimum supported devices, private offline retention and distribution qualification remain explicit decisions or evidence gaps.

## Input continuity

Repository pin: `b696f6ece243b48c94fc0bbc7ee1d4b284c46f97`.

Shared UI input: `recursion.ui-contract@candidate-2`, report SHA-256 `23fa223bc92fd53b6f5f82d27ea7bf7d4082f3e82f0653f190efd2e734efa931`.

Mobile contract input: corrected R-MOB report SHA-256 `b44826c1e46bd64c7e8e710a5258dfa34a4a810a9d962f672b3d60c34c29c65e`.

These corrected reports are in the previously delivered Revision 2 packet. Your local repository may have advanced while this research was underway; reconcile any newer changes before implementation.

## Local execution handoff

1. Review the advisory stack and design choices against current repository requirements; do not treat this packet as a ratified implementation decision
2. Select exact OS/device/build profiles and finite prototype budgets through the normal local task process
3. Exercise identical semantic journeys on both clients, including live connection loss, uncertain commands, input leases, Stop scopes, large text, accessibility, process recreation and slow streams
4. Compare equivalent release/profile builds and full-workflow costs; separate language, toolkit, rendering, batching, network and backend effects
5. Preserve failed, refused and unresolved outcomes. Return exact candidate/profile identities and independent results, rather than screenshots or a single benchmark score

All proposed app prototypes, runtime tests and performance experiments remain **UNEXECUTED**. No apps were built or installed; no Work/Codex sessions, model/provider calls, device/account/store actions, credentials, spending or live-host changes were used. The prior Revision 2 packet is unchanged.

The archive contains only this guide, the two reports and `SHA256SUMS.txt`. Internal review records, source captures and generation scripts are excluded.
