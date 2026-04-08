# Changelog

## 1.2.1

- Renamed the PyPI distribution to `tokensaver-ai` while keeping the CLI command as `tokensaver`
- Simplified package metadata for publishing by switching to SPDX license metadata
- Prepared install docs for the renamed package/repository path
- No schema or CLI behavior changes
## 1.2.0

- Added 4 new first-class framework plugins:
  - **Android Native** (`android_native`) — Activities, Fragments, Jetpack Compose `composable()` navigation, Retrofit `@GET`/`@POST` annotations, Ktor routes, `BuildConfig` field extraction, Gradle dependencies, `strings.xml` resource keys
  - **iOS / Swift** (`ios_swift`) — SwiftUI `View` structs, `NavigationLink`/`navigationDestination`, UIKit `UIViewController` subclasses, segue identifiers, `URLSession`/Alamofire API calls, `UserDefaults`, `@AppStorage`, `ProcessInfo.processInfo.environment`, `Bundle.main.infoDictionary`
  - **React (web)** (`react_web`) — React Router v5 (`<Route path=...>`) + v6 (`{ path: ... }`) routes, `<Link to=...>`, `navigate()` calls, axios/fetch API extraction, `REACT_APP_*` env vars, `.env` file parsing
  - **Angular** (`angular`) — `RouterModule` route definitions, `routerLink`/`router.navigate()`, `HttpClient` API calls, `environment.ts` config keys, `@Component`/`@Injectable` decorators
- Enhanced framework detection:
  - Angular detected via `@angular/core` in `package.json` dependencies
  - iOS detected via `.xcodeproj`/`.xcworkspace`/`Package.swift` presence with `.swift` files
  - Android Native remains the fallback for `build.gradle` without Spring Boot
- Added `.swift` to `CODE_EXTENSIONS` for token accounting
- Updated `module_roots` for Android Native (`app/src/main/java`), iOS (`*.swift` directories), and Angular (`src/app`)
- Removed `react` and `android_native` from the generic plugin's framework set — both now have dedicated first-class plugins
- Total first-class plugin count: 11 (Flutter, React Native, Next.js, Angular, React Web, FastAPI/Django/Flask, Spring Boot, Android Native, iOS Swift, Go) + generic fallback
- Added 4 new benchmark fixtures; fixture suite now covers 13 stacks, all passing with 100% framework detection accuracy
- Fixed README: removed invalid `pip install tokensaver` PyPI link, corrected all install instructions to source-based install, updated support matrix and architecture docs

## 1.1.0

- Added 4 new first-class framework plugins:
  - **Next.js** (`nextjs`) — App Router + Pages Router file-based routes, API route handlers, server actions, `next.config` extraction, `NEXT_PUBLIC_*` env vars
  - **FastAPI / Django / Flask** (`python_web`) — decorator routes, Django URL patterns, ORM/Pydantic models, middleware, `settings.py` keys
  - **Spring Boot** (`spring_boot`) — `@GetMapping`/`@PostMapping` annotations, `@Entity` models, JPA repositories, `application.properties`/`.yml` config
  - **Go** (`go`) — `net/http`, Gin, Chi, Echo, Fiber route extraction, Go structs, `os.Getenv`/Viper config, `go.mod` dependencies
- Enhanced framework detection:
  - Django detected via `manage.py` or dependency mentions
  - FastAPI/Flask detected via `requirements.txt`/`pyproject.toml` dependency names
  - Spring Boot detected via `build.gradle`/`pom.xml` Spring Boot references or `@SpringBootApplication` annotation
- Improved `module_roots` for Go (cmd/internal/pkg convention), Spring Boot (src/main/java), and Python web (app/ directory)
- Total first-class plugin count: 7 (Flutter, React Native, Next.js, FastAPI/Django/Flask, Spring Boot, Go) + generic fallback
- Rewrote README with benchmark tables, one-liner install, architecture diagram, and plugin guide

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
