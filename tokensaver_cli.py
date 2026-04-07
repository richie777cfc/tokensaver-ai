#!/usr/bin/env python3
"""
TokenSaver CLI — Compile repositories into minimal agent context.

Usage:
  python tokensaver_cli.py scan <path>     # Inspect the repo and print exact source token stats
  python tokensaver_cli.py build <path> [--output-dir <dir>]
  python tokensaver_cli.py metrics <path> [--output-dir <dir>]
  python tokensaver_cli.py benchmark <path> [--output-dir <dir>]
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tokensaver.build import OUTPUT_DIRNAME, build_project
from tokensaver.benchmark import benchmark_project
from tokensaver.eval import load_metrics, print_metrics
from tokensaver.scanner import scan_project


def cmd_scan(project_path: str):
    """Inspect a project and report exact source token counts."""
    result = scan_project(project_path)

    print(f"\n{'=' * 60}")
    print(f"TokenSaver Scan: {result.project_name}")
    print(f"{'=' * 60}\n")

    print(f"Framework:         {result.framework}")
    print(f"Tokenizer:         {result.tokenizer}")
    print(f"Package managers:  {', '.join(result.package_managers) if result.package_managers else 'none detected'}")
    print(f"Files:             {result.total_files:,}")
    print(f"Lines:             {result.total_lines:,}")
    print(f"Bytes:             {result.total_bytes:,}")
    print(f"Exact tokens:      {result.total_tokens:,}")

    if result.entrypoints:
        print(f"\nEntrypoints:")
        for entrypoint in result.entrypoints:
            print(f"  {entrypoint}")

    print(f"\nLanguages:")
    for language, info in result.languages.items():
        print(f"  {language:<15} {info['files']:>6} files  {info['tokens']:>10,} tokens")

    print(f"\nTop files by tokens:")
    for file_info in result.top_files[:10]:
        print(f"  {file_info['tokens']:>8,} tok  {file_info['path']}")

    print(f"\nTop directories by tokens:")
    for dir_info in result.top_dirs[:10]:
        print(f"  {dir_info['tokens']:>8,} tok  {dir_info['dir']}/")

    return result


def cmd_build(project_path: str, output_dir: str | None = None):
    """Generate all context artifacts for a project."""
    result = build_project(project_path, output_dir=output_dir)
    metrics = result["metrics"]

    print(f"\nBuilt TokenSaver artifacts in {result['output_dir']}\n")
    for artifact in metrics["artifacts"]:
        ratio = artifact["compression_ratio"]
        ratio_text = f"{ratio:.2f}x" if ratio else "n/a"
        print(
            f"  {artifact['name']:<20} "
            f"{artifact['source_tokens']:>10,} -> {artifact['output_tokens']:>10,} "
            f"({ratio_text})"
        )

    print()
    print_metrics(metrics)
    return result


def cmd_metrics(project_path: str, output_dir: str | None = None):
    """Print compression metrics for an existing build."""
    resolved_output_dir = Path(output_dir).resolve() if output_dir else (Path(project_path).resolve() / OUTPUT_DIRNAME)
    metrics_path = resolved_output_dir / "METRICS.json"
    if not metrics_path.exists():
        print(f"Missing {metrics_path}. Run 'python tokensaver_cli.py build {project_path}' first.")
        return None

    metrics = load_metrics(resolved_output_dir)
    print_metrics(metrics)
    return metrics


def cmd_benchmark(project_path: str, output_dir: str | None = None):
    """Run a reproducible benchmark and persist BENCHMARK.json."""
    result = benchmark_project(project_path, output_dir=output_dir)
    benchmark = result["benchmark"]

    print(f"\nBenchmarked TokenSaver against {benchmark['project']}")
    print(f"Plugin:            {benchmark['plugin']}")
    print(f"Runtime:           {benchmark['runtime_seconds']:.2f}s")
    print(f"Scan tokens:       {benchmark['scan']['total_tokens']:,}")
    print(f"Benchmark output:  {result['output_dir'] / 'BENCHMARK.json'}")
    print_metrics(benchmark["metrics"])
    return result


def _parse_output_dir(argv: list[str]) -> str | None:
    if "--output-dir" not in argv:
        return None
    index = argv.index("--output-dir")
    if index + 1 >= len(argv):
        print("Error: --output-dir requires a directory path")
        sys.exit(1)
    return argv[index + 1]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    project_path = sys.argv[2]
    output_dir = _parse_output_dir(sys.argv[3:])

    if not os.path.isdir(project_path):
        print(f"Error: {project_path} is not a directory")
        sys.exit(1)

    if command == "scan":
        cmd_scan(project_path)
    elif command in {"build", "generate"}:
        cmd_build(project_path, output_dir=output_dir)
    elif command in {"metrics", "eval"}:
        cmd_metrics(project_path, output_dir=output_dir)
    elif command == "benchmark":
        cmd_benchmark(project_path, output_dir=output_dir)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
