engine: claude
repo: /opt/recursion
sshkey: ~/.ssh/id_deploy
workdir: apps/chiron
acceptance: npm install && npm run build
automerge: yes
automerge_scope: apps/chiron

- [x] Scaffold a minimal Next.js Chiron shell that builds cleanly
- [~] Add a landing page: hero title, one-line pitch, and a primary CTA button (still builds)
- [ ] Add a /learn route with a static list of 3 placeholder lesson cards (still builds)
- [ ] Add a shared header/nav component linking Home and /learn (still builds)
- [ ] Add a /about route with a short static description (still builds)
