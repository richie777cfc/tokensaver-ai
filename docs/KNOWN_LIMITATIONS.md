# Known Limitations

TokenSaver is usable, but it is not omniscient. These are the current boundaries to keep in mind.

## Stack Coverage

### First-class supported

First-class extractors currently exist for:

- Flutter
- React Native
- Next.js
- Workspace (multi-app)
- Angular
- React (web)
- FastAPI
- Django
- Flask
- Spring Boot
- Android Native
- iOS Swift
- Go

These stacks have dedicated plugins with deep extraction for routes, navigation, API surfaces, config, and commands.

### Generic supported

The generic plugin provides useful artifacts for:

- Node.js / Express
- Python (FastAPI, Flask, decorator-based frameworks)
- PHP
- Next.js
- React (web)

The generic plugin provides:

- Module graph based on directory structure
- API index for Express/Node.js routes, Python decorator routes, and generic PHP router calls
- Route index for Express mount paths, React Router `<Route>` elements, Next.js file-based routes, Python decorator routes, and generic PHP router calls
- Config index for environment variable references (`process.env`, `os.getenv`, `os.environ`, `getenv`, `$_ENV`, `$_SERVER`, `.env` files)
- Commands from `package.json` scripts, `pyproject.toml` scripts, `composer.json` scripts, Makefiles, and GitHub Actions

### Detected-only / limited

Stacks with framework detection but limited artifact depth:

- Rust (detected via `Cargo.toml`)
- Go (detected via `go.mod`)
- Android Native (detected via `build.gradle`)

These produce correct framework detection but generic-quality artifacts.

## Artifact Quality

- Some artifact types compress extremely well (`module_graph`, many route maps).
- Some artifact types are intentionally conservative and may have low compression ratios on small or simple repos.
- API index extraction relies on pattern matching; dynamically constructed routes or unconventional frameworks may be missed.
- Not all artifact types apply to all stacks. The status logic considers a benchmark `ok` when at least two major artifacts contain extracted data, acknowledging that some artifact types are inherently inapplicable for certain stacks.

## Public Benchmarks

- Public fixture benchmarks are smoke tests, not performance leaderboards.
- Fixture repos are synthetic and intentionally small.
- Published ratios from fixture projects should be interpreted as contract verification, not product marketing claims.

## Unsupported or Partial Areas

- Monorepo support: TokenSaver now detects common nested multi-app workspaces such as `frontend/` + `backend/`, but broader multi-package monorepos still do not receive fully independent per-package builds.
- Dynamic route construction: Routes built from string interpolation or runtime values are not extracted.
- Custom build systems: Only `package.json`, `pyproject.toml`, `composer.json`, `Makefile`, and GitHub Actions workflows are scanned for commands.
- Non-file configuration: `.env` file keys are extracted if the file exists, but `.env` parsing is limited to simple `KEY=value` lines.

## Stability

- The output schema is versioned (`schema_version` in `_meta`) and protected by contract tests.
- The benchmark suite and public-export format are documented and tested.
- Usefulness tests verify that artifacts contain meaningful extracted data for all supported stacks.
- See [Compatibility Policy](COMPATIBILITY.md) for backward-compatibility guarantees.
