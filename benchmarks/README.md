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

Public fixture smoke suite:

```bash
python3 tokensaver_cli.py benchmark-suite benchmarks/fixtures/manifest.ci.json
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
3. Use `publish_label` for safe public-facing names (e.g., "Confidential Flutter App A")
4. Use safe `id` values that do not reveal repo names (e.g., `flutter-app-a`)
5. Run: `python3 tokensaver_cli.py benchmark-suite benchmarks/local/manifest.private.json`
6. The `benchmarks/local/` directory is entirely gitignored — private manifests and raw outputs are never committed

### Publishing Sanitized Results

To update the tracked public benchmark summaries from a private suite run:

1. Run the private suite: `python3 tokensaver_cli.py benchmark-suite benchmarks/local/manifest.private.json`
2. Review raw results in `benchmarks/local/output/SUITE_RESULTS.json`
3. Select representative repos — prefer those with `ok` status and meaningful coverage
4. Manually copy only anonymized metrics into `benchmarks/results.json` and `benchmarks/results.md`
5. Use only `publish_label` names — never real repo names, paths, or identifiers
6. Run the leak scan: `python3 scripts/release_smoke.py`

### What Must Never Be Committed

- `benchmarks/local/manifest.private.json` (contains absolute paths to private repos)
- `benchmarks/local/output/` (contains raw benchmark outputs with local paths)
- `benchmarks/local/leak_patterns.private.txt` (contains confidential project names)
- Any file containing real repo names, local paths, or machine-specific directories

### Leak Pattern File

Create `benchmarks/local/leak_patterns.private.txt` with one pattern per line. The release smoke test (`scripts/release_smoke.py`) scans all tracked files for these substrings before allowing a release. Patterns should include:

- Machine-specific path prefixes (e.g., `/Users/username`)
- Confidential project names used in the private manifest
- Organization-specific identifiers

Lines starting with `#` are treated as comments.

## Tracked Snapshots

Published benchmark snapshots in `benchmarks/results.json` and `benchmarks/results.md` contain only anonymized data from selected real-world repos. These files must never contain:

- Real repo names or project identifiers
- Local paths or usernames
- Machine-specific directories

The repository also includes public benchmark fixtures under `benchmarks/fixtures/` for CI and smoke testing. These fixtures are synthetic and safe to publish. Fixture results validate framework detection and artifact generation — they are not used for headline compression claims.

## Snapshot History and Diffing

Suite snapshots are saved to `history/<timestamp>.json` under the output directory. Use `diff-snapshots` to compare two snapshots and detect:

- New failures and fixed failures
- Compression ratio regressions and improvements
- Runtime deltas
- Framework detection changes
