# Output Schema

TokenSaver writes machine-readable JSON artifacts intended for coding agents and benchmark tooling.

## Core Build Outputs

`build` writes these files under `docs/tokensaver/` or the provided output directory:

- `PROJECT_SUMMARY.json`
- `COMMANDS.json`
- `MODULE_GRAPH.json`
- `API_INDEX.json`
- `ROUTE_INDEX.json`
- `CONFIG_INDEX.json`
- `METRICS.json`

Common conventions:

- extracted entities should carry `source`, `extractor`, and `confidence`
- metric fields are exact `tiktoken` counts
- top-level repo compression uses deduplicated union source tokens

## Benchmark Outputs

Single benchmark output:

- `BENCHMARK.json`

Suite output:

- `SUITE_RESULTS.json`
- `SUITE_RESULTS.public.json`
- `SUITE_RESULTS.md`
- `history/<timestamp>.json`

## `SUITE_RESULTS.json`

Top-level shape:

```json
{
  "_meta": {
    "extractor": "benchmark_suite_v2",
    "generated_at": "2026-04-07T00:00:00+00:00",
    "manifest": "/local/path/manifest.json"
  },
  "suite": "example-suite",
  "summary": {},
  "results": []
}
```

Per-result fields:

- `id`
- `label`
- `publish_label`
- `expected_framework`
- `tags`
- `private`
- `detected_framework`
- `plugin`
- `status`
- `failure_reason`
- `runtime_seconds`
- `scan`
- `repo`
- `artifacts`

## Status Values

- `ok`: run succeeded with expected major artifacts present
- `partial`: run succeeded but one or more major artifacts are empty or missing
- `unsupported`: framework is unknown
- `failed`: benchmark crashed or required output was not produced

## `summary`

Suite summaries include:

- `benchmark_count`
- `success_count`
- `failed_count`
- `unsupported_count`
- `partial_count`
- `success_rate`
- `framework_detection_accuracy`
- `per_stack`
- `artifact_presence_rate`
- `empty_artifact_rate`
- `low_value_artifact_rate`

## Public Export Rules

`SUITE_RESULTS.public.json` must:

- omit private manifest paths
- anonymize private benchmark ids
- use `publish_label` for private results
- strip local absolute paths from failure strings
- avoid leaking usernames or machine-specific directories
