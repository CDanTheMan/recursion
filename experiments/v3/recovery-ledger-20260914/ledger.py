"""Inert integer event/replay contract for the Recursion v3 recovery ledger.

This module performs no I/O other than explicit JSON serialization requested by its
caller.  It cannot dispatch work or admit real consumption.
"""

import copy
import json


MAX_EVENTS = 32
FORMAT = "recursion-v3-recovery-ledger-experiment-1"


class LedgerError(Exception):
    """Base class for deterministic ledger refusal."""


class ValidationError(LedgerError):
    """An event is malformed or has the wrong literal binding."""


class ConflictError(LedgerError):
    """An idempotency identity was reused with different content."""


class AdmissionError(LedgerError):
    """A valid reservation exceeds or cannot prove an admission limit."""


def _object_no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("duplicate JSON key: " + str(key))
        result[key] = value
    return result


def _canonical(value):
    try:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
    except (TypeError, ValueError) as exc:
        raise ValidationError("event is not canonical JSON data") from exc


def _exact_keys(value, expected, name):
    if type(value) is not dict:
        raise ValidationError(name + " must be an object")
    actual = set(value)
    expected = set(expected)
    if actual != expected:
        raise ValidationError(
            name
            + " keys differ: missing="
            + repr(sorted(expected - actual))
            + " extra="
            + repr(sorted(actual - expected))
        )


def _identifier(value, name):
    if type(value) is not str or not value or value.strip() != value:
        raise ValidationError(name + " must be a non-empty trimmed string")
    return value


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValidationError(name + " must be an integer >= " + str(minimum))
    return value


def _binding(value, name="binding"):
    _exact_keys(
        value,
        ("task_id", "goal_id", "unit", "quantum", "window_id"),
        name,
    )
    result = {
        "task_id": _identifier(value["task_id"], name + ".task_id"),
        "goal_id": _identifier(value["goal_id"], name + ".goal_id"),
        "unit": _identifier(value["unit"], name + ".unit"),
        "quantum": _integer(value["quantum"], name + ".quantum", 1),
        "window_id": value["window_id"],
    }
    if result["window_id"] is not None:
        _identifier(result["window_id"], name + ".window_id")
    return result


def _same_binding(actual, expected, name="binding"):
    actual = _binding(actual, name)
    if actual != expected:
        raise ValidationError(name + " does not match the frozen binding")


def _without_event_id(event):
    return {key: value for key, value in event.items() if key != "event_id"}


