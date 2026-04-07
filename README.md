# TokenSaver

TokenSaver compiles a repository into a small set of machine-readable context files so coding agents can answer common repo questions without opening most source files.

Status: beta

License: MIT

Commercial use is allowed under the MIT license.

The project is intentionally narrow:
- exact token accounting with `tiktoken`
- normalized context artifacts
- deduplicated compression metrics
- core framework plus technology plugins

It does not estimate model pricing or invent savings claims.

## Install

```bash
python3 -m pip install .
```

Installed CLI:

```bash
tokensaver --help
```

Or run directly from the repo:

```bash
python3 tokensaver_cli.py --help
```

## Architecture

TokenSaver is split into three layers:

- `tokensaver/core`: scan/build orchestration, plugin loading, shared models, and exact metrics
- `tokensaver/plugins`: technology-specific extractors such as `flutter`, `react_native`, and the generic fallback
- project overlays: not implemented yet, but intended to allow repo-specific tuning without hard-coding it into plugins

## Commands

```bash
tokensaver scan .
tokensaver build .
tokensaver metrics .
tokensaver benchmark .
tokensaver benchmark-suite benchmarks/manifest.example.json
tokensaver benchmark-suite <manifest.json> --previous <snapshot.json>
tokensaver diff-snapshots <old.json> <new.json>
```

Supported plugin paths today:

- `flutter`
- `react_native`
- `generic` fallback for other detected stacks

## Documentation

- [Output Schema](docs/OUTPUT_SCHEMA.md)
- [Known Limitations](docs/KNOWN_LIMITATIONS.md)
- [Benchmark Guide](benchmarks/README.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

`build` writes these files to `docs/tokensaver/`:

- `PROJECT_SUMMARY.json`
- `COMMANDS.json`
- `MODULE_GRAPH.json`
- `API_INDEX.json`
- `ROUTE_INDEX.json`
- `CONFIG_INDEX.json`
- `METRICS.json`

## Metric Semantics

TokenSaver reports only measurable compression metrics:

- `source_tokens`: exact `tiktoken` count for the files an artifact was derived from
- `output_tokens`: exact `tiktoken` count for the generated artifact
- `compression_ratio`: `source_tokens / output_tokens`
- `union_source_tokens`: exact tokens in the deduplicated union of all artifact source files
- `bundle_tokens`: exact tokens across all generated artifacts
- `overlap_source_tokens`: duplicated source tokens across artifact source sets

`METRICS.json` is the only top-level summary of compression. No dollar estimates are produced.

## Benchmarking

TokenSaver includes a reproducible `benchmark` command for cross-repo validation.

- It runs a full build
- persists `BENCHMARK.json` next to the generated artifacts
- records runtime, framework, selected plugin, exact scan totals, and compression metrics

Suite manifests define multi-repo benchmark runs. Each suite run produces:

- `SUITE_RESULTS.json` — full results with status, failure reasons, and summary metrics
- `SUITE_RESULTS.public.json` — safe public export with private identifiers stripped
- `SUITE_RESULTS.md` — compact Markdown summary
- `history/<timestamp>.json` — timestamped snapshots for regression tracking

Benchmark entries support `id`, `label`, `publish_label`, `root`, `expected_framework`, `tags`, and `private` fields. When `private=true`, public exports use `publish_label` instead of real repo names.

Suite runs are resilient: one repo failure does not abort the whole suite. Each result carries a `status` (`ok`, `partial`, `unsupported`, `failed`) and optional `failure_reason`.

Use `diff-snapshots` to compare two historical snapshots and detect regressions.

See `benchmarks/README.md` for the full manifest format and private-manifest workflow.

## Release Checks

This repo ships with public fixture projects and CI smoke checks.

Run them locally:

```bash
python3 scripts/release_smoke.py
```

The smoke check verifies:

- package imports and `py_compile`
- tracked-file leak scan
- benchmark-suite execution against public fixture repos
- suite JSON/public JSON/Markdown generation

## Output Contract

Every extracted fact should include:

- `source`
- `extractor`
- `confidence`

If TokenSaver cannot determine a value with enough confidence, it should leave that area empty rather than guessing.
