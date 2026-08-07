schema_version: 1
id: chiron-002
workstream: chiron
goal_id: goal-chiron-learning-shell
dependencies: chiron-001
goal: Add a landing page: hero title, one-line pitch, and a primary CTA button (still builds)
engine: claude
worker_class: claude
repo: /opt/recursion
sshkey: ~/.ssh/id_deploy
acceptance: cd apps/chiron && npm install && npm run build
workdir: apps/chiron
allowed_paths: apps/chiron
non_goals: foreground learning-loop autonomy
autonomy: auto
status: resolved
planned_from: state/roadmaps/chiron.md:10

Add a landing page: hero title, one-line pitch, and a primary CTA button (still builds)

(Auto-planned from the chiron roadmap. Fix the IMPLEMENTATION, not the test/fixtures. The gate
is the acceptance command above; keep every currently-passing check green.)
