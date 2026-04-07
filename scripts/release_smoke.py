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
    ]
    tracked_text_files = []
    for root in scan_roots:
        if root.is_file():
            tracked_text_files.append(root)
            continue
        tracked_text_files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and "benchmarks/local" not in str(path)
        )
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

        if suite_json["summary"]["benchmark_count"] != 3:
            raise SystemExit("Expected 3 fixture benchmarks in SUITE_RESULTS.json")
        if public_json["summary"]["benchmark_count"] != 3:
            raise SystemExit("Expected 3 fixture benchmarks in SUITE_RESULTS.public.json")
        if "Benchmark Results" not in suite_md:
            raise SystemExit("Markdown suite report is missing benchmark results")
        public_json_text = json.dumps(public_json)
        if "/tmp/" in public_json_text or "/private/tmp/" in public_json_text:
            raise SystemExit("Public suite JSON leaked a temporary path")
        if "/tmp/" in suite_md or "/private/tmp/" in suite_md:
            raise SystemExit("Markdown suite report leaked a temporary path")

        results_by_id = {item["id"]: item for item in suite_json["results"]}
        if results_by_id["flutter-fixture"]["status"] == "failed":
            raise SystemExit("Flutter fixture benchmark unexpectedly failed")
        if results_by_id["react-native-fixture"]["status"] == "failed":
            raise SystemExit("React Native fixture benchmark unexpectedly failed")


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
