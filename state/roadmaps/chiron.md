engine: claude
repo: /opt/recursion
sshkey: ~/.ssh/id_deploy
workdir: apps/chiron
acceptance: npm install && npm run build
automerge: yes
automerge_scope: apps/chiron

<!-- CONTRACT: apps/chiron/PRODUCT.md (why/scope). LEDGER: apps/chiron/features.json — authoritative
     for WHAT/ordering/deps; query with `node apps/chiron/features.cjs --next`. This checklist is the
     human-readable mirror; the ledger wins on ordering + deps. Build order follows deps (nav before
     the pages that embed it). C6 (real 5-series curriculum) is status=escalate — needs Lucas. -->

- [x] Scaffold a minimal Next.js Chiron shell that builds cleanly (ledger C1)
- [x] Add a landing page: hero title, one-line pitch, primary CTA to /learn (ledger C2)
- [ ] Add a shared header/nav component (links Home, /learn, /about) on every page (ledger C3)
- [ ] Add a /learn index: a responsive grid of lesson cards, each linking to its lesson page (ledger C4)
- [ ] Add a /about route with a short static description (ledger C5)
