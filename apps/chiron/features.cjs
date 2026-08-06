#!/usr/bin/env node
'use strict';
// features.cjs — query + VALIDATE the Chiron feature ledger (features.json) for the Recursion
// autonomous loop. PRODUCT.md is authoritative for scope/why; features.json for what to build next.
// This is the interface the loop reads — never hand-parse the JSON.
//
//   node features.cjs                 # human table of all slices
//   node features.cjs --buildable     # slices the loop MAY build now (open AND every dep done)
//   node features.cjs --next          # the SINGLE next buildable slice (array order) — planner input
//   node features.cjs --escalate      # slices that need Lucas (status=escalate) — never auto-built
//   node features.cjs --status=open   # filter by status
//   node features.cjs --json          # emit the (filtered) set as JSON, `buildable` derived
//   node features.cjs --validate      # validate only; exit 0 if clean, 3 if malformed
//
// A slice is BUILDABLE iff status==='open' AND every dep is 'done'. That is the whole point of the
// ledger: the planner never re-queues a done slice (the duplicate-landing-page bug) and never bases a
// slice on an unmerged dep (the base-branch failure). Exit: 0 ok · 2 usage · 3 malformed (a
// silence-breaker — a typo'd status, a missing field, or a dangling/cyclic dep FAILS loudly).
const fs = require('fs');
const path = require('path');

const STATUSES = new Set(['done', 'open', 'blocked', 'escalate']);
const REQUIRED = ['id', 'slice', 'status', 'deps'];

function die(code, msg) { process.stderr.write(msg + '\n'); process.exit(code); }

const REG_PATH = path.join(__dirname, 'features.json');
let reg;
try { reg = JSON.parse(fs.readFileSync(REG_PATH, 'utf8')); }
catch (e) { die(3, 'features: cannot read/parse ' + REG_PATH + ': ' + e.message); }

// ---- validate (silence-breaker): a malformed ledger must throw, not queue the wrong slice ----
function validate(r) {
  const errs = [];
  if (!Array.isArray(r.features)) { errs.push('features: missing "features" array'); return errs; }
  const ids = new Set(r.features.map((f) => f && f.id).filter(Boolean));
  const seen = new Set();
  for (const f of r.features) {
    const id = f && f.id ? f.id : '(no id)';
    for (const k of REQUIRED) if (f[k] === undefined || f[k] === null || f[k] === '')
      errs.push(id + ': missing required field "' + k + '"');
    if (f.status && !STATUSES.has(f.status))
      errs.push(id + ': unknown status "' + f.status + '" (allowed: ' + [...STATUSES].join(', ') + ')');
    if (seen.has(f.id)) errs.push(f.id + ': duplicate id');
    seen.add(f.id);
    if (Array.isArray(f.deps)) {
      for (const d of f.deps) {
        if (!ids.has(d)) errs.push(id + ': dep "' + d + '" is not a known slice id');
        if (d === f.id) errs.push(id + ': depends on itself');
      }
    }
    // an open slice the loop could build MUST carry a machine-checkable acceptance
    if (f.status === 'open' && !f.acceptance)
      errs.push(id + ': status open but no acceptance command — the loop cannot verify it');
    // an escalate slice must say WHY (so the escalation is actionable)
    if (f.status === 'escalate' && !f.escalate)
      errs.push(id + ': status escalate but no "escalate" reason — an escalation must be actionable');
  }
  // detect dependency cycles (a cycle would deadlock the planner)
  const byId = new Map(r.features.map((f) => [f.id, f]));
  const state = new Map(); // 0=visiting, 1=done
  const walk = (id, stack) => {
    if (state.get(id) === 1) return;
    if (state.get(id) === 0) { errs.push('dependency cycle: ' + stack.concat(id).join(' -> ')); return; }
    state.set(id, 0);
    const f = byId.get(id);
    for (const d of (f && Array.isArray(f.deps) ? f.deps : [])) if (byId.has(d)) walk(d, stack.concat(id));
    state.set(id, 1);
  };
  for (const f of r.features) if (f.id) walk(f.id, []);
  return errs;
}

const errs = validate(reg);
if (errs.length) die(3, 'features: ledger INVALID:\n  - ' + errs.join('\n  - '));

// ---- decorate with derived buildability ----
const doneIds = new Set(reg.features.filter((f) => f.status === 'done').map((f) => f.id));
const isBuildable = (f) => f.status === 'open' && (f.deps || []).every((d) => doneIds.has(d));
const features = reg.features.map((f) => ({ ...f, buildable: isBuildable(f) }));

// ---- filters ----
const args = process.argv.slice(2);
const flag = (f) => args.includes(f);
const opt = (k) => { const h = args.find((a) => a.startsWith('--' + k + '=')); return h ? h.slice(k.length + 3) : null; };

if (flag('--validate')) { process.stdout.write('features: ledger OK (' + features.length + ' slices)\n'); process.exit(0); }

// --next: the single next buildable slice in array order (the planner's pick)
if (flag('--next')) {
  const n = features.find((f) => f.buildable);
  if (!n) { process.stdout.write('(no buildable slice — queue not refilled; all done, or the next slice is blocked/escalate)\n'); process.exit(0); }
  process.stdout.write(JSON.stringify(n, null, 2) + '\n'); process.exit(0);
}

let out = features;
if (flag('--buildable') || flag('--queueable')) out = out.filter((f) => f.buildable);
if (flag('--escalate')) out = out.filter((f) => f.status === 'escalate');
const status = opt('status'); if (status) out = out.filter((f) => f.status === status);

if (flag('--json')) { process.stdout.write(JSON.stringify(out, null, 2) + '\n'); process.exit(0); }

// ---- human table ----
if (!out.length) { process.stdout.write('(no slices match)\n'); process.exit(0); }
const pad = (s, n) => String(s === null || s === undefined ? '' : s).padEnd(n).slice(0, n);
process.stdout.write(pad('ID', 5) + pad('STATUS', 10) + pad('BUILD', 7) + pad('DEPS', 14) + 'SLICE\n');
process.stdout.write('-'.repeat(96) + '\n');
for (const f of out) {
  process.stdout.write(
    pad(f.id, 5) + pad(f.status, 10) + pad(f.buildable ? 'yes' : '-', 7) +
    pad((f.deps || []).join(',') || '-', 14) + f.slice + '\n');
}
const b = features.filter((f) => f.buildable).length;
const e = features.filter((f) => f.status === 'escalate').length;
const d = features.filter((f) => f.status === 'done').length;
process.stdout.write('\n' + features.length + ' slices · ' + d + ' done · ' + b + ' buildable now · ' + e + ' escalate (need Lucas)\n');
