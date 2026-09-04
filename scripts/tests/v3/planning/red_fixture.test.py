#!/usr/bin/env python3
"""Validate the literal M1A red corpus, then fail until the reducer exists."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TEST_DIR = Path(__file__).resolve().parent
FIXTURE_DIR = TEST_DIR / "fixtures"
SCHEMA_PATH = ROOT / "schemas" / "control-plane" / "v3" / "planning" / "schema.json"
SCHEMA_TEST_PATH = TEST_DIR / "schema.test.py"
MATERIALIZER_PATH = TEST_DIR / "materialize_fixtures.py"
REDUCER_PATH = ROOT / "scripts" / "v3" / "planning" / "replay" / "kernel.py"
EXPECTED_SCHEMA_CANDIDATE = "ab9707480baf6ef7baff03b6bda444b890d78557"
EXPECTED_FIXTURE_IDS = [f"F-M1A-{number:03d}" for number in range(1, 24)]
GENESIS_DIGEST = "fb1168e6e4d1267c41ea3d7798ebb88963e6de7c05cc1500ed059ba4b2f75801"
SEALED_MARKERS = {
    "attestation_schema_version",
    "command_schema_version",
    "decode_failure_schema_version",
    "event_schema_version",
    "policy_schema_version",
    "projection_schema_version",
    "receipt_schema_version",
    "witness_schema_version",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schema_contract = load_module("m1a_schema_contract", SCHEMA_TEST_PATH)
fixture_materializer = load_module("m1a_fixture_materializer", MATERIALIZER_PATH)


def fail(message: str) -> None:
    raise AssertionError(message)


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def schema_validator(schema: dict, definition: str):
    return schema_contract.StrictValidator(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$ref": f"#/$defs/{definition}",
            "$defs": schema["$defs"],
        }
    )


def assert_schema_valid(validator, value, label: str) -> None:
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        rendered = []
        for error in errors[:20]:
            location = "/".join(str(part) for part in error.absolute_path) or "<root>"
            rendered.append(f"{location}: {error.message}")
        fail(f"{label} violates fixture_bundle schema:\n" + "\n".join(rendered))


def is_sealed(value: dict) -> bool:
    if "content_digest" not in value:
        return False
    if SEALED_MARKERS.intersection(value):
        return True
    return all(
        key in value
        for key in (
            "object_type",
            "schema_version",
            "id",
            "version",
            "created_by_actor_id",
            "payload",
        )
    )


def assert_digests(value, path: str) -> None:
    if isinstance(value, dict):
        if is_sealed(value):
            expected = fixture_materializer.digest(value, omit_content_digest=True)
            if value["content_digest"] != expected:
                fail(f"{path}/content_digest mismatch: expected {expected}")
        if "command_schema_version" in value:
            if value["payload_digest"] != fixture_materializer.digest(value["payload"]):
                fail(f"{path}/payload_digest mismatch")
            if value["candidate_digest"] != value["payload_digest"]:
                fail(f"{path}/candidate_digest must bind payload_digest")
        if "event_schema_version" in value:
            operand = {
                "event_type": value["event_type"],
                "primary_record": value["primary_record"],
                "related_records": value["related_records"],
            }
            if value["state_delta_digest"] != fixture_materializer.digest(operand):
                fail(f"{path}/state_delta_digest mismatch")
        if value.get("object_type") == "plan-revision" and "schema_version" in value:
            payload = value["payload"]
            operand = {
                "task_node_refs": payload["task_node_refs"],
                "dependency_edges": payload["dependency_edges"],
            }
            if payload["graph_digest"] != fixture_materializer.digest(operand):
                fail(f"{path}/payload/graph_digest mismatch")
        for key, item in value.items():
            assert_digests(item, f"{path}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_digests(item, f"{path}/{index}")


def assert_command_receipts(commands: list[dict], receipts: list[dict], label: str) -> None:
    if len(commands) != len(receipts):
        fail(f"{label}: command/receipt cardinality differs")
    for index, (command, receipt) in enumerate(zip(commands, receipts)):
        if receipt["command_id"] != command["command_id"]:
            fail(f"{label}: command/receipt ID mismatch at position {index}")
        if receipt["command_digest"] != command["content_digest"]:
            fail(f"{label}: receipt does not bind command at position {index}")


def assert_event_chain(
    events: list[dict], label: str, *, prior: str = GENESIS_DIGEST, expected_sequence: int = 1
) -> None:
    for event in events:
        if event["sequence"] != expected_sequence:
            fail(f"{label}: expected event sequence {expected_sequence}, got {event['sequence']}")
        if event["previous_event_digest"] != prior:
            fail(f"{label}: broken previous-event digest at {event['event_id']}")
        prior = event["content_digest"]
        expected_sequence += 1


def assert_case(
    case: dict, label: str, *, root_validator, event_validator
) -> tuple[set[str], set[str], set[str], set[str]]:
    initial_commands = case["initial_commands"]
    commands = case["commands"]
    initial_receipts = case["initial_receipts"]
    receipts = case["expected_receipts"]
    initial_events = case["initial_events"]
    events = case["expected_events"]
    assert_command_receipts(initial_commands, initial_receipts, label + "/initial")
    assert_command_receipts(commands, receipts, label + "/oracle")
    assert_event_chain([*initial_events, *events], label)

    all_command_digests: dict[str, set[str]] = {}
    for command in [*initial_commands, *commands]:
        all_command_digests.setdefault(command["command_id"], set()).add(command["content_digest"])
    all_events = [*initial_events, *events]
    events_by_command: dict[str, list[dict]] = {}
    for event in all_events:
        command_digests = all_command_digests.get(event["command_id"])
        if command_digests is None:
            fail(f"{label}: event {event['event_id']} has no command")
        if event["command_digest"] not in command_digests:
            fail(f"{label}: event {event['event_id']} command digest mismatch")
        events_by_command.setdefault(event["command_id"], []).append(event)

    for receipt in [*initial_receipts, *receipts]:
        emitted = (
            [
                event for event in events_by_command.get(receipt["command_id"], [])
                if event["command_digest"] == receipt["command_digest"]
            ]
            if receipt["disposition"] == "accepted"
            else []
        )
        event_ids = sorted(event["event_id"] for event in emitted)
        if receipt["event_ids"] != event_ids:
            fail(f"{label}: receipt {receipt['receipt_id']} event_ids mismatch")
        if emitted:
            sequences = [event["sequence"] for event in emitted]
            if receipt["first_event_sequence"] != min(sequences):
                fail(f"{label}: receipt {receipt['receipt_id']} first sequence mismatch")
            if receipt["last_event_sequence"] != max(sequences):
                fail(f"{label}: receipt {receipt['receipt_id']} last sequence mismatch")
        elif receipt["first_event_sequence"] is not None or receipt["last_event_sequence"] is not None:
            fail(f"{label}: eventless receipt has a sequence")

    if case["expected_final_digest"] != case["expected_final_state"]["content_digest"]:
        fail(f"{label}: expected_final_digest mismatch")
    if case["expected_final_state"]["last_event_sequence"] != len(all_events):
        fail(f"{label}: final sequence mismatch")
    expected_last = all_events[-1]["content_digest"] if all_events else GENESIS_DIGEST
    if case["expected_final_state"]["last_event_digest"] != expected_last:
        fail(f"{label}: final event digest mismatch")

    if len(case["decode_inputs"]) != len(case["expected_decode_failures"]):
        fail(f"{label}: decode input/failure cardinality differs")
    for raw, failure in zip(case["decode_inputs"], case["expected_decode_failures"]):
        if failure["raw_input_digest"] != sha_bytes(raw.encode("utf-8")):
            fail(f"{label}: decode failure raw_input_digest mismatch")
        try:
            decoded = schema_contract.strict_loads(raw)
        except schema_contract.StrictDecodeError as exc:
            if failure["primary_error"] == "E-SCHEMA-DUPLICATE" and "duplicate key" in str(exc):
                continue
            if failure["primary_error"] == "E-SCHEMA-BOUND" and "exceeded" in str(exc):
                continue
            fail(f"{label}: raw decode failure disagrees with {failure['primary_error']}: {exc}")
        if failure["primary_error"] in ("E-SCHEMA-DUPLICATE", "E-SCHEMA-BOUND"):
            fail(f"{label}: raw input unexpectedly passes strict decode for {failure['primary_error']}")
        if root_validator.is_valid(decoded):
            fail(f"{label}: expected decode failure is valid under the planning schema")

    for replay_index, replay in enumerate(case["replay_cases"]):
        replay_label = f"{label}/replay_cases/{replay_index}"
        assert_command_receipts(replay["commands"], replay["receipts"], replay_label)
        if replay["expected_disposition"] == "accepted" and replay["expected_projection_digest"] is None:
            fail(f"{replay_label}: accepted replay lacks projection digest")
        if replay["expected_disposition"] == "refused" and replay["expected_projection_digest"] is not None:
            fail(f"{replay_label}: refused replay exposes projection digest")
        if replay["checkpoint"] is not None:
            snapshot = replay["checkpoint"]["projection_snapshot"]
            checkpoint = replay["checkpoint"]["checkpoint_record"]
            if checkpoint["payload"]["state_digest"] != snapshot["content_digest"]:
                fail(f"{replay_label}: checkpoint does not bind snapshot")
            replay_prior = snapshot["last_event_digest"]
            replay_sequence = snapshot["last_event_sequence"] + 1
        else:
            replay_prior = GENESIS_DIGEST
            replay_sequence = 1
        parsed_events = [schema_contract.strict_loads(raw) for raw in replay["event_inputs"]]
        event_schema_valid = all(event_validator.is_valid(event) for event in parsed_events)
        chain_valid = True
        try:
            assert_event_chain(
                parsed_events,
                replay_label,
                prior=replay_prior,
                expected_sequence=replay_sequence,
            )
            for event_index, event in enumerate(parsed_events):
                assert_digests(event, f"{replay_label}/event_inputs/{event_index}")
        except AssertionError:
            chain_valid = False
        if replay["expected_disposition"] == "accepted":
            if not event_schema_valid or not chain_valid:
                fail(f"{replay_label}: accepted replay carrier is structurally invalid")
            if replay["receipts"] and (
                replay["expected_projection_digest"]
                != replay["receipts"][-1]["state_after_digest"]
            ):
                fail(f"{replay_label}: accepted replay digest is not receipt-bound")
        elif replay["primary_error"] == "E-SCHEMA-UNKNOWN-VERSION":
            if event_schema_valid:
                fail(f"{replay_label}: unknown-version replay carrier validates")
        elif replay["primary_error"] == "E-DIGEST-MISMATCH":
            if event_schema_valid and chain_valid:
                fail(f"{replay_label}: digest-mismatch replay has no structural falsifier")
        for raw in replay["event_inputs"]:
            try:
                schema_contract.strict_loads(raw)
            except schema_contract.StrictDecodeError as exc:
                fail(f"{replay_label}: raw replay carrier is not strict JSON: {exc}")

    command_types = {item["command_type"] for item in [*initial_commands, *commands]}
    event_types = {item["event_type"] for item in all_events}
    error_codes = {
        item["primary_error"]
        for item in [*initial_receipts, *receipts, *case["expected_decode_failures"]]
        if item["primary_error"] is not None
    }
    error_codes.update(
        item["primary_error"] for item in case["replay_cases"] if item["primary_error"] is not None
    )
    domain_types = set()

    def collect_domain(value):
        if isinstance(value, dict):
            if all(key in value for key in ("object_type", "schema_version", "created_by_actor_id")):
                domain_types.add(value["object_type"])
            for item in value.values():
                collect_domain(item)
        elif isinstance(value, list):
            for item in value:
                collect_domain(item)

    collect_domain(case)
    return command_types, event_types, error_codes, domain_types


def validate_corpus() -> int:
    schema_bytes = SCHEMA_PATH.read_bytes()
    schema = schema_contract.strict_loads(schema_bytes)
    manifest_path = FIXTURE_DIR / "manifest.json"
    manifest = schema_contract.strict_loads(manifest_path.read_bytes())
    if manifest["schema_candidate"] != EXPECTED_SCHEMA_CANDIDATE:
        fail("manifest schema candidate is not the frozen M1A-01 commit")
    if manifest["schema_sha256"] != sha_bytes(schema_bytes):
        fail("manifest schema_sha256 mismatch")
    if manifest["fixture_count"] != 23:
        fail("manifest fixture_count must be 23")

    defs = schema["$defs"]
    closed_commands = defs["command_type"]["enum"]
    closed_events = defs["event_type"]["enum"]
    closed_errors = defs["error_code"]["enum"]
    closed_domains = sorted(
        defs[branch["$ref"].split("/")[-1]]["properties"]["object_type"]["const"]
        for branch in defs["domain_record"]["oneOf"]
    )
    for key, expected in (
        ("schema_definitions", sorted(defs)),
        ("closed_command_types", closed_commands),
        ("closed_event_types", closed_events),
        ("closed_error_codes", closed_errors),
        ("domain_record_types", closed_domains),
        (
            "projection_terminal_states",
            defs["projection_state"]["properties"]["terminal_status"]["enum"],
        ),
    ):
        if manifest[key] != expected:
            fail(f"manifest {key} does not match schema")

    rows = manifest["fixtures"]
    if [row["fixture_id"] for row in rows] != EXPECTED_FIXTURE_IDS:
        fail("manifest fixture IDs are incomplete or out of order")
    fixture_validator = schema_validator(schema, "fixture_bundle")
    event_validator = schema_validator(schema, "planning_event")
    root_validator = schema_contract.StrictValidator(schema)
    observed_commands: set[str] = set()
    observed_events: set[str] = set()
    observed_errors: set[str] = set()
    observed_domains: set[str] = set()
    positive_fixture_count = 0

    for row in rows:
        path = FIXTURE_DIR / row["path"]
        data = path.read_bytes()
        if len(data) > 1_048_576:
            fail(f"{path.name}: fixture exceeds one MiB")
        if row["bytes"] != len(data) or row["sha256"] != sha_bytes(data):
            fail(f"{path.name}: manifest byte identity mismatch")
        bundle = schema_contract.strict_loads(data)
        if bundle["fixture_id"] != row["fixture_id"]:
            fail(f"{path.name}: bundle/manifest fixture ID mismatch")
        assert_schema_valid(fixture_validator, bundle, path.name)
        assert_digests(bundle, path.name)
        cases = bundle["cases"]
        if any(
            any(receipt["disposition"] == "accepted" for receipt in case["expected_receipts"])
            or any(replay["expected_disposition"] == "accepted" for replay in case["replay_cases"])
            for case in cases
        ):
            positive_fixture_count += 1
        if row["case_count"] != len(cases):
            fail(f"{path.name}: manifest case_count mismatch")
        if row["command_count"] != sum(
            len(case["initial_commands"]) + len(case["commands"]) for case in cases
        ):
            fail(f"{path.name}: manifest command_count mismatch")
        if row["receipt_count"] != sum(
            len(case["initial_receipts"]) + len(case["expected_receipts"])
            for case in cases
        ):
            fail(f"{path.name}: manifest receipt_count mismatch")
        if row["event_count"] != sum(
            len(case["initial_events"]) + len(case["expected_events"]) for case in cases
        ):
            fail(f"{path.name}: manifest event_count mismatch")
        if row["decode_failure_count"] != sum(
            len(case["expected_decode_failures"]) for case in cases
        ):
            fail(f"{path.name}: manifest decode_failure_count mismatch")
        if row["replay_case_count"] != sum(len(case["replay_cases"]) for case in cases):
            fail(f"{path.name}: manifest replay_case_count mismatch")
        if row["expected_final_digests"] != [case["expected_final_digest"] for case in cases]:
            fail(f"{path.name}: manifest final digests mismatch")
        fixture_errors = set()
        for case_index, case in enumerate(cases):
            coverage = assert_case(
                case,
                f"{path.name}/cases/{case_index}",
                root_validator=root_validator,
                event_validator=event_validator,
            )
            observed_commands.update(coverage[0])
            observed_events.update(coverage[1])
            observed_errors.update(coverage[2])
            fixture_errors.update(coverage[2])
            observed_domains.update(coverage[3])
        if row["error_codes"] != sorted(fixture_errors):
            fail(f"{path.name}: manifest error_codes mismatch")

    if observed_commands != set(closed_commands):
        fail(f"command coverage differs: missing={sorted(set(closed_commands) - observed_commands)}")
    if observed_events != set(closed_events):
        fail(f"event coverage differs: missing={sorted(set(closed_events) - observed_events)}")
    if observed_domains != set(closed_domains):
        fail(f"domain coverage differs: missing={sorted(set(closed_domains) - observed_domains)}")
    if observed_errors != set(closed_errors):
        fail(
            "error coverage differs: "
            f"missing={sorted(set(closed_errors) - observed_errors)} "
            f"unknown={sorted(observed_errors - set(closed_errors))}"
        )
    return positive_fixture_count


def main() -> int:
    positive_fixture_count = validate_corpus()
    if sys.argv[1:] == ["--validate-only"]:
        print("M1A_RED_STRUCTURE_PASS")
        return 0
    if sys.argv[1:]:
        print("usage: red_fixture.test.py [--validate-only]", file=sys.stderr)
        return 2
    if not REDUCER_PATH.is_file():
        print(
            f"M1A_RED_EXPECTED: {positive_fixture_count} positive fixture bundles "
            "cannot execute because reducer is missing",
            file=sys.stderr,
        )
        return 1
    print("M1A_RED_INVALIDATED: reducer exists; M1A-05 must bind execution", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"M1A_RED_CORPUS_INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
