"""Native connecting CLI for the read-only construction access service."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .p2_access import AccessClient, AccessRefused, MAX_ARTIFACT_READ, MAX_PAGE_SIZE


def _token(filename):
    path = Path(filename).resolve(strict=True)
    if not path.is_file() or path.stat().st_size > 4096:
        raise AccessRefused("authentication_refused", "token file must be a small regular file")
    token = path.read_text(encoding="utf-8").strip()
    if not token:
        raise AccessRefused("authentication_refused", "token file is empty")
    return token


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--socket", required=True)
    result.add_argument("--token-file", required=True)
    result.add_argument("--timeout", type=float, default=2.0)
    result.add_argument("--cache")
    result.add_argument("--allow-stale", action="store_true")
    subparsers = result.add_subparsers(dest="operation", required=True)
    for name in ("status", "tasks", "task", "events", "artifact"):
        command = subparsers.add_parser(name)
        command.add_argument("--project", required=True)
        if name == "tasks":
            command.add_argument("--limit", type=int, default=50)
            command.add_argument("--page-token", type=int, default=0)
        elif name == "task":
            command.add_argument("--task-id", required=True)
        elif name == "events":
            command.add_argument("--after-cursor", type=int, required=True)
            command.add_argument("--limit", type=int, default=50)
        elif name == "artifact":
            command.add_argument("--handle", required=True)
            command.add_argument("--offset", type=int, default=0)
            command.add_argument("--limit", type=int, default=64 * 1024)
    return result


def request_params(args):
    params = {"project": args.project}
    if args.operation == "tasks":
        if not 1 <= args.limit <= MAX_PAGE_SIZE:
            raise AccessRefused("malformed_request", "task page limit exceeds the client bound")
        params.update(limit=args.limit, page_token=args.page_token)
    elif args.operation == "task":
        params["task_id"] = args.task_id
    elif args.operation == "events":
        if not 1 <= args.limit <= MAX_PAGE_SIZE:
            raise AccessRefused("malformed_request", "event page limit exceeds the client bound")
        params.update(after_cursor=args.after_cursor, limit=args.limit)
    elif args.operation == "artifact":
        if not 1 <= args.limit <= MAX_ARTIFACT_READ:
            raise AccessRefused("malformed_request", "artifact limit exceeds the client bound")
        params.update(handle=args.handle, offset=args.offset, limit=args.limit)
    return params


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        client = AccessClient(args.socket, _token(args.token_file), timeout=args.timeout, cache_path=args.cache)
        response = client.request(args.operation, request_params(args), allow_stale=args.allow_stale)
        print(json.dumps(response, sort_keys=True, ensure_ascii=True))
        return 0 if response.get("ok") else 2
    except (AccessRefused, OSError, UnicodeError) as exc:
        code = exc.code if isinstance(exc, AccessRefused) else "client_refused"
        print(json.dumps({"ok": False, "error": {"code": code, "message": str(exc)}}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
