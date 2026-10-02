#!/usr/bin/env python3
"""Bounded trace bridge for the FU-03 reference oracle.

Given a finite trace (ordered events plus observed states/projections, or explicit command
admissions with an expected refusal), this checker replays every step against ``RefState`` and
reports the **first divergence index**.  It is a bounded consistency check of one finite observed
behaviour against the declared abstraction, not a refinement proof and not a live reducer.

Trace schema (language-neutral JSON)::

    {
      "trace_id": "example",
      "initial_log": [ <stored event map>, ... ],      # optional, default []
      "steps": [
        { "events": [ <stored event map>, ... ],        # optional
          "command": { "kind": 8, ... },                # optional admission step
          "expect": { "result": "fresh" | "cached" |
                      "refused", "code": 10, "detail": 21, "path": [9] },
          "observed_state_digest": "<64 hex>",          # optional
          "observed_projection": [ ... ] },             # optional
        ...
      ]
    }

Verdicts follow ds-FU-03 section 12: ``VALID_BOUNDED``, ``INVALID_TRACE``, ``OUT_OF_SCOPE`` and
``INCONCLUSIVE``.  The report always states what the bounded check proves and does **not** prove.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import refstate as R

PROVES = (
    "each observed step is consistent with a single deterministic fold of the supplied events",
    "all supplied event digests, ordinals, predecessor links, command bindings and semantic "
    "preconditions hold within MaxCommittedEvents=20",
    "each declared refusal matches the reference admission ordering and refusal taxonomy",
    "the first observed/expected mismatch, if any, is identified by index",
)

DOES_NOT_PROVE = (
    "quantification over all executions, fairness/liveness or a machine-checked refinement map",
    "that the implementation produced these events or that the observations are faithful",
    "external effect truth, durable storage, OS containment or provider behaviour",
    "that the reference equations themselves are correct (independently authored, not proven)",
    "any behaviour beyond the finite declared bounds (one aggregate/task, <=20 events, leases<=3)",
)


@dataclass
class TraceReport:
    verdict: str
    first_divergence_index: Optional[int] = None
    reason: str = ""
    steps_checked: int = 0
    detail: dict = field(default_factory=dict)
    proves: tuple = PROVES
    does_not_prove: tuple = DOES_NOT_PROVE

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "first_divergence_index": self.first_divergence_index,
            "reason": self.reason,
            "steps_checked": self.steps_checked,
            "detail": self.detail,
            "proves": list(self.proves),
            "does_not_prove": list(self.does_not_prove),
        }


def _refusal_dict(refusal: R.Refusal) -> dict:
    return refusal.to_dict()


def check_trace(trace: dict) -> TraceReport:
    """Replay a finite trace against the reference oracle.  Never raises for bad input."""
    try:
        log = list(trace.get("initial_log") or [])
        steps = list(trace.get("steps") or [])
    except AttributeError:
        return TraceReport("INCONCLUSIVE", None, "trace is not a mapping")

    initial = R.validate_log(log)
    if not initial.valid:
        return TraceReport("INVALID_TRACE", None, "initial_log invalid", 0, initial.to_dict())
    state = R.RefState(log)
    checked = 0

    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            return TraceReport("INCONCLUSIVE", index, "step is not a mapping", checked)

        # Admission-only step: build the command and check the declared outcome.
        if "command" in step:
            spec = step["command"]
            command = R.command_from_spec(state, spec)
            admission = R.admit(state, command)
            expect = step.get("expect")
            if expect is not None:
                want = expect.get("result")
                if admission.outcome != want:
                    return TraceReport(
                        "INVALID_TRACE", index,
                        f"admission outcome {admission.outcome!r} != expected {want!r}",
                        checked, {"observed": admission.outcome, "expected": want})
                if want == "refused":
                    refusal = admission.refusal
                    if refusal is None or refusal.code != expect.get("code") or \
                            refusal.detail != expect.get("detail"):
                        observed = _refusal_dict(refusal) if refusal else None
                        return TraceReport(
                            "INVALID_TRACE", index,
                            "refusal tuple differs", checked, {"observed": observed,
                                                               "expected": expect})
                    if "path" in expect and refusal.path != expect["path"]:
                        return TraceReport(
                            "INVALID_TRACE", index, "refusal path differs", checked,
                            {"observed": refusal.path, "expected": expect["path"]})
            if admission.outcome == "fresh":
                log = log + list(admission.batch.events)
                state = admission.batch.post_state
            # cached and refused leave the canonical log and state unchanged

        # Event step: append the supplied stored events and revalidate the whole prefix.
        if "events" in step:
            incoming = list(step.get("events") or [])
            log = log + incoming
            if len(log) > R.MAX_COMMITTED_EVENTS:
                return TraceReport("OUT_OF_SCOPE", index,
                                   "committed event count exceeds MaxCommittedEvents=20", checked)
            result = R.validate_log(log)
            if not result.valid:
                return TraceReport("INVALID_TRACE", index, "invalid committed prefix",
                                   checked, result.to_dict())
            state = R.RefState(log)

        # Observed digest binding.
        observed_digest = step.get("observed_state_digest")
        if observed_digest:
            computed = R.state_digest_hex(state)
            if computed != observed_digest:
                return TraceReport(
                    "INVALID_TRACE", index, "observed state digest differs", checked + 1,
                    {"observed": observed_digest, "computed": computed})

        # Observed projection binding.
        observed_projection = step.get("observed_projection")
        if observed_projection is not None:
            computed_projection = R.projection_json(state)
            if computed_projection != list(observed_projection):
                return TraceReport(
                    "INVALID_TRACE", index, "observed projection differs", checked + 1,
                    {"observed": list(observed_projection), "computed": computed_projection})

        checked += 1

    return TraceReport("VALID_BOUNDED", None, "all steps consistent", checked)


def main(argv: list[str]) -> int:
    import json
    import sys
    from pathlib import Path

    if len(argv) != 2:
        print("usage: python trace_checker.py <trace.json>", file=sys.stderr)
        return 2
    trace = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    report = check_trace(trace)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.verdict == "VALID_BOUNDED" else 1


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv))
