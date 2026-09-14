"""Exact-candidate acceptance gate for the inert recovery-ledger experiment."""

import argparse
import hashlib
import json
import os
import pathlib
import re
import runpy
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[3]
BASE = "0c908f6833e715af0eaa01b6f6788120eb577efd"
FROZEN_EXPECTATIONS_COMMIT = "1d9fbbf277372b455ea904c7b2800c0f84f74785"
BRANCH = "codex/v3-recovery-reservation-ledger-20260914"
CODE = "experiments/v3/recovery-ledger-20260914/"
DOCS = "docs/v3/construction/recovery-ledger-20260914/"
ALLOWED = {
    CODE + "ledger.py",
    CODE + "test_ledger.py",
    CODE + "check.py",
    DOCS + "SPEC.md",
    DOCS + "PROGRESS.md",
}
SOURCE_SHA256 = {
    "CONTROL_PLANE.md": "cb82c4a8b2ae7c80fb4b9556a4db681faedaf48b08e4b562e1491e198a5ef0b3",
    "ANCHOR.md": "b76b08c41f0a0f25f13ffbe9bf4f07b8d7eeda2ebd576e9ba392ab63308a102e",
    "AGENTS.md": "5483f312fe0fd8f7a3c8a1492098ed58dd15f376e1043f90b54ddd420d5ee0a4",
    "docs/v3/START-HERE.md": "f95c4718f42fb87daba71e9431cd38a117c268a8a9c9ccaec0a61481407addaf",
    "docs/v3/PRODUCT.md": "63c5f5e6ee79213622cac12e6ffac10cfca89d817e6c49b468102d12680e4215",
    "docs/v3/DECISION-REGISTER.md": "3344cbd8aa603753d9f71f596a7ab773dba5201cec7ee41e9671e3331d08221f",
    "docs/v3/ARCHITECTURE.md": "0f151d2f6d2dc8e6b8b1474f4b10333f96c75d7dbf09240db7d9db2809723ebe",
    "docs/v3/STATE.md": "cdba55654515a39c09d900d757b1d5460b3be1e3be8f7af0bd571198279171b4",
    "docs/v3/construction/next-work-20260914/COMMON.md": "09384534df1bc7d04e868969add212a1d0d146f3d4f58614175e7d6dd94a6778",
    "docs/v3/construction/next-work-20260914/03-sol-recovery-ledger.md": "4bfcf8f4aed37523bcfd5eebe40a05ee1b0394b489d0ece35eb28505d5ef66af",
    "experiments/v3/external-20260914/recovery_allowance.py": "b78135caf89d82f66cd6bbd0a95cd3e8351968d69e117c3d673cb3f2ea2b65f9",
    "experiments/v3/external-20260914/recovery_allowance_tests.py": "535f6b523fe6f27e66ddfd15ca5bc8d3d944dc65986ba419fa2a560a6c45eacf",
    "docs/v3/construction/external-rdt-20260914/reviews/recovery-allowance.json": "c64c70f42614caf4d0ecf5fa0230915e69e0de43ec923561824e804126ee327a",
}
REQUIRED_CASES = (
    "literal-prefix-audit",
    "positive-reserve-partial-settlement",
    "competing-reservations",
    "unknown-effect-serialize-reopen",
    "duplicate-settlement-charges-once",
    "conflicting-duplicate-refuses",
    "cumulative-retries-cap",
    "provider-reset-daemon-restart",
    "recovery-cost-not-normal-use",
    "verified-additional-normal-work",
    "unknown-baseline-window-blocks",
    "invalid-integers-fraction-quantum",
    "componentwise-parent-pool-resource",
    "unlike-units-never-combine",
    "observation-without-admission",
)
REQUIRED_MUTATIONS = (
    "erase-R-on-restart",
    "erase-C-on-provider-reset",
    "charge-duplicate-settlement",
    "ceil-instead-of-floor",
    "count-recovery-as-normal-use",
    "mix-unlike-units",
)

