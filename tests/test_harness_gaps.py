"""Fake-only coverage for harness branches the main suite left dark."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.v3.harness import cooldowns, config, doctor, routing, run, state, streams
from scripts.v3.harness.capabilities import select_candidates
from scripts.v3.harness.errors import HarnessError

ROOT = Path(__file__).resolve().parents[1]


def _completed(argv: list[str], code: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(argv, code, stdout, stderr)


def test_module_entry_points_use_the_fixture_provider() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    module = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", "-m", "scripts.v3.harness", "--task", "Say hello"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )
    assert module.returncode == 0, module.stderr
    assert json.loads(module.stdout)["task"] == "Say hello"
    script = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(ROOT / "scripts" / "v3" / "harness" / "run.py"), "--task", "Say hello"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )
    bare = os.environ.copy()
    bare.pop("PYTHONPATH", None)
    direct = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(ROOT / "scripts" / "v3" / "harness" / "__main__.py"), "--task", "Say hello"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=bare,
        check=False,
    )
    assert direct.returncode == 0, direct.stderr
    assert script.returncode == 0, script.stderr
    assert run.main(["--task", "   "]) == 2
    assert run.main(["--task", "Say hello", "--provider", "missing"]) == 2


def test_stream_parsers_reject_bad_lines_and_read_cursor_blocks() -> None:
    text = "\n".join(
        [
            '{"type":"assistant","message":{"content":"hello "}}',
            '{"type":"assistant","message":{"content":[{"text":"world"}, "skip", {"text": 1}]}}',
            '{"type":"assistant","message":"nope"}',
            '{"type":"system"}',
        ]
    )
    assert streams.parse_transcript("cursor", text)["text"] == "hello world"
    result = '{"type":"result","result":"done"}\n{"type":"assistant","message":{"content":"ignored"}}'
    assert streams.parse_transcript("cursor", result)["text"] == "done"
    gemini = '\n{"type":"message","role":"assistant","content":"hi"}\n{"type":"message","role":"user","content":"no"}\n'
    assert streams.parse_transcript("gemini", gemini)["text"] == "hi"
    assert streams.parse_transcript("gemini", '{"type":"message","role":"assistant","content":1}')["text"] == ""
    opencode = '{"type":"text","part":{"text":"a"}}\n{"type":"text","part":"no"}'
    assert streams.parse_transcript("opencode", opencode)["text"] == "a"
    with pytest.raises(HarnessError, match="not JSON"):
        streams.parse_transcript("gemini", "{")
    with pytest.raises(HarnessError, match="not an object"):
        streams.parse_transcript("gemini", "1")
    with pytest.raises(HarnessError, match="no transcript parser"):
        streams.parse_transcript("claude", "{}")


def test_config_rejects_bad_files_and_helper_inputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(HarnessError, match="missing provider config"):
        config.load_config(missing)
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    with pytest.raises(HarnessError, match="not JSON"):
        config.load_config(broken)
    array = tmp_path / "array.json"
    array.write_text("[]", encoding="utf-8")
    with pytest.raises(HarnessError, match="must be an object"):
        config.load_config(array)
    secret = tmp_path / "secret.json"
    secret.write_text('{"token": "x", "nested": [{"password": "y"}]}', encoding="utf-8")
    with pytest.raises(HarnessError, match="not allowed"):
        config.load_config(secret)
    rootless = tmp_path / "rootless.json"
    rootless.write_text("{}", encoding="utf-8")
    with pytest.raises(HarnessError, match="rootless.json:"):
        config.load_config(rootless)

    monkeypatch.setattr(config, "_VALIDATOR", None)
    monkeypatch.setattr(config, "SCHEMA_PATH", tmp_path / "no-schema.json")
    with pytest.raises(HarnessError, match="missing config schema"):
        config.load_config(ROOT / "config" / "harness.json")
    bad_schema = tmp_path / "schema.json"
    bad_schema.write_text("{", encoding="utf-8")
    monkeypatch.setattr(config, "SCHEMA_PATH", bad_schema)
    monkeypatch.setattr(config, "_VALIDATOR", None)
    with pytest.raises(HarnessError, match="config schema is not JSON"):
        config.load_config(ROOT / "config" / "harness.json")

    assert config.default_config_path() == ROOT / "config" / "harness.json"
    assert config._schema_location([]) == ""
    assert config._schema_location([0, "name"]) == "[0].name"
    assert config._schema_location(["providers", 0]) == "providers[0]"
    with pytest.raises(HarnessError, match="keys mismatch"):
        config._require_exact_keys({"a": 1}, {"b"}, "sample")
    with pytest.raises(HarnessError, match="non-empty list"):
        config._providers([])
    with pytest.raises(HarnessError, match="must be an object"):
        config._providers(["nope"])
    with pytest.raises(HarnessError, match="unknown provider"):
        config._providers([{"name": "nope", "argv": [], "capabilities": [], "enabled": True, "timeout_seconds": 1}])
    with pytest.raises(HarnessError, match="must be an object"):
        config._routing([], [])
    with pytest.raises(HarnessError, match="must be an object"):
        config._weights([], [])
    with pytest.raises(HarnessError, match="must name each provider"):
        config._weights({}, ["fixture"])
    with pytest.raises(HarnessError, match="integer >= 1"):
        config._weights({"fixture": True}, ["fixture"])
    with pytest.raises(HarnessError, match="must be an object"):
        config._orchestration([])
    with pytest.raises(HarnessError, match="must be an object"):
        config._review([])
    with pytest.raises(HarnessError, match="must be an object"):
        config._landing([])
    with pytest.raises(HarnessError, match="must be a boolean"):
        config._bool("yes", "review.accept_unreviewed")
    with pytest.raises(HarnessError, match="git ref"):
        config._git_ref("bad\nref", "landing.base_ref")
    with pytest.raises(HarnessError, match="must be an object"):
        config._budgets([])
    assert config._optional_int(None, "budgets.max_input_tokens") is None
    with pytest.raises(HarnessError, match="integer >= 0"):
        config._optional_int(-1, "budgets.max_input_tokens")
    with pytest.raises(HarnessError, match="number >= 0"):
        config._optional_number(True, "budgets.max_cost")
    assert config._optional_number(1, "budgets.max_cost") == 1.0
    with pytest.raises(HarnessError, match="integer >= 1"):
        config._positive_int(0, "orchestration.concurrency")
    with pytest.raises(HarnessError, match="unknown providers"):
        config.starter_config({"not-a-provider"})
    with pytest.raises(HarnessError, match="non-empty strings"):
        config._string_tuple([""], "routing.preference")
    with pytest.raises(HarnessError, match="duplicate"):
        config._string_tuple(["a", "a"], "routing.preference")
    with pytest.raises(HarnessError, match="non-empty list"):
        config._string_tuple("execute", "routing.required_capabilities")
    fresh = config.starter_config({"fixture"})
    duplicated = json.loads(json.dumps(fresh["providers"]))
    duplicated.append(dict(duplicated[0]))
    with pytest.raises(HarnessError, match="duplicate provider"):
        config._providers(duplicated)
    not_bool = json.loads(json.dumps(fresh["providers"]))
    not_bool[0]["enabled"] = 1
    with pytest.raises(HarnessError, match="enabled must be a boolean"):
        config._providers(not_bool)
    wrong_argv = json.loads(json.dumps(fresh["providers"]))
    wrong_argv[0]["argv"] = ["other"]
    with pytest.raises(HarnessError, match="argv does not match"):
        config._providers(wrong_argv)
    wrong_caps = json.loads(json.dumps(fresh["providers"]))
    wrong_caps[0]["capabilities"] = ["nope"]
    with pytest.raises(HarnessError, match="capabilities do not match"):
        config._providers(wrong_caps)
    with pytest.raises(HarnessError, match="missing providers"):
        config._providers(fresh["providers"][:1])
    names = list(config.adapters())
    routing_value = {
        "backoff_seconds": True,
        "cooldown_seconds": 1,
        "preference": names,
        "required_capabilities": ["execute"],
        "retries": 0,
        "weights": {name: 1 for name in names},
    }
    with pytest.raises(HarnessError, match="retries"):
        config._routing({**routing_value, "retries": True}, names)
    with pytest.raises(HarnessError, match="backoff_seconds"):
        config._routing(routing_value, names)
    with pytest.raises(HarnessError, match="cooldown_seconds"):
        config._routing({**routing_value, "backoff_seconds": 1, "cooldown_seconds": True}, names)
    with pytest.raises(HarnessError, match="list each provider once"):
        config._routing({**routing_value, "backoff_seconds": 1, "preference": names[1:]}, names)
    with pytest.raises(HarnessError, match="is a directory"):
        config.write_starter(tmp_path, {"fixture"})
    existing = tmp_path / "starter.json"
    existing.write_text("{}\n", encoding="utf-8")
    with pytest.raises(HarnessError, match="overwrite"):
        config.write_starter(existing, {"fixture"})
    written = config.write_starter(existing, {"fixture"}, force=True)
    assert written["providers"]
    original_check = config._check_schema
    monkeypatch.setattr(config, "_check_schema", lambda payload, source: None)
    versioned = tmp_path / "version.json"
    versioned.write_text(
        (ROOT / "config" / "harness.json").read_text(encoding="utf-8").replace('"version": 1', '"version": 2', 1),
        encoding="utf-8",
    )
    with pytest.raises(HarnessError, match="version must be 1"):
        config.load_config(versioned)
    import builtins

    real_import = builtins.__import__

    def block_jsonschema(name: str, *args, **kwargs):
        if name == "jsonschema":
            raise ImportError("blocked")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block_jsonschema)
    monkeypatch.setattr(config, "_VALIDATOR", None)
    monkeypatch.setattr(config, "SCHEMA_PATH", ROOT / "config" / "harness.schema.json")
    monkeypatch.setattr(config, "_check_schema", original_check)
    with pytest.raises(HarnessError, match="jsonschema is required"):
        config.load_config(ROOT / "config" / "harness.json")


def test_candidate_selection_names_the_failure() -> None:
    loaded = config.load_config()
    with pytest.raises(HarnessError, match="unknown provider"):
        select_candidates(loaded, provider="missing")
    disabled = json.loads(json.dumps(loaded))
    for item in disabled["providers"]:
        if item["name"] == "fixture":
            item["enabled"] = False
    with pytest.raises(HarnessError, match="is disabled"):
        select_candidates(disabled, provider="fixture")
    for item in disabled["providers"]:
        item["enabled"] = False
    with pytest.raises(HarnessError, match="no enabled provider"):
        select_candidates(disabled)


def test_route_admission_refuses_unknown_fixtures() -> None:
    with pytest.raises(HarnessError, match="not an M1B fixture id"):
        routing.select_route("nope")
    with pytest.raises(HarnessError, match="missing M1B fixture"):
        routing.select_route("F-M1B-999")
    with pytest.raises(HarnessError, match="was not selected"):
        routing.require_selected({"status": "refused"})


def test_cooldown_file_keeps_only_active_rows(tmp_path: Path) -> None:
    path = tmp_path / "cooldowns.json"
    store = cooldowns.CooldownStore(path)
    assert store.active(now=10) == {}
    store.record("claude", "rate-limited", 50)
    assert store.active(now=10)["claude"]["reason"] == "rate-limited"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["providers"]["grok"] = "not-a-row"
    payload["providers"]["codex"] = {"reason": "quota-exhausted", "until": "not-a-time"}
    payload["providers"]["gemini"] = {"reason": "auth-expired", "until": "1970-01-01T00:00:00Z"}
    path.write_text(json.dumps(payload), encoding="utf-8")
    kept = store.active(now=10)
    assert "grok" not in kept
    assert kept["codex"]["until"] == "not-a-time"
    assert "gemini" not in kept
    path.write_text("{", encoding="utf-8")
    with pytest.raises(HarnessError, match="malformed cooldown file"):
        store.active()
    path.write_text('{"providers": []}', encoding="utf-8")
    with pytest.raises(HarnessError, match="malformed cooldown file"):
        store.snapshot()
    assert cooldowns.resolve_until(None, True, 10, 5) == 15
    assert cooldowns.resolve_until(None, 4, 10, 5) == 14
    assert cooldowns.resolve_until("not-a-date", None, 10, 5) == 15
    assert cooldowns.resolve_until("2020-01-01T00:00:00Z", 3, 10, 5) == cooldowns._parse("2020-01-01T00:00:00Z")
    assert cooldowns._parse(1) is None


def test_run_store_rejects_malformed_records(tmp_path: Path) -> None:
    store = state.RunStore(tmp_path / "runs")
    with pytest.raises(HarnessError, match="not a run id"):
        store.load("nope")
    run_id = "RUN-" + "ab" * 8
    with pytest.raises(HarnessError, match="unknown run"):
        store.load(run_id)
    with pytest.raises(HarnessError, match="missing run_id"):
        store.update(run_id, lambda record: None)
    path = tmp_path / "runs" / f"{run_id}.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(HarnessError, match="malformed run record"):
        store.load(run_id)
    path.write_text(json.dumps({"run_id": "RUN-" + "cd" * 8}), encoding="utf-8")
    with pytest.raises(HarnessError, match="malformed run record"):
        store.load(run_id)
    path.unlink()
    (tmp_path / "runs" / "RUN-zzzzzzzzzzzzzzzz.json").write_text("{}\n", encoding="utf-8")
    assert store.list_runs() == []
    gone = state.RunStore(tmp_path / "gone")
    real_is_dir = Path.is_dir

    def hidden(self: Path) -> bool:
        if self == gone.root:
            return False
        return real_is_dir(self)

    patch = pytest.MonkeyPatch()
    patch.setattr(Path, "is_dir", hidden)
    try:
        assert gone.list_runs() == []
    finally:
        patch.undo()


def test_doctor_parses_sign_in_without_starting_a_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert doctor._cursor_state('{"authenticated": true}') == "signed-in"
    assert doctor._cursor_state('{"loggedIn": false}') == "signed-out"
    assert doctor._cursor_state('{"status": "Logged In"}') == "signed-in"
    assert doctor._cursor_state('{"status": "not_logged_in"}') == "signed-out"
    assert doctor._cursor_state('{"status": 1}') == "unknown"
    assert doctor._cursor_state("You are logged in") == "signed-in"
    assert doctor._cursor_state("not logged in") == "signed-out"
    assert doctor._cursor_state("nope") == "unknown"
    assert doctor._cursor_state("[1]") == "unknown"
    assert doctor._opencode_state("") == "unknown"
    assert doctor._opencode_state("not json") == "unknown"
    assert doctor._opencode_state("[]") == "signed-out"
    assert doctor._opencode_state('[{"name":"x"}]') == "signed-in"
    assert doctor._opencode_state('{"integrations": []}') == "signed-out"
    assert doctor._opencode_state('{"integrations": ["a"]}') == "signed-in"
    assert doctor._opencode_state('{"credentials": []}') == "signed-out"
    assert doctor._opencode_state('{"extra": 1}') == "signed-in"
    assert doctor._opencode_state("{}") == "signed-out"
    assert doctor._opencode_state("No authenticated integrations") == "signed-out"
    assert doctor._opencode_state("no credentials here") == "signed-out"
    assert doctor._opencode_state("3 credentials") == "signed-in"
    assert doctor._opencode_state("0 credentials") == "signed-out"
    assert doctor._opencode_state("alpha stored") == "signed-in"
    assert doctor._claude_method("nope") is None
    assert doctor._claude_method('{"authMethod": "oauth_token"}') == "oauth_token"
    assert doctor._claude_method('{"authMethod": "nope"}') is None
    assert doctor._claude_method("[1]") is None

    home = tmp_path / "home"
    (home / ".gemini").mkdir(parents=True)
    (home / ".gemini" / "oauth_creds.json").write_text("cached", encoding="utf-8")
    (home / ".grok").mkdir()
    (home / ".local" / "share" / "opencode").mkdir(parents=True)
    assert doctor._signed_in("gemini", None, environ={}, home=home, run=None) == ("signed-in", "cached")
    assert doctor._signed_in("grok", None, environ={}, home=home, run=None) == ("signed-out", None)
    assert doctor._file_auth(home / ".gemini" / "oauth_creds.json") == ("signed-in", "cached")
    (home / ".grok" / "auth.json").write_text("", encoding="utf-8")
    assert doctor._file_auth(home / ".grok" / "auth.json") == ("signed-out", None)

    original_stat = Path.stat
    original_is_file = Path.is_file
    Path.stat = lambda self: (_ for _ in ()).throw(OSError("unreadable"))
    Path.is_file = lambda self: True
    try:
        assert doctor._file_auth(home / ".gemini" / "oauth_creds.json") == ("unknown", None)
    finally:
        Path.stat = original_stat
        Path.is_file = original_is_file

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("claude", "codex", "grok", "gemini", "cursor-agent", "opencode"):
        (bin_dir / name).write_text("stub\n", encoding="utf-8")
    calls: list[list[str]] = []

    def fake_run(argv: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        calls.append(list(argv))
        if "auth" in argv and "status" in argv:
            return _completed(argv, 0, '{"authMethod": "claude.ai"}\n')
        if argv[1:3] == ["login", "status"]:
            return _completed(argv, 0, "")
        if "status" in argv and "--format" in argv:
            return _completed(argv, 0, '{"authenticated": false}')
        if "auth" in argv and "list" in argv:
            return _completed(argv, 0, "[]")
        if argv[-1] == "--version":
            return _completed(argv, 0, "1.2.3\n")
        if argv[:2] == ["git", "--version"]:
            return _completed(argv, 0, "git version cursor-secret-value\n")
        if argv[:4] == ["git", "config", "--get", "core.longpaths"]:
            return _completed(argv, 0, "yes\n")
        return _completed(argv, 1, "")

    report = doctor.diagnose(
        config.load_config(),
        environ={"PATH": str(bin_dir), "CURSOR_API_KEY": "cursor-secret-value"},
        platform="linux",
        home=home,
        path=str(bin_dir),
        run=fake_run,
        git_run=fake_run,
    )
    assert report["ok"] is True
    assert report["git"]["available"] is True
    by_name = {row["name"]: row for row in report["providers"]}
    assert by_name["claude"]["signed_in"] == "signed-in"
    assert by_name["codex"]["signed_in"] == "signed-in"
    assert by_name["cursor"]["signed_in"] == "signed-in"
    assert by_name["opencode"]["version"] == "1.2.3"
    assert "cursor-secret-value" not in json.dumps(report)

    def missing(_argv: list[str], _timeout: float) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(["x"], 1)

    unknown = doctor._claude_auth(missing, bin_dir / "claude")
    assert unknown == ("unknown", None)
    assert doctor._codex_auth(lambda argv, timeout: _completed(argv, 1, ""), bin_dir / "codex") == (
        "signed-out",
        "login-status",
    )
    assert doctor._cursor_auth(lambda argv, timeout: _completed(argv, 0, "nope"), bin_dir / "cursor-agent") == (
        "unknown",
        None,
    )
    assert doctor._opencode_auth(lambda argv, timeout: _completed(argv, 2, ""), bin_dir / "opencode") == (
        "unknown",
        None,
    )
    assert doctor._claude_auth(lambda argv, timeout: _completed(argv, 1, ""), bin_dir / "claude") == (
        "signed-out",
        None,
    )
    assert doctor._claude_auth(lambda argv, timeout: _completed(argv, 3, ""), bin_dir / "claude") == (
        "unknown",
        None,
    )
    assert doctor._version(lambda argv, timeout: _completed(argv, 0, "\n"), bin_dir / "claude") is None
    assert doctor._version(lambda argv, timeout: "not-a-process", bin_dir / "claude") is None
    assert doctor._git_row(platform="linux", run=missing)["available"] is False
    windows = doctor._git_row(platform="win32", run=fake_run)
    assert windows["longpaths"] is True
    assert doctor._longpaths(lambda argv, timeout: _completed(argv, 0, "no\n")) is False
    assert doctor._signed_in("other", bin_dir / "claude", environ={}, home=home, run=fake_run) == ("unknown", None)
    assert doctor._codex_auth(missing, bin_dir / "codex") == ("unknown", None)
    assert doctor._cursor_auth(missing, bin_dir / "cursor-agent") == ("unknown", None)
    assert doctor._opencode_auth(lambda argv, timeout: _completed(argv, 0, "nope"), bin_dir / "opencode") == (
        "unknown",
        None,
    )
    assert doctor._longpaths(missing) is False
    assert doctor._json_object("{") is None
    assert doctor._json_object('{"ok": true}') == {"ok": True}
    probed = doctor._default_run([sys.executable, "-c", "print('ok')"], 10)
    assert probed.returncode == 0
    assert "ok" in probed.stdout
    repeated = doctor._candidate_names("claude", win32=True, pathext=".cmd;.CMD")
    assert repeated.count("claude.cmd") == 1
    assert doctor._signed_in("claude", bin_dir / "claude", environ={}, home=home, run=fake_run)[0] == "signed-in"
    assert doctor.resolve_executable("", platform="linux") is None
    assert doctor.resolve_executable(str(tmp_path / "missing-bin"), platform="linux") is None
    assert doctor.resolve_executable("foo/bar", platform="linux") is None
    assert doctor.live_requested("claude", environ={"CI": "1", "RECURSION_LIVE": "1"}, platform="linux") is False
    assert doctor.live_requested("claude", environ={"RECURSION_LIVE": "0"}, platform="linux") is False
    assert "fixture" in doctor.discover_installed(path="", platform="linux")

    win = tmp_path / "win"
    win.mkdir()
    (win / "Claude.CMD").write_text("@echo off\n", encoding="utf-8")
    found = doctor.resolve_executable("claude", path=str(win), pathext=".EXE;;cmd", platform="win32")
    assert found is not None
    assert found.name == "Claude.CMD"
    assert doctor._find_named(tmp_path / "absent", "claude", win32=True) is None
    names = doctor._candidate_names("claude.exe", win32=True, pathext=".EXE")
    assert names[0] == "claude.exe"
    assert "claude.exe.exe" not in names

    def fail_iter(self: Path):
        raise OSError("denied")

    monkeypatch.setattr(Path, "iterdir", fail_iter)
    assert doctor._find_named(win, "Claude.CMD", win32=True) is None
