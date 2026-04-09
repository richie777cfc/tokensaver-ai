"""Framework-agnostic artifact builders."""

from __future__ import annotations

import json

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

from tokensaver.core.helpers import categorize_command, language_source_refs, meta, sources, value_with_meta
from tokensaver.core.models import ArtifactResult, BuildContext
from tokensaver.workspaces import iter_project_roots, relative_cwd


def build_common_artifacts(ctx: BuildContext) -> list[ArtifactResult]:
    return [
        build_project_summary(ctx),
        build_commands(ctx),
    ]


def build_project_summary(ctx: BuildContext) -> ArtifactResult:
    root = ctx.root
    scan = ctx.scan
    source_files = {root / path for path in scan.manifests + scan.entrypoints if (root / path).exists()}
    source_files.update(path for path in root.glob("README*") if path.is_file())

    payload = {
        "_meta": meta(root, "project_summary_v1", source_files),
        "project_name": value_with_meta(scan.project_name, [], "project_summary_v1", 1.0),
        "framework": value_with_meta(scan.framework, sources(root, source_files), "project_summary_v1", 0.95),
        "tokenizer": value_with_meta(scan.tokenizer, [], "project_summary_v1", 1.0),
        "package_managers": value_with_meta(scan.package_managers, sources(root, source_files), "project_summary_v1", 0.95),
        "languages": [
            {
                "language": language,
                "files": stats["files"],
                "tokens": stats["tokens"],
                "source": language_source_refs(root, language),
                "extractor": "project_summary_v1",
                "confidence": 1.0,
            }
            for language, stats in scan.languages.items()
        ],
        "entrypoints": [
            {
                "path": path,
                "source": [{"file": path}],
                "extractor": "project_summary_v1",
                "confidence": 0.9,
            }
            for path in scan.entrypoints
        ],
        "manifests": [
            {
                "path": path,
                "source": [{"file": path}],
                "extractor": "project_summary_v1",
                "confidence": 1.0,
            }
            for path in scan.manifests
        ],
    }
    return ArtifactResult(
        name="project_summary",
        file_name="PROJECT_SUMMARY.json",
        payload=payload,
        source_files=source_files,
        entity_count=len(payload["languages"]) + len(payload["entrypoints"]) + len(payload["manifests"]),
    )