# Digests of each literal signature in the first-slice prefix table.  Recomputed
# projections must match each digest; changing expected data to follow the reducer also
# fails because the literal table itself is checked against the same independent list.
PREFIX_DIGESTS = {
    "floor-non-integral/1": "164fa01d629a44eeb1d1d182844076f6346c20a8df7cb68d26372dc156bc6331",
    "reserve-partial-settle/1": "96110e1d52df188d5cdedb75b78e67635f88e7d43f6b2dcf7a4f1ac4f66e1e1e",
    "reserve-partial-settle/2": "6cce82dac4a562e89a00dad09dc4df291ccfad86d63717d166108a955703472a",
    "reserve-partial-settle/3": "41b346b9c61c44435b946fdfcbb33b2d4c5b2e14f7436fb9e48d363f9ca7d7af",
    "unknown-reset-restart/1": "2953d03a1ca5de8d7fee794c1e4842e3432e027687f5b2b707e43b9c92a2124e",
    "unknown-reset-restart/2": "fbe1c5b7b08269a1203b20b222810e9c0fcdff3447ca6ed450b8ec2483aef938",
    "unknown-reset-restart/3": "ba940a0c91b2a8b56128c734e76b15980e2995276858a8ce039ffe08d002dc55",
    "unknown-reset-restart/4": "ba940a0c91b2a8b56128c734e76b15980e2995276858a8ce039ffe08d002dc55",
    "unknown-reset-restart/5": "ba940a0c91b2a8b56128c734e76b15980e2995276858a8ce039ffe08d002dc55",
    "verified-normal-successor/1": "6f6adc347a53e88850920eb3f6e2146adad45a09f52741221061d53b600c7208",
    "verified-normal-successor/2": "885a536fa411f0f43dfda39aed7cff724005446d36ace1f0216961d5f95787dd",
    "verified-normal-successor/3": "5c3f91fd312a85593839c463312e7cf939c031ff55d8484834ef7c5f9511108d",
    "componentwise-limits/1": "495f2b2ca4845d1ba5e8719fd0aa309f48fed71c67f6567cd8a44766d4ef286f",
    "componentwise-limits/2": "4abcbac1bf1bc4f739c3d5d6cc0564e2488261d245795327c8f56ab66c155127",
    "componentwise-limits/3": "6efec0e84d74975a4279a5858e53a035faa1619c14e2dfb8c7c6042610706fdd",
    "componentwise-limits/4": "1fd61ad44c8f525276ac3ca6e1df78cebe9bfadbd1ec4ccb370f24e9b09e1bb3",
    "componentwise-limits/5": "24d9d11cb87df26fd219c9869bb4bbdd60c2babafc024529b27754e5fcd829f9",
    "unlike-units-distinct/1": "d7e1c61b2a2b099dc831b2718b9816ee235fab3beb0dd41c75bb0f3797d1b1b4",
    "unlike-units-distinct/2": "04e0c76dbdd2dccd4692f2b3cf821df7414d70f1f747743d5a3dd29ca8bb0670",
    "unlike-units-distinct/3": "520a6d4de7aacc2082bd91abb5d730d0c6f0fc1dbf3a2321130c2f6779ad2516",
    "unlike-units-distinct/4": "9f23ebc2cf07b27231e2d59d45af0a5aa2fac58a49f446966f61c9d1aeaaf236",
}


class GateFailure(Exception):
    pass


def require(condition, message):
    if not condition:
        raise GateFailure(message)


def git(*args, raw=False):
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise GateFailure(
            "git " + " ".join(args) + " failed: " + result.stderr.decode("utf-8", "replace")
        )
    return result.stdout if raw else result.stdout.decode("utf-8").strip()


