"""Strict construction packets. No model output is an authority record."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import PurePosixPath


class Refused(ValueError):
    pass


JOB_TOOLS = ('list_files', 'read_file', 'search', 'write_file', 'run_command', 'fetch_source')


def require(value, reason):
    if not value:
        raise Refused(reason)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(filename) -> str:
    """Bounded memory even when 100 clients verify a large executable together."""
    result = hashlib.sha256()
    with open(filename, 'rb') as stream:
        while chunk := stream.read(262144):
            result.update(chunk)
    return result.hexdigest()


def encoded(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":")).encode()


def strict_json(data: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result
    try:
        return json.loads(data, object_pairs_hook=pairs,
                          parse_constant=lambda x: require(False, f"nonfinite: {x}"))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Refused(f"invalid JSON: {exc}") from exc


def keys(obj, expected):
    require(type(obj) is dict and set(obj) == set(expected),
            f"expected fields: {','.join(expected)}")


def integer(value, low, high):
    require(type(value) is int and low <= value <= high,
            f"expected integer {low}..{high}")


def identifier(value):
    require(type(value) is str and re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", value),
            "invalid identifier")
    return value


def path(value):
    require(type(value) is str and value and len(value) <= 240, "invalid path")
    p = PurePosixPath(value)
    require(not p.is_absolute() and str(p) == value and
            all(re.fullmatch(r"[A-Za-z0-9_.-]+", part) and part not in {".", ".."}
                and not part.endswith((".", " ")) for part in p.parts),
            "path must be canonical relative POSIX path")
    for part in p.parts:
        require(part.lower().split('.')[0] not in
                {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(10)),
                 *(f"lpt{i}" for i in range(10))}, "reserved Windows path")
    require(not any(part.startswith('.') for part in p.parts), "hidden input forbidden")
    return value


def timestamp(value):
    require(type(value) is str, "deadline must be UTC string")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Refused("invalid UTC deadline") from exc
    require(dt.utcoffset() is not None and dt.utcoffset().total_seconds() == 0,
            "deadline requires UTC")
    return dt.timestamp()


def now():
    return datetime.now(timezone.utc).isoformat()


def validate_plan(plan):
    keys(plan, ["version", "run_id", "parent_goal", "authorization", "source_commit",
                "deadline_utc", "limits", "route", "jobs"])
    require(type(plan["version"]) is int and plan["version"] == 1, "unsupported plan version")
    identifier(plan["run_id"])
    identifier(plan["parent_goal"])
    require(type(plan["authorization"]) is str and 10 <= len(plan["authorization"]) <= 4000,
            "specific owner authorization reference required")
    require(type(plan["source_commit"]) is str and
            re.fullmatch(r"[0-9a-f]{40}", plan["source_commit"]), "full source commit required")
    timestamp(plan["deadline_utc"])
    lim = plan["limits"]
    keys(lim, ["model_slots", "test_slots", "domain_slots", "max_dispatches",
               "max_attempts", "timeout_seconds", "output_bytes", "input_bytes"])
    for name, low, high in [("model_slots", 1, 50), ("test_slots", 1, 4),
                            ("domain_slots", 1, 8), ("max_dispatches", 1, 10000),
                            ("max_attempts", 1, 5), ("timeout_seconds", 1, 1200),
                            ("output_bytes", 1024, 8 * 1024 * 1024),
                            ("input_bytes", 1024, 2 * 1024 * 1024)]:
        integer(lim[name], low, high)
    route = plan["route"]
    keys(route, ["backend", "executable", "sha256", "model", "capacity_basis"])
    require(route["backend"] in {"devin", "fixture"}, "unqualified automatic provider adapter")
    require(type(route["executable"]) is str and route["executable"], "executable required")
    require(type(route["sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", route["sha256"]),
            "executable digest required")
    require(route["model"] == ("swe-2-max" if route["backend"] == "devin" else "fixture"),
            "unqualified model; no implicit substitution")
    require(type(route["capacity_basis"]) is str and len(route["capacity_basis"]) >= 10,
            "capacity evidence reference required")
    jobs = plan["jobs"]
    require(type(jobs) is list and 1 <= len(jobs) <= 500, "1..500 jobs required")
    ids = set()
    for job in jobs:
        keys(job, ["id", "domain", "kind", "brief", "inputs", "depends_on", "allowed_paths"])
        identifier(job["id"])
        identifier(job["domain"])
        require(job["id"] not in ids, "duplicate claim/job")
        ids.add(job["id"])
        require(job["kind"] in {"research", "develop", "review", "synthesis"}, "invalid job kind")
        require(type(job["brief"]) is str and 10 <= len(job["brief"]) <= 32000, "bounded brief required")
        for field in ["inputs", "depends_on", "allowed_paths"]:
            value = job[field]
            require(type(value) is list and len(value) <= 200 and
                    all(type(x) is str for x in value) and len(set(value)) == len(value),
                    f"invalid {field}")
        for value in job["inputs"] + job["allowed_paths"]:
            path(value)
        require(len({x.casefold() for x in job['allowed_paths']}) == len(job['allowed_paths']),
                "case-aliased write paths")
        require(not job["allowed_paths"] or job["kind"] == "develop", "only development proposes files")
        for value in job["allowed_paths"]:
            require(value.startswith(("experiments/", "tools/", "docs/")),
                    "construction writes limited to experiments/tools/docs")
        require(job["id"] not in job["depends_on"], "self dependency")
    done = set()
    while len(done) < len(ids):
        ready = {j["id"] for j in jobs if set(j["depends_on"]) <= done} - done
        require(ready, "dependency cycle or missing job")
        done |= ready
    return plan


def validate_allowed_tools(job):
    """Validate the explicit native-v3 tool surface for one job."""
    value = job.get('allowed_tools')
    require(type(value) is list and len(value) <= len(JOB_TOOLS) and
            all(type(name) is str for name in value) and len(value) == len(set(value)),
            'explicit unique allowed_tools required')
    require(set(value) <= set(JOB_TOOLS), 'unknown allowed_tools entry')
    require(not job['allowed_paths'] or 'write_file' in value,
            'writable job must allow write_file')
    require('write_file' not in value or
            (job['kind'] == 'develop' and bool(job['allowed_paths'])),
            'write_file requires a development job with allowed paths')
    return tuple(name for name in JOB_TOOLS if name in value)


def validate_filing(value, job, input_refs):
    keys(value, ["job_id", "summary", "findings", "evidence", "dissent", "limitations", "files"])
    require(value["job_id"] == job["id"], "wrong job identity")
    require(type(value["summary"]) is str and 1 <= len(value["summary"]) <= 8000,
            "bounded summary required")
    for name in ["findings", "evidence", "dissent", "limitations"]:
        require(type(value[name]) is list and len(value[name]) <= 100 and
                all(type(x) is str and len(x) <= 8000 for x in value[name]), f"invalid {name}")
    require(set(value["evidence"]) <= set(input_refs), "unbound evidence citation")
    require(type(value["files"]) is list and len(value["files"]) <= 30, "invalid proposed files")
    seen = set()
    for item in value["files"]:
        keys(item, ["path", "content"])
        name = path(item["path"])
        require(name in job["allowed_paths"] and name.casefold() not in seen,
                "unapproved/duplicate proposed path")
        seen.add(name.casefold())
        require(type(item["content"]) is str and len(item["content"].encode()) <= 262144,
                "proposed file too large")
    return value
