#!/usr/bin/env python3
"""Red control: worker-sandbox.sh --engine-plan generic plugin dispatch, logical mode.

Frozen contract: docs/plans/engine-plugin-architecture.md, "Controls" #4, and the
worked spec handed down with this control set. Requires bash (Git Bash on Windows,
plain bash elsewhere); SKIPs (exit 0) if bash is unavailable. The plan must carry the
reviewed provider profile and its scoped environment allowlist through logical launch.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
SANDBOX_SCRIPT = SOURCE / "scripts" / "worker-sandbox.sh"
BASH = shutil.which("bash") or (r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else None)
CYGPATH = shutil.which("cygpath") or (r"C:\Program Files\Git\usr\bin\cygpath.exe" if os.name == "nt" else None)

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def _cygpath(flag: str, value: str) -> str | None:
    if CYGPATH is None:
        return None
    try:
        result = subprocess.run([CYGPATH, flag, value], capture_output=True, text=True)
    except FileNotFoundError:
        return None
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def to_posix(path: Path) -> str:
    """Convert a filesystem path to the POSIX form bash expects (helper, see module docstring)."""
    converted = _cygpath("-u", str(path))
    if converted is not None:
        return converted
    s = str(path).replace("\\", "/")
    if len(s) > 1 and s[1] == ":":
        s = f"/{s[0].lower()}{s[2:]}"
    return s


def to_local_path(posix_path: str) -> Path:
    converted = _cygpath("-w", posix_path)
    if converted is not None:
        return Path(converted)
    return Path(posix_path)


def bash_run(sandbox_script_posix: str, argv_after_script: list[str], extra_path_dir_posix: str, env: dict):
    bash_dir = to_posix(Path(BASH).parent) if os.name == "nt" and BASH else ""
    wrapper = 'export PATH="$1:$2:$PATH"; shift 2; exec "$1" "${@:2}"'
    argv = [BASH, "-lc", wrapper, "bash_wrapper", extra_path_dir_posix, bash_dir, sandbox_script_posix] + argv_after_script
    return subprocess.run(argv, capture_output=True, text=True, env=env)


def main() -> int:
    if BASH is None:
        print("SKIP - bash not found on PATH")
        return 0

    mktemp = subprocess.run([BASH, "-lc", "mktemp -d"], capture_output=True, text=True)
    if mktemp.returncode != 0 or not mktemp.stdout.strip():
        print("SKIP - bash mktemp -d failed; cannot build a /tmp root")
        return 0
    root_posix = mktemp.stdout.strip()
    root_local = to_local_path(root_posix)

    geteuid = getattr(os, "geteuid", None)
    is_linux_root = os.name != "nt" and bool(geteuid) and geteuid() == 0

    try:
        scripts_dir = root_local / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        sandbox_copy = scripts_dir / "worker-sandbox.sh"
        sandbox_copy.write_bytes(SANDBOX_SCRIPT.read_bytes())
        (scripts_dir / "provider-egress-profiles.json").write_bytes(
            (SOURCE / "scripts" / "provider-egress-profiles.json").read_bytes()
        )
        engines_dir = scripts_dir / "engines"
        engines_dir.mkdir()
        sandbox_copy_posix = to_posix(sandbox_copy)

        wt_local = root_local / "wt"
        wt_local.mkdir(parents=True, exist_ok=True)
        wt_posix = to_posix(wt_local)

        bin_dir = root_local / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        stub_path = bin_dir / "stubeng"
        stub_body = (
            "#!/usr/bin/env bash\n"
            'out="${STUB_ARGV_OUT:-/dev/null}"\n'
            ': > "$out"\n'
            'for a in "$@"; do printf "%s\\n" "$a" >> "$out"; done\n'
            'if [ -n "${STUB_ENV_OUT:-}" ]; then printf "%s" "${STUBENG_API_KEY:-}" > "$STUB_ENV_OUT"; fi\n'
        )
        stub_path.write_bytes(stub_body.encode("utf-8"))
        bin_dir_posix = to_posix(bin_dir)
        chmod_result = subprocess.run(
            [BASH, "-lc", f"chmod +x '{to_posix(stub_path)}'"], capture_output=True, text=True
        )
        check(chmod_result.returncode == 0, "stub executable is chmod +x")

        plan = {
            "schema_version": 1,
            "engine": "stubeng",
            "executable": "stubeng",
            "argv": ["{{EXE}}", "-p", "{{PROMPT}}"],
            "model_required": False,
            "model_argv_suffix": ["--model", "{{MODEL}}"],
            "billing": {"basis": "metered", "provider": "google-gemini"},
            "network": {"policy": "provider-only", "profile": "gemini",
                         "endpoints": ["generativelanguage.googleapis.com"]},
            "availability_probe": None,
            "concurrency_cap": None,
            "env_passthrough": ["GEMINI_API_KEY"],
        }
        manifest = {
            "schema_version": 1,
            "name": "stubeng",
            "description": "logical worker sandbox fixture",
            "executable": "stubeng",
            "argv": plan["argv"],
            "model": {"required": False, "argv_suffix": plan["model_argv_suffix"]},
            "roles": ["implementer"],
            "billing": plan["billing"],
            "network": plan["network"],
            "availability_probe": None,
            "concurrency_cap": None,
            "env_passthrough": plan["env_passthrough"],
        }
        manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
        manifest_path = engines_dir / "stubeng.json"
        manifest_path.write_bytes(manifest_bytes)
        subprocess.run(["git", "init", "-q", "-b", "main", str(root_local)], check=True)
        subprocess.run(["git", "-C", str(root_local), "add", "scripts"], check=True)
        subprocess.run(
            ["git", "-C", str(root_local), "-c", "user.name=test", "-c", "user.email=test@example.invalid",
             "commit", "-qm", "controller fixture"],
            check=True,
        )
        controller_sha = subprocess.check_output(
            ["git", "-C", str(root_local), "rev-parse", "HEAD"], text=True,
        ).strip()
        plan_path = root_local / "plan.json"
        resolver_env = dict(os.environ)
        resolver_env.update({
            "RECURSION_ROOT": str(root_local),
            "RECURSION_ENGINE_PLUGINS": "1",
            "RECURSION_ENGINE_STUBENG_ENABLED": "1",
        })
        resolved = subprocess.run(
            [sys.executable, str(SOURCE / "scripts" / "resolve-engine.py"), "stubeng",
             "--role", "implementer", "--emit-plan", str(plan_path),
             "--controller-root", str(root_local), "--controller-commit", controller_sha],
            capture_output=True, text=True, env=resolver_env,
        )
        check(
            resolved.returncode == 0,
            f"resolve-engine emits an authenticated plugin plan (got {resolved.returncode}, stderr={resolved.stderr.strip()!r})",
        )
        if resolved.returncode == 0 and plan_path.exists():
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan_posix = to_posix(plan_path)

        base_env = dict(os.environ)
        base_env.update(
            {
                "RECURSION_TEST_WORKER": "logical",
                "RECURSION_TEST_PROVIDER_NETWORK": "logical",
                "RECURSION_ROOT": root_posix,
                "RECURSION_PYTHON": to_posix(Path(sys.executable)),
            }
        )
        common_tail = ["--worktree", wt_posix, "--role", "implementer", "--network-policy", "provider-only"]

        def invoke(engine_args: list[str], prompt: str, env: dict, model: str | None = None):
            args = engine_args + common_tail + ["--prompt", prompt]
            if model is not None:
                args += ["--model", model]
            return bash_run(sandbox_copy_posix, args, bin_dir_posix, env)

        # --- (1) builtin engine + --engine-plan must be refused (contract: exit 92) ---
        result = invoke(["--engine", "claude", "--engine-plan", plan_posix], "hi", dict(base_env))
        check(
            result.returncode == 92,
            f"builtin engine + --engine-plan exits 92 (got {result.returncode}, stderr={result.stderr.strip()!r})",
        )

        # --- (2) non-builtin engine without --engine-plan must be refused (exit 92) ---
        result = invoke(["--engine", "stubeng"], "hi", dict(base_env))
        check(
            result.returncode == 92,
            f"non-builtin engine without --engine-plan exits 92 (got {result.returncode})",
        )

        # A plan-shaped file without authenticated controller provenance is not executable,
        # even when the logical provider capability is available.
        unbound_plan = root_local / "plan-unbound.json"
        unbound = dict(plan)
        unbound.pop("authority", None)
        unbound_plan.write_bytes((json.dumps(unbound, indent=2) + "\n").encode("utf-8"))
        result = invoke(["--engine", "stubeng", "--engine-plan", to_posix(unbound_plan)], "hi", dict(base_env))
        check(
            result.returncode == 92,
            f"unbound execution plan is refused before launch (got {result.returncode})",
        )

        # --- (3) valid plan: prompt is one exact argv element, no --model when none passed ---
        injection_prompt = 'a b "; rm -rf /"'
        argv_out_3 = root_local / "argv-3.out"
        env3 = dict(base_env)
        env3["STUB_ARGV_OUT"] = to_posix(argv_out_3)
        result = invoke(["--engine", "stubeng", "--engine-plan", plan_posix], injection_prompt, env3)
        check(
            result.returncode == 0,
            f"plugin engine with valid plan executes (got {result.returncode}, stderr={result.stderr.strip()!r})",
        )
        if argv_out_3.exists():
            lines = argv_out_3.read_text(encoding="utf-8").splitlines()
            prompt_ok = "-p" in lines and lines[lines.index("-p") + 1] == injection_prompt
            check(prompt_ok, "prompt is carried as one exact argv element after -p")
            check("--model" not in lines, "no --model element when --model was not passed")
        else:
            check(False, "stub argv capture file was created (no-model case)")
            check(False, "no --model element when --model was not passed")

        # --- (4) same, with --model: suffix appended as two separate elements ---
        argv_out_4 = root_local / "argv-4.out"
        env4 = dict(base_env)
        env4["STUB_ARGV_OUT"] = to_posix(argv_out_4)
        result = invoke(
            ["--engine", "stubeng", "--engine-plan", plan_posix], injection_prompt, env4, model="qwen-30b"
        )
        check(result.returncode == 0, f"plugin engine with model executes (got {result.returncode})")
        if argv_out_4.exists():
            lines = argv_out_4.read_text(encoding="utf-8").splitlines()
            model_ok = "--model" in lines and lines[lines.index("--model") + 1] == "qwen-30b"
            check(model_ok, "model_argv_suffix appended as two separate elements (--model, qwen-30b)")
        else:
            check(False, "stub argv capture file exists for --model case")

        # --- (5) env_passthrough plumbing: logical mode declares the passthrough set ---
        # Logical mode inherits the controller environment, so a value-reaches-the-stub
        # assertion could never fail; the meaningful hermetic control is that the plan's
        # env_passthrough names travel plan -> loader -> launch (the --setenv /
        # EnvironmentFile wiring itself is a box-suite control).
        argv_out_5 = root_local / "argv-5.out"
        env5 = dict(base_env)
        env5["STUB_ARGV_OUT"] = to_posix(argv_out_5)
        env5["GEMINI_API_KEY"] = "sekret"
        result = invoke(["--engine", "stubeng", "--engine-plan", plan_posix], "hi", env5)
        check(result.returncode == 0, f"plugin engine with env_passthrough executes (got {result.returncode})")
        check(
            "worker-sandbox: env-passthrough GEMINI_API_KEY" in result.stderr,
            "logical mode declares the plan's env_passthrough names on stderr",
        )

        # --- (6) model_required plan without a model is refused (exit 92) ---
        mreq_plan = dict(plan)
        mreq_plan["model_required"] = True
        mreq_path = root_local / "plan-mreq.json"
        mreq_path.write_bytes((json.dumps(mreq_plan, indent=2) + "\n").encode("utf-8"))
        result = invoke(["--engine", "stubeng", "--engine-plan", to_posix(mreq_path)], "hi", dict(base_env))
        check(
            result.returncode == 92,
            f"model_required plan without --model exits 92 (got {result.returncode}, stderr={result.stderr.strip()!r})",
        )
        result = invoke(
            ["--engine", "stubeng", "--engine-plan", to_posix(mreq_path)], "hi", dict(base_env), model="qwen-30b"
        )
        check(result.returncode == 0, f"model_required plan with --model executes (got {result.returncode})")

        # --- (7) hostile engine name is refused before any use as a filename (exit 92) ---
        hostile_plan = dict(plan)
        hostile_plan["engine"] = "../../../etc/pwn"
        hostile_path = root_local / "plan-hostile.json"
        hostile_path.write_bytes((json.dumps(hostile_plan, indent=2) + "\n").encode("utf-8"))
        result = invoke(
            ["--engine", "../../../etc/pwn", "--engine-plan", to_posix(hostile_path)], "hi", dict(base_env)
        )
        check(
            result.returncode == 92,
            f"path-traversal engine name exits 92 (got {result.returncode}, stderr={result.stderr.strip()!r})",
        )

        # --- permission control: plan file ownership/writability (Linux root only) ---
        if os.name == "nt" or not is_linux_root:
            print("SKIP - plan file ownership/permission control (requires Linux + root)")
        else:
            bad_plan = root_local / "plan-bad-perms.json"
            bad_plan.write_bytes((json.dumps(plan, indent=2) + "\n").encode("utf-8"))
            os.chmod(bad_plan, 0o666)
            argv_out_bad = root_local / "argv-bad.out"
            env_bad = dict(base_env)
            env_bad["STUB_ARGV_OUT"] = to_posix(argv_out_bad)
            result = invoke(["--engine", "stubeng", "--engine-plan", to_posix(bad_plan)], "hi", env_bad)
            check(result.returncode == 95, f"group/other-writable plan file is refused (got {result.returncode})")
    finally:
            subprocess.run([BASH, "-lc", f"rm -rf -- '{root_posix}'"], capture_output=True, text=True)

    if failures:
        print(f"worker-sandbox-plugin.test: {len(failures)} FAILED")
        return 1
    print("worker-sandbox-plugin.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
