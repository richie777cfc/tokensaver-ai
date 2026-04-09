"""Workspace discovery helpers for nested multi-app repositories."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

DISCOVERY_SKIP_DIRS = {
    ".git",
    ".next",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "Pods",
    "venv",
}

PROJECT_MARKERS = {
    "composer.json",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "manage.py",
    "uv.lock",
    "Cargo.toml",
    "go.mod",
    "build.gradle",
    "build.gradle.kts",
    "pom.xml",
    "pubspec.yaml",
    "Package.swift",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
}

PYTHON_WEB_FRAMEWORKS = {"fastapi", "django", "flask"}
NODE_FRAMEWORKS = {"node", "react", "react_native", "nextjs", "angular"}


@dataclass(frozen=True)
class WorkspaceComponent:
    root: Path
    framework: str


def iter_project_roots(root: Path, *, max_depth: int = 3) -> list[Path]:
    """Return candidate app roots for a repository, including nested workspaces."""
    root = root.resolve()
    results = [root]
    seen = {root}

    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        try:
            rel = current.relative_to(root)
        except ValueError:
            continue

        depth = len(rel.parts)
        dirnames[:] = [d for d in dirnames if d not in DISCOVERY_SKIP_DIRS and not d.startswith(".")]
        if depth >= max_depth:
            dirnames[:] = []

        if current == root:
            continue

        if any(name in PROJECT_MARKERS for name in filenames):
            resolved = current.resolve()
            if resolved not in seen:
                seen.add(resolved)
                results.append(resolved)

    return sorted(results, key=lambda path: (0 if path == root else 1, str(path.relative_to(root))))


def has_project_marker(project_root: Path) -> bool:
    return any((project_root / marker).exists() for marker in PROJECT_MARKERS)


def top_level_project_roots(root: Path) -> list[Path]:
    roots = iter_project_roots(root)
    pruned: list[Path] = []
    for project_root in roots:
        if project_root == root and not has_project_marker(project_root):
            continue
        if any(project_root != kept and project_root.is_relative_to(kept) for kept in pruned):
            continue
        pruned.append(project_root)
    return pruned


def relative_cwd(root: Path, project_root: Path) -> str:
    rel = project_root.relative_to(root)
    return "." if not rel.parts else str(rel)


def detect_node_framework(project_root: Path) -> str | None:
    package_json = project_root / "package.json"
    if not package_json.exists():
        return None

    try:
        package_data = json.loads(package_json.read_text())
    except json.JSONDecodeError:
        package_data = {}

    deps = {
        **package_data.get("dependencies", {}),
        **package_data.get("devDependencies", {}),
    }
    if "react-native" in deps:
        return "react_native"
    if "next" in deps:
        return "nextjs"
    if "@angular/core" in deps:
        return "angular"
    if "react" in deps:
        return "react"
    return "node"


def _is_ios_project(project_root: Path) -> bool:
    has_xcodeproj = any(project_root.glob("*.xcodeproj")) or any(project_root.glob("*.xcworkspace"))
    has_package_swift = (project_root / "Package.swift").exists()
    if not has_xcodeproj and not has_package_swift:
        return False
    if (project_root / "pubspec.yaml").exists():
        return False
    if (project_root / "package.json").exists():
        return False
    return any(project_root.rglob("*.swift"))


def _has_spring_boot(project_root: Path) -> bool:
    for gradle_name in ("build.gradle.kts", "build.gradle"):
        gradle = project_root / gradle_name
        if gradle.exists():
            content = gradle.read_text(errors="ignore")[:3000]
            if "spring-boot" in content or "org.springframework.boot" in content:
                return True
    pom = project_root / "pom.xml"
    if pom.exists():
        content = pom.read_text(errors="ignore")[:5000]
        if "spring-boot" in content:
            return True
    src_main = project_root / "src" / "main" / "java"
    if src_main.exists():
        for fp in src_main.rglob("*Application.java"):
            try:
                content = fp.read_text(errors="ignore")[:1000]
            except OSError:
                continue
            if "@SpringBootApplication" in content:
                return True
    return False


def detect_python_framework(project_root: Path) -> str | None:
    has_manage_py = (project_root / "manage.py").exists()
    has_pyproject = (project_root / "pyproject.toml").exists()
    has_requirements = (project_root / "requirements.txt").exists()
    has_uv_lock = (project_root / "uv.lock").exists()

    if not has_manage_py and not has_pyproject and not has_requirements and not has_uv_lock:
        return None

    if has_manage_py:
        return "django"

    dep_content = ""
    for name in ("requirements.txt", "pyproject.toml", "uv.lock"):
        path = project_root / name
        if not path.exists():
            continue
        try:
            dep_content += path.read_text(errors="ignore").lower()
        except OSError:
            continue

    if "django" in dep_content:
        return "django"
    if "fastapi" in dep_content:
        return "fastapi"
    if "flask" in dep_content:
        return "flask"
    return "python"


def detect_project_framework(project_root: Path) -> str | None:
    if (project_root / "pubspec.yaml").exists():
        return "flutter"
    if _is_ios_project(project_root):
        return "ios_swift"

    node_framework = detect_node_framework(project_root)
    if node_framework:
        return node_framework

    if (project_root / "build.gradle.kts").exists() or (project_root / "build.gradle").exists():
        return "spring_boot" if _has_spring_boot(project_root) else "android_native"

    if (project_root / "pom.xml").exists() and _has_spring_boot(project_root):
        return "spring_boot"

    python_framework = detect_python_framework(project_root)
    if python_framework:
        return python_framework

    if (project_root / "Cargo.toml").exists():
        return "rust"
    if (project_root / "go.mod").exists():
        return "go"
    if (project_root / "composer.json").exists():
        return "php"
    if any(project_root.glob("*.php")):
        return "php"
    return None


def detect_workspace_components(root: Path) -> list[WorkspaceComponent]:
    components = []
    for project_root in top_level_project_roots(root):
        framework = detect_project_framework(project_root)
        if framework:
            components.append(WorkspaceComponent(root=project_root, framework=framework))
    return components
