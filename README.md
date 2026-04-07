# TokenSaver

**Compile any repository into minimal agent context — with exact token compression metrics.**

```bash
pip install --no-build-isolation .
tokensaver build .
# Done. Exact metrics. Stable schema. Agent-ready context.
```

TokenSaver scans your codebase, extracts the structural facts that coding agents actually need (modules, APIs, routes, config, commands), and compresses them into 7 compact JSON artifacts. Agents read **thousands** of tokens instead of **hundreds of thousands**.

---

## Why TokenSaver?

| Without TokenSaver | With TokenSaver |
|---|---|
| Agent reads 800K tokens of raw source | Agent reads ~15K tokens of structured context |
| Every prompt re-parses the entire codebase | Artifacts are pre-built, cached, and incremental |
| No awareness of project structure | Module graph, API index, route map, config keys |
| Context window fills up fast | Exact per-artifact and repo-level compression metrics |

**Published real-world benchmarks** (anonymized, exact `tiktoken` counts):

| Repo | Framework | Source tokens | Bundle tokens | Compression |
|---|---|
| Confidential Flutter App A | `flutter` | 8,510,170 covered-set tokens | 157,466 | **54.04x** |
| Confidential React Native App B | `react_native` | 804,476 covered-set tokens | 28,394 | **28.33x** |

Public fixture benchmarks are used for contract validation and support coverage, not headline compression claims.

---

## Quick Start

### Install from source

```bash
git clone https://github.com/richie777cfc/tokensaver.git
cd tokensaver
pip install --no-build-isolation .
```

### Scan

```bash
tokensaver scan /path/to/repo
```

Outputs exact file counts, token counts, detected framework, and language breakdown.

### Build

```bash
tokensaver build /path/to/repo
```

Generates 7 artifacts in `docs/tokensaver/` and auto-installs agent integrations for **Cursor**, **Claude Code**, **Codex**, and **Windsurf**.

### Incremental Rebuild

```bash
tokensaver build /path/to/repo
# Only changed artifacts are regenerated (SHA-256 diffing)

tokensaver build /path/to/repo --force
# Force full rebuild
```

### Impact Analysis

```bash
tokensaver impact /path/to/repo
# Shows blast-radius: which modules, APIs, routes are affected by recent changes

tokensaver impact /path/to/repo --files src/auth/login.py,src/models/user.py
```

### MCP Server

```bash
pip install --no-build-isolation ".[mcp]"
tokensaver serve /path/to/repo
# Starts MCP server — agents can query modules, APIs, routes interactively
```

---

## Supported Frameworks (15 stacks, 11 plugins)

### First-Class Plugins (deep extraction)

| Framework | Plugin | Detection | What's Extracted |
|---|---|---|---|
| **Flutter** | `flutter` | `pubspec.yaml` | GetX routes, Dart API URLs, RemoteConfig keys, module graph |
| **React Native** | `react_native` | `package.json` → `react-native` | Stack.Screen navigation, Axios/fetch APIs, RN Config, module graph |
| **Next.js** | `nextjs` | `package.json` → `next` | App Router + Pages Router, API routes, server actions, `next.config`, `NEXT_PUBLIC_*` env |
| **Angular** | `angular` | `package.json` → `@angular/core` | RouterModule routes, HttpClient APIs, `environment.ts` config, `@Component`/`@Injectable` |
| **React (web)** | `react_web` | `package.json` → `react` | React Router v5+v6, fetch/axios APIs, `REACT_APP_*` env, lazy imports |
| **FastAPI** | `python_web` | deps → `fastapi` | Decorator routes, Pydantic models, middleware, env config |
| **Django** | `python_web` | `manage.py` or deps → `django` | URL patterns, ORM models, middleware, `settings.py` keys |
| **Flask** | `python_web` | deps → `flask` | Route decorators, models, middleware, env config |
| **Spring Boot** | `spring_boot` | `build.gradle`/`pom.xml` → `spring-boot` | `@GetMapping`/`@PostMapping`, `@Entity` models, JPA repos, `application.properties`/`.yml` |
| **Android Native** | `android_native` | `build.gradle` (non-Spring) | Activities, Fragments, Jetpack Compose `composable()` routes, Retrofit APIs, `BuildConfig`, `strings.xml` |
| **iOS (Swift)** | `ios_swift` | `.xcodeproj` / `Package.swift` | SwiftUI Views, NavigationLink, UIKit ViewControllers, URLSession/Alamofire APIs, UserDefaults, `@AppStorage`, Info.plist |
| **Go** | `go` | `go.mod` | `net/http`, Gin, Chi, Echo, Fiber routes, structs, `os.Getenv`, Viper config, `go.mod` deps |

