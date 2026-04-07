#!/usr/bin/env python3
"""Release smoke checks for TokenSaver."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_MANIFEST = REPO_ROOT / "benchmarks" / "fixtures" / "manifest.ci.json"
PRIVATE_LEAK_PATTERNS_FILE = REPO_ROOT / "benchmarks" / "local" / "leak_patterns.private.txt"


def main() -> int:
    _run_py_compile()
    _run_tracked_leak_scan()
    _run_package_install_check()
    _run_fixture_suite()
    _run_schema_version_check()
    _run_public_only_check()
    print("Release smoke checks passed.")
    return 0


def _run_py_compile() -> None:
    targets = ["tokensaver_cli.py", "scripts/release_smoke.py"]
    for package_dir in ("tokensaver", "generators"):
        targets.extend(
            str(path.relative_to(REPO_ROOT))
            for path in sorted((REPO_ROOT / package_dir).rglob("*.py"))
        )
    subprocess.run(
        [sys.executable, "-m", "py_compile", *targets],
        cwd=REPO_ROOT,
        check=True,
    )


def _run_tracked_leak_scan() -> None:
    scan_roots = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "benchmarks",
        REPO_ROOT / "tokensaver",
        REPO_ROOT / "tokensaver_cli.py",
        REPO_ROOT / "pyproject.toml",
        REPO_ROOT / "LICENSE",
        REPO_ROOT / ".github",
        REPO_ROOT / "docs",
        REPO_ROOT / "tests",
        REPO_ROOT / "scripts",
    ]
    tracked_text_files = []
    skip_dirs = {"__pycache__", ".pytest_cache", "node_modules"}
    skip_suffixes = {".pyc", ".pyo", ".egg-info"}
    for root in scan_roots:
        if root.is_file():
            tracked_text_files.append(root)
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if "benchmarks/local" in str(path):
                continue
            if any(part in skip_dirs for part in path.parts):
                continue
            if path.suffix in skip_suffixes:
                continue
            tracked_text_files.append(path)
    patterns = _default_leak_patterns()
    patterns.extend(_load_private_leak_patterns())

    for pattern in patterns:
        for path in tracked_text_files:
            try:
                content = path.read_text(errors="ignore")
            except OSError as exc:
                raise SystemExit(f"Could not read {path}: {exc}") from exc
            if pattern in content:
                raise SystemExit(f"Leak scan failed for pattern {pattern!r} in {path}")


def _run_fixture_suite() -> None:
    with tempfile.TemporaryDirectory(prefix="tokensaver-release-smoke-") as temp_dir:
        output_dir = Path(temp_dir) / "suite"
        subprocess.run(
            [
                sys.executable,
                "tokensaver_cli.py",
                "benchmark-suite",
                str(FIXTURE_MANIFEST),
                "--output-dir",
                str(output_dir),
            ],
            cwd=REPO_ROOT,
            check=True,
        )

        suite_json = json.loads((output_dir / "SUITE_RESULTS.json").read_text())
        public_json = json.loads((output_dir / "SUITE_RESULTS.public.json").read_text())
        suite_md = (output_dir / "SUITE_RESULTS.md").read_text()

        if suite_json["summary"]["benchmark_count"] != 5:
            raise SystemExit("Expected 5 fixture benchmarks in SUITE_RESULTS.json")
        if public_json["summary"]["benchmark_count"] != 5:
            raise SystemExit("Expected 5 fixture benchmarks in SUITE_RESULTS.public.json")
        if "Benchmark Results" not in suite_md:
            raise SystemExit("Markdown suite report is missing benchmark results")
        public_json_text = json.dumps(public_json)
        if "/tmp/" in public_json_text or "/private/tmp/" in public_json_text:
            raise SystemExit("Public suite JSON leaked a temporary path")
        if "/tmp/" in suite_md or "/private/tmp/" in suite_md:
            raise SystemExit("Markdown suite report leaked a temporary path")

        results_by_id = {item["id"]: item for item in suite_json["results"]}
        for fixture_id in ("flutter-fixture", "react-native-fixture", "python-fixture", "node-fixture", "nextjs-fixture"):
            status = results_by_id.get(fixture_id, {}).get("status", "missing")
            if status == "failed":
                raise SystemExit(f"{fixture_id} benchmark unexpectedly failed")
            if status != "ok":
                raise SystemExit(f"{fixture_id} benchmark expected 'ok' but got '{status}'")


def _run_schema_version_check() -> None:
    """Verify that fixture suite outputs contain schema_version."""
    with tempfile.TemporaryDirectory(prefix="tokensaver-schema-") as temp_dir:
        output_dir = Path(temp_dir) / "schema"
        subprocess.run(
            [
                sys.executable,
                "tokensaver_cli.py",
                "benchmark-suite",
                str(FIXTURE_MANIFEST),
                "--output-dir",
                str(output_dir),
            ],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        suite_json = json.loads((output_dir / "SUITE_RESULTS.json").read_text())
        public_json = json.loads((output_dir / "SUITE_RESULTS.public.json").read_text())

        if "schema_version" not in suite_json.get("_meta", {}):
            raise SystemExit("SUITE_RESULTS.json missing schema_version in _meta")
        if "schema_version" not in public_json.get("_meta", {}):
            raise SystemExit("SUITE_RESULTS.public.json missing schema_version in _meta")

        for bench_id in ("flutter-fixture", "react-native-fixture", "python-fixture", "node-fixture", "nextjs-fixture"):
            bench_dir = output_dir / bench_id
            if not bench_dir.exists():
                continue
            for artifact_name in (
                "PROJECT_SUMMARY.json",
                "COMMANDS.json",
                "MODULE_GRAPH.json",
                "API_INDEX.json",
                "ROUTE_INDEX.json",
                "CONFIG_INDEX.json",
                "METRICS.json",
            ):
                artifact_path = bench_dir / artifact_name
                if not artifact_path.exists():
                    continue
                artifact_data = json.loads(artifact_path.read_text())
                if "schema_version" not in artifact_data.get("_meta", {}):
                    raise SystemExit(f"{bench_id}/{artifact_name} missing schema_version")


def _run_public_only_check() -> None:
    """Verify that --public-only mode omits raw suite and benchmark outputs."""
    with tempfile.TemporaryDirectory(prefix="tokensaver-pubonly-") as temp_dir:
        output_dir = Path(temp_dir) / "public"
        subprocess.run(
            [
                sys.executable,
                "tokensaver_cli.py",
                "benchmark-suite",
                str(FIXTURE_MANIFEST),
                "--output-dir",
                str(output_dir),
                "--public-only",
            ],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        if not (output_dir / "SUITE_RESULTS.public.json").exists():
            raise SystemExit("--public-only did not produce SUITE_RESULTS.public.json")
        if not (output_dir / "SUITE_RESULTS.md").exists():
            raise SystemExit("--public-only did not produce SUITE_RESULTS.md")
        if (output_dir / "SUITE_RESULTS.json").exists():
            raise SystemExit("--public-only should not produce SUITE_RESULTS.json")
        if (output_dir / "history").exists():
            raise SystemExit("--public-only should not produce history/ directory")
        if list(output_dir.glob("*/BENCHMARK.json")):
            raise SystemExit("--public-only should not produce per-benchmark BENCHMARK.json files")


def _run_package_install_check() -> None:
    with tempfile.TemporaryDirectory(prefix="tokensaver-pkg-") as temp_dir:
        target_dir = Path(temp_dir) / "site"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                ".",
                "--no-deps",
                "--no-build-isolation",
                "-t",
                str(target_dir),
            ],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.path.insert(0, sys.argv[1]); import tokensaver; print(tokensaver.__version__)",
                str(target_dir),
            ],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )


def _load_private_leak_patterns() -> list[str]:
    patterns: list[str] = []
    env_value = os.getenv("TOKENSAVER_EXTRA_LEAK_PATTERNS", "")
    if env_value.strip():
        patterns.extend(item.strip() for item in env_value.split(",") if item.strip())

    if PRIVATE_LEAK_PATTERNS_FILE.exists():
        patterns.extend(
            line.strip()
            for line in PRIVATE_LEAK_PATTERNS_FILE.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
    return patterns


def _default_leak_patterns() -> list[str]:
    patterns: list[str] = []
    home = str(Path.home())
    if home and home not in {"/", "."}:
        patterns.append(home)
    return patterns


if __name__ == "__main__":
    raise SystemExit(main())
