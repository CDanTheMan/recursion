# SC-EPOCH-03 research — 2026-09-08

Primary repository sources in manifest.json: [executive contracts](../../EXECUTIVES.md),
[interaction surfaces](../../INTERACTION-SURFACES.md), [M1A wire profile](../../M1A-WIRE-PROFILE.md),
[planning contract](../../M1A-AUTONOMOUS-PLANNING.md), original formal-boundaries and
comparison-contract, frozen interface consultation vectors and M1A validation/kernel.
M1A binds exact goal ObjectRef and LeaseRef, allows only Owner GoalSpec amendment,
and refuses stale authority. Consultation is a proposed application envelope absent
its closed event union; no literal consultation arm is invented.

Independent read-only research identified the actual resource wait cycle through the
executor, historical adoption versus current permission, and evidence received before
alias expiry versus data dropped before receipt. The Erlang primary documentation
[process aliases](https://www.erlang.org/doc/system/ref_man_processes.html#process-aliases)
was checked on2026-09-08: deactivated aliases prevent later mailbox delivery while
already delivered messages remain. This is supporting mechanism research only, not
an Erlang selection, installed-runtime test or proof of Recursion cancellation.

An early constructed model shared a flaw across both reducers and the third relation:
Stop could assign an already-current generation. Independent challenge supplied the
concrete expiry/request/Stop sequence. Explicit alias retirement resolves it without
inventing a third generation or conflating cancellation with remote settlement.
