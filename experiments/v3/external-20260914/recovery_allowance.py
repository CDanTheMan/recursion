"""Inert exact-arithmetic prototype for accepted OR-032 (v3 recovery allowance).

This module is a *candidate calculation API only*. It computes, in exact
rational arithmetic (``fractions.Fraction``), the additional recovery
allowance implied by an operator-configured fraction of pre-shutdown task
consumption, constrained by an existing remaining cap supplied by the caller.

OR-032 context (docs/v3/DECISION-REGISTER.md): the maximum additional recovery
consumption is a configured fraction of pre-shutdown task use, in tokens,
subscription quota or API spending. The register's worked example is that a
configured 10% applied to a prior 10%-of-allowance consumption permits one
additional percentage point of the *same* allowance. The fraction is not a
percentage of retained work, is not a universal default, and does not widen
any other cap.

Caller premises (documented, not enforced or interpreted here):

* Unit identity: all quantity arguments (``prior_*``, ``used_*`` and
  ``remaining_*``) must already be expressed in one homogeneous unit chosen
  by the caller (tokens, subscription-quota units, or API-spend units). This
  function never sums, mixes or converts heterogeneous tokens/quota/money.
* Allowance/window identity: "the same allowance" (quota window, billing
  period, task budget) is established by the caller. This function does not
  infer a quota reset identity, a window boundary or an allowance identity.
* Cumulative accounting: ``used`` is the cumulative consumption already
  charged against the recovery allowance across *all* prior recovery
  attempts for the task, not a fresh budget per retry. ``remaining`` is the
  caller's remaining headroom under the existing cap at call time.
* Missing telemetry is supplied by the caller as ``None`` in any position;
  the result is then ``blocked`` and this function never fabricates a
  substitute value.

Non-goals: this module never dispatches recovery, reads live quota or
telemetry, modifies reservations, selects a configured default, chooses a
product unit/store/framework, or integrates with M1 schemas or canonical
accounting. It is a reviewable, inert proposal only.
"""

from fractions import Fraction

_BLOCKED = {"status": "blocked", "reason": "unknown-accounting"}


def _quantity(num, den, name):
    """Validate one non-negative exact rational given as int (num, den)."""
    if isinstance(num, bool) or isinstance(den, bool):
        raise ValueError(name + ": bool is not an exact integer input")
    if not isinstance(num, int) or not isinstance(den, int):
        raise ValueError(name + ": numerator and denominator must be ints")
    if den <= 0:
        raise ValueError(name + ": denominator must be positive")
    if num < 0:
        raise ValueError(name + ": quantity must be non-negative")
    return Fraction(num, den)


def _pair(value):
    """Render a Fraction as a reduced {'num': int, 'den': int} pair."""
    return {"num": value.numerator, "den": value.denominator}


def calculate(
    prior_num,
    prior_den,
    fraction_num,
    fraction_den,
    used_num,
    used_den,
    remaining_num,
    remaining_den,
):
    """Compute the OR-032 recovery allowance ceiling and admissible extra.

    All inputs are explicit integer numerator/denominator pairs. ``None`` in
    any position means the caller's accounting input is unknown and returns
    ``{'status': 'blocked', 'reason': 'unknown-accounting'}`` with no numeric
    outputs. Malformed inputs (bool, float or other non-int objects, negative
    numerators, non-positive denominators, or a configured fraction above
    100%) raise ``ValueError``.

    On success returns::

        {'status': 'ok',
         'ceiling': {'num': ..., 'den': ...},
         'remaining_recovery': {'num': ..., 'den': ...},
         'admissible_extra': {'num': ..., 'den': ...}}

    where each pair is reduced and:

    * ``ceiling = prior * fraction``
    * ``remaining_recovery = max(0, ceiling - used)``
    * ``admissible_extra = min(remaining_recovery, remaining)``
    """
    args = (
        prior_num, prior_den, fraction_num, fraction_den,
        used_num, used_den, remaining_num, remaining_den,
    )
    if any(arg is None for arg in args):
        return dict(_BLOCKED)

    prior = _quantity(prior_num, prior_den, "prior")
    fraction = _quantity(fraction_num, fraction_den, "fraction")
    used = _quantity(used_num, used_den, "used")
    remaining = _quantity(remaining_num, remaining_den, "remaining")
    if fraction > 1:
        raise ValueError("fraction: configured fraction exceeds 100%")

    ceiling = prior * fraction
    remaining_recovery = max(Fraction(0), ceiling - used)
    admissible_extra = min(remaining_recovery, remaining)
    return {
        "status": "ok",
        "ceiling": _pair(ceiling),
        "remaining_recovery": _pair(remaining_recovery),
        "admissible_extra": _pair(admissible_extra),
    }
