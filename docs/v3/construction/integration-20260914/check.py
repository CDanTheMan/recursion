"""Exact source composition and inert regression gate; no scientific admission."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
DIRECTORY = "docs/v3/construction/integration-20260914/"
MANIFEST = ROOT / DIRECTORY / "manifest.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(
        ["git", "-c", "core.longpaths=true", *args], cwd=ROOT, timeout=30
    ).decode("utf8").strip()


def tree(revision):
    result = {}
    for line in git("ls-tree", "-r", revision).splitlines():
        meta, name = line.split("\t", 1)
        mode, kind, oid = meta.split()
        require(kind == "blob" and mode in ("100644", "100755"), "ordinary source blobs only")
        result[name] = (mode, oid)
    return result


def verify_composition(actual, baseline, imported, integration):
    require(set(actual) == set(baseline) | set(imported) | set(integration), "exact combined path union")
    require(not (set(baseline) & set(imported)), "imports must be additive")
    require(not (set(integration) & (set(baseline) | set(imported))), "integration paths must be additive")
    for path, expected in (baseline | imported).items():
        require(actual[path] == expected, "preserved mode/blob changed: " + path)


def composition_controls(actual, baseline, imported, integration):
    cases = {}
    path = next(iter(imported))
    cases["changed-imported-blob"] = actual | {path: (actual[path][0], "0" * 40)}
    path = next(iter(baseline))
    cases["changed-baseline-blob"] = actual | {path: (actual[path][0], "0" * 40)}
    cases["extra-path"] = actual | {"unexpected-integration-file": ("100644", "0" * 40)}
    missing = dict(actual)
    del missing[next(iter(imported))]
    cases["missing-import"] = missing
    for name, forged in cases.items():
        try:
            verify_composition(forged, baseline, imported, integration)
        except ValueError:
            continue
        raise ValueError("composition control not rejected: " + name)
    return list(cases)


def source_check(candidate, evidence_root, manifest):
    require(re.fullmatch("[0-9a-f]{40}", candidate) is not None, "full candidate SHA required")
    require(git("rev-parse", "HEAD") == candidate, "candidate must equal HEAD")
    require(not git("status", "--porcelain=v1", "--untracked-files=all"), "clean candidate required")
    git("merge-base", "--is-ancestor", manifest["observed_master"], manifest["task_base"])
    git("merge-base", "--is-ancestor", manifest["task_base"], candidate)
    git("diff", "--check", manifest["task_base"], candidate)
    baseline = tree(manifest["task_base"])
    imported = {}
    for origin in manifest["origins"]:
        oid = origin["candidate"]
        git("merge-base", "--is-ancestor", manifest["task_base"], oid)
        git("merge-base", "--is-ancestor", oid, candidate)
        require(git("rev-parse", oid + "^{tree}") == origin["tree"], "origin tree pin")
        origin_tree = tree(oid)
        paths = set(origin["paths"])
        require(len(paths) == len(origin["paths"]), "unique origin paths")
        verify_composition(origin_tree, baseline, {p: origin_tree[p] for p in paths}, [])
        require(not paths & set(imported), "disjoint origin changes")
        imported.update({p: origin_tree[p] for p in paths})
    actual = tree(candidate)
    verify_composition(actual, baseline, imported, manifest["integration_paths"])
    controls = composition_controls(actual, baseline, imported, manifest["integration_paths"])
    working_hashes = {}
    for name, (_mode, oid) in actual.items():
        path = ROOT / name
        require(not path.is_symlink(), "no source symlink: " + name)
        readable = Path("\\\\?\\" + str(path)) if os.name == "nt" else path
        raw = readable.read_bytes()
        valid = False
        for content in (raw, raw.replace(b"\r\n", b"\n")):
            blob = b"blob " + str(len(content)).encode() + b"\0" + content
            valid |= hashlib.sha1(blob).hexdigest() == oid
        require(valid, "working bytes differ from candidate: " + name)
        working_hashes[name] = hashlib.sha256(raw).hexdigest()
    evidence = {}
    for item in manifest["intake_evidence"]:
        path = evidence_root / item["name"]
        require(path.is_file() and not path.is_symlink(), "required intake evidence missing")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == item["sha256"], "intake evidence digest: " + item["name"])
        evidence[item["name"]] = digest
    return {
        "candidate": candidate,
        "tree": git("rev-parse", candidate + "^{tree}"),
        "working_digest": hashlib.sha256(json.dumps(working_hashes, sort_keys=True).encode()).hexdigest(),
        "baseline_files": len(baseline),
        "imported_files": len(imported),
        "source_files": len(actual),
        "origins": {x["id"]: x["candidate"] for x in manifest["origins"]},
        "intake_evidence": evidence,
        "composition_controls": controls,
    }


def load_component(path, name):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def component_check(component):
    if component == "ledger":
        module = load_component(ROOT / "experiments/v3/recovery-ledger-20260914/check.py", "ledger_gate")
        tests = module.load_tests()
        prefixes = module.prefix_audit(tests)
        mutants = module.independent_mutations(tests)
        components = module.component_guard_audit(tests)
        resets = module.reset_scope_audit(tests)
        module.subprocess_gate(tests)
        result = dict(prefixes=prefixes, mutations=len(mutants), component_guards=len(components), reset_guards=resets)
        require(result == dict(prefixes=21, mutations=6, component_guards=3, reset_guards=3), "ledger audit inventory")
    else:
        directory = ROOT / "experiments/v3/delegated-q-coupling-20260914"
        checks = load_component(directory / "check.py", "check")
        checks.validate_plan(json.loads((ROOT / "docs/v3/construction/delegated-q-coupling-20260914/plan.json").read_text()))
        tests = load_component(directory / "test_contract.py", "test_contract")
        result = tests.run()
        require(result["status"] == "FAKE_CONTRACT_PASS", "DQ fake gate")
        require(len(result["controls"]) == 40 and all(x["detected"] is True for x in result["controls"]), "DQ controls")
        require(result["valid_fixtures"] == 3 and result["fake_certificates"] == 31, "DQ fixture inventory")
        require(result["inherited_state_visits"] == result["provider_calls"] == 0, "inert DQ only")
        result["plan_validated"] = True
    print(json.dumps(dict(status="COMPONENT_CHECK_PASS", component=component, result=result)))


def run_gate(name, arguments, timeout, output, marker):
    result = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", *arguments], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout
    )
    (output / (name + ".txt")).write_bytes(result.stdout)
    require(len(result.stdout) < 33554432, "bounded gate output")
    require(result.returncode == 0, name + " failed; retained output")
    text = result.stdout.decode("utf8", "replace")
    require(marker in text and "skipped" not in text.lower(), name + " required evidence absent or skipped")
    return dict(name=name, exit_code=result.returncode, output_sha256=hashlib.sha256(result.stdout).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--component", choices=("ledger", "dq"))
    args = parser.parse_args()
    if args.component:
        component_check(args.component)
        return
    require(args.candidate and args.evidence_root and args.output, "candidate, evidence-root and output required")
    output = args.output.resolve()
    require(not output.exists() and not output.is_relative_to(ROOT), "fresh external output directory")
    output.mkdir(parents=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf8"))
    record = dict(status="INTEGRATION_FAILED", candidate=args.candidate, gates=[],
                  scientific_admission=False, fleet_activation=False, provider_calls=0)
    try:
        binding = source_check(args.candidate, args.evidence_root.resolve(), manifest)
        record["binding"] = binding
        commands = [
            ("handoff", ["docs/v3/construction/next-work-20260914/check_handoff.py"], 60, "HANDOFF_SOURCE_PASS"),
            ("p1", ["-m", "unittest", "-v", "tools.construction_swarm.test_p1_core"], 60, "Ran 18 tests"),
            ("p2", ["-m", "unittest", "-v", "tools.construction_swarm.test_p2_access"], 120, "Ran 19 tests"),
            ("ledger", [DIRECTORY + "check.py", "--component", "ledger"], 60, "COMPONENT_CHECK_PASS"),
            ("dq", [DIRECTORY + "check.py", "--component", "dq"], 60, "COMPONENT_CHECK_PASS"),
        ]
        for name, arguments, timeout, marker in commands:
            record["gates"].append(run_gate(name, arguments, timeout, output, marker))
        require(binding == source_check(args.candidate, args.evidence_root.resolve(), manifest), "source/evidence changed during gate")
        record["status"] = "INTEGRATION_SOURCE_AND_INERT_PASS"
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        record["reason"] = str(error)
        raise
    finally:
        (output / "receipt.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf8")
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print("INTEGRATION_GATE_FAILED: " + str(error), file=sys.stderr)
        sys.exit(1)
