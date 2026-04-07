# Benchmarks

Use `python3 tokensaver_cli.py benchmark <repo> --output-dir <dir>` to generate a reproducible benchmark bundle.
Use `python3 tokensaver_cli.py benchmark-suite <manifest.json> --output-dir <dir>` to run multiple benchmarks from one manifest.

Each benchmark run writes:

- `BENCHMARK.json`: runtime, selected plugin, scan totals, and exact compression metrics
- the standard TokenSaver artifacts (`PROJECT_SUMMARY.json`, `COMMANDS.json`, `MODULE_GRAPH.json`, `API_INDEX.json`, `ROUTE_INDEX.json`, `CONFIG_INDEX.json`, `METRICS.json`)

Tracked benchmark snapshots live in:

- `benchmarks/results.json`
- `benchmarks/results.md`

An example local suite manifest is provided in:

- `benchmarks/manifest.example.json`

The goal is not leaderboard-style claims. The goal is to keep framework-level benchmark runs auditable and repeatable across supported repositories.
