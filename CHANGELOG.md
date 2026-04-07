# Changelog

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
