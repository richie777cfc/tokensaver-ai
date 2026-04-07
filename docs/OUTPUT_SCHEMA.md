# Output Schema

TokenSaver writes machine-readable JSON artifacts intended for coding agents and benchmark tooling.

All canonical artifacts carry `schema_version` in their `_meta` block. See [Compatibility Policy](COMPATIBILITY.md) for versioning rules.

## Schema Version

Current `schema_version`: **1.0.0**

The `schema_version` field describes the output contract. It is distinct from:
- `__version__` (the package version)
- `extractor` (the internal extractor that produced the artifact)

Downstream consumers should key stability expectations on `schema_version`.

## Core Build Outputs

`build` writes these files under `docs/tokensaver/` or the provided output directory:

- `PROJECT_SUMMARY.json`
- `COMMANDS.json`
- `MODULE_GRAPH.json`
- `API_INDEX.json`
- `ROUTE_INDEX.json`
- `CONFIG_INDEX.json`
- `METRICS.json`

### Common `_meta` Shape

Every artifact's `_meta` block includes:

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-04-07T00:00:00+00:00",
  "extractor": "extractor_name_v1",
  "source_files": ["relative/path/to/source.ext"]
}
```

### Stable vs Implementation-Specific

| Field | Stability | Notes |
|-------|-----------|-------|
| `schema_version` | Stable | Follows semver; see Compatibility Policy |
| `generated_at` | Volatile | Changes on every run |
| `extractor` | Implementation | May change without schema version bump |
| `source_files` | Stable shape | Content varies per project |

### Entity Conventions

Extracted entities should carry `source`, `extractor`, and `confidence`:

```json
{
  "value": "...",
  "source": [{"file": "path/to/file.ext", "line": 42}],
  "extractor": "extractor_name_v1",
  "confidence": 0.95
}
```

Metric fields are exact `tiktoken` counts. Top-level repo compression uses deduplicated union source tokens.

## Benchmark Outputs

Single benchmark output:

- `BENCHMARK.json`

Suite output (default mode):

- `SUITE_RESULTS.json`
- `SUITE_RESULTS.public.json`
- `SUITE_RESULTS.md`
- `history/<timestamp>.json`

Suite output (`--public-only` mode):

- `SUITE_RESULTS.public.json`
- `SUITE_RESULTS.md`

## `SUITE_RESULTS.json`

Top-level shape:

```json
{
  "_meta": {
    "schema_version": "1.0.0",
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

- carry `schema_version` in `_meta`
- omit private manifest paths
- anonymize private benchmark ids
- use `publish_label` for private results
- strip local absolute paths from failure strings
- avoid leaking usernames or machine-specific directories

## Public-Only Mode

When `--public-only` is passed to `benchmark-suite`, only public-safe outputs are produced:

- `SUITE_RESULTS.public.json` — sanitized results
- `SUITE_RESULTS.md` — Markdown report derived from public data

No raw `SUITE_RESULTS.json` or `history/` snapshot is written. This is the recommended mode for publishing benchmark results.
Per-benchmark raw artifacts such as `BENCHMARK.json` and generated build outputs are also omitted from the requested output directory.