class Ledger:
    """Replayable in-memory projection over accepted immutable events."""

    def __init__(self):
        self._events = []
        self._event_fingerprints = {}
        self._boundaries = {}
        self._accounts = {}
        self._components = {}
        self._reservations = {}
        self._settlements = {}
        self._normal_sources = {}

    def boundary_ids(self):
        return tuple(sorted(self._boundaries))

    def component_ids(self):
        return tuple(sorted(self._components))

    def append(self, raw_event):
        if type(raw_event) is not dict:
            raise ValidationError("event must be an object")
        event = copy.deepcopy(raw_event)
        event_id = _identifier(event.get("event_id"), "event_id")
        event_type = _identifier(event.get("type"), "type")
        fingerprint = _canonical(event)
        prior = self._event_fingerprints.get(event_id)
        if prior is not None:
            if prior == fingerprint:
                return "duplicate"
            raise ConflictError("event_id reused with different content: " + event_id)
        if len(self._events) >= MAX_EVENTS:
            raise ValidationError("event sequence exceeds " + str(MAX_EVENTS))

        handlers = {
            "boundary_frozen": self._apply_boundary,
            "cap_configured": self._apply_cap,
            "reservation_created": self._apply_reservation,
            "effect_unknown": self._apply_unknown,
            "reservation_settled": self._apply_settlement,
            "normal_use_verified": self._apply_normal,
            "provider_counter_reset": self._apply_reset,
            "process_restarted": self._apply_restart,
        }
        handler = handlers.get(event_type)
        if handler is None:
            raise ValidationError("unknown event type: " + event_type)
        disposition = handler(event)
        if disposition == "duplicate":
            # A semantic duplicate delivered under a new event identity is still
            # evidence.  Bind that identity so it cannot later name other content,
            # and serialize it so reopening preserves the conflict boundary.
            self._events.append(event)
            self._event_fingerprints[event_id] = fingerprint
            return disposition
        self._events.append(event)
        self._event_fingerprints[event_id] = fingerprint
        return "applied"

    def _apply_boundary(self, event):
        _exact_keys(
            event,
            (
                "event_id",
                "type",
                "boundary_id",
                "binding",
                "normal_use",
                "fraction",
                "previous_boundary_id",
                "normal_source_ids",
                "component_ids",
            ),
            "boundary_frozen",
        )
        boundary_id = _identifier(event["boundary_id"], "boundary_id")
        binding = _binding(event["binding"])
        normal_use = event["normal_use"]
        if normal_use is not None:
            normal_use = _integer(normal_use, "normal_use")
        _exact_keys(event["fraction"], ("p", "q"), "fraction")
        p = _integer(event["fraction"]["p"], "fraction.p")
        q = _integer(event["fraction"]["q"], "fraction.q", 1)
        if p > q:
            raise ValidationError("fraction must be between zero and one")
        previous = event["previous_boundary_id"]
        sources = event["normal_source_ids"]
        if type(sources) is not list:
            raise ValidationError("normal_source_ids must be a list")
        source_ids = tuple(_identifier(item, "normal_source_id") for item in sources)
        if len(source_ids) != len(set(source_ids)):
            raise ValidationError("normal_source_ids must be unique")
        components = event["component_ids"]
        if type(components) is not list:
            raise ValidationError("component_ids must be a list")
        component_ids = tuple(_identifier(item, "component_id") for item in components)
        if len(component_ids) != len(set(component_ids)):
            raise ValidationError("component_ids must be unique")
        for component_id in component_ids:
            if component_id not in self._components:
                raise ValidationError("unknown required component: " + component_id)

        normalized = _canonical(_without_event_id(event))
        if boundary_id in self._boundaries:
            if self._boundaries[boundary_id]["fingerprint"] == normalized:
                return "duplicate"
            raise ConflictError("boundary_id reused with different content: " + boundary_id)

        account_key = (
            binding["task_id"],
            binding["goal_id"],
            binding["unit"],
            binding["quantum"],
        )
        consumed_sources = []
        if previous is None:
            if source_ids:
                raise ValidationError("initial boundary cannot cite normal additions")
            if account_key in self._accounts:
                raise ConflictError("allowance lineage already has an initial boundary")
            account = {"C": 0, "R": 0, "blockers": set(), "current_boundary_id": boundary_id}
        else:
            previous = _identifier(previous, "previous_boundary_id")
            if previous not in self._boundaries:
                raise ValidationError("unknown previous boundary")
            if not source_ids:
                raise ValidationError("successor boundary requires attributed normal use")
            prior = self._boundaries[previous]
            if prior["account_key"] != account_key:
                raise ValidationError("successor changed allowance lineage")
            account = self._accounts[account_key]
            if account["current_boundary_id"] != previous:
                raise ConflictError("successor must extend the current boundary")
            if component_ids != prior["component_ids"]:
                raise ValidationError("successor changed required component inventory")
            for key in ("task_id", "goal_id", "unit", "quantum"):
                if binding[key] != prior["binding"][key]:
                    raise ValidationError("successor binding changed " + key)
            if prior["N"] is None:
                raise ValidationError("unknown prior baseline cannot create successor")
            addition = 0
            for source_id in source_ids:
                source = self._normal_sources.get(source_id)
                if source is None or source["boundary_id"] != previous:
                    raise ValidationError("normal source is absent or belongs elsewhere")
                if source["used_by"] is not None:
                    raise ConflictError("normal source already used by a successor")
                addition += source["amount"]
                consumed_sources.append(source)
            if normal_use != prior["N"] + addition:
                raise ValidationError("successor N does not equal prior N plus cited normal use")

        blockers = set()
        if normal_use is None:
            blockers.add("unknown-baseline")
        if binding["window_id"] is None:
            account["blockers"].add("unknown-window")
        allowance = None if normal_use is None else (p * normal_use) // q
        if previous is None:
            self._accounts[account_key] = account
        else:
            account["current_boundary_id"] = boundary_id
        self._boundaries[boundary_id] = {
            "binding": binding,
            "N": normal_use,
            "p": p,
            "q": q,
            "B": allowance,
            "blockers": blockers,
            "account_key": account_key,
            "component_ids": component_ids,
            "fingerprint": normalized,
        }
        for source in consumed_sources:
            source["used_by"] = boundary_id
        return "applied"

    def _apply_cap(self, event):
        _exact_keys(
            event,
            (
                "event_id",
                "type",
                "component_id",
                "kind",
                "scope_id",
                "unit",
                "quantum",
                "window_id",
                "ceiling",
                "used",
                "identity_status",
            ),
            "cap_configured",
        )
        component_id = _identifier(event["component_id"], "component_id")
        kind = event["kind"]
        if kind not in ("parent", "pool", "resource"):
            raise ValidationError("cap kind must be parent, pool or resource")
        scope_id = _identifier(event["scope_id"], "scope_id")
        unit = _identifier(event["unit"], "unit")
        quantum = _integer(event["quantum"], "quantum", 1)
        window = event["window_id"]
        if window is not None:
            _identifier(window, "window_id")
        ceiling = _integer(event["ceiling"], "ceiling")
        used = _integer(event["used"], "used")
        status = event["identity_status"]
        if status not in ("known", "unknown"):
            raise ValidationError("identity_status must be known or unknown")
        normalized = _canonical(_without_event_id(event))
        if component_id in self._components:
            if self._components[component_id]["fingerprint"] == normalized:
                return "duplicate"
            raise ConflictError("component_id reused with different content")
        blockers = set()
        if status == "unknown":
            blockers.add("unknown-component-identity")
        if window is None:
            blockers.add("unknown-window")
        self._components[component_id] = {
            "kind": kind,
            "scope_id": scope_id,
            "unit": unit,
            "quantum": quantum,
            "window_id": window,
            "ceiling": ceiling,
            "used": used,
            "C": 0,
            "R": 0,
            "blockers": blockers,
            "fingerprint": normalized,
        }
        return "applied"

    def _validate_reservation_common(self, event, event_name, amount_name):
        boundary_id = _identifier(event["boundary_id"], "boundary_id")
        boundary = self._boundaries.get(boundary_id)
        if boundary is None:
            raise ValidationError("unknown boundary")
        _same_binding(event["binding"], boundary["binding"])
        amount = _integer(event[amount_name], amount_name, 0 if amount_name == "actual" else 1)
        components = event["components"]
        if type(components) is not list:
            raise ValidationError(event_name + ".components must be a list")
        claims = {}
        for index, row in enumerate(components):
            name = event_name + ".components[" + str(index) + "]"
            _exact_keys(row, ("component_id", "unit", "quantum", "window_id", "amount"), name)
            component_id = _identifier(row["component_id"], name + ".component_id")
            if component_id in claims:
                raise ValidationError("duplicate component claim")
            component = self._components.get(component_id)
            if component is None:
                raise ValidationError("unknown component: " + component_id)
            unit = _identifier(row["unit"], name + ".unit")
            quantum = _integer(row["quantum"], name + ".quantum", 1)
            window = row["window_id"]
            if window is not None:
                _identifier(window, name + ".window_id")
            if (unit, quantum, window) != (
                component["unit"],
                component["quantum"],
                component["window_id"],
            ):
                raise ValidationError("component claim binding mismatch")
            claims[component_id] = _integer(row["amount"], name + ".amount")
        if set(claims) != set(boundary["component_ids"]):
            raise ValidationError("component claim inventory differs from frozen boundary")
        return boundary_id, boundary, self._accounts[boundary["account_key"]], amount, claims

    def _apply_reservation(self, event):
        _exact_keys(
            event,
            (
                "event_id",
                "type",
                "reservation_id",
                "effect_id",
                "boundary_id",
                "binding",
                "upper_bound",
                "components",
            ),
            "reservation_created",
        )
        reservation_id = _identifier(event["reservation_id"], "reservation_id")
        effect_id = _identifier(event["effect_id"], "effect_id")
        normalized = _canonical(_without_event_id(event))
        if reservation_id in self._reservations:
            if self._reservations[reservation_id]["fingerprint"] == normalized:
                return "duplicate"
            raise ConflictError("reservation_id reused with different content")
        if any(row["effect_id"] == effect_id for row in self._reservations.values()):
            raise ConflictError("effect_id already has a reservation")
        boundary_id, boundary, account, upper, claims = self._validate_reservation_common(
            event, "reservation_created", "upper_bound"
        )
        if account["current_boundary_id"] != boundary_id:
            raise AdmissionError("reservation targets a superseded boundary")
        if boundary["blockers"] or account["blockers"]:
            raise AdmissionError("boundary accounting is unknown")
        if account["C"] + account["R"] + upper > boundary["B"]:
            raise AdmissionError("recovery allowance exceeded")
        for component_id, amount in claims.items():
            component = self._components[component_id]
            if component["blockers"]:
                raise AdmissionError("component accounting is unknown")
            total = component["used"] + component["C"] + component["R"] + amount
            if total > component["ceiling"]:
                raise AdmissionError("component ceiling exceeded: " + component_id)
        account["R"] += upper
        for component_id, amount in claims.items():
            self._components[component_id]["R"] += amount
        self._reservations[reservation_id] = {
            "effect_id": effect_id,
            "boundary_id": boundary_id,
            "binding": copy.deepcopy(boundary["binding"]),
            "upper_bound": upper,
            "components": claims,
            "status": "reserved",
            "actual": None,
            "component_actual": None,
            "fingerprint": normalized,
            "unknown_fingerprint": None,
            "settlement_id": None,
        }
        return "applied"

    def _apply_unknown(self, event):
        _exact_keys(
            event,
            (
                "event_id",
                "type",
                "reservation_id",
                "effect_id",
                "boundary_id",
                "binding",
            ),
            "effect_unknown",
        )
        reservation_id = _identifier(event["reservation_id"], "reservation_id")
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            raise ValidationError("unknown reservation")
        _identifier(event["effect_id"], "effect_id")
        _identifier(event["boundary_id"], "boundary_id")
        _same_binding(event["binding"], reservation["binding"])
        if event["effect_id"] != reservation["effect_id"] or event["boundary_id"] != reservation["boundary_id"]:
            raise ValidationError("unknown-effect identity mismatch")
        normalized = _canonical(_without_event_id(event))
        if reservation["status"] == "unknown":
            if reservation["unknown_fingerprint"] == normalized:
                return "duplicate"
            raise ConflictError("conflicting unknown-effect event")
        if reservation["status"] == "settled":
            raise ConflictError("settled reservation cannot become unknown")
        reservation["status"] = "unknown"
        reservation["unknown_fingerprint"] = normalized
        return "applied"

    def _apply_settlement(self, event):
        _exact_keys(
            event,
            (
                "event_id",
                "type",
                "settlement_id",
                "reservation_id",
                "effect_id",
                "boundary_id",
                "binding",
                "actual",
                "components",
            ),
            "reservation_settled",
        )
        settlement_id = _identifier(event["settlement_id"], "settlement_id")
        normalized = _canonical(_without_event_id(event))
        if settlement_id in self._settlements:
            if self._settlements[settlement_id] == normalized:
                return "duplicate"
            raise ConflictError("settlement_id reused with different content")
        reservation_id = _identifier(event["reservation_id"], "reservation_id")
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            raise ValidationError("unknown reservation")
        boundary_id, boundary, account, actual, actual_components = self._validate_reservation_common(
            event, "reservation_settled", "actual"
        )
        if boundary_id != reservation["boundary_id"] or event["effect_id"] != reservation["effect_id"]:
            raise ValidationError("settlement identity mismatch")
        if reservation["status"] == "settled":
            raise ConflictError("reservation already settled under another identity")
        if actual > reservation["upper_bound"]:
            raise ValidationError("actual exceeds reserved upper bound")
        if set(actual_components) != set(reservation["components"]):
            raise ValidationError("settlement component inventory differs from reservation")
        for component_id, amount in actual_components.items():
            if amount > reservation["components"][component_id]:
                raise ValidationError("component actual exceeds reserved upper bound")

        account["R"] -= reservation["upper_bound"]
        account["C"] += actual
        for component_id, reserved in reservation["components"].items():
            component = self._components[component_id]
            component["R"] -= reserved
            component["C"] += actual_components[component_id]
        reservation["status"] = "settled"
        reservation["actual"] = actual
        reservation["component_actual"] = actual_components
        reservation["settlement_id"] = settlement_id
        self._settlements[settlement_id] = normalized
        return "applied"

    def _apply_normal(self, event):
        _exact_keys(
            event,
            (
                "event_id",
                "type",
                "source_id",
                "boundary_id",
                "binding",
                "amount",
            ),
            "normal_use_verified",
        )
        source_id = _identifier(event["source_id"], "source_id")
        normalized = _canonical(_without_event_id(event))
        if source_id in self._normal_sources:
            if self._normal_sources[source_id]["fingerprint"] == normalized:
                return "duplicate"
            raise ConflictError("normal source id reused with different content")
        boundary_id = _identifier(event["boundary_id"], "boundary_id")
        boundary = self._boundaries.get(boundary_id)
        if boundary is None:
            raise ValidationError("unknown boundary")
        _same_binding(event["binding"], boundary["binding"])
        account = self._accounts[boundary["account_key"]]
        if account["current_boundary_id"] != boundary_id:
            raise ValidationError("normal use targets a superseded boundary")
        amount = _integer(event["amount"], "amount", 1)
        self._normal_sources[source_id] = {
            "boundary_id": boundary_id,
            "amount": amount,
            "used_by": None,
            "fingerprint": normalized,
        }
        return "applied"

    def _apply_reset(self, event):
        _exact_keys(
            event,
            ("event_id", "type", "boundary_id", "binding", "identity_status"),
            "provider_counter_reset",
        )
        boundary_id = _identifier(event["boundary_id"], "boundary_id")
        boundary = self._boundaries.get(boundary_id)
        if boundary is None:
            raise ValidationError("unknown boundary")
        _same_binding(event["binding"], boundary["binding"])
        account = self._accounts[boundary["account_key"]]
        status = event["identity_status"]
        if status == "unknown":
            account["blockers"].add("unknown-counter-reset-identity")
        elif status == "reconciled":
            account["blockers"].discard("unknown-counter-reset-identity")
        else:
            raise ValidationError("identity_status must be reconciled or unknown")
        return "applied"

    def _apply_restart(self, event):
        _exact_keys(event, ("event_id", "type"), "process_restarted")
        return "applied"

    def observe(self, boundary_id):
        boundary_id = _identifier(boundary_id, "boundary_id")
        boundary = self._boundaries.get(boundary_id)
        if boundary is None:
            raise ValidationError("unknown boundary")
        account = self._accounts[boundary["account_key"]]
        blockers = sorted(boundary["blockers"] | account["blockers"])
        available = None
        if not blockers and boundary["B"] is not None:
            available = max(0, boundary["B"] - account["C"] - account["R"])
        reservations = []
        for reservation_id in sorted(self._reservations):
            row = self._reservations[reservation_id]
            reservation_boundary = self._boundaries[row["boundary_id"]]
            if reservation_boundary["account_key"] == boundary["account_key"]:
                reservations.append(
                    {
                        "reservation_id": reservation_id,
                        "effect_id": row["effect_id"],
                        "status": row["status"],
                        "upper_bound": row["upper_bound"],
                        "actual": row["actual"],
                    }
                )
        pending = sum(
            row["amount"]
            for row in self._normal_sources.values()
            if row["boundary_id"] == boundary_id and row["used_by"] is None
        )
        return {
            "boundary_id": boundary_id,
            "binding": copy.deepcopy(boundary["binding"]),
            "N": boundary["N"],
            "p": boundary["p"],
            "q": boundary["q"],
            "B": boundary["B"],
            "C": account["C"],
            "R": account["R"],
            "available": available,
            "pending_normal_use": pending,
            "blockers": blockers,
            "reservations": reservations,
        }

    def observe_component(self, component_id):
        component_id = _identifier(component_id, "component_id")
        component = self._components.get(component_id)
        if component is None:
            raise ValidationError("unknown component")
        blockers = sorted(component["blockers"])
        available = None
        if not blockers:
            available = max(
                0,
                component["ceiling"]
                - component["used"]
                - component["C"]
                - component["R"],
            )
        return {
            "component_id": component_id,
            "kind": component["kind"],
            "scope_id": component["scope_id"],
            "unit": component["unit"],
            "quantum": component["quantum"],
            "window_id": component["window_id"],
            "used": component["used"],
            "ceiling": component["ceiling"],
            "C": component["C"],
            "R": component["R"],
            "available": available,
            "blockers": blockers,
        }

    def to_json(self):
        return _canonical({"format": FORMAT, "events": self._events}) + "\n"

    @classmethod
    def from_json(cls, raw):
        if type(raw) is not str:
            raise ValidationError("serialized ledger must be text")
        try:
            payload = json.loads(raw, object_pairs_hook=_object_no_duplicate_keys)
        except ValidationError:
            raise
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValidationError("invalid serialized ledger JSON") from exc
        _exact_keys(payload, ("format", "events"), "serialized ledger")
        if payload["format"] != FORMAT:
            raise ValidationError("unknown serialized ledger format")
        return replay(payload["events"])


def replay(events):
    if type(events) not in (list, tuple):
        raise ValidationError("events must be a list or tuple")
    if len(events) > MAX_EVENTS:
        raise ValidationError("event sequence exceeds " + str(MAX_EVENTS))
    instance = Ledger()
    for event in events:
        instance.append(event)
    return instance
