id: chiron-003
workstream: chiron
goal: Add a landing page: hero title, one-line pitch, and a primary CTA button (still builds)
engine: claude
repo: /opt/recursion
sshkey: ~/.ssh/id_deploy
acceptance: npm install && npm run build
workdir: apps/chiron
autonomy: auto
status: passed
planned_from: state/roadmaps/chiron.md:10

Add a landing page: hero title, one-line pitch, and a primary CTA button (still builds)

(Auto-planned from the chiron roadmap. Fix the IMPLEMENTATION, not the test/fixtures. The gate
is the acceptance command above; keep every currently-passing check green.)