def build_commands(ctx: BuildContext) -> ArtifactResult:
    root = ctx.root
    commands = []
    source_files = set()

    for project_root in iter_project_roots(root):
        cwd = relative_cwd(root, project_root)

        package_json = project_root / "package.json"
        if package_json.exists():
            try:
                package_data = json.loads(package_json.read_text())
            except json.JSONDecodeError:
                package_data = {}
            rel_package = str(package_json.relative_to(root))
            for name, command in package_data.get("scripts", {}).items():
                scoped_name = name if cwd == "." else f"{cwd}:{name}"
                commands.append(
                    {
                        "name": scoped_name,
                        "category": categorize_command(name),
                        "command": command,
                        "cwd": cwd,
                        "verified": False,
                        "source": [{"file": rel_package}],
                        "extractor": "package_json_scripts_v1",
                        "confidence": 1.0,
                    }
                )
            source_files.add(package_json)

        pyproject = project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                pyproject_data = tomllib.loads(pyproject.read_text())
            except Exception:
                pyproject_data = {}
            rel_pyproject = str(pyproject.relative_to(root))
            for name, command in pyproject_data.get("project", {}).get("scripts", {}).items():
                scoped_name = name if cwd == "." else f"{cwd}:{name}"
                commands.append(
                    {
                        "name": scoped_name,
                        "category": categorize_command(name),
                        "command": command,
                        "cwd": cwd,
                        "verified": False,
                        "source": [{"file": rel_pyproject}],
                        "extractor": "pyproject_scripts_v1",
                        "confidence": 1.0,
                    }
                )
            for name, command in pyproject_data.get("tool", {}).get("taskipy", {}).get("tasks", {}).items():
                scoped_name = name if cwd == "." else f"{cwd}:{name}"
                commands.append(
                    {
                        "name": scoped_name,
                        "category": categorize_command(name),
                        "command": command if isinstance(command, str) else str(command),
                        "cwd": cwd,
                        "verified": False,
                        "source": [{"file": rel_pyproject}],
                        "extractor": "pyproject_taskipy_v1",
                        "confidence": 0.9,
                    }
                )
            if pyproject_data:
                source_files.add(pyproject)

        composer_json = project_root / "composer.json"
        if composer_json.exists():
            try:
                composer_data = json.loads(composer_json.read_text())
            except json.JSONDecodeError:
                composer_data = {}
            rel_composer = str(composer_json.relative_to(root))
            for name, command in composer_data.get("scripts", {}).items():
                scoped_name = name if cwd == "." else f"{cwd}:{name}"
                if isinstance(command, list):
                    command_text = " && ".join(str(item) for item in command)
                else:
                    command_text = str(command)
                commands.append(
                    {
                        "name": scoped_name,
                        "category": categorize_command(name),
                        "command": command_text,
                        "cwd": cwd,
                        "verified": False,
                        "source": [{"file": rel_composer}],
                        "extractor": "composer_scripts_v1",
                        "confidence": 1.0,
                    }
                )
            source_files.add(composer_json)

    makefile = root / "Makefile"
    if makefile.exists():
        for line_no, line in enumerate(makefile.read_text(errors="ignore").splitlines(), start=1):
            if not line or line.startswith("\t") or line.startswith("#") or ":" not in line:
                continue
            target = line.split(":", 1)[0].strip()
            if not target or " " in target or "." in target:
                continue
            commands.append(
                {
                    "name": target,
                    "category": categorize_command(target),
                    "command": f"make {target}",
                    "cwd": ".",
                    "verified": False,
                    "source": [{"file": "Makefile", "line": line_no}],
                    "extractor": "makefile_targets_v1",
                    "confidence": 0.95,
                }
            )
        source_files.add(makefile)

    workflow_dir = root / ".github" / "workflows"
    if workflow_dir.exists():
        for workflow_file in sorted(workflow_dir.glob("*.y*ml")):
            for line_no, line in enumerate(workflow_file.read_text(errors="ignore").splitlines(), start=1):
                if not line:
                    continue
                match = __import__("re").search(r"^\s*run:\s*(.+)$", line)
                if not match:
                    continue
                commands.append(
                    {
                        "name": f"{workflow_file.stem}:{line_no}",
                        "category": "ci",
                        "command": match.group(1).strip(),
                        "cwd": ".",
                        "verified": False,
                        "source": [{"file": str(workflow_file.relative_to(root)), "line": line_no}],
                        "extractor": "github_actions_run_v1",
                        "confidence": 0.75,
                    }
                )
            source_files.add(workflow_file)

    flutter_commands = [
        ("pub_get", "setup", "flutter pub get", 0.95),
        ("run", "dev", "flutter run", 0.95),
        ("test", "test", "flutter test", 0.95),
        ("analyze", "lint", "flutter analyze", 0.95),
    ]
    for project_root in iter_project_roots(root):
        pubspec = project_root / "pubspec.yaml"
        if not pubspec.exists():
            continue
        cwd = relative_cwd(root, project_root)
        rel_pubspec = str(pubspec.relative_to(root))
        for name, category, command, confidence in flutter_commands:
            scoped_name = name if cwd == "." else f"{cwd}:{name}"
            commands.append(
                {
                    "name": scoped_name,
                    "category": category,
                    "command": command,
                    "cwd": cwd,
                    "verified": False,
                    "source": [{"file": rel_pubspec}],
                    "extractor": "flutter_standard_commands_v1",
                    "confidence": confidence,
                }
            )
        source_files.add(pubspec)

    return ArtifactResult(
        name="commands",
        file_name="COMMANDS.json",
        payload={"_meta": meta(root, "commands_v1", source_files), "commands": commands},
        source_files=source_files,
        entity_count=len(commands),
    )
