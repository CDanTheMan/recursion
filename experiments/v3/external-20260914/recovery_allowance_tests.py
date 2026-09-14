"""Deterministic unit tests for the inert OR-032 recovery-allowance prototype.

Gate: python3 -B experiments/v3/external-20260914/recovery_allowance_tests.py
Exits zero and prints V3_RECOVERY_ALLOWANCE_PASS only if every named test
passes. A failing test is a reported result, not a pass. This file is a
reviewable proposal: it makes no timing/performance claim and does not
integrate with M1 schemas or canonical accounting.
"""

import math
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recovery_allowance import calculate


def _frac(pair):
    return Fraction(pair["num"], pair["den"])


def _check_pair(pair):
    assert set(pair) == {"num", "den"}, pair
    assert type(pair["num"]) is int and type(pair["den"]) is int, pair
    assert pair["den"] > 0 and pair["num"] >= 0, pair
    assert math.gcd(pair["num"], pair["den"]) == 1, pair


def _expect_value_error(*args):
    try:
        calculate(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError for %r" % (args,))


def test_percentage_point_ceiling():
    # OR-032 worked example: 10% of a prior 10%-of-allowance consumption is
    # one additional percentage point of the same allowance.
    result = calculate(1, 10, 1, 10, 0, 1, 1, 1)
    assert result["status"] == "ok"
    assert result["ceiling"] == {"num": 1, "den": 100}
    assert result["remaining_recovery"] == {"num": 1, "den": 100}
    assert result["admissible_extra"] == {"num": 1, "den": 100}


def test_remaining_and_admissible_tokens():
    # prior=100 tokens, fraction=1/10, used=3, other_cap=50 -> 10/7/7.
    result = calculate(100, 1, 1, 10, 3, 1, 50, 1)
    assert result["status"] == "ok"
    assert result["ceiling"] == {"num": 10, "den": 1}
    assert result["remaining_recovery"] == {"num": 7, "den": 1}
    assert result["admissible_extra"] == {"num": 7, "den": 1}


def test_admissible_bounded_by_other_cap():
    # Same as above but other_cap=5 -> remaining still 7, admissible 5.
    result = calculate(100, 1, 1, 10, 3, 1, 5, 1)
    assert result["remaining_recovery"] == {"num": 7, "den": 1}
    assert result["admissible_extra"] == {"num": 5, "den": 1}


def test_second_retry_cumulative_used():
    # used is cumulative across retries: used=7 -> remaining=3.
    result = calculate(100, 1, 1, 10, 7, 1, 50, 1)
    assert result["ceiling"] == {"num": 10, "den": 1}
    assert result["remaining_recovery"] == {"num": 3, "den": 1}
    assert result["admissible_extra"] == {"num": 3, "den": 1}


def test_used_over_ceiling_is_zero():
    # used=11 against ceiling=10 -> remaining/admissible clamp to zero.
    result = calculate(100, 1, 1, 10, 11, 1, 50, 1)
    assert result["remaining_recovery"] == {"num": 0, "den": 1}
    assert result["admissible_extra"] == {"num": 0, "den": 1}


def test_zero_fraction():
    result = calculate(100, 1, 0, 1, 0, 1, 50, 1)
    assert result["status"] == "ok"
    for key in ("ceiling", "remaining_recovery", "admissible_extra"):
        assert result[key] == {"num": 0, "den": 1}, result


def test_zero_prior():
    result = calculate(0, 1, 1, 10, 0, 1, 50, 1)
    assert result["status"] == "ok"
    for key in ("ceiling", "remaining_recovery", "admissible_extra"):
        assert result[key] == {"num": 0, "den": 1}, result


def test_unknown_inputs_blocked():
    expected = {"status": "blocked", "reason": "unknown-accounting"}
    base = [100, 1, 1, 10, 3, 1, 50, 1]
    for index in range(8):
        args = list(base)
        args[index] = None
        result = calculate(*args)
        assert result == expected, (index, result)


def test_malformed_inputs_raise():
    ok = (100, 1, 1, 10, 3, 1, 50, 1)
    _expect_value_error(True, 1, 1, 10, 3, 1, 50, 1)      # bool num
    _expect_value_error(100, True, 1, 10, 3, 1, 50, 1)    # bool den
    _expect_value_error(100.0, 1, 1, 10, 3, 1, 50, 1)     # float num
    _expect_value_error(100, 1.0, 1, 10, 3, 1, 50, 1)     # float den
    _expect_value_error(0.1, 1, 1, 10, 3, 1, 50, 1)       # float value
    _expect_value_error(Fraction(1, 2), 1, 1, 10, 3, 1, 50, 1)  # non-int
    _expect_value_error("100", 1, 1, 10, 3, 1, 50, 1)     # string num
    _expect_value_error(-1, 1, 1, 10, 3, 1, 50, 1)        # negative quantity
    _expect_value_error(100, 1, 1, 10, -3, 1, 50, 1)      # negative used
    _expect_value_error(100, 1, 1, 10, 3, 1, -50, 1)      # negative cap
    _expect_value_error(100, 0, 1, 10, 3, 1, 50, 1)       # zero denominator
    _expect_value_error(100, -3, 1, 10, 3, 1, 50, 1)      # negative den
    _expect_value_error(100, 1, 11, 10, 3, 1, 50, 1)      # fraction > 100%
    _expect_value_error(100, 1, 2, 1, 3, 1, 50, 1)        # fraction 200%
    calculate(*ok)  # baseline sanity: the valid tuple still computes


def test_large_integers_exact():
    # Beyond 2**53 a float implementation silently rounds; exact pairs must
    # preserve the odd numerator.
    prior_num = 2**53 + 1
    result = calculate(prior_num, 1, 1, 2, 1, 1, 2**60, 1)
    assert result["ceiling"] == {"num": prior_num, "den": 2}
    assert result["remaining_recovery"] == {"num": prior_num - 2, "den": 2}
    assert result["admissible_extra"] == {"num": prior_num - 2, "den": 2}
    big = 2**70 + 3
    used = big // 100
    result = calculate(big, 7, 3, 11, used, 1, 2**80, 1)
    expected_ceiling = Fraction(big, 7) * Fraction(3, 11)
    assert _frac(result["ceiling"]) == expected_ceiling
    assert _frac(result["remaining_recovery"]) == expected_ceiling - used
    assert _frac(result["admissible_extra"]) == expected_ceiling - used


def test_enumeration_monotonic_and_caps():
    # Deterministic enumeration of <=1000 valid rational tuples.
    priors = [Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(7, 10),
              Fraction(100)]
    fractions_ = [Fraction(0), Fraction(1, 10), Fraction(1, 3), Fraction(1, 2),
                  Fraction(1)]
    caps = [Fraction(0), Fraction(1, 4), Fraction(5), Fraction(50)]
    useds = [Fraction(0), Fraction(1, 10), Fraction(1, 2), Fraction(1),
             Fraction(3), Fraction(7), Fraction(11), Fraction(100)]
    count = 0
    for prior in priors:
        for fraction in fractions_:
            for cap in caps:
                prev_remaining = None
                prev_admissible = None
                for used in useds:  # non-decreasing used sequence
                    count += 1
                    assert count <= 1000
                    result = calculate(
                        prior.numerator, prior.denominator,
                        fraction.numerator, fraction.denominator,
                        used.numerator, used.denominator,
                        cap.numerator, cap.denominator,
                    )
                    assert result["status"] == "ok"
                    for key in ("ceiling", "remaining_recovery",
                                "admissible_extra"):
                        _check_pair(result[key])
                    ceiling = _frac(result["ceiling"])
                    remaining = _frac(result["remaining_recovery"])
                    admissible = _frac(result["admissible_extra"])
                    assert ceiling == prior * fraction
                    assert remaining == max(Fraction(0), ceiling - used)
                    # hard-cap preservation
                    assert admissible <= cap
                    assert admissible <= remaining
                    assert admissible == min(remaining, cap)
                    # monotonicity as used increases
                    if prev_remaining is not None:
                        assert remaining <= prev_remaining
                        assert admissible <= prev_admissible
                    prev_remaining = remaining
                    prev_admissible = admissible
    assert count == 800


TESTS = [
    ("percentage_point_ceiling", test_percentage_point_ceiling),
    ("remaining_and_admissible_tokens", test_remaining_and_admissible_tokens),
    ("admissible_bounded_by_other_cap", test_admissible_bounded_by_other_cap),
    ("second_retry_cumulative_used", test_second_retry_cumulative_used),
    ("used_over_ceiling_is_zero", test_used_over_ceiling_is_zero),
    ("zero_fraction", test_zero_fraction),
    ("zero_prior", test_zero_prior),
    ("unknown_inputs_blocked", test_unknown_inputs_blocked),
    ("malformed_inputs_raise", test_malformed_inputs_raise),
    ("large_integers_exact", test_large_integers_exact),
    ("enumeration_monotonic_and_caps", test_enumeration_monotonic_and_caps),
]


def main():
    failures = 0
    for name, fn in TESTS:
        try:
            fn()
        except Exception as exc:
            failures += 1
            print("FAIL %s: %r" % (name, exc))
        else:
            print("PASS %s" % name)
    print("named-tests=%d failures=%d" % (len(TESTS), failures))
    if failures:
        return 1
    print("V3_RECOVERY_ALLOWANCE_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
