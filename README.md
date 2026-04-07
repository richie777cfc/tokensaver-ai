# TokenSaver

TokenSaver compiles a repository into a small set of machine-readable context files so coding agents can answer common repo questions without opening most source files.

The project is intentionally narrow:
- exact token accounting with `tiktoken`
- normalized context artifacts
- deduplicated compression metrics
- core framework plus technology plugins

It does not estimate model pricing or invent savings claims.

## Architecture

TokenSaver is split into three layers:

- `tokensaver/core`: scan/build orchestration, plugin loading, shared models, and exact metrics
- `tokensaver/plugins`: technology-specific extractors such as `flutter`, `react_native`, and the generic fallback
- project overlays: not implemented yet, but intended to allow repo-specific tuning without hard-coding it into plugins

## Commands

```bash
python3 tokensaver_cli.py scan .
python3 tokensaver_cli.py build .
python3 tokensaver_cli.py metrics .
python3 tokensaver_cli.py benchmark .
```

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

This is intended to be framework-level validation, similar in spirit to open benchmark harnesses such as [MemPalace](https://github.com/milla-jovovich/mempalace), but the reported numbers stay focused on exact token compression rather than retrieval-quality claims.

## Output Contract

Every extracted fact should include:

- `source`
- `extractor`
- `confidence`

If TokenSaver cannot determine a value with enough confidence, it should leave that area empty rather than guessing.
