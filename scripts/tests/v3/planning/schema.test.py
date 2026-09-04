#!/usr/bin/env python3
"""M1A-01 strict-schema acceptance tests (no reducer import)."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError, validators


ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / "schemas" / "control-plane" / "v3" / "planning" / "schema.json"
MATERIALIZER_PATH = SCHEMA_PATH.with_name("materialize.py")
MAX_UINT = 9_007_199_254_740_991


class StrictDecodeError(ValueError):
    pass


def _nested_value(value, path):
    if path == "$value":
        return value
    current = value
    for segment in path.split("."):
        current = current[segment]
    return current


def _sort_key(value, selector):
    if isinstance(selector, list):
        return tuple(_nested_value(value, part) for part in selector)
    selected = _nested_value(value, selector)
    return tuple(selected) if isinstance(selected, list) else selected


def _validate_sorted_by(validator, selector, instance, schema):
    if not isinstance(instance, list):
        return
    try:
        keys = [_sort_key(value, selector) for value in instance]
    except (KeyError, TypeError):
        return
    if keys != sorted(keys):
        yield ValidationError(f"array is not sorted by {selector!r}")


def _utf16_key(value):
    if isinstance(value, str):
        encoded = value.encode("utf-16-be")
        return tuple(
            int.from_bytes(encoded[index:index + 2], "big")
            for index in range(0, len(encoded), 2)
        )
    if isinstance(value, (list, tuple)):
        return tuple(_utf16_key(item) for item in value)
    return value


def _validate_sorted_by_utf16(validator, selector, instance, schema):
    if not isinstance(instance, list):
        return
    try:
        keys = [_utf16_key(_sort_key(value, selector)) for value in instance]
    except (KeyError, TypeError, UnicodeEncodeError):
        return
    if keys != sorted(keys):
        yield ValidationError(f"array is not UTF-16 sorted by {selector!r}")


def _validate_unique_by(validator, selector, instance, schema):
    if not isinstance(instance, list):
        return
    try:
        keys = [_sort_key(value, selector) for value in instance]
    except (KeyError, TypeError):
        return
    for index, key in enumerate(keys):
        if key in keys[:index]:
            yield ValidationError(f"array has duplicate stable key {key!r} for {selector!r}")
            return


def _validate_utf8_bytes(validator, maximum, instance, schema):
    if isinstance(instance, str):
        try:
            size = len(instance.encode("utf-8", errors="strict"))
        except UnicodeEncodeError:
            yield ValidationError("string contains an unpaired surrogate")
            return
        if size > maximum:
            yield ValidationError(f"UTF-8 string is {size} bytes; maximum is {maximum}")


def _canonical_size(value) -> int:
    return len(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def _validate_canonical_bytes(validator, maximum, instance, schema):
    try:
        size = _canonical_size(instance)
    except (TypeError, UnicodeEncodeError):
        return
    if size > maximum:
        yield ValidationError(f"canonical JSON is {size} bytes; maximum is {maximum}")


StrictValidator = validators.extend(
    Draft202012Validator,
    {
        "x-sortedBy": _validate_sorted_by,
        "x-sortedByUtf16": _validate_sorted_by_utf16,
        "x-uniqueBy": _validate_unique_by,
        "x-maxUtf8Bytes": _validate_utf8_bytes,
        "x-maxCanonicalBytes": _validate_canonical_bytes,
    },
)


def _reject_float(value):
    raise StrictDecodeError("I-JSON forbids floating-point values in M1A")


def _reject_constant(value):
    raise StrictDecodeError(f"I-JSON forbids {value}")


def _parse_int(raw):
    if raw == "-0":
        raise StrictDecodeError("I-JSON forbids lexical negative zero")
    digits = raw[1:] if raw.startswith("-") else raw
    if len(digits) > 16:
        raise StrictDecodeError("non-I-JSON integer")
    try:
        value = int(raw)
    except ValueError as exc:
        raise StrictDecodeError("invalid integer") from exc
    if abs(value) > MAX_UINT:
        raise StrictDecodeError("non-I-JSON integer")
    return value


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise StrictDecodeError(f"duplicate key: {key}")
        result[key] = value
    return result


def _check_tree(value, *, depth=0):
    if depth > 16:
        raise StrictDecodeError("nesting depth exceeded")
    if isinstance(value, str):
        if "\x00" in value:
            raise StrictDecodeError("NUL is forbidden")
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise StrictDecodeError("unpaired surrogate") from exc
    elif isinstance(value, bool) or value is None:
        return
    elif isinstance(value, int):
        if abs(value) > MAX_UINT:
            raise StrictDecodeError("non-I-JSON integer")
    elif isinstance(value, list):
        if len(value) > 2048:
            raise StrictDecodeError("array count exceeded")
        for item in value:
            _check_tree(item, depth=depth + 1)
    elif isinstance(value, dict):
        if len(value) > 2048:
            raise StrictDecodeError("object count exceeded")
        for key, item in value.items():
            _check_tree(key, depth=depth + 1)
            _check_tree(item, depth=depth + 1)
    else:
        raise StrictDecodeError("unsupported JSON value")


def strict_loads(raw: str | bytes):
    if isinstance(raw, bytes):
        if len(raw) > 1_048_576:
            raise StrictDecodeError("input byte bound exceeded")
        try:
            raw = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise StrictDecodeError("input is not UTF-8") from exc
    else:
        try:
            raw_size = len(raw.encode("utf-8", errors="strict"))
        except UnicodeEncodeError as exc:
            raise StrictDecodeError("unpaired surrogate") from exc
        if raw_size > 1_048_576:
            raise StrictDecodeError("input byte bound exceeded")
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_pairs_no_duplicates,
            parse_int=_parse_int,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except StrictDecodeError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise StrictDecodeError("malformed JSON") from exc
    _check_tree(value)
    return value


class ExampleFactory:
    def __init__(self, schema):
        self.schema = schema

    def make(self, schema):
        if "$ref" in schema:
            name = schema["$ref"].split("/")[-1]
            scalar_examples = {
                "id": "X-ID",
                "command_id": "CMD-X",
                "token": "token",
                "digest": "0" * 64,
                "text": "",
                "nonempty_text": "x",
                "json_input_text": "{}",
                "resource_path": "resource",
            }
            if name in scalar_examples:
                return scalar_examples[name]
            return self.make(self.schema["$defs"][name])
        if "const" in schema:
            return copy.deepcopy(schema["const"])
        if "oneOf" in schema:
            return self.make(schema["oneOf"][0])
        if "anyOf" in schema:
            return self.make(schema["anyOf"][0])
        if "enum" in schema:
            return schema["enum"][0]
        kind = schema.get("type")
        if kind == "object":
            value = {
                key: self.make(schema["properties"][key])
                for key in schema.get("required", [])
            }
            for conjunction in schema.get("allOf", []):
                selected = conjunction.get("oneOf", [conjunction])[0]
                self._overlay(value, schema, selected)
            return value
        if kind == "array":
            count = schema.get("minItems", 0)
            return [self.make(schema["items"]) for _ in range(count)]
        if kind == "integer":
            return schema.get("minimum", 0)
        if kind == "boolean":
            return False
        if kind == "null":
            return None
        if kind == "string":
            pattern = schema.get("pattern", "")
            for prefix in (
                "evidence", "proposition", "operation", "capability", "dependency", "delta"
            ):
                if pattern.startswith(f"^{prefix}-"):
                    return f"{prefix}-x"
            minimum = schema.get("minLength", 0)
            return "x" if minimum else ""
        raise AssertionError(f"cannot synthesize schema: {schema}")

    def _overlay(self, value, base_schema, overlay):
        for key, constraint in overlay.get("properties", {}).items():
            if "const" in constraint or "$ref" in constraint or "enum" in constraint:
                value[key] = self.make(constraint)
            elif constraint.get("minItems", 0) > len(value.get(key, [])):
                base_property = base_schema["properties"][key]
                resolved = base_property
                if "$ref" in resolved:
                    resolved = self.schema["$defs"][resolved["$ref"].split("/")[-1]]
                item_schema = resolved["items"]
                value[key] = [self.make(item_schema) for _ in range(constraint["minItems"])]


class SchemaContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = StrictValidator(cls.schema)
        cls.factory = ExampleFactory(cls.schema)

    def validator_for(self, definition):
        return StrictValidator(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$ref": f"#/$defs/{definition}",
                "$defs": self.schema["$defs"],
            }
        )

    def assert_valid(self, definition, instance):
        errors = list(self.validator_for(definition).iter_errors(instance))
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def assert_invalid(self, definition, instance):
        self.assertFalse(self.validator_for(definition).is_valid(instance))

    def test_meta_schema_and_closed_alphabets(self):
        defs = self.schema["$defs"]
        self.assertEqual(22, len(defs["command_type"]["enum"]))
        self.assertEqual(27, len(defs["event_type"]["enum"]))
        self.assertEqual(28, len(defs["error_code"]["enum"]))
        self.assertEqual(25, len(defs["domain_record"]["oneOf"]))
        self.assertEqual(22, len(defs["command_envelope"]["oneOf"]))
        self.assertEqual(27, len(defs["planning_event"]["oneOf"]))
        self.assertEqual(16, self.schema["x-maxDepth"])

    def test_materializer_is_byte_identical(self):
        spec = importlib.util.spec_from_file_location("m1a_schema_materializer", MATERIALIZER_PATH)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        expected = json.dumps(module.build_schema(), ensure_ascii=False, indent=2) + "\n"
        self.assertEqual(expected, SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_every_domain_record_arm_has_a_valid_closed_instance(self):
        for branch in self.schema["$defs"]["domain_record"]["oneOf"]:
            name = branch["$ref"].split("/")[-1]
            with self.subTest(name=name):
                self.assert_valid(name, self.factory.make(branch))

    def test_every_command_arm_has_a_valid_closed_instance(self):
        for branch in self.schema["$defs"]["command_envelope"]["oneOf"]:
            name = branch["$ref"].split("/")[-1]
            with self.subTest(name=name):
                self.assert_valid(name, self.factory.make(branch))

    def test_every_event_arm_has_a_valid_closed_instance(self):
        for branch in self.schema["$defs"]["planning_event"]["oneOf"]:
            name = branch["$ref"].split("/")[-1]
            event = self.factory.make(branch)
            if event["event_type"] == "PlanRevisionAdmitted":
                event["related_records"] = sorted(
                    [
                        self.factory.make({"$ref": "#/$defs/plan_transition_record"}),
                        self.factory.make({"$ref": "#/$defs/task_node_record"}),
                    ],
                    key=lambda record: (record["object_type"], record["id"], record["version"]),
                )
            elif event["event_type"] == "ReplanAdmitted":
                event["related_records"] = sorted(
                    [
                        self.factory.make({"$ref": "#/$defs/route_assignment_record"}),
                        self.factory.make({"$ref": "#/$defs/budget_reservation_record"}),
                    ],
                    key=lambda record: (record["object_type"], record["id"], record["version"]),
                )
            with self.subTest(name=name):
                self.assert_valid(name, event)

    def test_auxiliary_and_bundle_unions_have_valid_closed_instances(self):
        for name in (
            "command_receipt",
            "decode_failure",
            "error_witness",
            "genesis_config",
            "authority_attestation",
            "policy_fixture",
            "replay_expectation",
            "projection_state",
            "fixture_bundle",
        ):
            with self.subTest(name=name):
                value = self.factory.make({"$ref": f"#/$defs/{name}"})
                self.assert_valid(name, value)

    def test_replay_expectation_keeps_invalid_events_as_raw_inputs(self):
        accepted = self.factory.make({"$ref": "#/$defs/replay_expectation"})
        accepted["event_inputs"] = ['{"event_schema_version":"unknown"}']
        self.assert_valid("replay_expectation", accepted)
        refused = copy.deepcopy(accepted)
        refused["expected_disposition"] = "refused"
        refused["primary_error"] = "E-SCHEMA-UNKNOWN-VERSION"
        refused["expected_projection_digest"] = None
        self.assert_valid("replay_expectation", refused)
        refused["expected_projection_digest"] = "0" * 64
        self.assert_invalid("replay_expectation", refused)

    def test_every_declared_object_schema_is_closed(self):
        open_objects = []

        def visit(value, path):
            if isinstance(value, dict):
                if value.get("type") == "object" and value.get("additionalProperties") is not False:
                    open_objects.append(path)
                for key, child in value.items():
                    visit(child, f"{path}/{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    visit(child, f"{path}/{index}")

        visit(self.schema, "#")
        self.assertEqual([], open_objects)

    def test_unknown_missing_and_unknown_version_fail_closed(self):
        record = self.factory.make({"$ref": "#/$defs/owner_intent_record"})
        unknown = copy.deepcopy(record)
        unknown["unexpected"] = True
        self.assert_invalid("owner_intent_record", unknown)
        missing = copy.deepcopy(record)
        del missing["payload"]
        self.assert_invalid("owner_intent_record", missing)
        version = copy.deepcopy(record)
        version["schema_version"] = "m1a-owner-intent-2"
        self.assert_invalid("owner_intent_record", version)

    def test_identifier_digest_integer_and_count_bounds(self):
        self.assertFalse(self.validator_for("id").is_valid("lowercase-id"))
        self.assertFalse(self.validator_for("digest").is_valid("A" * 64))
        self.assertFalse(self.validator_for("uint").is_valid(MAX_UINT + 1))
        self.assertFalse(self.validator_for("id_set").is_valid(["X-ID"] * 257))
        too_long = "CMD-" + "x" * 117
        self.assertEqual(121, len(too_long))
        self.assertFalse(self.validator_for("command_id").is_valid(too_long))

    def test_custom_utf8_and_sort_constraints_are_enforced(self):
        self.assertFalse(self.validator_for("text").is_valid("é" * 3000))
        self.assertFalse(self.validator_for("id_set").is_valid(["Z-ID", "A-ID"]))
        self.assertTrue(self.validator_for("id_set").is_valid(["A-ID", "Z-ID"]))

        disposition = self.factory.make({"$ref": "#/$defs/disposition"})
        duplicate_key = copy.deepcopy(disposition)
        duplicate_key["reason_digest"] = "1" * 64
        self.assertFalse(self.validator_for("disposition_set").is_valid([disposition, duplicate_key]))

        astral = self.factory.make({"$ref": "#/$defs/canonical_diff_entry"})
        astral["path_segments"] = ["\U00010000"]
        bmp = copy.deepcopy(astral)
        bmp["path_segments"] = ["\ue000"]
        self.assertTrue(self.validator_for("canonical_diff").is_valid([astral, bmp]))
        self.assertFalse(self.validator_for("canonical_diff").is_valid([bmp, astral]))

    def test_strict_json_rejects_duplicate_float_constant_utf8_and_depth(self):
        for raw in (
            '{"x":1,"x":2}',
            '{"x":1.0}',
            '{"x":NaN}',
            b'"\xff"',
            '"\ud800"',
            '-0',
            "[" * 17 + "0" + "]" * 17,
        ):
            with self.subTest(raw=repr(raw)), self.assertRaises(StrictDecodeError):
                strict_loads(raw)

    def test_strict_json_rejects_non_i_json_integer_and_collection_bound(self):
        with self.assertRaises(StrictDecodeError):
            strict_loads(str(MAX_UINT + 1))
        with self.assertRaises(StrictDecodeError):
            strict_loads("[" + ",".join("0" for _ in range(2049)) + "]")
        self.assertEqual(-1, strict_loads("-1"))
        self.assertFalse(self.validator_for("uint").is_valid(strict_loads("-1")))

    def test_command_payload_discriminator_is_exact(self):
        command = self.factory.make({"$ref": "#/$defs/command_record_owner_intent"})
        command["command_type"] = "accept-goal-spec"
        self.assert_invalid("command_envelope", command)
        command["command_type"] = "unknown-command"
        self.assert_invalid("command_envelope", command)

    def test_event_primary_record_discriminator_is_exact(self):
        event = self.factory.make({"$ref": "#/$defs/event_OwnerIntentRecorded"})
        event["event_type"] = "GoalSpecAccepted"
        self.assert_invalid("planning_event", event)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SchemaContractTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
    print("M1A_SCHEMA_PASS")
