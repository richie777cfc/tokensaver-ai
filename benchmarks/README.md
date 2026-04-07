# Benchmarks

## Running Benchmarks

Single repo:

```bash
python3 tokensaver_cli.py benchmark <repo> --output-dir <dir>
```

Suite from manifest:

```bash
python3 tokensaver_cli.py benchmark-suite <manifest.json> --output-dir <dir>
```

Compare two snapshots:

```bash
python3 tokensaver_cli.py diff-snapshots <old-snapshot.json> <new-snapshot.json>
```

Compare against a previous run:

```bash
python3 tokensaver_cli.py benchmark-suite <manifest.json> --previous <snapshot.json>
```

## Outputs

Each single benchmark writes:

- `BENCHMARK.json`: runtime, selected plugin, scan totals, and exact compression metrics
- The standard TokenSaver artifacts

Each suite run writes:

- `SUITE_RESULTS.json`: full results with status, failure reasons, and summary metrics
- `SUITE_RESULTS.public.json`: safe public export with private paths/names stripped
- `SUITE_RESULTS.md`: compact Markdown summary
- `history/<timestamp>.json`: timestamped snapshot for regression tracking

## Manifest Format

Suite manifests define a list of benchmarks to run. See `manifest.example.json` for the full schema.

Per-benchmark entry fields:

| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | Unique identifier for the benchmark |
| `label` | no | Human-readable label for local/private use |
| `publish_label` | no | Safe public label (used in public exports when `private=true`) |
| `root` | yes | Absolute or relative path to the project |
| `expected_framework` | no | Expected framework for detection-accuracy reporting |
| `tags` | no | Arbitrary metadata tags for grouping |
| `private` | no | If `true`, local paths and names are stripped from public exports |

## Status Values

Each benchmark result includes a `status` field:

| Status | Meaning |
|--------|---------|
| `ok` | Run succeeded with expected outputs |
| `partial` | Run succeeded but one or more major artifacts are empty |
| `unsupported` | Framework or plugin not supported |
| `failed` | Benchmark crashed or required output missing |

## Summary Metrics

Suite-level summary includes:

- `benchmark_count`, `success_count`, `failed_count`, `unsupported_count`, `partial_count`
- `success_rate`, `framework_detection_accuracy`
- `per_stack` breakdown with repo count, success count, median runtime, median compression
- `artifact_presence_rate`, `empty_artifact_rate`, `low_value_artifact_rate`

## Privacy

Public exports (`SUITE_RESULTS.public.json`) never include:

- Local absolute paths
- Raw repo names when `private=true`
- User home directories or machine-specific paths
- Private manifest file paths

## Private Local Manifest Workflow

For running benchmarks against private local repos:

1. Create `benchmarks/local/manifest.private.json` (this path is gitignored)
2. Set `private: true` for entries with confidential repo names
3. Use `publish_label` for safe public-facing names
4. Run: `python3 tokensaver_cli.py benchmark-suite benchmarks/local/manifest.private.json`
5. The `benchmarks/local/` directory is entirely gitignored — private manifests and raw outputs are never committed

## Tracked Snapshots

Published benchmark snapshots in `benchmarks/results.json` and `benchmarks/results.md` contain only anonymized data. Do not add confidential repo names or local paths to these files.

## Snapshot History and Diffing

Suite snapshots are saved to `history/<timestamp>.json` under the output directory. Use `diff-snapshots` to compare two snapshots and detect:

- New failures and fixed failures
- Compression ratio regressions and improvements
- Runtime deltas
- Framework detection changes