def digest(value):
    if not isinstance(value, (bytes, bytearray)):
        value = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def candidate_checks(candidate):
    require(re.fullmatch(r"[0-9a-f]{40}", candidate) is not None, "candidate must be a full lowercase SHA")
    require(git("cat-file", "-t", candidate) == "commit", "candidate is not a commit")
    require(git("rev-parse", "HEAD") == candidate, "candidate differs from checked-out HEAD")
    require(git("branch", "--show-current") == BRANCH, "wrong task branch")
    require(not git("status", "--porcelain=v1"), "candidate checkout is not clean")
    git("merge-base", "--is-ancestor", BASE, candidate)
    git("merge-base", "--is-ancestor", FROZEN_EXPECTATIONS_COMMIT, candidate)
    changed = set(git("diff", "--name-only", BASE, candidate).splitlines())
    require(changed == ALLOWED, "changed-path inventory differs from packet scope: " + repr(sorted(changed)))
    require(not git("diff", "--name-only", "--diff-filter=D", BASE, candidate), "baseline path deleted")
    require(not git("diff", "--check", BASE, candidate), "git diff --check failed")
    total = sum((ROOT / path).stat().st_size for path in ALLOWED)
    require(total <= 32 * 1024 * 1024, "artifact budget exceeds 32 MiB")
    return total


def source_preservation(candidate):
    for path, expected in SOURCE_SHA256.items():
        base_raw = git("show", BASE + ":" + path, raw=True)
        candidate_raw = git("show", candidate + ":" + path, raw=True)
        require(digest(base_raw) == expected, "TASK_BASE input digest changed or gate binding is wrong: " + path)
        require(candidate_raw == base_raw, "candidate changed preserved source: " + path)


def load_tests():
    module = runpy.run_path(str(ROOT / (CODE + "test_ledger.py")))
    require(tuple(module["REQUIRED_CASES"]) == REQUIRED_CASES, "required case inventory changed")
    require(tuple(module["TEST_METHOD_TO_CASE"].values()) == REQUIRED_CASES, "test-to-case mapping changed")
    require(tuple(module["MUTATION_NAMES"]) == REQUIRED_MUTATIONS, "mutation inventory changed")
    require(tuple(module["MUTANT_CLASSES"]) == REQUIRED_MUTATIONS, "behavioral mutant inventory changed")
    require(module["PREFIX_COUNT"] == 21, "selected prefix count changed")
    require(len(module["PREFIX_CASES"]) == 6, "selected sequence inventory changed")
    require(len(module["DECLARED_SEQUENCES"]) == 6, "selected sequence inventory changed")
    require(module["DECLARED_SEQUENCE_LIMIT"] == 256 <= 1024, "sequence budget exceeded")
    require(module["MAX_SEQUENCE_EVENTS"] == 32, "event budget changed")
    return module


def prefix_audit(module):
    observed = {}
    literal = {}
    for name, case in module["PREFIX_CASES"].items():
        require(len(case["events"]) == len(case["expected"]), "prefix expected inventory mismatch")
        for end, expected in enumerate(case["expected"], 1):
            key = name + "/" + str(end)
            literal[key] = digest(expected)
            state = module["replay"](case["events"][:end])
            actual = module["selected_signature"](state, case["boundaries"], case["caps"])
            observed[key] = digest(actual)
    require(literal == PREFIX_DIGESTS, "frozen literal prefix outcomes changed")
    require(observed == PREFIX_DIGESTS, "independent replay prefix audit failed")
    return len(observed)


