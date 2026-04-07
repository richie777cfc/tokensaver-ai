# Changelog

## 1.0.1

- Fixed packaged CLI installation by including `tokensaver_cli.py` in setuptools `py-modules`
- Strengthened release smoke checks to verify the installed CLI module is importable
- Clarified local install guidance for source installs in constrained environments

## 1.0.0

- Promoted from beta to stable v1.0.0
- Generic plugin improvements:
  - Python `module_roots` now discovers `src/` subdirectories and falls back to root when only top-level `.py` files exist
  - Added Express mount-path route extraction (`app.use("/path", router)`)
  - Added Python route decorator extraction for `route_index`
  - Added `.env` / `.env.example` / `.env.sample` file parsing for `config_index`
  - Added `pyproject.toml` `[project.scripts]` and `[tool.taskipy.tasks]` command extraction
- Benchmark status logic updated: requires at least 2 non-empty major artifacts for `ok` status, acknowledging that not all artifact types apply to all stacks
- Added Next.js public fixture with file-based routes, API routes, env config, and commands
- Expanded Python fixture with package directory structure, route decorators, and env references
- Added usefulness tests (`test_artifact_usefulness.py`) verifying meaningful content for all supported stacks
- Strengthened fixture-suite contract tests: all public fixtures must be present, none may be `failed`, all supported fixtures must be `ok`
- All 5 public fixtures (Flutter, React Native, Python, Node, Next.js) now produce `ok` benchmark status
- Framework detection accuracy is 100% across all fixtures
- Updated support matrix documentation with explicit first-class / generic supported / detected-only tiers
- Updated release smoke checks to validate all 5 fixtures

## 0.5.0

- Added explicit `schema_version` to all canonical artifact `_meta` blocks
- Added compatibility policy documentation (`docs/COMPATIBILITY.md`)
- Added contract/golden tests for build output shapes, public export sanitization, and fixture suite stability
- Added `--public-only` mode to `benchmark-suite` for safe publishing (omits raw JSON and history)
- Added Node.js backend public fixture for generic plugin coverage
- Strengthened CI with contract test steps, public-only verification, and schema version checks
- Extended release smoke script to scan docs, tests, and scripts for leaks; verify schema versions; and test public-only mode
- Updated support matrix, readiness docs, and output schema documentation
- Updated output schema docs to document `schema_version`, stable vs volatile fields, and public-only mode

## 0.4.0

- Added schema, limitations, changelog, and contribution docs
- Added unit tests for benchmark privacy, summary, diffing, and fixture suite output
- Added CI unit-test coverage alongside release smoke checks
- Promoted the public release status from alpha to beta

## 0.3.0

- Added MIT licensing for open commercial use
- Added installable package metadata and `tokensaver` CLI entrypoint
- Added public benchmark fixture suite for Flutter, React Native, and Python
- Added release smoke checks and GitHub Actions CI
- Added benchmark suite history, public export, and diff support
- Hardened benchmark privacy handling for public outputs
- Fixed generic Python API benchmark extraction
