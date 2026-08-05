id: chiron-001
workstream: chiron
goal: Scaffold a minimal Next.js Chiron learning-app shell that builds cleanly
engine: claude
acceptance: npm install && npm run build
workdir: apps/chiron
autonomy: auto
status: queued

Build a MINIMAL but real Next.js 14 application (App Router, TypeScript) in the directory
apps/chiron. This is the shell for Chiron, Lucas's physics learning engine (see
recursion/docs/chiron-design.md) — the canvas-first tutor UI comes later; this task only
needs to stand up a clean, buildable foundation that a later task can grow into.

Requirements:
- package.json with next (^14), react (^18), react-dom (^18), typescript, @types/react,
  @types/node, and a "build" script set to "next build". Use versions that resolve on npm
  and build cleanly with no experimental flags.
- app/layout.tsx and app/page.tsx (App Router). The landing page renders "Chiron" as a
  heading and a one-line tagline ("Get ahead of the 5-series."). Plain React/JSX, no
  external UI/CSS libraries.
- tsconfig.json (strict), next.config.mjs, and a Next.js-appropriate .gitignore
  (node_modules, .next, out).
- No experimental/canary features. Standard server build only.
- Do NOT install packages or run any build yourself — write files only. A separate verifier
  runs: npm install && npm run build.

Correct-and-minimal beats feature-rich-and-broken. The single success criterion is that
`npm install && npm run build` exits 0.