def independent_mutations(module):
    Base = module["Ledger"]

    class EraseR(Base):
        def _apply_restart(self, event):
            result = super()._apply_restart(event)
            for account in self._accounts.values():
                account["R"] = 0
            return result

    class EraseC(Base):
        def _apply_reset(self, event):
            result = super()._apply_reset(event)
            account = self._accounts[self._boundaries[event["boundary_id"]]["account_key"]]
            account["C"] = 0
            return result

    class DuplicateCharge(Base):
        def _apply_settlement(self, event):
            result = super()._apply_settlement(event)
            if result == "duplicate":
                reservation = self._reservations[event["reservation_id"]]
                account = self._accounts[
                    self._boundaries[reservation["boundary_id"]]["account_key"]
                ]
                account["C"] += event["actual"]
            return result

    class Ceil(Base):
        def _apply_boundary(self, event):
            result = super()._apply_boundary(event)
            if result == "applied":
                boundary = self._boundaries[event["boundary_id"]]
                if boundary["N"] is not None:
                    boundary["B"] = (
                        boundary["p"] * boundary["N"] + boundary["q"] - 1
                    ) // boundary["q"]
            return result

    class RecoveryIsNormal(Base):
        def _apply_settlement(self, event):
            result = super()._apply_settlement(event)
            if result == "applied":
                boundary = self._boundaries[event["boundary_id"]]
                boundary["N"] += event["actual"]
                boundary["B"] = boundary["p"] * boundary["N"] // boundary["q"]
            return result

    class MixUnits(Base):
        def _apply_reservation(self, event):
            result = super()._apply_reservation(event)
            if result == "applied":
                source = self._boundaries[event["boundary_id"]]
                for key, account in self._accounts.items():
                    if key != source["account_key"] and key[1] == source["binding"]["goal_id"]:
                        account["R"] += event["upper_bound"]
            return result

    mutants = {
        "erase-R-on-restart": (EraseR, "unknown-reset-restart", None),
        "ceil-instead-of-floor": (Ceil, "floor-non-integral", None),
        "count-recovery-as-normal-use": (RecoveryIsNormal, "reserve-partial-settle", None),
        "mix-unlike-units": (MixUnits, "unlike-units-distinct", None),
    }

    def replay_with(ledger_class, events):
        state = ledger_class()
        for event in events:
            state.append(event)
        return state

    def prefix_rejects(ledger_class, case_name):
        case = module["PREFIX_CASES"][case_name]
        try:
            for end, expected in enumerate(case["expected"], 1):
                state = replay_with(ledger_class, case["events"][:end])
                actual = module["selected_signature"](state, case["boundaries"], case["caps"])
                if actual != expected:
                    return True
        except (module["AdmissionError"], module["ConflictError"], module["ValidationError"]):
            return True
        return False

    detected = []
    if prefix_rejects(EraseR, "unknown-reset-restart"):
        detected.append("erase-R-on-restart")

    partial_expected = module["PREFIX_CASES"]["reserve-partial-settle"]["expected"][-1][0][0][1]
    reset_events = module["PARTIAL_EVENTS"] + (
        module["reset"]("gate-reset", "partial", module["TOKENS"], "reconciled"),
    )
    if module["boundary_signature"](replay_with(EraseC, reset_events), "partial") != partial_expected:
        detected.append("erase-C-on-provider-reset")

    duplicate = module["settle"](
        "gate-duplicate", "s-partial", "r-partial", "partial", module["TOKENS"], 3
    )
    if module["boundary_signature"](
        replay_with(DuplicateCharge, module["PARTIAL_EVENTS"] + (duplicate,)), "partial"
    ) != partial_expected:
        detected.append("charge-duplicate-settlement")

    for name in (
        "ceil-instead-of-floor",
        "count-recovery-as-normal-use",
        "mix-unlike-units",
    ):
        ledger_class, case_name, _ = mutants[name]
        if prefix_rejects(ledger_class, case_name):
            detected.append(name)

    require(tuple(detected) == REQUIRED_MUTATIONS, "independent behavioral mutations incomplete")
    require(tuple(module["run_mutation_controls"]()) == REQUIRED_MUTATIONS, "test mutation controls incomplete")
    return detected


