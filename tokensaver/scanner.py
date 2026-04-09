"""Project scanner focused on exact token accounting."""

from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from tokensaver.tokenizer import count_file_tokens, tokenizer_name
from tokensaver.workspaces import (
    detect_project_framework,
    detect_python_framework,
    detect_workspace_components,
    iter_project_roots,
    top_level_project_roots,
)

SKIP_DIRS = {
    "node_modules",
    ".git",
    "vendor",
    "build",
    ".dart_tool",
    ".gradle",
    "Pods",
    "__pycache__",
    ".next",
    "dist",
    ".build",
    "DerivedData",
    ".pub-cache",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
}

EXT_MAP = {
    ".dart": "dart",
    ".kt": "kotlin",
    ".java": "java",
    ".swift": "swift",
    ".php": "php",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".py": "python",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "csharp",
    ".m": "objc",
    ".h": "c_header",
}

PACKAGE_MANAGER_FILES = {
    "composer.lock": "composer",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "package-lock.json": "npm",
    "bun.lockb": "bun",
    "bun.lock": "bun",
    "poetry.lock": "poetry",
    "uv.lock": "uv",
    "Pipfile.lock": "pipenv",
    "Cargo.lock": "cargo",
    "go.sum": "go",
    "pubspec.lock": "pub",
}


@dataclass
class ScanResult:
    root: str
    project_name: str
    framework: str
    total_files: int = 0
    total_lines: int = 0
    total_bytes: int = 0
    total_tokens: int = 0
    tokenizer: str = tokenizer_name()
    package_managers: list[str] = field(default_factory=list)
    manifests: list[str] = field(default_factory=list)
    languages: dict = field(default_factory=dict)
    top_files: list = field(default_factory=list)
    top_dirs: list = field(default_factory=list)
    entrypoints: list[str] = field(default_factory=list)


def scan_project(root: str | Path) -> ScanResult:
    """Scan a project directory and return exact file and token counts."""
    root = Path(root).resolve()
    framework = _detect_framework(root)
    result = ScanResult(
        root=str(root),
        project_name=root.name or str(root),
        framework=framework,
        package_managers=_detect_package_managers(root),
        manifests=_detect_manifests(root),
        entrypoints=_detect_entrypoints(root),
    )

    lang_bytes = defaultdict(int)
    lang_files = defaultdict(int)
    lang_tokens = defaultdict(int)
    dir_sizes = defaultdict(lambda: {"bytes": 0, "tokens": 0})
    file_sizes = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        rel_dir = os.path.relpath(dirpath, root)

        for fname in filenames:
            fpath = Path(dirpath) / fname
            ext = fpath.suffix.lower()
            if ext not in EXT_MAP:
                continue

            try:
                size = fpath.stat().st_size
                content = fpath.read_text(errors="ignore")
            except OSError:
                continue

            lang = EXT_MAP[ext]
            lines = content.count("\n") + (1 if content else 0)
            tokens = count_file_tokens(fpath, text=content)

            lang_bytes[lang] += size
            lang_files[lang] += 1
            lang_tokens[lang] += tokens

            result.total_files += 1
            result.total_lines += lines
            result.total_bytes += size
            result.total_tokens += tokens

            parts = Path(rel_dir).parts
            top_dir = "." if rel_dir == "." else parts[0]
            dir_sizes[top_dir]["bytes"] += size
            dir_sizes[top_dir]["tokens"] += tokens

            file_sizes.append(
                {
                    "path": os.path.relpath(fpath, root),
                    "bytes": size,
                    "lines": lines,
                    "tokens": tokens,
                }
            )

    result.languages = {
        lang: {
            "files": lang_files[lang],
            "bytes": lang_bytes[lang],
            "tokens": lang_tokens[lang],
        }
        for lang in sorted(lang_tokens, key=lang_tokens.get, reverse=True)
    }
    result.top_files = sorted(file_sizes, key=lambda item: item["tokens"], reverse=True)[:20]
    result.top_dirs = [
        {"dir": name, "bytes": stats["bytes"], "tokens": stats["tokens"]}
        for name, stats in sorted(
            dir_sizes.items(),
            key=lambda item: item[1]["tokens"],
            reverse=True,
        )[:15]
    ]
    return result


def _detect_framework(root: Path) -> str:
    root_framework = detect_project_framework(root)
    nested_components = [item for item in detect_workspace_components(root) if item.root != root]
    nested_project_roots = [path for path in top_level_project_roots(root) if path != root]
    if len(nested_project_roots) >= 2:
        return "workspace"
    if root_framework:
        return root_framework
    for component in nested_components:
        return component.framework
    if any(root.glob("*.php")) or any(child.is_dir() and any(child.glob("*.php")) for child in root.iterdir()):
        return "php"
    if any(root.glob("*.py")) or any(child.is_dir() and (child / "__init__.py").exists() for child in root.iterdir()):
        return "python"
    return "unknown"

def _detect_python_framework(root: Path) -> str | None:
    """Detect specific Python web framework (FastAPI, Django, Flask) or generic Python."""
    return detect_python_framework(root)


def _detect_package_managers(root: Path) -> list[str]:
    managers = []
    seen = set()

    for project_root in iter_project_roots(root):
        project_has_manager = False
        for file_name, manager in PACKAGE_MANAGER_FILES.items():
            if not (project_root / file_name).exists():
                continue
            project_has_manager = True
            if manager not in seen:
                seen.add(manager)
                managers.append(manager)
        if (project_root / "package.json").exists():
            if not project_has_manager and "npm" not in seen:
                seen.add("npm")
                managers.append("npm")
        if (project_root / "pubspec.yaml").exists():
            if not project_has_manager and "pub" not in seen:
                seen.add("pub")
                managers.append("pub")
        if (project_root / "composer.json").exists():
            if not project_has_manager and "composer" not in seen:
                seen.add("composer")
                managers.append("composer")
    return managers


def _detect_manifests(root: Path) -> list[str]:
    manifest_names = [
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "pubspec.yaml",
        "Cargo.toml",
        "go.mod",
        "Dockerfile",
        "composer.json",
        "docker-compose.yml",
        "docker-compose.yaml",
        "Makefile",
    ]
    manifests = []
    seen = set()
    for project_root in iter_project_roots(root):
        for name in manifest_names:
            path = project_root / name
            if not path.exists():
                continue
            rel = str(path.relative_to(root))
            if rel not in seen:
                seen.add(rel)
                manifests.append(rel)
    return manifests


def _detect_entrypoints(root: Path) -> list[str]:
    candidates = [
        "App.tsx",
        "App.js",
        "index.ts",
        "index.js",
        "main.py",
        "app.py",
        "index.php",
        "public/index.php",
        "routes/api.php",
        "manage.py",
        "server.py",
        "tokensaver_cli.py",
        "src/main.ts",
        "src/index.ts",
        "src/index.js",
        "src/app/page.tsx",
        "src/app/layout.tsx",
        "app/main.py",
        "main.dart",
        "lib/main.dart",
    ]
    entrypoints = []
    seen = set()
    for project_root in iter_project_roots(root):
        for candidate in candidates:
            path = project_root / candidate
            if not path.exists():
                continue
            rel = str(path.relative_to(root))
            if rel not in seen:
                seen.add(rel)
                entrypoints.append(rel)
    return entrypoints
