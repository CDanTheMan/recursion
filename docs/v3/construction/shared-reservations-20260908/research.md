# Research assumptions — 2026-09-08

Read-only independent method packet: reservation_method_research; at most20 minutes,
no writes or nested delegation. Sole writer/integrator records its source findings.

[Balegas et al., Extending Eventually Consistent Cloud Databases for Enforcing Numeric Invariants](https://arxiv.org/html/1503.09052), sections II-A, III-B and IV-D/E,
assumes persistent memory survives recovery and per-replica mutations serialize.
Conservative stale incoming information can reduce availability; restoring an
owner's old debit/spend state is not safe under that result. SC-WR-01 constructs
one durable debit/application relation and states those persistence premises.

[AWS, Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
motivates atomic identity/mutation recording and rejection of reused identity with
a different intent. SC-WR-01 binds fixed request tuples and retains terminal
request tombstones; it does not infer an exactly-once provider from local dedup.

[RIFL](https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf), sections3–4,
requires durable completion records associated with effects, retry rendezvous and
safe record retirement. This campaign deliberately retains unknown after receipt
loss and blocks blind send; relocation and record retirement remain residuals.

These sources motivate hypotheses and counterexamples, not proof of this model.
Independent finite obligations require free+in-flight+reserved+consumed=10 and
reserved+consumed<=10. Confirmed consumption never replenishes cumulative budget.
Local worker spend, provider windows, pins, literal classification and replay are
separate accounting/ownership domains. Rights(5,5) can deny while central admits;
that availability difference is a required result, not an equivalence failure.

One transfer's duplicate-credit mutant detects conservation failure but cannot
establish the two-opposite-transfer12-unit admission witness. The mandatory central
6+6-from10 schedule remains intact and supplies the oversubscription control.