### Generic Fallback (all other projects)

| Framework | Detection | What's Extracted |
|---|---|---|
| Node.js / Express | `package.json` | Express routes, mount paths, `process.env`, module graph |
| Python (generic) | `*.py` files | Decorator routes, env config, module graph |
| Rust | `Cargo.toml` | Module graph, framework detection |

---

## Benchmark Results (13 fixture suite)

All 13 fixtures pass with `ok` status, 100% framework detection accuracy:

| Fixture | Framework | Status | Plugin |
|---|---|---|---|
| Flutter | `flutter` | ok | `flutter` |
| React Native | `react_native` | ok | `react_native` |
| Next.js | `nextjs` | ok | `nextjs` |
| Angular | `angular` | ok | `angular` |
| React Web | `react` | ok | `react_web` |
| FastAPI | `fastapi` | ok | `python_web` |
| Django | `django` | ok | `python_web` |
| Spring Boot | `spring_boot` | ok | `spring_boot` |
| Android Native | `android_native` | ok | `android_native` |
| iOS Swift | `ios_swift` | ok | `ios_swift` |
| Go | `go` | ok | `go` |
| Node.js | `node` | ok | `generic` |
| Python | `python` | ok | `generic` |

---

## Build Outputs

`tokensaver build` generates these artifacts:

| Artifact | Contents |
|---|---|
| `PROJECT_SUMMARY.json` | Framework, languages, entrypoints, manifests |
| `COMMANDS.json` | Build/dev/test/lint commands from package.json, Makefile, CI |
| `MODULE_GRAPH.json` | Module names, file counts, token counts |
| `API_INDEX.json` | API endpoints with methods, paths, source locations |
| `ROUTE_INDEX.json` | UI routes / URL patterns with navigation graph |
| `CONFIG_INDEX.json` | Environment variables, settings keys, config references |
| `METRICS.json` | Exact compression metrics per artifact and overall |

Every artifact carries `schema_version` in `_meta`. See [Output Schema](docs/OUTPUT_SCHEMA.md).

---

## Agent Integrations

`tokensaver build` automatically installs integration files so agents pick up context without manual referencing:

| Agent | File Generated | How It Works |
|---|---|---|
| **Cursor** | `.cursor/rules/tokensaver.mdc` | Auto-injected as context rule |
| **Claude Code** | `CLAUDE.md` | Read by Claude on project open |
| **Codex** | `AGENTS.md` | Read by Codex on project open |
| **Windsurf** | `.windsurfrules` | Read by Windsurf on project open |
| **Cursor MCP** | `.cursor/mcp.json` | Interactive MCP querying |
| **Claude MCP** | `.mcp.json` | Interactive MCP querying |

---

## Architecture

