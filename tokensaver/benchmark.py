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
