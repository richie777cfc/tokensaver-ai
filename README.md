# TokenSaver

TokenSaver compiles a repository into a small set of machine-readable context files so coding agents can answer common repo questions without opening most source files.

Status: **stable (v1.0.0)**

License: MIT

Commercial use is allowed under the MIT license.

The project is intentionally narrow:
- exact token accounting with `tiktoken`
- normalized context artifacts with stable, versioned output schemas
- deduplicated compression metrics
- core framework plus technology plugins

It does not estimate model pricing or invent savings claims.

## Install

```bash
python3 -m pip install . --no-build-isolation
```

For local source installs in constrained environments, prefer `--no-build-isolation` so pip does not try to download build dependencies.

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
tokensaver benchmark-suite <manifest.json> --public-only
tokensaver diff-snapshots <old.json> <new.json>
```

## Support Matrix

### First-class supported

| Stack | Plugin | Status |
|-------|--------|--------|
| Flutter | `flutter` | First-class extraction: routes, modules, API surface, config, commands |
| React Native | `react_native` | First-class extraction: navigation, modules, API surface, config, commands |

### Generic supported

| Stack | Plugin | Status |
|-------|--------|--------|
| Node.js / Express | `generic` | Commands, Express API routes, mount-path routes, env config, module graph |
| Python (FastAPI, Flask, etc.) | `generic` | Commands (package.json, pyproject.toml, Makefile), decorator API routes, env config, module graph |
| Next.js | `generic` | Commands, file-based routes, env config, module graph |
| React (web) | `generic` | Commands, JSX routes, env config, module graph |

### Detected-only / limited

| Stack | Plugin | Status |
|-------|--------|--------|
| Rust | `generic` | Framework detection via `Cargo.toml`; generic artifact depth |
| Go | `generic` | Framework detection via `go.mod`; generic artifact depth |
| Android Native | `generic` | Framework detection via `build.gradle`; generic artifact depth |

### v1.0 stability bar

All first-class and generic supported stacks are covered by public fixtures, usefulness tests, and contract tests. Every public fixture must produce `ok` benchmark status with non-empty module graphs, commands, and at least one domain artifact (API, routes, or config). Framework detection accuracy is 100% across all fixtures.

## Documentation

- [Output Schema](docs/OUTPUT_SCHEMA.md) — canonical artifact shapes
- [Compatibility Policy](docs/COMPATIBILITY.md) — versioning, backward compatibility, deprecation
- [Known Limitations](docs/KNOWN_LIMITATIONS.md) — current boundaries
- [Benchmark Guide](benchmarks/README.md) — manifest format, privacy workflow
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Build Outputs

`build` writes these files to `docs/tokensaver/`:

- `PROJECT_SUMMARY.json`
- `COMMANDS.json`
- `MODULE_GRAPH.json`
- `API_INDEX.json`
- `ROUTE_INDEX.json`
- `CONFIG_INDEX.json`
- `METRICS.json`

Every artifact carries `schema_version` in its `_meta` block. See [Compatibility Policy](docs/COMPATIBILITY.md) for versioning semantics.

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

### Public-Safe Publishing

Use `--public-only` to generate only public-safe outputs:

```bash
tokensaver benchmark-suite <manifest.json> --output-dir results/ --public-only
```

In this mode, only `SUITE_RESULTS.public.json` and `SUITE_RESULTS.md` are written. No raw suite JSON, history snapshots, or per-benchmark raw artifacts are produced under the output directory. This is the recommended path for publishing benchmark results.

See `benchmarks/README.md` for the full manifest format and private-manifest workflow.

## Release Checks

This repo ships with public fixture projects and CI smoke checks.

Run them locally:

```bash
python3 scripts/release_smoke.py
```

The smoke check verifies:

- package imports and `py_compile`
- tracked-file leak scan (docs, tests, scripts, source)
- schema version presence in all canonical outputs
- benchmark-suite execution against public fixtures
- public-only mode produces only safe outputs
- suite JSON/public JSON/Markdown generation

## Output Contract

Every extracted fact should include:

- `source`
- `extractor`
- `confidence`

Every canonical artifact carries `schema_version` in `_meta`. See [Compatibility Policy](docs/COMPATIBILITY.md).

If TokenSaver cannot determine a value with enough confidence, it should leave that area empty rather than guessing.

## v1.0.0 release criteria (met)

- All contract tests pass for every supported stack
- Public fixtures cover each first-class plugin and three generic stacks (Python, Node, Next.js)
- Usefulness tests verify meaningful artifact content, not just shape
- All public fixtures produce `ok` benchmark status
- Framework detection accuracy is 100% across all fixtures
- Compatibility policy is fully documented and tested
- Schema version is stable at `1.0.0`
- No known regressions in CI
