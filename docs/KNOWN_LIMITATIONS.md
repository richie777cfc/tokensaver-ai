# Known Limitations

TokenSaver is usable, but it is not omniscient. These are the current boundaries to keep in mind.

## Stack Coverage

First-class extractors currently exist for:

- Flutter
- React Native

Other stacks fall back to generic extraction. The generic plugin provides:

- Module graph based on directory structure
- API index for Express/Node.js routes and Python decorator routes
- Config index for environment variable references
- Commands from `package.json` scripts, Makefiles, and GitHub Actions

Stacks with framework detection but limited artifact depth:

- Rust (detected via `Cargo.toml`)
- Go (detected via `go.mod`)
- Android Native (detected via `build.gradle`)

These produce correct framework detection but generic-quality artifacts.

## Artifact Quality

- Some artifact types compress extremely well (`module_graph`, many route maps).
- Some artifact types are intentionally conservative and may have low compression ratios on small or simple repos.
- Generic stack support can produce `partial` benchmark status when major artifacts are empty or not applicable.
- API index extraction relies on pattern matching; dynamically constructed routes or unconventional frameworks may be missed.

## Public Benchmarks

- Public fixture benchmarks are smoke tests, not performance leaderboards.
- Fixture repos are synthetic and intentionally small.
- Published ratios from fixture projects should be interpreted as contract verification, not product marketing claims.

## Unsupported or Partial Areas

- Monorepo support: TokenSaver scans from a single root. Multi-package monorepos are partially handled via module graph detection but do not receive per-package builds.
- Dynamic route construction: Routes built from string interpolation or runtime values are not extracted.
- Custom build systems: Only `package.json`, `Makefile`, `pyproject.toml`, and GitHub Actions workflows are scanned for commands.
- Non-file configuration: Environment variables loaded from `.env` files are not parsed; only code-level references are extracted.

## Stability

- The output schema is now versioned (`schema_version` in `_meta`) and protected by contract tests.
- The benchmark suite and public-export format are documented and tested.
- The project should still be treated as beta — improvements to extractor quality are expected, especially for non-Flutter and non-React Native stacks.
- See [Compatibility Policy](COMPATIBILITY.md) for backward-compatibility guarantees.
