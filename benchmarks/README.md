# Benchmarks

Use `python3 tokensaver_cli.py benchmark <repo> --output-dir <dir>` to generate a reproducible benchmark bundle.

Each benchmark run writes:

- `BENCHMARK.json`: runtime, selected plugin, scan totals, and exact compression metrics
- the standard TokenSaver artifacts (`PROJECT_SUMMARY.json`, `COMMANDS.json`, `MODULE_GRAPH.json`, `API_INDEX.json`, `ROUTE_INDEX.json`, `CONFIG_INDEX.json`, `METRICS.json`)

The goal is not leaderboard-style claims. The goal is to keep framework-level benchmark runs auditable and repeatable across supported repositories.
