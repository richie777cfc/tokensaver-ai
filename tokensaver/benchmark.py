"""Benchmark helpers for reproducible TokenSaver runs."""

from __future__ import annotations

import json
import time
from pathlib import Path

from tokensaver.build import build_project
from tokensaver.core.helpers import timestamp


def benchmark_project(root: str | Path, output_dir: str | Path | None = None) -> dict:
    """Run a full build and persist a benchmark summary next to the outputs."""
    started_at = time.perf_counter()
    result = build_project(root, output_dir=output_dir)
    duration_seconds = time.perf_counter() - started_at

    payload = {
        "_meta": {
            "extractor": "benchmark_v1",
            "generated_at": timestamp(),
        },
        "project": result["scan"].project_name,
        "root": result["scan"].root,
        "framework": result["scan"].framework,
        "plugin": result["plugin"],
        "runtime_seconds": round(duration_seconds, 2),
        "scan": {
            "total_files": result["scan"].total_files,
            "total_tokens": result["scan"].total_tokens,
            "languages": result["scan"].languages,
            "manifests": result["scan"].manifests,
            "entrypoints": result["scan"].entrypoints,
        },
        "metrics": result["metrics"],
    }

    benchmark_path = Path(result["output_dir"]) / "BENCHMARK.json"
    benchmark_path.write_text(json.dumps(payload, indent=2) + "\n")
    result["benchmark"] = payload
    return result


def benchmark_suite(manifest_path: str | Path, output_root: str | Path | None = None) -> dict:
    """Run a benchmark suite defined by a JSON manifest."""
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text())
    manifest_dir = manifest_path.parent

    resolved_output_root = (
        Path(output_root).resolve()
        if output_root
        else _resolve_path(manifest.get("output_root", "./output/benchmark-suite"), manifest_dir)
    )
    resolved_output_root.mkdir(parents=True, exist_ok=True)

    suite_results = []
    for item in manifest.get("benchmarks", []):
        bench_id = item["id"]
        root = _resolve_path(item["root"], manifest_dir)
        bench_output_dir = _resolve_path(item.get("output_dir", str(resolved_output_root / bench_id)), manifest_dir)
        result = benchmark_project(root, output_dir=bench_output_dir)
        suite_results.append(
            {
                "id": bench_id,
                "label": item.get("label", bench_id),
                "framework": result["scan"].framework,
                "plugin": result["plugin"],
                "runtime_seconds": result["benchmark"]["runtime_seconds"],
                "scan": {
                    "total_files": result["scan"].total_files,
                    "total_tokens": result["scan"].total_tokens,
                },
                "repo": result["metrics"]["repo"],
                "artifacts": {
                    artifact["name"]: {
                        "source_tokens": artifact["source_tokens"],
                        "output_tokens": artifact["output_tokens"],
                        "compression_ratio": artifact["compression_ratio"],
                    }
                    for artifact in result["metrics"]["artifacts"]
                },
                "output_dir": str(result["output_dir"]),
            }
        )

    payload = {
        "_meta": {
            "extractor": "benchmark_suite_v1",
            "generated_at": timestamp(),
            "manifest": str(manifest_path),
        },
        "suite": manifest.get("name", manifest_path.stem),
        "results": suite_results,
    }

    suite_path = resolved_output_root / "SUITE_RESULTS.json"
    suite_path.write_text(json.dumps(payload, indent=2) + "\n")
    return {
        "manifest": manifest_path,
        "output_root": resolved_output_root,
        "suite_results": payload,
        "suite_path": suite_path,
    }


def _resolve_path(value: str, base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()