def component_guard_audit(module):
    detected = []
    for target_kind in ("parent", "pool", "resource"):
        prefix = "gate-guard-" + target_kind
        component_ids = (prefix + "-parent", prefix + "-pool", prefix + "-resource")
        ceilings = {
            "parent": 6 if target_kind == "parent" else 20,
            "pool": 6 if target_kind == "pool" else 20,
            "resource": 6 if target_kind == "resource" else 20,
        }
        events = []
        for index, kind in enumerate(("parent", "pool", "resource"), 1):
            events.append(
                module["cap"](
                    prefix + "-cap-" + str(index),
                    prefix + "-" + kind,
                    kind,
                    prefix + "-scope-" + kind,
                    "tokens",
                    1,
                    "provider-window-1",
                    ceilings[kind],
                )
            )
        events.append(
            module["freeze"](
                prefix + "-freeze",
                prefix + "-boundary",
                module["TOKENS"],
                200,
                1,
                10,
                required_components=component_ids,
            )
        )
        claims = tuple(
            module["claim"](item, "tokens", 1, "provider-window-1", 6)
            for item in component_ids
        )
        events.append(
            module["reserve"](
                prefix + "-reserve",
                prefix + "-r-six",
                prefix + "-boundary",
                module["TOKENS"],
                6,
                claims,
            )
        )
        state = module["replay"](tuple(events))
        one_claims = tuple(
            module["claim"](item, "tokens", 1, "provider-window-1", 1)
            for item in component_ids
        )
        try:
            state.append(
                module["reserve"](
                    prefix + "-over",
                    prefix + "-r-over",
                    prefix + "-boundary",
                    module["TOKENS"],
                    1,
                    one_claims,
                )
            )
        except module["AdmissionError"]:
            detected.append(target_kind)
        else:
            raise GateFailure("component guard did not refuse exhausted " + target_kind)

    omitted = module["reserve"](
        "gate-component-omit",
        "gate-r-component-omit",
        "component",
        module["TOKENS"],
        1,
        (),
    )
    try:
        module["replay"](module["COMPONENT_EVENTS"] + (omitted,))
    except module["ValidationError"]:
        pass
    else:
        raise GateFailure("missing required component claims were admitted")
    require(tuple(detected) == ("parent", "pool", "resource"), "component guards incomplete")
    return detected


def subprocess_gate(module):
    command = [sys.executable, "-X", "utf8", "-B", CODE + "test_ledger.py"]
    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
        env=dict(os.environ),
    )
    require(result.returncode == 0, "test subprocess failed:\n" + result.stdout)
    require("skipped" not in result.stdout.lower(), "test subprocess skipped a case")
    for method in module["TEST_METHOD_TO_CASE"]:
        require(
            re.search(r"^" + re.escape(method) + r" \(.*\) \.\.\. ok$", result.stdout, re.MULTILINE)
            is not None,
            "passing test method missing: " + method,
        )
    marker = "RECOVERY_LEDGER_TEST_PASS "
    lines = [line for line in result.stdout.splitlines() if line.startswith(marker)]
    require(len(lines) == 1, "test pass marker missing or duplicated")
    payload = json.loads(lines[0][len(marker):])
    require(
        payload
        == {
            "cases": 15,
            "max_events_limit": 32,
            "mutations": 6,
            "prefixes": 21,
            "provider_calls": 0,
            "selected_sequences": 6,
            "sequence_limit": 256,
        },
        "test pass marker payload differs",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    artifact_bytes = candidate_checks(args.candidate)
    source_preservation(args.candidate)
    module = load_tests()
    prefixes = prefix_audit(module)
    mutations = independent_mutations(module)
    component_guards = component_guard_audit(module)
    subprocess_gate(module)
    print(
        "RECOVERY_LEDGER_GATE_PASS "
        + json.dumps(
            {
                "artifact_bytes": artifact_bytes,
                "base": BASE,
                "candidate": args.candidate,
                "cases": len(REQUIRED_CASES),
                "component_guards": len(component_guards),
                "mutations": len(mutations),
                "prefixes": prefixes,
                "provider_calls": 0,
                "source_bindings": len(SOURCE_SHA256),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (GateFailure, KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError) as exc:
        print("RECOVERY_LEDGER_GATE_FAIL " + str(exc), file=sys.stderr)
        sys.exit(1)
