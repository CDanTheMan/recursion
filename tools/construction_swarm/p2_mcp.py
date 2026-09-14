"""Thin stdio MCP bridge for the read-only construction access protocol.

This process is only a client.  It never starts, supervises, or changes the
construction service.
"""
from __future__ import annotations

import argparse
import json
import sys

from .p2_access import AccessClient, AccessRefused, MAX_REQUEST_BYTES
from .p2_cli import _token


TOOL_ARGUMENTS = {
    "construction_status": {
        "type": "object", "additionalProperties": False,
        "properties": {"project": {"type": "string"}}, "required": ["project"],
    },
    "construction_tasks": {
        "type": "object", "additionalProperties": False,
        "properties": {
            "project": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            "page_token": {"type": "integer", "minimum": 0},
        },
        "required": ["project"],
    },
    "construction_task": {
        "type": "object", "additionalProperties": False,
        "properties": {"project": {"type": "string"}, "task_id": {"type": "string"}},
        "required": ["project", "task_id"],
    },
    "construction_events": {
        "type": "object", "additionalProperties": False,
        "properties": {
            "project": {"type": "string"}, "after_cursor": {"type": "integer", "minimum": 0},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
        },
        "required": ["project", "after_cursor"],
    },
    "construction_artifact": {
        "type": "object", "additionalProperties": False,
        "properties": {
            "project": {"type": "string"}, "handle": {"type": "string"},
            "offset": {"type": "integer", "minimum": 0},
            "limit": {"type": "integer", "minimum": 1, "maximum": 1048576},
        },
        "required": ["project", "handle"],
    },
}

TOOL_DESCRIPTIONS = {
    "construction_status": "Read a bounded, freshness-labelled project status snapshot.",
    "construction_tasks": "Read one bounded page of project tasks.",
    "construction_task": "Read one project-scoped task.",
    "construction_events": "Read bounded events after a cursor; replay gaps require a snapshot.",
    "construction_artifact": "Read a bounded chunk from a project-scoped immutable artifact handle.",
}

TOOL_OPERATIONS = {name: name.removeprefix("construction_") for name in TOOL_ARGUMENTS}


def _result(identifier, value):
    return {"jsonrpc": "2.0", "id": identifier, "result": value}


def _error(identifier, code, message, data=None):
    value = {"code": code, "message": message}
    if data is not None:
        value["data"] = data
    return {"jsonrpc": "2.0", "id": identifier, "error": value}


def _tool_result(response):
    text = json.dumps(response, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return {"content": [{"type": "text", "text": text}], "isError": not response.get("ok", False)}


class McpBridge:
    def __init__(self, client):
        self.client = client

    def handle(self, request):
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return _error(request.get("id") if isinstance(request, dict) else None, -32600, "Invalid Request")
        identifier = request.get("id")
        method = request.get("method")
        if method == "initialize":
            params = request.get("params")
            if not isinstance(params, dict):
                return _error(identifier, -32602, "Invalid params")
            return _result(identifier, {
                "protocolVersion": params.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "recursion-construction-readonly", "version": "1"},
                "instructions": "Read-only connector; freshness and unavailable fields are authoritative.",
            })
        if method == "notifications/initialized":
            return None
        if method == "ping":
            return _result(identifier, {})
        if method == "tools/list":
            tools = [
                {"name": name, "description": TOOL_DESCRIPTIONS[name], "inputSchema": TOOL_ARGUMENTS[name]}
                for name in TOOL_ARGUMENTS
            ]
            return _result(identifier, {"tools": tools})
        if method == "tools/call":
            params = request.get("params")
            if not isinstance(params, dict) or set(params) != {"name", "arguments"}:
                return _error(identifier, -32602, "Invalid params")
            name = params.get("name")
            arguments = params.get("arguments")
            if name not in TOOL_OPERATIONS or not isinstance(arguments, dict):
                return _error(identifier, -32602, "Unknown read tool or invalid arguments")
            operation = TOOL_OPERATIONS[name]
            values = dict(arguments)
            if operation == "tasks":
                values.setdefault("limit", 50)
                values.setdefault("page_token", 0)
            elif operation == "events":
                values.setdefault("limit", 50)
            elif operation == "artifact":
                values.setdefault("offset", 0)
                values.setdefault("limit", 64 * 1024)
            try:
                response = self.client.request(operation, values, allow_stale=True)
            except AccessRefused as exc:
                response = {"ok": False, "error": {"code": exc.code, "message": exc.message, **exc.detail}}
            return _result(identifier, _tool_result(response))
        return _error(identifier, -32601, "Method not found")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--cache")
    args = parser.parse_args(argv)
    try:
        bridge = McpBridge(AccessClient(
            args.socket, _token(args.token_file), timeout=args.timeout, cache_path=args.cache,
        ))
    except (AccessRefused, OSError, UnicodeError) as exc:
        print(json.dumps(_error(None, -32000, str(exc)), sort_keys=True), flush=True)
        return 2
    while True:
        line = sys.stdin.buffer.readline(MAX_REQUEST_BYTES + 2)
        if not line:
            return 0
        if len(line) > MAX_REQUEST_BYTES + 1 or not line.endswith(b"\n"):
            print(json.dumps(_error(None, -32600, "Request exceeds stdio byte bound"), sort_keys=True), flush=True)
            return 2
        try:
            request = json.loads(line)
            response = bridge.handle(request)
        except (UnicodeDecodeError, json.JSONDecodeError):
            response = _error(None, -32700, "Parse error")
        except Exception:
            response = _error(None, -32603, "Internal error")
        if response is not None:
            print(json.dumps(response, sort_keys=True, separators=(",", ":"), ensure_ascii=True), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