```
tokensaver/
  core/             # Scan, build orchestration, plugin protocol, shared models
    plugin_api.py    # TokenSaverPlugin protocol
    registry.py      # Plugin registry (ordered matching)
    helpers.py       # Shared regex patterns, utilities
    models.py        # ArtifactResult, BuildContext
  plugins/           # Framework-specific extractors
    flutter.py       # Flutter (GetX, Dart APIs, RemoteConfig)
    react_native.py  # React Native (Stack navigation, Axios)
    nextjs.py        # Next.js (App Router, API routes, server actions)
    angular.py       # Angular (RouterModule, HttpClient, environment.ts)
    react_web.py     # React web (React Router, fetch/axios, REACT_APP_*)
    python_web.py    # FastAPI / Django / Flask
    spring_boot.py   # Spring Boot (annotations, JPA, properties)
    android_native.py # Android (Compose, Retrofit, BuildConfig, strings.xml)
    ios_swift.py     # iOS (SwiftUI, UIKit, URLSession, UserDefaults)
    go_mod.py        # Go (net/http, Gin, Chi, Echo, Fiber)
    generic.py       # Fallback for all other stacks
  scanner.py         # Framework detection + token accounting
  build.py           # Build orchestration + incremental diffing
  snapshot.py        # SHA-256 snapshot for incremental builds
  impact.py          # Blast-radius change-impact analysis
  integrations.py    # IDE/agent config file generation
  mcp_server.py      # MCP server (FastMCP)
  benchmark.py       # Reproducible benchmarking + suite runner
tokensaver_cli.py    # CLI entry point
```

---

## CLI Reference

```bash
tokensaver scan <path>                                    # Scan and report token counts
tokensaver build <path> [--output-dir <dir>] [--force]    # Build artifacts
tokensaver impact <path> [--files f1,f2]                  # Blast-radius analysis
tokensaver serve <path>                                   # Start MCP server
tokensaver metrics <path>                                 # Print existing metrics
tokensaver benchmark <path>                               # Run reproducible benchmark
tokensaver benchmark-suite <manifest>                     # Run multi-repo benchmark suite
tokensaver diff-snapshots <old> <new>                     # Compare benchmark snapshots
```

---

## Adding a New Plugin

TokenSaver's plugin system is designed for easy extension. Each plugin is ~200-300 lines:

1. Create `tokensaver/plugins/your_framework.py`
2. Implement the `TokenSaverPlugin` protocol: `name`, `frameworks`, `build_artifacts(ctx)`
3. Return 4 artifacts: `module_graph`, `api_index`, `route_index`, `config_index`
4. Register in `tokensaver/core/registry.py`
5. Add framework detection in `tokensaver/scanner.py`

```python
@dataclass(frozen=True)
class YourPlugin:
    name: str = "your_framework"
    frameworks: set[str] = frozenset({"your_framework"})

    def build_artifacts(self, ctx: BuildContext) -> list[ArtifactResult]:
        return [
            build_module_graph(ctx),
            build_api_index(ctx),
            build_route_index(ctx),
            build_config_index(ctx),
        ]
```

---

## Metric Semantics

TokenSaver reports only **measurable** compression metrics — no estimates, no dollar claims:

| Metric | Definition |
|---|---|
| `source_tokens` | Exact `tiktoken` (o200k_base) count for source files |
| `output_tokens` | Exact count for generated artifact |
| `compression_ratio` | `source_tokens / output_tokens` |
| `union_source_tokens` | Deduplicated token count across all source files |
| `bundle_tokens` | Total tokens across all artifacts |

---

## Benchmarking

```bash
tokensaver benchmark .                    # Single repo
tokensaver benchmark-suite manifest.json  # Multi-repo suite
tokensaver benchmark-suite manifest.json --public-only  # Safe for publishing
tokensaver diff-snapshots old.json new.json  # Regression detection
```

See [Benchmark Guide](benchmarks/README.md) for manifest format.

---

## Documentation

- [Output Schema](docs/OUTPUT_SCHEMA.md) — canonical artifact shapes
- [Compatibility Policy](docs/COMPATIBILITY.md) — versioning and backward compatibility
- [Known Limitations](docs/KNOWN_LIMITATIONS.md) — current boundaries
- [Benchmark Guide](benchmarks/README.md) — manifest format, privacy workflow
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

## License

MIT — commercial use allowed.
